"""
NB -- THIS CODE IS WRITEN FOR AN EARLY VERSION OF THE HANDLE METADATA PROFILE ... NO LONGER SUPPORTED
Example page: https://handle8.dkrz.de/landingpagedemo/10876.test/ca9e9abd-e66e-413e-ab29-6c26fe00b859
"""

import uuid, collections, os

class dhdl(object):
  def __init__(self,value=None):
    if value == None:
      self.value = 'xxxxx/%s' % str( uuid.uuid1() )
    else:
      self.value = value

parentHandle1 = '10876.test/49634b69-6662-4a52-9175-45f296dc9578'

url1 = 'http://hdl.handle.net/api/handles/10876.test/f05ca8f4-f011-11e4-8220-5404a60d96b5'

fn1 = 'novar_fx_dummy_historical_r3i1p1.nc'

expectedC = ['creation_date', 'AGGREGATION_LEVEL', 'HS_ADMIN', '10320/loc', 'checksum', 'URL', 'IS_PART_OF']
expectedP = ['creation_date', 'AGGREGATION_LEVEL', 'HS_ADMIN', '10320/loc', 'checksum', 'URL', 'HAS_PARTS', 'tracking_id']

class map(object):
  def __init__(self):
    self.f = {}
    self.t = {}
  def add(self,a,b):
    self.t[a] = b
    self.f[b] = a

class dummyHandles(object):
  ##
  ## current data model does not support change in file name
  ##
  f1 = { 'ds1':( (('f1','aaaa'),('f2','bbbb')), \
                 (('f1','aaaa'),('f2','bbbc')), \
                 (('f1','aaaa'),('f3','bbb4')), \
                 (('f1b','aaac'),('f3','bbb4')) ) }
  mp = map()
  for a,b in [('bbbb','bbbc'), ('bbbc','bbb4'),('aaaa','aaac') ]:
    mp.add(a,b)

  def __init__(self):
    self.hh = {}
    self.uds = collections.defaultdict( dhdl )
    self.uf = collections.defaultdict( dhdl )
    self.loadIds()
    self.genDummy()
    self.saveIds()

  def loadIds(self):
    if not os.path.isfile( 'cachedDummyHandles.txt' ):
      return

    oo = open('cachedDummyHandles.txt', 'r')
    for l in oo.readlines():
      bits = l.strip().split( '\t' )
      if bits[0] == 'f':
        self.uf[bits[1]] = dhdl(value=bits[2])
      else:
        self.uds[(bits[1], int(bits[2]) )] = dhdl(value=bits[3])
    oo.close()
       
  def saveIds(self):
    oo = open('cachedDummyHandles.txt', 'w')
    for k in self.uds:
      oo.write( 't\t%s\t%s\t%s\n' % (k[0],k[1],self.uds[k].value ) )
    for k in self.uf:
      oo.write( 'f\t%s\t%s\n' % (k,self.uf[k].value ) )
    oo.close()
    
  def genDummy(self):
    dv = {}
    ddv = {'AGGREGATION_LEVEL':'DATASET'}
    ddf = {'AGGREGATION_LEVEL':'FILE'}
    self.dsd = {}
    for ds in self.f1.keys():
      kds=0
      for t in self.f1[ds]:
        values = []
        kds += 1
        cl = []
        for fn, cs in t:
          u = self.uf[cs]
          cl.append( u.value )
          if u.value not in self.hh:
            extr = []
            ddf['URL'] = 'd.dummy.dd/xx/%s' % fn
            ddf['tracking_id'] = u.value
            ddf['parent'] = self.uds[(ds,kds)].value
            if cs in self.mp.t:
              ddf['replaced_by'] = self.uf[ self.mp.t[cs] ].value
              extr.append( 'replaced_by' )
              ##print '>>> %s replaced_by %s' % (cs,ddf['replaced_by'])
            if cs in self.mp.f:
              ddf['replaces'] = self.uf[ self.mp.f[cs] ].value
              extr.append( 'replaces' )
              ##print '>>> %s replaces %s' % (cs,ddf['replaces'])
            thisV = []
            kk = 0
            for k in expectedC + extr:
              kk += 1
              thisV.append( {'index':kk, 'type':k, 'data':{'format':'string', 'value':ddf.get(k,'dummy')} } )
            self.hh[u.value] = {"responseCode":1, "handle":u.value, "values":thisV}
        dv[('children',kds)] = str(cl)
        dv[('tracking_id',kds)] = self.uds[(ds,kds)].value
          
        kk = 0
        for k in expectedP:
          kk += 1
          values.append( {'index':kk, 'type':k, 'data':{'format':'string', 'value':dv.get((k,kds),ddv.get(k,'dummy'))} } )

        if kds < 4:
          values.append( {'index':kk, 'type':'isReplacedBy', 'data':{'format':'string', 'value':self.uds[(ds,kds+1)].value} } )
        if kds > 1:
          values.append( {'index':kk, 'type':'replaces', 'data':{'format':'string', 'value':self.uds[(ds,kds-1)].value} } )
        self.dsd[(ds,kds)] = {"responseCode":1,"handle":self.uds[(ds,kds)].value, "values":values}
        self.hh[self.dsd[(ds,kds)]["handle"]] = self.dsd[(ds,kds)]
      
      
    

