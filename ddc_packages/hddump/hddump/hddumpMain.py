"""
Demonstration handle dump for CMIP/ESGF files ..

USAGE
=====

 -h: print this message;
 -v: print version;
 -t: run a test
 -f <file name>: examine file, print path to replacement if this file is obsolete, print path to sibling files (or replacements).
 -id <tracking id>: examine handle record of tracking id.
 -V: verbose
 --debug: debug
 --DEBUG: debug with extended output
"""
## see https://www.handle.net/proxy_servlet.html for info on restfull API

import collections, os, re
##import cfdm
try:
  import netCDF4
  NETCDF_SUPPORTED = True
except:
  NETCDF_SUPPORTED = False

import xml
import http
from xml.dom import minidom
import hddump.packageConfig  as packageConfig

import urllib
from urllib import request

from hddump.testdata import *

class Phandle(object):
  
  def __init__(self, hdlDict, k='values'):
    """Obsolete class to parse handle metadat ... replaced by Open class"""
    self.h = hdlDict
    self.d = {}
    try:
      for r in hdlDict[k]:
        self.d[r['type']] = r['data']
    except:
      print ( hdlDict[k] )
      raise

class Remote(object):
  htmpl = 'http://hdl.handle.net/api/handles/%s'
  dh = dummyHandles()
  httpcodes = {x.value:x.name for x in http.HTTPStatus}
  def __init__(self,hdl,url=None):
     """Class to retrieve a handle .. optionally to retrieve from test data.
     Still needs some error handling based on the HTTP response code."""

     if hdl[:5] == 'xxxxx':
       self.msg = self.dh.hh[hdl]
     else:
       if url == None:
         thisid = hdl.replace('hdl:999999', '10876.test' )
         if thisid[:4] == 'hdl:':
           thisid = thisid[4:]
         url = self.htmpl % thisid
       self.fetch(url)

  def fetch(self,url):
     """Retrieve the handle data, using urllib ir requests library; handle metadata is stored in self.msg"""


     try:
        fh = request.urlopen( url ) 
        self.httpCode = fh.getcode()
     except urllib.error.HTTPError as e:
        print ( e.headers )
        print( '%s: %s' % (e.code,self.httpcodes.get(e.code,'????')) )
        self.httpCode = e.code
        raise
     
     msg = eval( fh.read() )

     assert type( msg ) == type( {} ), 'Response of wrong type'
     for k in ['responseCode', 'handle']:
       assert k in msg, 'Required key %s not found: %s' % (k, str( msg.keys() ) )

     self.msg = msg


class Open(object):
  """Create a handle object defined by a handle ID.
  Initial object simply holds the id, to retrieve the object, execute the get() method.
  If the argument is a ";" separated list, the tolist() method should be executed to convert to 
  a list of handle objects before executing the get() method on each element of the list.

  This approach is perhaps a little unusual for an "Open" class ... but works well with given
  handle record structure.
"""
  cache = {}
  htmpl = 'http://hdl.handle.net/api/handles/%s'
  dh = dummyHandles()

  def __init__(self,id,debug=False):
    self.REC_id = id
    self.REC_got = False
    self.debug = debug
    self.rec = dict()

  def __repr__(self):
    return self.REC_id

  def tolist(self):
    if self.REC_id.find( ';' ) == -1:
      return [self, ]
    else:
      this = []
      for id in self.REC_id.split(';'):
        this.append( Open( id.strip() ) )
      return this
    
  def toDict(self):
    if not self.REC_got:
      self.get()
    return self.rec

  def dump(self):
      print (self.toDict() )

  def get(self, extract=True):
    if self.REC_got:
      return
