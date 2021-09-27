"""
Demonstration handle dump for CMIP/ESGF files ..

 -h: print this message;
 -v: print version;
 -t: run a test [NOT WORKING .. BASED ON OBSOLETE METADATA PROFILE];
 -f <file name>: examine file, print path to replacement if this file is obsolete, print path to sibling files (or replacements).
 -id <tracking id>: examine handle record of tracking id.
"""
## see https://www.handle.net/proxy_servlet.html for info on restfull API

import collections, os
import ncq3
import xml
from xml.dom import minidom

try:
 URLLIB = True
 import urllib
 from urllib import request
except:
 URLLIB = False
 import requests

from testdata import *

class phandle(object):
  
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
  def __init__(self,hdl,url=None):
     """Class to retrieve a handle .. optionally to retrieve from test data.
     Still needs some error handling based on 'responseCode'."""

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

     if URLLIB:
       fh = request.urlopen( url )
       msg = eval( fh.read() )
     else:
       r = requests.get( url )
       msg = r.json()

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

  def __init__(self,id):
    self.REC_id = id
    self.REC_got = False

  def tolist(self):
    if self.REC_id.find( ';' ) == -1:
      return [self, ]
    else:
      this = []
      for id in self.REC_id.split(';'):
        this.append( Open( id.strip() ) )
      return this
    
  def get(self, extract=True):
    if self.REC_got:
      return

# rationalisation ... makinh GHandles redundant by using the class object to store the cache of retrieved handles.
    if self.REC_id not in self.__class__.cache:
      self.remote = Remote( self.REC_id )
      self.__class__.cache[self.REC_id] = self.remote.msg

    if extract:
      self._extract( self.__class__.cache[self.REC_id] )

  def _extract( self, msg ):
    """Extract alues from a handle message dictionary, and insert into self.__dict__"""

    print( msg.keys() )
    print( msg['handle'] )
    for r in msg['values']:
   
        if str(r['type']) in ['IS_PART_OF','HAS_PARTS','replaces', 'replacedBy', 'isReplacedBy','parent','REPLACED_BY']:
          self.__dict__[r['type']] = Open( r['data']['value'] ).tolist()

        else:
          self.__dict__[r['type']] = r['data']['value']

    if self.AGGREGATION_LEVEL == 'DATASET':
       self.obsolete = 'REPLACED_BY' in self.__dict__

    if 'URL' in self.__dict__:
      fn = self.__dict__['URL'].split( '/' )[-1]
      self.__dict__['filename'] = fn
    else:
      self.__dict__['filename'] = '__unnamed__'

  def addLatest(self):
    """Retrieve handle records for replacements until a current dataset is found."""
    if not self.obsolete:
      return
    self.REPLACED_BY.get()
    self.replacements=[self.REPLACED_BY,]
    while self.replacements[-1].obsolete:
        self.replacements.append( self.replacements[-1].REPLACED_BY.get() )
    self.latest = self.replacements[-1]

  def addSiblings(self):
     if self.AGGREGATION_LEVEL != 'FILE':
       print( 'No known siblings .....' )
       return

     if 'IS_PART_OF' not in self.__dict__:
       print( 'No parent' )
       return

     for p in self.IS_PART_OF:
            p.get()

     self.p.obsolete = all( [p.obsolete for p in self.p.IS_PART_OF] )

     self.siblings = []
     for p in self.IS_PART_OF:
       for c in p.HAS_PARTS:
         c.get()
         self.siblings.append( c )

class Main(object):
  """Main: entry point, parsing comman line arguments.

USAGE
-----
    m = Main( argList )
"""
  knownargs0 = ['-h','-v','-t']
  knownargs1 = ['-f','-id']

  def __init__(self, args):
    self.htmpl = 'http://hdl.handle.net/api/handles/%s'
    self.version = '0.01.01'
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

    if '-f' in self.d:
      fn = self.d['-f']
      self.dumpF(fn)

    if '-id' in self.d:
      id = self.d['-id']
      self.dumpF('',id=id)

  def dumpF(self,fn, id=None):
    if id == None:
      assert os.path.isfile( fn ), 'File %s not found' % fn
      nchead = NcHead( fn )
      thisid = nchead['tracking_id'].replace( 'hdl:999999', '10876.test' )
    else:
      thisid = id.replace('hdl:999999', '10876.test' )

    print (thisid)
    self.p = Open(  thisid )
    self.p.get()

    if 'IS_PART_OF' not in self.p.__dict__:
      print( 'No parent' )
    else:
      for p in self.p.IS_PART_OF:
            p.get()
      self.p.obsolete = all( [p.obsolete for p in self.p.IS_PART_OF] )
      print( 'Dataset version(s): %s' % [p.VERSION_NUMBER for p in self.p.IS_PART_OF] )
      if self.p.obsolete:
        print( '******* OBSOLETE FILE ******' )

      ##self.p.addLatest()
      ##for this in self.p.replacements:
        ##print 'REPLACED BY: ',this.URL, this.REC_id
      else:
        print( '****** File is current' )

  def runTest(self):
    """This test does not work any more ... the 10876.test handles appear to have been deleted ... they did not follow the current
    schema.
    """
    nchead = NcHead( fn1 )
    url = self.htmpl % nchead['tracking_id']
    hdl = nchead['tracking_id'].replace( 'hdl:999999', '10876.test' )
    print (hdl )
    remote = Remote( hdl )
    self.p = phandle(  remote.msg )
    expected= ['creation_date', 'AGGREGATION_LEVEL', 'HS_ADMIN', '10320/loc', 'checksum', 'URL', 'parent']
    ## 'REPLACED_BY' if obsolete
    for k in expected:
      assert k in self.p.d, 'Expected handle content key %s not found:: %s' % (k,str(self.p.d.keys()))
    assert 'tracking_id' in self.p.d or 'trackingID' in self.p.d, 'No tracking id found: %s' % str(self.p.d.keys())
    for k in expected:
      print ('%s: %s' % (k,self.p.d[k]))

    print ('PARSING PARENT ..... ' )
    print ( self.htmpl % self.p.d['parent']['value'] )
    remote = Remote( self.p.d['parent']['value'] )
    self.pp = phandle(  remote.msg )
    for k in self.pp.d.keys():
      print ('%s: %s' % (k,self.pp.d[k]))
    #'isReplacedBy' if obsolete
    expected= ['creation_date', 'AGGREGATION_LEVEL', 'HS_ADMIN', '10320/loc', 'checksum', 'URL', 'children', 'tracking_id']

  def parseArgs(self):
    self.d = {}
    kn = self.knownargs0 + self.knownargs1
    xx = []
    al = self.args[1:]
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
        
class NcHead(dict):
  def __init__(self, fn):
    """Read global attributes of a NetCDF file"""
    nc0 = ncq3.open( fn )
    nc0.getDigest()
    for a in nc0.alla:
      self[a.name] = a.value
      
if __name__ == "__main__":
  import sys
  if len(sys.argv) == 1 or '-h' in sys.argv:
     print ( __doc__ )
  else:
    m = Main( sys.argv )


