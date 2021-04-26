""""
   Scan output from consol_to_json.py and create C3S error report.

   Test
   ----
   Initial scan assessing completeness and consistency of json files.

   JprepRanges
   -----------

   Sa
"""
import collections


MASKS = {'LImon.snd': 'fx.sftlf', 'LImon.snw': 'fx.sftlf', 'Lmon.mrro': 'fx.sftlf', 'Lmon.mrsos': 'fx.sftlf', 'Ofx.deptho': 'Ofx.sftof', 'Omon.sos': 'Ofx.sftof', 'Omon.tos': 'Ofx.sftof', 'Omon.zos': 'Ofx.sftof', 'SImon.siconc': 'Ofx.sftof', 'SImon.simass': 'Ofx.sftof', 'SImon.sitemptop': 'SImon.siconc', 'SImon.sithick': 'SImon.siconc', 'fx.mrsofc': 'fx.sftlf'}


schema = {
  "header": {
    "qc_check:": "CF-checker",
    "author": "Ruth Petrie",
    "institution": "CEDA",
    "date": "2020-07-22T09:02:51.352928",
    "version": "1.0"
  },
  "datasets": {
    "<handle>": {
      "dset_id": "<id>",
      "qc_status": "pass|fail",
      "dataset_qc": {
        "error_severity": "na|minor|major|unknown",
        "error_message": "<output from check>|na"
      },
      "files": {
        "<handle>": {
          "filename": "<filename>",
          "qc_status": "pass|fail",
          "error_severity": "na|minor|major|unknown",
          "error_message": "<output from check>|na"
        },
        "<handle>": {
          "filename": "<filename>",
          "qc_status": "pass|fail",
          "error_severity": "na|minor|major|unknown",
          "error_message": "<output from check>|na"
        }
      }
    }
  }
}


class Dcheck(object):
  REQUIRED = dict( datasets = dict( dset_id='identifier', qc_status='IN:pass|fail', dataset_qc='dictionary' ),
                   header = dict( cq_check='name', author='person', institution='name', date='datetime', version='string' ),
                   files = dict( filename='string', qc_status='IN:pass|fail', error_severity='IN:na|minor|major|unknown', error_message='message or na' ) )
  def __init__(self):
    self.errors = dict()

  def check(self,dd):
    assert all( [x in dd.keys() for x in ['header','datasets']] ), 'Dictionary must contain header and datasets entries'
    self.check_header( dd['header'] )
    self.check_datasets( dd['datasets'] )
    if len(self.errors.keys() ) == 0:
      print( 'NO ERRORS FOUND' )
    else:
      print ( self.errors )

  def check_header(self,ee):
    ma = [k for k in self.REQUIRED['header'].keys() if k not in ee]
    if len(ma) != 0:
        self.errors['header'] = 'Missing attribute(s): %s' % (sorted(ma))

  def check_datasets(self,ee):
    cc = collections.defaultdict( int )
    for h,ds in ee.items():
       ma = [k for k in self.REQUIRED['datasets'].keys() if k not in ds]
       for a in ma:
         cc[a] += 1
    if cc.keys() != 0:
      ma = sorted( list( cc.keys() ) )
      self.errors['datasets'] = 'Missing attribute(s): %s' % ', '.join( ['%s (%s)' % (k,cc[k]) for k in ma] )
    

import csv, json, time, glob, os
from local_utilities import get_new_ranges

ds_pass_msg = dict( error_severity='na', error_message='No handle registry errors detected' )

input_dataset_list = 'c3s34g_pids_qcTest_Oct2020.txt'
major_error_codes = {'ERROR.ds.0900'}
minor_error_codes = {'ERROR.ds.0040'}

##workflow_errors_detected = ['Lmon.mrro', 'Amon.psl']
##print('NEED TO REVISIT DATA FOR %s' % workflow_errors_detected )
workflow_errors_detected = []

class Base(object):
    DataRoot = '../../cmip6_range_check/scripts/json_03/'
    DataRoot = './json_05/'

def get_result_directories(root_dir=None):
        if root_dir == None:
          root_dir = Base.DataRoot
        dirs = sorted( [x for x in glob.glob( '%s/*' % root_dir ) if os.path.isdir(x)] )
        dirs_excluded = [x for x in dirs if x.rpartition( '/' )[-1] in workflow_errors_detected]
        dirs_passed = [x for x in dirs if x not in dirs_excluded]
        return dirs_passed,dirs_excluded