hsamp2 = {"responseCode":1,"handle":"10876.test/f05ca8f4-f011-11e4-8220-5404a60d96b5","values":[{"index":1,"type":"URL","data":{"format":"string","value":"http://clipc-services.ceda.ac.uk/testdata/v1/novar_fx_dummy_historical_r2i1p1.nc"},"ttl":86400,"timestamp":"2015-06-09T12:46:07Z"},{"index":100,"type":"HS_ADMIN","data":{"format":"admin","value":{"handle":"0.NA/10876.TEST","index":200,"permissions":"011111110011"}},"ttl":86400,"timestamp":"2015-06-09T12:46:07Z"},{"index":2,"type":"10320/loc","data":{"format":"string","value":"<locations chooseby=\"locatt,weighted\">\n<location ctype=\"text/html\" weight=\"1\" href=\"https://handle8.dkrz.de/landingpagedemo/10876.test/f05ca8f4-f011-11e4-8220-5404a60d96b5\" />\n<location http_role=\"conneg\" weight=\"0\" href=\"http://clipc-services.ceda.ac.uk/testdata/v1/novar_fx_dummy_historical_r2i1p1.nc\" />\n</locations>"},"ttl":86400,"timestamp":"2015-06-10T16:17:03Z"},{"index":3,"type":"creation_date","data":{"format":"string","value":"2015-05-01"},"ttl":86400,"timestamp":"2015-06-10T11:57:02Z"},{"index":4,"type":"tracking_id","data":{"format":"string","value":"f05ca8f4-f011-11e4-8220-5404a60d96b5"},"ttl":86400,"timestamp":"2015-06-10T11:57:08Z"},{"index":5,"type":"replaced_by","data":{"format":"string","value":"10876.test/f05f7caa-f011-11e4-8220-5404a60d96b5"},"ttl":86400,"timestamp":"2015-06-10T11:57:14Z"},{"index":6,"type":"checksum","data":{"format":"string","value":"ad99a037946fc7e9eaa1d916c8682a11"},"ttl":86400,"timestamp":"2015-06-09T12:46:07Z"},{"index":7,"type":"parent","data":{"format":"string","value":"10876.test/49634b69-6662-4a52-9175-45f296dc9578"},"ttl":86400,"timestamp":"2015-06-10T11:57:21Z"},{"index":8,"type":"aggregation_level","data":{"format":"string","value":"file"},"ttl":86400,"timestamp":"2015-06-10T11:57:34Z"}]}
hsample = {"responseCode":1,"handle":"10876.test/f0600a58-f011-11e4-8220-5404a60d96b5","values":[{"index":1,"type":"URL","data":{"format":"string","value":"http://clipc-services.ceda.ac.uk/testdata/v2/novar_fx_dummy_historical_r3i1p1.nc"},"ttl":86400,"timestamp":"2015-06-09T12:39:53Z"},{"index":100,"type":"HS_ADMIN","data":{"format":"admin","value":{"handle":"0.NA/10876.TEST","index":200,"permissions":"011111110011"}},"ttl":86400,"timestamp":"2015-06-09T12:39:53Z"},{"index":2,"type":"10320/loc","data":{"format":"string","value":"<locations chooseby=\"locatt,weighted\">\n<location ctype=\"text/html\" weight=\"1\" href=href=\"https://handle8.dkrz.de/landingpagedemo/10876.test/f0600a58-f011-11e4-8220-5404a60d96b5\" />\n<location http_role=\"conneg\" weight=\"0\" href=\"http://clipc-services.ceda.ac.uk/testdata/v2/novar_fx_dummy_historical_r3i1p1.nc\" />\n</locations>"},"ttl":86400,"timestamp":"2015-06-10T16:21:11Z"},{"index":3,"type":"creation_date","data":{"format":"string","value":"2015-05-01"},"ttl":86400,"timestamp":"2015-06-10T12:01:04Z"},{"index":4,"type":"replaces","data":{"format":"string","value":"10876.test/f05d326a-f011-11e4-8220-5404a60d96b5"},"ttl":86400,"timestamp":"2015-06-09T12:39:53Z"},{"index":5,"type":"trackingID","data":{"format":"string","value":"f0600a58-f011-11e4-8220-5404a60d96b5"},"ttl":86400,"timestamp":"2015-06-09T12:39:53Z"},{"index":6,"type":"checksum","data":{"format":"string","value":"e2e71fe45c106298dc15fbd08f9707e1"},"ttl":86400,"timestamp":"2015-06-09T12:39:53Z"},{"index":7,"type":"parent","data":{"format":"string","value":"10876.test/ca9e9abd-e66e-413e-ab29-6c26fe00b859"},"ttl":86400,"timestamp":"2015-06-10T12:01:10Z"},{"index":8,"type":"aggregation_level","data":{"format":"string","value":"file"},"ttl":86400,"timestamp":"2015-06-10T12:01:21Z"}]}

