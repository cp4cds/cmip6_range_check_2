import json

def ingest01(file='../_work/QC_template.json'):
    ee = json.load( open( file ) )
    ds = ee['datasets']
    oo = open( 'QC_template_flist.txt', 'w' )
    oo2 = open( 'c3s34g_pids_qcTest_Feb2021.txt', 'w' )
    for k,rec in ds.items():
        oo.write( '\t'.join( ['>',k,rec['dset_id']] ) + '\n' )
        oo2.write( ','.join( [rec['dset_id'],k] ) + '\n' )
        for kk,rr in rec['files'].items():
          oo.write( '\t'.join( ['+',kk,rr['filename']] ) + '\n' )
    oo.close()
    oo2.close()

ingest01()