class FileReport(object):
  def __init__(self,json_file):
    assert os.path.isfile( json_file )
    self.ee = json.load( open( json_file, 'r' ) )
    dat = self.ee['data']
    files = sorted( list( dat['headers'].keys() ) )
    tmp = collections.defaultdict( set )

    for r in dat['records'].keys():
      fn,xxx,tag = r.rpartition( ':' )
      assert fn[:-3] in files
      ##print( 'xxxx',r,fn,files)
      tmp[fn].add(tag)

    self.records = dict()
    for fn,x in tmp.items():
      self.records[fn] = sorted( list( x ) )

def range_dump( ofile='ranges_clean.csv',c3s_filter=True):
        nr = get_new_ranges()
        ks = sorted( list( nr.keys() ) )
        print(ks)
        if c3s_filter:
          ee = json.load( open('data/c3s34g_variables.json' ) )
          requested = set()
          for k,l in ee['requested'].items():
            for i in l:
              requested.add( '%s.%s' % (k,i) )
          ks = [k for k in ks if k in requested]
        oo = open( ofile, 'w' )
        for k in ks:
          this = nr[k]._asdict()
          #rec = [k,] + [str(this[x].value) for x in ['max', 'min', 'ma_max', 'ma_min', 'max_l0', 'min_l0'] ]
          rec = [k,] + [str(this[x].value) for x in ['max', 'min', 'ma_max', 'ma_min'] ]
          print( rec )
          oo.write( '\t'.join( rec ) + '\n' )
        oo.close()

class Test(Base):
    def __init__(self,idir=None):
        if idir == None:
          idir = self.DataRoot
        nr = get_new_ranges()
        print (nr.keys())
        dirs = sorted( [x for x in glob.glob( '%s/*' % idir ) if os.path.isdir(x)] )
        oo = open( 'jprep_ranges_test.csv','w')
        for d in dirs:
            dn = d.rpartition( '/' )[-1]
            ss = set()
            for f in sorted( glob.glob( '%s/*.json' % d ) ):
                ee = json.load( open( f ) )
                if 'mask' not in ee['data']['summary'].keys():
                  print ('No mask item::',f)
                ss.add( tuple( sorted( ee['data']['summary'].keys() ) ) )
            print( d, dn in nr, ss )
            rec = [str(x) for x in [d,dn in nr, ss, len(ss) == 1]]
            oo.write( '\t'.join(rec) + '\n' )
        oo.close()

def apply_conditional( func, ll, tt, kk ):
   this =  [x[kk] for x in ll if type(x[kk]) == tt ]
   if len( this ) > 0:
     return func( this )
   return None

def record_checks(fn, tags, rcbook,with_mask=False):
     """Look through the NetCDF file level json output and generate QC report.
      current version gets as far as basic information .. need to add ranges , and mask info """
     basic = [ rcbook[ '%s:%s' % (fn,t) ]['basic'] for t in tags ]
     try:
       quantiles = [ rcbook[ '%s:%s' % (fn,t) ]['quantiles'] for t in tags ]
     except:
       print( 'quantiles missing' )
       quantiles = None
     nn = sum( [x[3] for x in basic] )
     try:
       brep = ( min( [x[0] for x in basic] ),
              max( [x[1] for x in basic] ),
              min( [x[2] for x in basic] ),
              max( [x[2] for x in basic] ),
              nn )
     except:
       print( fn, 'FAILED TO EXTRACT EXTREMES, nn=', nn )
       print ( basic[0][0], type( basic[0][0] ) )
       try:
           basicx = [x for x in basic if type(x[0]) == type(1.)]
           brep = ( apply_conditional( min, basic, type(1.0), 0 ),
              apply_conditional( max, basic, type(1.0), 1 ),
              apply_conditional( min, basic, type(1.0), 2 ),
              apply_conditional( max, basic, type(1.0), 2 ),
              nn )
       except:
          print( fn, 'FAILED AGAIN TO EXTRACT EXTREMES', basic)
          raise

     if with_mask:
       try:
         mask = [ rcbook[ '%s:%s' % (fn,t) ]['mask_ok'] for t in tags ]
         mrep = all( [x[0] == 'masks_match' for x in mask ] )
       except:
         mrep = False

     else:
       mrep = None

     if quantiles == None:
       qrep = None
     else:
       try:
         qrep = ( *[ max( [x[k] for x in quantiles] ) for k in range(5)],
                *[ min( [x[-5+k] for x in quantiles] ) for k in range(5)] )
       except:
         qrep = None

     if tags[0].find('-') == -1:
       lrep = None
     else:
       cc = collections.defaultdict( list)      
       for t in tags:
         lev = int( t.split('-')[-1] )
         basic =  rcbook[ '%s:%s' % (fn,t) ]['basic']
         try:
           cc[lev].append( float(basic[0]) )
         except:
           pass
           ##print( 'SKIPPPING LREP BASIC:',basic[0] )
           ##raise

       lrep = []
       for l in range(19):
         if len( cc[l] ) > 0:
           lrep.append( min(cc[l]) )
         else:
           lrep.append(None)

     return brep, mrep, qrep, lrep
  
