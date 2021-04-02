import json, collections, os, glob, sys
import local_utilities as lu

BASE_DIR = '/badc/cmip6/data/'

##`CMIP/E3SM-Project/E3SM-1-1-ECA/piControl/r1i1p1f1/Lmon/mrsos/gr/v20191218/mrsos_Lmon_E3SM-1-1-ECA_piControl_r1i1p1f1_gr_195001-195912.nc

TEMPLATE = '%(base)s/%(era)s/%(mip)s/%(inst)s/%(model)s/%(expt)s/%(variant)s/%(table)s/%(var)s/%(grid)s/%(version)s/'

class Rprep( object ):
    def __init__(self,with_limits=True, group=1):
        ee01 = json.load( open( 'data/c3s34g_variables.json', 'r' ) )
        req = ee01['requested']
        sreq = set()
        for t,l in req.items():
          for v in l:
            sreq.add( '%s.%s' % (t,v) )
        jfile = "handle_scan_report_20201019.json"
        ee = json.load( open( 'data/%s' % jfile, 'r' ) )
        ff = dict()
        nf1 = 0
        nf2 = 0
        np2 = 0
        lims = lu.get_new_ranges()
        kkkk = 0
        print( sreq )
        print ( len( ee['results'].keys() ) )
        ##sys.exit(0)
        for h in ee['results'].keys():
            print (kkkk,h)
            d = ee['results'][h]
            kkkk += 1
            if d['qc_status'] == 'pass' or d['dataset_qc']['error_severity'] != 'major':
              ds = d['dset_id']
              this = dict( dset_id=ds )
              era,mip,inst,model,expt,variant,table,var,grid,version = ds.split('.')
              ##if '%s.%s' % (table,var) in sreq and mip == 'CMIP':
              if True:
                base=BASE_DIR
                p1 = TEMPLATE % locals()
                if not os.path.isdir( p1 ):
                    ## print ('NOT FOUND: %s' % p1 )
                    nf1 += 1
                    if nf1 == 5000:
                       sys.exit(0)
                    this['qc_status'] = 'ERROR'
                    this['qc_message'] = 'Dataset not present at STFC'
                else:
                    fl = glob.glob( '%s/*.nc' % p1 )
                    if len( fl ) == 0:
                      this['qc_status'] = 'ERROR'
                      this['qc_message'] = 'Dataset at STFC empty'
                    else:
                      this['qc_status'] = 'pass'
                      this['files'] = [x.rpartition('/')[-1] for x in sorted( list( fl) )] 
                      this['dir'] = p1
                if this['qc_status'] == 'pass' and with_limits:
                   var_id = '%s.%s' % (table,var)
                   if var_id not in lims:
                      this['qc_status'] = 'ERROR'
                      this['qc_message'] = 'No variable limits provided'

                if this['qc_status'] != 'pass':
                 ##  print (ds,this['qc_status'])
                   nf2 += 1
                else:
                   np2 += 1
                ff[h] = this

        print( np2, nf2, nf1 )
        oo = open( 'scanned_dset_for_qc_%2.2i.json' % group, 'w' )
        json.dump( {'info':{"title":"List of Scanned Datasets and their Files"}, 'data':ff}, oo, indent=4, sort_keys=True )
        oo.close()

class Rsplat(object):
  def __init__(self,group=1):
     self.group=group
     jfile = "handle_scan_report_extended_20201019.json"
     jfile = 'scanned_dset_for_qc_%2.2i.json' % group
     jfile = '../_work/QC_template.json'
     jfile = '../_work/QC_template_v3_20210317.json'
     jfile = '../_work/QC_template_v5_2021-03-25.json'
     ee = json.load( open( jfile, 'r' ) )
     cc = collections.defaultdict( list )
     ff = collections.defaultdict( list )
     __all__ = True
     __ignore_qc__ = True
##
## was ee['data'] for group 3
##
     for h,d in ee['datasets'].items():
       ds = d['dset_id']
       era,mip,inst,model,expt,variant,table,var,grid,version = ds.split('.')
       d['file_root'] = '_'.join( [var,table,model,expt,variant,grid] )
       if 'dir' not in d:
         d['dir'] = '/badc/cmip6/data/CMIP6/%s/%s/%s/%s/%s/%s/%s/%s/%s/' % (mip,inst,model,expt,variant,table,var,grid,version)
