import json, collections, os, time

     ## ee = json.load( open('../_work/QC_template.json' ) )
QC_TEMPLATE = '../_work/QC_template_v5_2021-03-25.json'

HEADER = {
        "abstract": "Results from a review of data ranges, provided as a dictionary for each handle identifier. Error level 0 indicates no errors found. The report also includes a check on the availability of mask files ",
        "contact": "support@ceda.ac.uk (ref C3S 34g,Martin Juckes)",
        "creation_date": None,
        "history": "Created at CEDA, based on a scan of all data files",
        "inputs": "QC_template_v5_2021-03-25.json",
        "source": "jprep_ranges.py",
        "summary": None,
        "title": "Data Range QC Report"
    }

SUMMARY_FMT =  "12200 records, 10334 passed, 1866 failed",
SUMMARY_FMT =  "%s records, %s passed, %s failed"

def run():
     oo = open( 'QC_dset_summary.csv', 'w' )
     ee = json.load( open(QC_TEMPLATE ) )
     dsl = ee['datasets'].items()
     cc = collections.defaultdict( set )
     cc2 = collections.defaultdict( lambda : collections.defaultdict(int) )
     print (len(dsl) )
     for k,this in dsl:
       id = this['dset_id']
##"dset_id": "CMIP6.ScenarioMIP.MOHC.UKESM1-0-LL.ssp119.r1i1p1f2.Lmon.mrro.gn.v20190830",
       era, mip, inst, model, expt, variant, table, var, grid, version = id.split('.')
## tas_Amon_GFDL-CM4_ssp585_r1i1p1f1_gr1.json
       id2 = '_'.join( [var,table,model,expt,variant,grid] )
       cc[ '%s.%s' % (table,var) ].add( (id2,k) )
     print (cc.keys())
     print ('Summary: <name> - <dsets>: pass, <minor>, <fail>, <missing>, <missing files> -- pass includes minor, fail includes missing files'  )
     for k in sorted( cc.keys() ):
       table,var = k.split( '.' )
       if not os.path.isdir( 'json_rep_05/%s' % k ):
         print ('MISSING: %s' % k )
         cc2['dset']['MISSING_ALL'] += 1
       elif table == 'Lmonxx':
         cc2['dset']['SKIPPED'] += 1
       else:
         nds = len(cc[k])
         ok = 0
         okm = 0
         nfa = 0
         nfm = 0
         nn = 0
         nnh = 0
         for id2, kk in cc[k]:
           this_targ = ee['datasets'][kk]
           if os.path.isfile( 'json_rep_05/%s/%s.json' % (k,id2) ):
              files_missing = 0
              files_minor = 0
              this_item = json.load( open( 'json_rep_05/%s/%s.json' % (k,id2) ) )
              assert 'dset_qc_status' in this_item, 'File %s has no dset_qc_status:' % id2
              for x in ['dset_error_message','dset_error_severity','dset_id','dset_qc_status']:
                this_targ[x] = this_item.get(x,'')
              for h in this_targ['files']:
                if h not in this_item['files']:
                   ##print( h,this_targ['files'][h]['filename'] )
                   files_missing += 1
                   nnh+=1
                   cc2['file']['MISSING'] += 1
                else:
                   this_file = this_item['files'][h]
                   assert 'file_qc_status' in this_file
                   for x in ['file_error_message','file_error_severity','filename','file_qc_status']:
                      this_targ['files'][h][x] = this_file.get(x,'')
                   cc2['file'][(this_file['file_qc_status'],this_file['file_error_severity'])] += 1
                   if (this_file['file_qc_status'],this_file['file_error_severity']) == ('pass','minor'):
                     files_minor += 1
              if files_missing == 0:
                if files_minor > 0 and this_item['dset_qc_status'] == 'pass' and this_targ['dset_error_severity'] == 'na':
                  this_targ['dset_error_message'] = '%s file(s) with minor errors'  % files_minor
                  this_targ['dset_error_severity'] = 'minor'
              else:
                nfm += 1
                this_targ['dset_error_message'] = this_targ['dset_error_message'] + ' %s file(s) missing'  % files_missing
                this_targ['dset_error_severity'] = 'major'
                this_targ['dset_qc_status'] = 'fail'
              if this_targ['dset_qc_status'] == 'pass':
                ok +=1
                if this_targ['dset_error_severity'] == 'minor':
                  okm +=1
              else:
                nfa += 1
              cc2['dset'][(this_targ['dset_qc_status'],this_targ['dset_error_severity'])] += 1
              oo.write( 'REPORT,%s, %s-%s, %s,\n' % (this_targ['dset_id'], this_targ['dset_qc_status'],this_targ['dset_error_severity'], this_targ['dset_error_message'] ) )
           else:
              nn += 1
              cc2['dset']['MISSING'] += 1
              oo.write( 'MISSING, %s,\n' % this_targ['dset_id'] )
         print ('OK: %16s - %4s: %s, %s, %s, %s, %s' % (k, nds, ok, okm, nfa, nn, nfm) )

     oo.close()
     HEADER['creation_date'] = str( time.ctime() )
     HEADER['summary'] = 'TODO'
     ee['header'] = HEADER
     print( cc2['dset'], cc2['file'] )
     oo = open( 'QC_ranges.json', 'w' )
     json.dump( ee, oo, indent=4, sort_keys=True )
     oo.close()


run()