class Hlook(object):
  def __init__(self):
    ee = json.load( open( '../_work/QC_template_v5_2021-03-25.json' ) )
    self.ee = dict()
    self.ff = dict()
    for h,i in ee['datasets'].items():
      self.ee[h] = i['dset_id']
      self.ff[i['dset_id']] = h

class TestFile(object):
  ATTRIBUTES = ('basic', 'drs', 'empty_count', 'extremes', 'mask', 'quantiles')
  def __init__(self,hlk):
    self.hlk = hlk
    
  def check_file(self,jfile, vmax=None, vmin=None, vmamax=None, vmamin=None, with_mask=False, jrep_file=None, fcsv=None, ffcsv=None, mkd=None):
    print (jfile )
    fr = FileReport( jfile )
    reps = {}
## json_03/Amon.ts/ts_Amon_INM-CM5-0_ssp245_r1i1p1f1_gr1.json
    if jrep_file == None:
      jrep_file = jfile.replace( 'json_', 'json_rep_' )
      tree = jrep_file.split( '/' )
      if tree[0] == '.':
        tree=tree[1:]
      assert os.path.isdir( tree[0] )
      if not os.path.isdir( '/'.join( tree[:2] ) ):
        os.mkdir( '/'.join( tree[:2] ) )
    
    
    ests = set()
    esvs = set()
    dsfail = False
    for fn,tags in fr.records.items():
      fns = fn[:-3]
      tid = fr.ee['data']['headers'][fns]['tech']['file_info']['tid']
      contact = fr.ee['data']['headers'][fns]['tech']['file_info']['contact']
      if contact == None:
        contact = '-'
##
## table, var, inst, model, mip, expt, variant, grid, version
      drs = fr.ee['data']['headers'][fns]['tech']['file_info']['drs']
      table, var, inst, model, mip, expt, variant, grid, version = drs
      path = '/badc/cmip6/data/CMIP6/' + '/'.join( [mip,inst,model,expt,variant,table,var,grid,version] )