#/badc/cmip6/data//CMIP6/ScenarioMIP/CCCma/CanESM5/ssp126/r1i1p1f1/AERmon/od550aer/gn/v20190429/
       if table == 'fx':
         print ( '001: %s' % ds )
       if __ignore_qc__ or d['qc_status'] == 'pass' or (__all__ and d['qc_status'] != 'ERROR'):
         cc[(expt,table,var)].append( d )
       elif d['qc_message'] == 'No variable limits provided':
           ff[(table,var)].append(ds)
     self.cc = cc
     self.ff = ff

  def analysis(self):
      ks = sorted( list( self.ff.keys() ), key=lambda x:len( self.ff[x] ) )
      for k in ks[-20:]:
          print( k,len( self.ff[k] ) )
      print( len(ks) )

  def splat(self):
     cc = self.cc

     for k,item in cc.items():
       d0 = 'inputs_%2.2i/%s' %  (self.group,k[0])
       if not os.path.isdir(d0):
         os.mkdir( d0 )
       oo = open( 'inputs_%2.2i/%s/x1_%s_%s.txt' % (self.group,*k), 'w' )
       for d in item:
         if k[1] == 'fx':
           print ( '002: %s, %s' % (d['dset_id'], len( d['files'])) )
         d1 = d['dir']
         l1 = len( d['file_root'] )
         for fhdl,f in d['files'].items():
           if f['filename'][:l1] != d['file_root']:
             print( 'SKIP BAD FILE NAME: %s -- %s' % (f['filename'], d['dset_id'] ) )
           else:
             oo.write( '%s/%s\n' % (d1,f['filename']) )
       oo.close()
       

def scan_group(a='inputs_05b', var='Omon.sos', input_key='x3a', out_key='x4'):
  """INCOMPLETE"""
  tab,vn = var.split( '.' )
  dl = glob.glob( '%s/*' % a )
  fl = []
  nn = 0
  na = 0
  nnn =0
  np = 0
  for d in dl:
    fl = sorted( list( glob.glob( '%s/%s_%s_%s.txt' % (d,input_key,tab,vn) ) ) )
    for  file_manifest in sorted( fl ):
       pl = [x.strip() for x in open(file_manifest).readlines() ]
       np += len(pl)
       flo = []
       flo2 = []
       for p in pl:
         if not( os.path.isfile( p ) ):
           if os.path.isfile( p[:-2] ):
             na += 1
           else:
       ##      print( p )
             nn += 1
             flo.append(p)
         else:
           fn = p.rpartition( '/' )[-1]
           fs = fn.rpartition( '.' )[0]
           thisf = 'out_05/%s/%s' % (var,fs)
           if not os.path.isfile( thisf ):
             nnn += 1
             flo.append(p)
           else:
             ii = open( thisf ).readlines()
             if len(ii) == 0 or (len( ii[-1] ) < 9) or (ii[-1][:9] != 'OK: tc900'):
               nnn+=1
               print ( 'FILE INCOMPLETE: %s' % thisf )
               flo2.append(p)
               os.rename( thisf, 'incomplete_05b/%s' % thisf.rpartition( '/' )[-1] )

       if len(flo) > 0 or len(flo2) > 0:
         #op = file_manifest.replace( 'inputs_05', 'inputs_05b' )
         op = file_manifest
         op1 = op.replace( '%s_' % input_key, '%sa_' % out_key )
         op2 = op.replace( '%s_' % input_key, '%sb_' % out_key )
         #diro = d.replace( 'inputs_05', 'inputs_05b' )
         diro = d
         if not os.path.isdir( diro ):
           os.mkdir( diro )
         if len( flo + flo2 ) > 0:
           oo = open( op1, 'w' )
           for l in flo + flo2:
             oo.write(l + '\n' )
           oo.close()
         if len( flo2 ) > 0:
           oo = open( op2, 'w' )
           for l in flo2:
             oo.write(l + '\n' )
           oo.close()
           
  print( var, np, na, nn, nnn )

def compare_groups(a='inputs_06',b='inputs_05'):
  """INCOMPLETE"""
  dl = glob.glob( '%s/*' % a )
  fl = []
  for d in dl:
    for f in glob.glob( '%s/*.txt' % d ):
      fl.append( f )
  for  f in sorted( fl ):
     f0 = f.replace( a,b )
     if not os.path.isfile( f0 ):
       print( 'MISSING: %s' % f0 )
     else:
       s = set( [x.strip() for x in open(f).readlines() ] )
       s0 = set( [x.strip() for x in open(f).readlines() ] )

if __name__ == '__main__':
  ##rp = Rprep(with_limits=False, group=3)
  import sys
  ##vars = [x.strip() for x in open( 'data/vars.txt' ).readlines()]
  vars = [x.strip() for x in open( 'vars3.txt' ).readlines()]
  if len(sys.argv) > 1:
    if sys.argv[1] == '-s':
#
# text .. run with specific variable
       scan_group(a='inputs_06',var='Amon.ts')
    elif sys.argv[1] == '-S':
#
# current production: run over coded subset
#
       tt = 'bar'
       if len( sys.argv ) == 3:
         tt = sys.argv[2]
       for v in vars:
         tab = v.rpartition('.')[0]
         if tt == 'bar' and tab not in ['Amon','Omon']:
           scan_group(a='inputs_06',var=v)
         elif tt == tab or tt == 'all':
           scan_group(a='inputs_07',var=v, input_key='x1', out_key='x4')
  else:
    r = Rsplat(group=7)
    r.splat()
    r.analysis()
