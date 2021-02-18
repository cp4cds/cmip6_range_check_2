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

workflow_errors_detected = ['Lmon.mrro', 'Amon.psl']
print('NEED TO REVISIT DATA FOR %s' % workflow_errors_detected )

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

def record_checks(fn, tags, rcbook,with_mask=False):
     """Look through the NetCDF file level json output and generate QC report.
      current version gets as far as basic information .. need to add ranges , and mask info """
     basic = [ rcbook[ '%s:%s' % (fn,t) ]['basic'] for t in tags ]
     brep = ( min( [x[0] for x in basic] ),
              max( [x[1] for x in basic] ),
              min( [x[2] for x in basic] ),
              max( [x[2] for x in basic] ),
              sum( [x[3] for x in basic] ) )

     if with_mask:
       try:
         mask = [ rcbook[ '%s:%s' % (fn,t) ]['mask_ok'] for t in tags ]
         mrep = all( [x[0] == 'masks_match' for x in mask ] )
       except:
         mrep = False

     else:
       mrep = None
     return brep, mrep
  

class TestFile(object):
  ATTRIBUTES = ('basic', 'drs', 'empty_count', 'extremes', 'mask', 'quantiles')
  def __init__(self):
    pass
    
  def check_file(self,jfile, vmax=None, vmin=None, vmamax=None, vmamin=None, with_mask=False, jrep_file=None, fcsv=None):
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
    for fn,tags in fr.records.items():
      fns = fn[:-3]
      tid = fr.ee['data']['headers'][fns]['tech']['file_info']['tid']
##
## table, var, inst, model, mip, expt, variant, grid, version
      drs = fr.ee['data']['headers'][fns]['tech']['file_info']['drs']
      table, var, inst, model, mip, expt, variant, grid, version = drs
      path = '/badc/cmip6/data/CMIP6/' + '/'.join( [mip,inst,model,expt,variant,table,var,grid,version] )

      rcs,mcs = record_checks(fn,tags,fr.ee['data']['records'],with_mask=with_mask)
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
      if rcs[0] < vmin:
        emsg.append( 'Minimum %s < %s' % (rcs[0],vmin) )
      if rcs[1] > vmax:
        emsg.append( 'Maximum %s > %s' % (rcs[1],vmax) )
      if vmamin != None and rcs[2] < vmamin:
        emsg.append( 'Mean absolute %s < %s' % (rcs[2],vmamin) )
      if vmamax != None and rcs[3] > vmamax:
        emsg.append( 'Mean absolute %s > %s' % (rcs[3],vmamax) )

      range_errors = len(emsg) > 0
      mv_errors = rcs[4] != 0
      if rcs[4] != 0:
        emsg.append( 'Missing values flagged' )

      mask_errors = with_mask and (not mcs)
      if mask_errors:
        emsg.append( 'Masks not matching' )

      if len(emsg) == 0:
        error_message = error_severity = 'na'
        error_status = 'pass'
      else:
        error_message = '; '.join( emsg)
        if range_errors or mv_errors:
           error_status='fail'
           error_severity='major'
        else:
           error_status='pass'
           error_severity='minor'

      ests.add( error_status )
      esvs.add( error_severity )
      reps[tid] = dict( filename=fn, error_message = error_message, error_status=error_status, error_severity = error_severity )
      if fcsv != None:
        fcsv.write( '\t'.join( [path + '/' + fn,error_status,error_severity, error_message] ) + '\n' )
      print ( fn, tests )
    print ('OUTPUT TO: %s' % jrep_file )
    oo = open( jrep_file, 'w' )
    if 'fail' in ests:
      qc_status = 'fail'
      dsqc = dict( error_severity='major', error_message='Major errors encountered: details in file error log' )
    else:
      qc_status = 'pass'
      dsqc = dict( error_severity='na', error_message='na' )
      if 'minor' in esvs:
        dsqc['error_message'] = 'Minor errors encountered: details in file error log'
    json.dump( dict( files=reps, dset_id='__todo__', qc_status=qc_status, dataset_qc=dsqc ), oo, indent=4, sort_keys=True )
      ##"dset_id": "<id>",
      ##"qc_status": "pass|fail",
      ##"dataset_qc": {
        ##"error_severity": "na|minor|major|unknown",
        ##"error_message": "<output from check>|na"
      ##},
    oo.close()
    return jrep_file, qc_status, dsqc
        
        

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

    def run_test( self, test_var='LImon.snd', all=False, fcsv=None ):
        assert test_var in self.nr
        assert test_var in self.dirs
        fl = sorted( glob.glob( '%s/*.json' % self.dirs[test_var] ) )
        tf = TestFile()
        print (self.nr[test_var])
        r = self.nr[test_var]
        if not all:
          tf.check_file( fl[0], vmax=r.max.value, vmin=r.min.value, vmamax=r.ma_max.value, vmamin=r.ma_min.value, with_mask=test_var in MASKS, fcsv=fcsv )
        else:
          for f in fl:
            tf.check_file( f, vmax=r.max.value, vmin=r.min.value, vmamax=r.ma_max.value, vmamin=r.ma_min.value, with_mask=test_var in MASKS, fcsv=fcsv )

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
    #j = Jprep()
    ##Test()
    j = JprepRanges()
    ##j.run_test(all=True)
    fcsv = open( 'fx.orog.csv', 'w' )
    j.run_test(test_var='fx.orog', all=True, fcsv=fcsv )
    fcsv.close()
    ##tf = TestFile()
    ##tf.check_file('json_03/Amon.ts/ts_Amon_INM-CM5-0_ssp245_r1i1p1f1_gr1.json')