psampl1 = {"responseCode":1,"handle":"10876.test/49634b69-6662-4a52-9175-45f296dc9578","values":[{"index":1,"type":"URL","data":{"format":"string","value":"http://clipc-services.ceda.ac.uk/testdata/v1"},"ttl":86400,"timestamp":"2015-06-10T08:04:45Z"},{"index":100,"type":"HS_ADMIN","data":{"format":"admin","value":{"handle":"0.NA/10876.TEST","index":200,"permissions":"011111110011"}},"ttl":86400,"timestamp":"2015-06-10T08:04:45Z"},{"index":2,"type":"10320/loc","data":{"format":"string","value":"<locations chooseby=\"locatt,weighted\">\n<location ctype=\"text/html\" weight=\"1\" href=href=\"https://handle8.dkrz.de/landingpagedemo/10876.test/49634b69-6662-4a52-9175-45f296dc9578\" />\n<location http_role=\"conneg\" weight=\"0\" href=\"http://clipc-services.ceda.ac.uk/testdata/v1/\" />\n</locations>"},"ttl":86400,"timestamp":"2015-06-10T16:24:37Z"},{"index":3,"type":"creation_date","data":{"format":"string","value":"2015-05-01"},"ttl":86400,"timestamp":"2015-06-10T12:04:29Z"},{"index":4,"type":"tracking_id","data":{"format":"string","value":"none"},"ttl":86400,"timestamp":"2015-06-10T12:04:35Z"},{"index":5,"type":"isReplacedBy","data":{"format":"string","value":"10876.test/ca9e9abd-e66e-413e-ab29-6c26fe00b859"},"ttl":86400,"timestamp":"2015-06-10T08:04:45Z"},{"index":6,"type":"checksum","data":{"format":"string","value":"todo"},"ttl":86400,"timestamp":"2015-06-10T08:04:45Z"},{"index":7,"type":"children","data":{"format":"string","value":"[\"10876.test/f05e5f1e-f011-11e4-8220-5404a60d96b5\", \"10876.test/f05d326a-f011-11e4-8220-5404a60d96b5\", \"10876.test/f05ca8f4-f011-11e4-8220-5404a60d96b5\", \"10876.test/f05c1876-f011-11e4-8220-5404a60d96b5\", \"10876.test/f05dc00e-f011-11e4-8220-5404a60d96b5\"]"},"ttl":86400,"timestamp":"2015-06-10T12:04:46Z"},{"index":8,"type":"aggregation_level","data":{"format":"string","value":"dataset"},"ttl":86400,"timestamp":"2015-06-10T12:04:57Z"}]}