#
# using the class object to store the cache of retrieved handles.
# This enables some caching ... NOT TESTED
#
    if self.REC_id not in self.__class__.cache:
      self.remote = Remote( self.REC_id )
      self.__class__.cache[self.REC_id] = self.remote.msg

    if extract:
      self._extract( self.__class__.cache[self.REC_id] )

  def _extract( self, msg ):
    """Extract alues from a handle message dictionary, and insert into self.rec"""

    if self.debug:
      print( msg.keys() )
      print( msg['handle'] )
    for r in msg['values']:
   
        if str(r['type']) in ['IS_PART_OF','HAS_PARTS','replaces', 'replacedBy', 'isReplacedBy','parent','REPLACED_BY']:
          self.rec[r['type']] = Open( r['data']['value'] ).tolist()

        else:
          self.rec[r['type']] = r['data']['value']

    if self.rec['AGGREGATION_LEVEL'] == 'DATASET':
       self.obsolete = 'REPLACED_BY' in self.rec


  def addLatest(self):
    """Retrieve handle records for replacements until a current dataset is found."""
    if not self.obsolete:
      return
    self.rec['REPLACED_BY'].get()
    self.replacements=[self.rec['REPLACED_BY'],]
    while self.replacements[-1].obsolete:
        self.replacements.append( self.replacements[-1].rec['REPLACED_BY'].get() )
    self.latest = self.replacements[-1]

  def addSiblings(self):
     if self.rec['AGGREGATION_LEVEL'] != 'FILE':
       print( 'No known siblings .....' )
       return

     if 'IS_PART_OF' not in self.rec:
       print( 'No parent' )
       return

     for p in self.IS_PART_OF:
            p.get()

     self.p.obsolete = all( [p.obsolete for p in self.p.rec['IS_PART_OF']] )

     self.siblings = []
     for p in self.rec['IS_PART_OF']:
       for c in p.rec['HAS_PARTS']:
         c.get()
         self.siblings.append( c )

class Main(object):
  """Main: entry point, parsing comman line arguments.

USAGE
-----
    m = Main( argList )
"""
  knownargs0 = ['-h','-v','-t','-V','--debug', '--DEBUG']
  knownargs1 = ['-f','-id']
  re1 = re.compile( 'host="(.*?)"' )
  re2 = re.compile( '<location(.*?)/>' )

  def __init__(self, args):
    self.re_dict = dict()
    for k in ['host','href']:
       self.re_dict[k] = re.compile( '%s="(.*?)"' % k )

    self.htmpl = 'http://hdl.handle.net/api/handles/%s'
    self.version = packageConfig.version
    self.args = args
    self.parseArgs()
    if self.d.get( '-v', False ):
      print ( self.version )
      return

    if self.d.get( '-h', False ):
      print (self.version)
      print ( __doc__ )
      return

    if self.d.get( '-t', False ):
      self.runTest()
      return

    self.debugPlus = '--DEBUG' in self.d
    self.debug = '--debug' in self.d or self.debugPlus
    self.verbose = ( '-V' in self.d ) or self.debug

    if '-f' in self.d:
      fn = self.d['-f']
      self.dumpF(fn)

    if '-id' in self.d:
      id = self.d['-id']
      self.dumpF('',id=id)

  def dumpF(self,fn, id=None):
    """Dump information about a file"""
    if id == None:
      assert os.path.isfile( fn ), 'File %s not found' % fn
      nchead = NcHead( fn )
      thisid = nchead['tracking_id'].replace( 'hdl:999999', '10876.test' )
    else:
      thisid = id.replace('hdl:999999', '10876.test' )

    if self.debug:
      print (thisid)
    self.res = {'id':thisid, 'name':fn}

    self.p = Open(  thisid )
    self.p.get()
    if self.debug:
        print( 'KEYS: ', self.p.rec.keys() )
    if self.debugPlus:
      for k in sorted( self.p.rec.keys() ):
        print( '%s: %s' % (k, self.p.rec[k] ) )
      self._globals( self.p )

    thisType = 'none'

    if 'IS_PART_OF' in self.p.rec:
      thisType = 'file'
      for p in self.p.rec['IS_PART_OF']:
        p.get()
      self.p.obsolete = all( [p.obsolete for p in self.p.rec['IS_PART_OF']] )
      self.res['parents'] = [(p.REC_id, p.rec['DRS_ID'], p.rec['VERSION_NUMBER']) for p in self.p.rec['IS_PART_OF']]
      self.res['obsolete'] = self.p.obsolete
      self.res['RC'] = {False:'OK', True:'OBSOLETE'}[self.res['obsolete']]
      self.res['name'] = self.p.rec['FILE_NAME']
      if not self.p.obsolete:
        current = [p for p in self.p.rec['IS_PART_OF'] if not p.obsolete]
        if not len(current) == 1:
          print ('ERROR: dataset has more than one current version ...' )
        self._extractDataset( current[0] )
