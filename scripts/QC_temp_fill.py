import json, collections, os


def run():
     ee = json.load( open('../_work/QC_template.json' ) )
     dsl = ee['datasets'].items()
     cc = collections.defaultdict( set )
     print (len(dsl) )
     for k,this in dsl:
       id = this['dset_id']
##"dset_id": "CMIP6.ScenarioMIP.MOHC.UKESM1-0-LL.ssp119.r1i1p1f2.Lmon.mrro.gn.v20190830",
       era, mip, inst, model, expt, variant, table, var, grid, version = id.split('.')
## tas_Amon_GFDL-CM4_ssp585_r1i1p1f1_gr1.json
       id2 = '_'.join( [var,table,model,expt,variant,grid] )
       cc[ '%s.%s' % (table,var) ].add( (id2,k) )
     print (cc.keys())
     for k in sorted( cc.keys() ):
       if not os.path.isdir( 'json_rep_05/%s' % k ):
         print ('MISSING: %s' % k )
       else:
         ok = 0
         nn = 0
         nnh = 0
         for id2, kk in cc[k]:
           this_targ = ee['datasets'][kk]
           if os.path.isfile( 'json_rep_05/%s/%s.json' % (k,id2) ):
              this_item = json.load( open( 'json_rep_05/%s/%s.json' % (k,id2) ) )
              this_targ['qc_status'] = this_item['qc_status']
              this_targ['dataset_qc']['error_message'] = this_item['dataset_qc']['error_message']
              this_targ['dataset_qc']['error_severity'] = this_item['dataset_qc']['error_severity']
              for h in this_targ['files']:
                if h not in this_item['files']:
                   nnh+=1
                else:
                   for x in ['error_message','error_severity','filename']:
                      this_targ['files'][h][x] = this_item['files'][h][x]
                   this_targ['files'][h]['qc_status'] = this_item['files'][h]['error_status']
              ok +=1
           else:
              nn += 1
         print ('OK: %s (%s -- %s) [%s]' % (k,ok,nn,nnh) )

     oo = open( 'QC_ranges.json', 'w' )
     json.dump( ee, oo, indent=4, sort_keys=True )
     oo.close()


run()