#
# should be unique in a set of file records
##
      esgf_id = '.'.join( ['CMIP6', mip, inst, model, expt, variant, table, var, grid, version ] )
      if esgf_id not in self.hlk.ff:
        print( "SEVERE: esgf ID not found: %s" % esgf_id )
        hdl = 'hdl_not_found'
      else:
        hdl = self.hlk.ff[ esgf_id ]

      rcs,mcs,qrep,lrep = record_checks(fn,tags,fr.ee['data']['records'],with_mask=with_mask)

      if rcs[0] == None:
        tests = [False,False]
      else:
        tests = [rcs[0] >= vmin, rcs[1] <= vmax]

      if vmamin != None:
        tests.append( rcs[2] >= vmamin )
      else:
        tests.append( None )
      if vmamax != None:
        tests.append( rcs[3] <= vmamax )
      else:
        tests.append( None )

      tests.append( rcs[4] == 0 )

      if with_mask:
        tests.append ( mcs )
      else:
        tests.append( None )

      emsg = []
      if rcs[0] == None:
        emsg.append( 'Minimum value not found' )
      elif rcs[0] < vmin:
        emsg.append( 'Minimum %s < %s' % (rcs[0],vmin) )

      if rcs[1] == None:
        emsg.append( 'Maximum value not found' )
      elif rcs[1] > vmax:
        emsg.append( 'Maximum %s > %s' % (rcs[1],vmax) )

      if vmamin != None and rcs[2] < vmamin:
        emsg.append( 'Mean absolute %s < %s' % (rcs[2],vmamin) )

      if vmamax != None and rcs[3] > vmamax:
        emsg.append( 'Mean absolute %s > %s' % (rcs[3],vmamax) )

      range_errors = len(emsg) > 0

      if table == 'Amon' and var in ['ta','ua','va','zg','hur','hus']:
        mv_errors = False
      elif table in ['Omon', 'Ofx','Lmon','LImon']:
        mv_errors = False
      elif var in ['mrsofc']:
        mv_errors = False
      else:
        mv_errors = rcs[4] != 0

      if mv_errors:
        emsg.append( 'Missing values flagged' )

      mask_errors = with_mask and (not mcs)
      if mask_errors:
        emsg.append( 'Masks not matching' )

      if len(emsg) == 0:
        error_message = error_severity = 'na'
        error_status = 'pass'
          
      else:
        error_message = '; '.join( emsg)
        if range_errors and (table == 'Omon' or not mv_errors):
           error_status='fail'
           error_severity='major'
           if model == 'HadGEM3-GC31-MM' and var in ['simass','sithick']:
             if tests[0]:
                ## ex01.001: Extreme seaice thickness in HadGEM3-GC31-MM simulations
                error_status = 'pass'
                error_severity = 'minor'
                error_message += '[ex01.001]'
           elif model == 'CIESM' and var in ['rsdt']:
              if rcs[0] > -0.0001:
                error_status = 'pass'
                error_severity = 'minor'
                error_message += '[ex01.005]'
           elif model in ['EC-Earth3','EC-Earth3-Veg-LR', 'EC-Earth3-AerChem','EC-Earth3-CC','EC-Earth3-Veg'] and var in ['rlds','rsus']:
              if rcs[0] > 0.0:
                error_status = 'pass'
                error_severity = 'minor'
                error_message += '[ex01.006]'
              elif qrep != None and qrep[-3] > 0:
                error_status = 'pass'
                error_severity = 'minor'
                error_message += '[ex03.004]'
           elif model in ['KACE-1-0-G'] and var in ['rsus']:
              if rcs[0] > 0.0:
                error_status = 'pass'
                error_severity = 'minor'
                error_message += '[ex02.002]'
           elif model in ['AWI-ESM-1-1-LR', 'AWI-CM-1-1-MR', 'xxGISS-E2-1-H'] and var in ['simass','sithick']:
             if tests[0] and rcs[1] < 300.:
                ## ex01.001: Extreme seaice thickness in GISS-E2-1-H
                error_status = 'pass'
                error_severity = 'minor'
                error_message += '[ex01.002]'
           elif table == 'Omon' and var in ['sos']:
             if rcs[0] > -15. and tests[1]:
                if qrep != None and qrep[-4] > 0:
                  ## ex01.009: slight negative near surface salinity in MPI-M.MPI-ESM1-2-HR
                  error_status = 'pass'
                  error_severity = 'minor'
                  error_message += '[ex01.009]'
                else:
                  print( '###Omon.sos: ',rcs[0],qrep)
             elif rcs[1] < 200. and tests[0]:
                if qrep != None and qrep[1] < 100.:
                  error_status = 'pass'
                  error_severity = 'minor'
                  error_message += '[ex03.003]'
                else:
                  print( '###Omon.sos: ',rcs[1],qrep)
                  ## ex01.009: slight negative near surface salinity in MPI-M.MPI-ESM1-2-HR
           elif model == 'ACCESS-ESM1-5' and var in ['zos']:
             if tests[0]:
                ## ex01.001: Extreme seaice thickness in GISS-E2-1-H
                error_status = 'pass'
                error_severity = 'minor'
                error_message += '[ex01.007]'
           elif model in ['MIROC-ES2L','MIROC6','NorCPM1'] and var in ['zos']:
                ## ex01.001: Extreme seaice thickness in GISS-E2-1-H
                error_status = 'pass'
                error_severity = 'minor'
                error_message += '[ex01.008] Disjoint ocean mesh regions'
           elif model in ['MCM-UA-1-0'] and var in ['huss']:
                if rcs[0] > -0.005:
                  error_status = 'pass'
                  error_severity = 'minor'
                  error_message += '[ex02.005] Small negative values found in the data'
           elif model in ['IITM-ESM', 'MCM-UA-1-0'] and var in ['hus']:
                if rcs[0] > -0.005:
                  error_status = 'pass'
                  error_severity = 'minor'
                  error_message += '[ex02.006] Small negative values found in the data'
           elif var == 'evspsbl' and (not mv_errors) and tests[1]:
              if rcs[0] > -0.0003:
                error_status = 'pass'
                error_severity = 'minor'
                error_message += '[ex01.003]'
           elif table == 'Lmon' and var in ['mrro']:
              if rcs[1] < 0.02 and tests[0]:
                if qrep != None and qrep[4] < 0.004:
                  error_status = 'pass'
                  error_severity = 'minor'
                  error_message += '[ex03.001]'
                else:
                  print( '###Lmon.mrro: ',rcs[1],qrep)
           elif table == 'Lmon' and var in ['mrsos']:
              if rcs[1] < 400 and tests[0]:
                  error_status = 'pass'
                  error_severity = 'minor'
                  error_message += '[ex03.002]'
           elif table == 'Amon' and var in ['hur']:
              if tests[1]:
                if rcs[0] > -10.0:
                  error_status = 'pass'
                  error_severity = 'minor'
                  error_message += '[ex02.007]'
                else:
                  try:
                    if all( [lrep[x] > 0 for x in range(18)] ):
                      error_status = 'pass'
                      error_severity = 'minor'
                      error_message += '[ex03.005]'
                      print( 'LREP PASS ................' )
                  except:
                    pass
                    ## lrep array may have None values ...
           elif table == 'day' and var in ['sfcWind']:
              if rcs[0] > -10.0 and tests[1]:
                error_status = 'pass'
                error_severity = 'minor'
                error_message += '[ex02.003]'
           elif table == 'Amon' and var in ['prsn']:
              if rcs[0] > -1.e-05 and all(tests[1:4]):
                error_status = 'pass'
                error_severity = 'minor'
                error_message += '[ex02.008]'
           elif var == 'areacello' and (not mv_errors) and tests[1] and grid == 'gn':
              if rcs[0] > -0.0002:
                error_status = 'pass'
                error_severity = 'na'
                error_message += '[c01.001]'
           elif var == 'deptho' and (not mv_errors) and tests[0] and model in ['FGOALS-g3','FGOALS-f3-L']:
              if rcs[1] < 2000000:
                error_status = 'pass'
                error_severity = 'na'
                error_message += '[c01.002]'
             
           
        elif mv_errors:
           if table in ['SImon']:
             error_status='pass'
             error_severity='minor'
           elif var in ['sftgif'] and model in ['MIROC-ES2L','CESM2','CESM2-WACCM','ACCESS-CM2','CMCC-CM2-SR5',
                                    'CMCC-ESM2',
                                    'ACCESS-ESM1-5', 'CESM2-FV2', 'CESM2-WACCM-FV2', 'CMCC-CM2-HR4', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1']:
               error_status='pass'
               error_severity='minor'
               error_message += '[ex02.001]'
           elif inst == 'CMCC' and var == 'orog':
             error_status = 'pass'
             error_severity = 'minor'
             error_message += '[ex01.001]'
           else:
             error_status='fail'
             error_severity='major'
        else:
           error_status='pass'
           error_severity='minor'

      ests.add( error_status )
      esvs.add( error_severity )
      reps[tid] = dict( filename=fn, file_error_message = error_message, file_qc_status=error_status, file_error_severity = error_severity )
      if error_status == 'fail':
         dsfail = True
      if fcsv != None:
        fcsv.write( '\t'.join( [path + '/' + fn,error_status,error_severity, error_message] ) + '\n' )
      if ffcsv != None and error_status == 'fail':
        ffcsv.write( '\t'.join( [path + '/' + fn,error_status,error_severity, error_message, tid, contact, hdl, esgf_id] ) + '\n' )
      print ( fn, tests )

    if mkd != None and dsfail:
        id_link = "[%s](https://cera-www.dkrz.de/WDCC/ui/cerasearch/cerarest/exportcmip6?input=%s)" % (esgf_id,esgf_id)
        pid_link = "[%s](http://hdl.handle.net/%s)" % (hdl,hdl[4:])
        mkd.write( '%s: %s [%s]\n' % (id_link,pid_link,contact) )
    print ('OUTPUT TO: %s' % jrep_file )
    oo = open( jrep_file, 'w' )
    if 'fail' in ests:
      qc_status = 'fail'
      dset_error_severity='major'
      dset_error_message='Major errors encountered: details in file error log'
    else:
      qc_status = 'pass'
      dset_error_severity='na' 
      dset_error_message='na'
      if 'minor' in esvs:
        dset_error_message = 'Minor errors encountered: details in file error log'

    jdict = dict( files=reps, dset_id=esgf_id, dset_qc_status=qc_status,
                  dset_error_severity=dset_error_severity, dset_error_message=dset_error_message )
    json.dump( jdict, oo, indent=4, sort_keys=True )
      ##"dset_id": "<id>",
      ##"qc_status": "pass|fail",
      ##"dataset_qc": {
        ##"error_severity": "na|minor|major|unknown",
        ##"error_message": "<output from check>|na"
      ##},
    oo.close()
    return jrep_file, qc_status
        
        

##"filename": "mrro_Lmon_UKESM1-0-LL_ssp119_r1i1p1f2_gn_201501-204912.nc",
                    ##"qc_status": "",
                    ##"error_severity": "",
                    ##"error_message": ""
##pass|fail
##na|minor|major|unknown

      


class JprepRanges(object):
    def __init__(self, version='02-01',test_var='Amon.tas'):
        dirs, excluded = get_result_directories()
        self.dirs = {x.rpartition('/')[-1]:x for x in dirs}
        print ('Excluding: ',excluded )
        self.nr = get_new_ranges()

    def run_test( self, test_var='LImon.snd', all=False, fcsv=None, ffcsv=None, mkd=None ):
        assert test_var in self.nr
        assert test_var in self.dirs
        fl = sorted( glob.glob( '%s/*.json' % self.dirs[test_var] ) )
        tf = TestFile(hlk=Hlook())
        print (self.nr[test_var])
        r = self.nr[test_var]
        if not all:
          tf.check_file( fl[0], vmax=r.max.value, vmin=r.min.value, vmamax=r.ma_max.value, vmamin=r.ma_min.value, with_mask=test_var in MASKS, fcsv=fcsv, ffcsv=ffcsv, mkd=mkd )
        else:
          for f in fl:
            tf.check_file( f, vmax=r.max.value, vmin=r.min.value, vmamax=r.ma_max.value, vmamin=r.ma_min.value, with_mask=test_var in MASKS, fcsv=fcsv, ffcsv=ffcsv, mkd=mkd )

    def run(self):
        
        refile_june = '../esgf_fetch/lists/wg1subset-r1-datasets-pids-clean.csv'
        refile = "../esgf_fetch/lists/%s" % input_dataset_list
        review = 'summary-reviewed_datasets_%s_%s.csv'
        nbad = 0

        self.ref = dict()
        ii = open( refile ).readlines()
        for record in csv.reader( ii[1:], delimiter=',' ):
            if len(record) != 2:
                print ('BAD REF FILE RECORD: ',record)
                nbad +=1
            else:
                dsidv, hdl = record
                self.ref[dsidv.strip()] = hdl.strip()
        assert nbad == 0
        print ( len(self.ref) )

        self.aa = dict()
        self.aa_oflow = dict()
        for tab in ['Amon_s','Amon_c','Lmon','day','Omon','other']:
            f = review % (tab, version)
            print ( 'TABLE - START: %s, len dict: %s' % (tab, len(self.aa) ) )
            self.scan1(f)
            print ( 'TABLE: %s, len dict: %s' % (tab, len(self.aa) ) )
        self.jdump()

    def scan1(self,f):            
        nbad = 0
        ii = open( f ).readlines()
        for record in csv.reader( ii, delimiter='\t' ):
            if len(record) != 5:
                print ('BAD RECORD: ',record)
                nbad +=1
            else:
                dsid, version, f1, f2, mask = record
                dsidv = '%s.%s' % (dsid.strip(), version)
                if dsidv in self.ref:
                    h = self.ref[dsidv]
                    self.aa[h] = ((f1=='OK') and (f2=='OK'), dsid,version,f1,f2,mask)
                else:
                    print( 'WARN.scan.002: dataset not found: ',dsidv)
                    self.aa_oflow[(dsid,version)] = ((f1=='OK') and (f2=='OK'), f1,f2,mask)

        print ( 'INFO.scan.001:', f, len(self.aa), len( [ x for x,v in self.aa.items() if v[0] ] ), len(self.aa_oflow) )
        assert nbad == 0

    def jdump(self,jfile='handle_scan_report_%s.json'):

        title = 'Handle Record QC Report'
        abstract = 'Results from a review of handle records, provided as a dictionary for each handle identifier. Error level 0 indicates no errors found. The report also includes a check on the availability of mask files '
        date = '%4.4i%2.2i%2.2i' % time.gmtime()[:3]
        jf = jfile % date
        ee = {}
        ee2 = {}
        for h,r in self.aa.items():
            dsidv = '%s.%s' % r[1:3]
            if r[0]:
                this = {'qc_status':'pass', 'dset_id':dsidv, 'dataset_qc':ds_pass_msg}
            else:
                eseverity='unknown'
                f1,f2 = r[3:5]
                msg = ''
                if f1 != 'OK':
                    msg = f1
                    ecode = msg.split(':')[0]
                    ecat = 'Handle Registry'
                    if ecode in major_error_codes:
                        eseverity='major'
                    elif ecode in minor_error_codes:
                        eseverity='minor'
                if f2 != 'OK':
                    if msg != '':
                        msg += '; '
                    msg += f2
                    ecat = 'Mask Availability'
                this = {'qc_status':'fail', 'dset_id':dsidv, 
                        'dataset_qc':dict( error_message=msg, error_severity=eseverity, error_category=ecat, error_code=ecode ) }
            that = this.copy()
            if that['qc_status'] == 'pass' and r[5] != 'na':
               that['mask']= r[5]
               print (that['mask'])
            ee[h] = this
            ee2[h] = that
            
        n = len(ee)
        npass = len( [h for h,e in ee.items() if e['qc_status'] == 'pass'] )
        summary = '%s records, %s passed, %s failed' % (n,npass,n-npass)
        print (summary)
        info = dict( source='jprep.py', history='Created at CEDA, based on a scan of handle records',
                  title = title, abstract=abstract, summary=summary,
                  inputs='(1) %s: list of ESGF datasets, (2) filtered to MIP=CMIP or ScenarioMIP' % input_dataset_list,
                  creation_date=time.ctime(),
                  contact='support@ceda.ac.uk (ref C3S 34g,Martin Juckes)' )


        oo = open( jf, 'w' )
        json.dump( {'header':info, 'datasets':ee}, oo, indent=4, sort_keys=True )
        oo.close()
        jf = jfile % ('extended_%s' % date )
        oo = open( jf, 'w' )
        json.dump( {'header':info, 'datasets':ee2}, oo, indent=4, sort_keys=True )
        oo.close()


if __name__ == "__main__":
    import sys
    j = JprepRanges()
    if len(sys.argv) == 1:
    #j = Jprep()
    ##Test()
    ##j.run_test(all=True)
      fcsv = open( 'fx.orog.csv', 'w' )
      j.run_test(test_var='fx.orog', all=True, fcsv=fcsv )
      fcsv.close()
    ##tf = TestFile()
    ##tf.check_file('json_03/Amon.ts/ts_Amon_INM-CM5-0_ssp245_r1i1p1f1_gr1.json')
    elif sys.argv[1] == '-d':
      range_dump()
    elif sys.argv[1] == '-v':
      var = sys.argv[2]
      assert os.path.isdir( 'json_05/%s' % var )
      fcsv = open( 'csv_05b/%s.csv' % var, 'w' )
      ffcsv = open( 'csvf_05b/%s_fails.csv' % var, 'w' )
      mkd = open( 'csvf_05b/%s_fails.md' % var, 'w' )
      j.run_test(test_var=var, all=True, fcsv=fcsv, ffcsv=ffcsv, mkd=mkd )
      fcsv.close()