#
# Extract replica information. Results will be stored to self.res['replicas']
#
        self._extractReplicas( current[0] )
        


      print( 'File: %(name)s [%(id)s] %(RC)s' % self.res )

    elif 'HAS_PARTS' in self.p.rec:
        thisType = 'ds'
        self._extractDataset( self.p )
#
# Extract replica information. Results will be stored to self.res['replicas']
#
        self._extractReplicas( self.p )
        self.res['obsolete'] = self.p.obsolete
        self.res['RC'] = {False:'OK', True:'OBSOLETE'}[self.res['obsolete']]
        self.res['name'] = self.p.rec['DRS_ID']
        print( 'Dataset: %(name)s [%(id)s] %(RC)s' % self.res )

    elif 'IS_PART_OF' not in self.p.rec:
      print ( 'dumpF - 01' )
      print ( self.p.rec.keys() )
      if self.debug:
        print( 'No parent' )
      self.res['parents'] = None
      return

    if self.verbose:
      if thisType == 'file':
        print( 'Master host: %(master_host)s' % self.res )
        print( '\nDatasets:' )
        for p in self.res['parents'] :
          print( 'ID: %s, NAME: %s, VERSION: %s' % p )
        print( '\nSiblings:' )

        for p in sorted(self.res['siblings'], key=lambda x: x[0]):
          if p[1] != self.res['id']:
            print( 'NAME: %s, ID: %s' % p )

        if len( self.res['replicas'] ) > 0:
          print( '\nReplicas:' )
          for p in self.res['replicas'] :
            print( 'Host: %s' % p )
        else:
          print( '\nNo replicas.' )

      elif thisType == 'ds':
        print( 'Master host: %(master_host)s' % self.res )
        print( '\nFiles:' )
        #for p in self.res['siblings'] :
        for p in sorted(self.res['siblings'], key=lambda x: x[0]):
            print( 'NAME: %s, ID: %s' % p )
        if len( self.res['replicas'] ) > 0:
          print( '\nReplicas:' )
          for p in self.res['replicas'] :
            print( 'Host: %s' % p )
        else:
          print( '\nNo replicas.' )
        
  def _globals(self,current):
    if NETCDF_SUPPORTED:
      self._extractFileURL(current)
      dods = self.res['href'].replace('fileServer','dodsC')
      nc = netCDF4.Dataset( dods )
      for a in sorted( nc.ncattrs() ):
          print ('  %s:: %s' % (a, nc.getncattr( a )) )
    else:
       print ( "Netcdf not supported ... check installation of netCDF4 module")

  def _extractFileURL( self, current ):
        """Extract the file URL from a file handle object"""
        if "URL_ORIGINAL_DATA" in current.rec:
           this = current.rec['URL_ORIGINAL_DATA']
           locs = self.re2.findall( this )
           href = self.re_dict['href'].findall( locs[0] )[0]
           self.res['href'] = href
        else:
            print ('NO URL ORiGINAL DATA')

  def _extractReplicas( self, current ):
        """Extract replica information from a DATASET handle object"""

        if 'REPLICA_NODE' in current.rec:
          rep = current.rec['REPLICA_NODE']
          locs = self.re2.findall( rep )
          reps = [self.re_dict['host'].findall(l)[0] for l in locs]
          self.res['replicas'] = reps
        else:
          self.res['replicas'] = []

  def _extractDataset( self, current ):
        for c in current.rec['HAS_PARTS']:
          c.get()
        self.res['siblings'] = [(c.rec['FILE_NAME'],c.REC_id) for c in current.rec['HAS_PARTS']]
        master = current.rec['HOSTING_NODE']
        this = self.re1.findall( master )
        assert len(this) == 1, 'Unexpected matches in search for master host'
        self.res['master_host'] = this[0]

  def runTest(self):
    """This test does not work any more ... the 10876.test handles appear to have been deleted ... they did not follow the current
    schema.
    """
    ex1 = ['hdl:21.14100/062520a0-f3d8-41bd-8b94-3fe0e4a6ab0e','tas_Amon_MPI-ESM1-2-LR_1pctCO2_r1i1p1f1_gn_185001-186912.nc']
    ex1a = ['REC_id', 'REC_got', 'remote', "URL", 'AGGREGATION_LEVEL', 'FIXED_CONTENT', 'FILE_NAME', 'FILE_SIZE', 'IS_PART_OF', 'FILE_VERSION', 'CHECKSUM', 'CHECKSUM_METHOD', 'URL_ORIGINAL_DATA', "URL_REPLICA", 'HS_ADMIN', 'filename']
    hdl = ex1[0]
    self.p = Open( hdl )
    self.p.get()
    expected = ["URL", 'AGGREGATION_LEVEL', 'FILE_NAME', 'FILE_SIZE', 'IS_PART_OF', 'FILE_VERSION', 'CHECKSUM', 'CHECKSUM_METHOD', 'URL_ORIGINAL_DATA', "URL_REPLICA", 'HS_ADMIN']
