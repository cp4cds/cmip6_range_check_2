
import pyesgf
import pyesgf.search as search
import collections, os, shelve, sys
from report_utils import BaseUtils
import glob

import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


nodes = {'CMIP6':['esgf-index1.ceda.ac.uk','esgf-node.ipsl.upmc.fr','esgf-index1.ceda.ac.uk'], 'CMIP5':['esgf-index1.ceda.ac.uk']}


class FileCallBack(BaseUtils):
  """The exec method should be called for each file, to accumulate statistics over the file collection.
     Designed to be called from within a loop through datasets."""

  def __init__(self):
    self.cc = collections.defaultdict( int )

  def __call__(self,file):
      self.cc[ self._boxFileSize( file.json['size'] ) ] += 1

## https://cera-www.dkrz.de/WDCC/ui/cerasearch/cerarest/exportcmip6?input=CMIP6.CMIP.IPSL.IPSL-CM6A-LR&wt=XML

class Order(object):
  def __init__(self,activity='CMIP6'):
    self.activity = activity
    self._source = {'CMIP5':'model', 'CMIP6':'source_id'}[activity]
    self._base = {'CMIP5':'sh', 'CMIP6':'sh6'}[activity]
    self._table = {'CMIP5':'cmor_table', 'CMIP6':'table_id'}[activity]
    self._expt = {'CMIP5':'experiment', 'CMIP6':'experiment_id'}[activity]
    self.baseDir = './%s' % self._base
    ml = glob.glob( '%s/*' % self.baseDir )
    el = collections.defaultdict( set )
    for m in ml:
      for x in glob.glob( '%s/*' % m):
        for s in glob.glob( '%s/*' % x ):
#CMIP6.CMIP.MIROC.MIROC6.historical.r9i1p1f1.SImon.siconc.gn.v20181212|esgf-data2.diasjp.net
          dsid,dn = s.split( '|' )
          el[dsid].add( dn )

    print 'Number of datasets: %s' % len(el.keys())
    self.sh = shelve.open( s, 'r' )
    print self.sh.keys()


    ss = set()
    for dsid in el.keys():
      this = dsid.split( '/' )[-1]
      fn = '%s|%s' % (dsid, sorted( list( el[dsid] ) )[0] )
      sh = shelve.open( fn )
      j = sh['json']
      model = j[self._source][0]
      table = j[self._table][0]
      for v in j['variable']:
        ss.add( (model,table,v) )

    oo = open( '%s_mtv.csv' % activity, 'w' )
    for m,t,v in ss:
      oo.write( '\t'.join( [m,t,v] ) + '\n' )
    oo.close()
    
    ##sh6/MIROC6/historical/

class Dataset(object):
  """Class to manage psesgf dataset search results"""
  def __init__(self,nmax=500,activity='CMIP6'):
    self.activity = activity
    self.sz = 0
    self.nf = 0
    self.nd = 0
    self.nmax = nmax
    self.newOnly = True
    self._source = {'CMIP5':'model', 'CMIP6':'source_id'}[activity]
    self._base = {'CMIP5':'sh', 'CMIP6':'sh6'}[activity]
    self._expt = {'CMIP5':'experiment', 'CMIP6':'experiment_id'}[activity]
    self.baseDir = './%s' % self._base

  def review(self,d,lev,fileCallBack=None):
    """First look at a dataset ... d is a pyesgf search result for a dataset"""
    self.lev = lev
    self.fileCallBack = fileCallBack
    ##print d.json.keys()
    self.shnm = self._getShelveName( d.json['id'], d.json[self._source][0], d.json[self._expt][0] )

  def retrieve(self):
          """Get file metadata for a dataset, and store json object in a shelf file;
             the json object is as returned by pyesgf with fielname added"""
          d = self.d
          sh = shelve.open( self.shnm )
          sh['json'] = d.json
          if self.lev[0] > 1:
            files = d.file_context().search()
            for f in files:
              f.json['filename'] = f.filename
              sh[str( '__files__%s' % f.json['id'] )]  = f.json
              if self.fileCallBack != None:
                self.fileCallBack( f )
          self.sz += d.json['size']
          self.nf += d.json['number_of_files']
          sh.close()

  def _getShelveName(self,id, src,expt):
        d1 = '%s/%s' % (self.baseDir,src)
        if not os.path.isdir( d1 ):
          os.mkdir(d1)
        d2 = '%s/%s/%s' % (self.baseDir,src,expt)
        if not os.path.isdir( d2 ):
          os.mkdir(d2)
        thisSh = '%s/%s' % (d2,id )
        return thisSh

  def __call__(self,d,lev,fileCallBack=None):
      self.d = d
      if self.nd > self.nmax:
        return -1
      else:
        self.review(d,lev,fileCallBack=fileCallBack)
        if self.newOnly and os.path.isfile( self.shnm ) :
          pass
        else:
          self.retrieve()
          self.nd += 1
          if (self.nd/500)*500 == self.nd:
             log.info( 'info.001: nd=%s, nf=%s' % (self.nd,self.nf) )
        return 1

class Reporter(object):
  searchUrlTemplate = 'https://%s/esg-search'
  def __init__(self,lev=(1,0)):
    self.lev = lev

  def __call__(self,activity,nmax=1000,src=None,cxOnly=False):
    url = self.searchUrlTemplate % nodes[activity][1]
    c = search.connection.SearchConnection( url=url, distrib=True )
    self.cx = c.new_context( project=activity, source_id=src, experiment_id='historical' )
    if cxOnly:
      log.info( 'info.002: facets: %s' % sorted( self.cx.facet_counts.keys() ) )
      return
    facets = sorted([k for k in self.cx.facet_counts if len( self.cx.facet_counts[k] ) > 0])
##

##
## retrieve dataset level search results 
##
    datasets = self.cx.search()
# ------------------------------------------------
    nd0 = len(datasets)
    fcb = None

    if self.lev[0] > 1:
      fcb = FileCallBack()
    dcb = Dataset(nmax=nmax,activity=activity)

    for d in datasets:
      if dcb(d,self.lev,fileCallBack=fcb) < 0:
        break

    strSz = '%s:: %6.1fTB' % (src,dcb.sz*1.e-12)
    
    print ( 'Number of datasets: %s, Number of files: %s, size: %s' % (dcb.nd, dcb.nf, strSz ) )
    if self.lev[0] > 1:
      print ( ' '.join( ['%s:%s' % (k,fcb.cc[k]) for k in sorted( fcb.cc.keys() )] ) )
    

if __name__ == "__main__":
  r = Reporter(lev=(1,0))
##
  sl = "BCC-CSM2-MR CESM2 CNRM-CM6-1 E3SM-1-0 GFDL-AM4 GISS-E2-1-G IPSL-CM6A-ATM-HR MIROC6 BCC-ESM1 CESM2-WACCM CNRM-ESM2-1 FGOALS-f3-L GFDL-CM4 HadGEM3-GC31-LL IPSL-CM6A-LR MRI-ESM2-0".split()
  sl = "IPSL-CM6A-LR MRI-ESM2-0".split()
  for s in sl:
    r('CMIP6',nmax=50000,src=s)
  
