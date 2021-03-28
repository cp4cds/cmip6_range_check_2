import json, collections

def ingest01(file='../_work/QC_template.json'):
    ee = json.load( open( file ) )
    ds = ee['datasets']
    cc = collections.defaultdict( lambda :collections.defaultdict(set) )
    oo = open( 'QC_template_flist_March2021.txt', 'w' )
    oo2 = open( 'c3s34g_pids_qcTest_March2021.txt', 'w' )
    for k,rec in ds.items():
        oo.write( '\t'.join( ['>',k,rec['dset_id']] ) + '\n' )
        era,mip,inst,source,expt,variant,table,var,grid, version = rec['dset_id'].split('.')
        cc[ (era,mip,inst,source,expt) ][variant].add( (var,table) )
        oo2.write( ','.join( [rec['dset_id'],k] ) + '\n' )
        for kk,rr in rec['files'].items():
          oo.write( '\t'.join( ['+',kk,rr['filename']] ) + '\n' )
    ks = [x for x,v in cc.items() if len( v.keys() ) > 1]
    for k in sorted(ks):
        this = cc[k]
        ss = set()
        for ki,i in this.items():
            for s in i:
                ss.add(s)
        kks = sorted( list( this.keys() ), key=lambda x: len(this[x]) )
        if all( [x in ss for x in [('vas','Amon'),('uas','Amon')]] ):
          if not all( [x in this[kks[-1]] for x in [('vas','Amon'),('uas','Amon')]] ):
            msg = 'u/vas split'
          else:
            msg = ''
        print ('.'.join(k),'|'.join( ['%s (%s)' % (kk,len(vv)) for kk,vv in cc[k].items()] ), msg )
        ##for kk in kks:
            ##print ('--',kk,this[kk])
    oo.close()
    oo2.close()
    print (len(ks))

ingest01(file ='../_work/QC_template_v5_2021-03-25.json')