## 'REPLACED_BY' if obsolete
    for k in expected:
      assert k in self.p.__dict__, 'Expected handle content key %s not found:: %s' % (k,str(self.p.__dict__.keys()))
    for k in expected:
      print ('%s: %s' % (k,self.p.__dict__[k]))

    print ('PARSING PARENT ..... ' )
    print ( self.htmpl % self.p.__dict__['IS_PART_OF'] )
    ##remote = Remote( self.p.__dict__['IS_PART_OF']['value'] )
    self.pp = self.p.__dict__['IS_PART_OF']
    for p in self.pp:
      p.get()
      for k in p.__dict__.keys():
        print ('%s: %s' % (k,p.__dict__[k]))
    #'isReplacedBy' if obsolete
    ##expected= ['creation_date', 'AGGREGATION_LEVEL', 'HS_ADMIN', '10320/loc', 'checksum', 'URL', 'children', 'tracking_id']

  def parseArgs(self):
    self.d = {}
    kn = self.knownargs0 + self.knownargs1
    xx = []
    al = self.args
    while len(al) > 0:
      a = al.pop(0)
      if a not in kn:
        xx.append(a)
      elif a in self.knownargs1:
         self.d[a] = al.pop(0)
      else:
         self.d[a] = True
    if len(xx) > 0:
      print ('ARGUMENTS NOT RECOGNISED: %s' % str(xx) )
      print ('FROM LIST: %s' % al)
        
class NcHead(dict):
  def __init__(self, fn):
    """Read global attributes of a NetCDF file"""
    nc0 = netCDF4.Dataset(fn, 'r')
    for a in ['tracking_id','contact']:
      if a in nc0.ncattrs():
        self[a] = nc0.getncattr(a)

    ##nc0 = cfdm.read( fn )
    ##for a in ['tracking_id','contact']:
      ##if a in nc0[0].nc_global_attributes().keys():
        ##self[a] = nc0[0].get_property(a)

def run_test():
    """Run a simple test using a known handle"""
    ex1 = ('hdl:21.14100/062520a0-f3d8-41bd-8b94-3fe0e4a6ab0e','tas_Amon_MPI-ESM1-2-LR_1pctCO2_r1i1p1f1_gn_185001-186912.nc')
    print ("Running a test using tracking id %s\nfrom file %s\n---------------------------\n" % ex1 )
    m = Main( ['-id',ex1[0],'-V'] )

def command_line_entry():
  import sys
  if len(sys.argv) == 1 or '-h' in sys.argv:
     print ( __doc__ )
  elif '-t' in sys.argv:
     run_test()
  else:
    m = Main( sys.argv[1:] )
      
if __name__ == "__main__":
  command_line_entry()


