import glob, json
import collections
import datetime


class Scan01(object):
  def __init__(self,years=[2018,2019]):
    from datetime import datetime as dt
    self._dt = dt
    ii = []
    for year in years:
      ii += glob.glob( '/datacentre/stats/uptime/%s/uptimerobot.*.json' % year )
    dd = collections.defaultdict( dict )
    cc = collections.defaultdict( list )
    upt= collections.defaultdict( float )
    tt1= collections.defaultdict( float )
    ll1= collections.defaultdict( list )
    self.tt2= collections.defaultdict( dict )
    self.ll2= collections.defaultdict( dict )
    for f in sorted( ii ):
      fn = f.split( '/' )[-1]
      fdate = fn.split('.')[1]
      ee = json.load( open( f ) )
      for this in ee['monitors']:
        for l in this['logs']:
          l['file_date'] = fdate
          dd[this['friendly_name']][l["datetime"]] = l
          cc[(l['reason']['code'],this['friendly_name'])].append( l )
          if l["type"] != 1:
              upt[this['friendly_name']] += l["duration"]

    tt = len(ii)*24*3600
    for k in upt:
      print '%s:: Uptime: %s, downtime: %s, %s' % (k,upt[k],tt-upt[k], (tt-upt[k])/tt*100)


    for n in dd:
      for t in dd[n]:
        l = dd[n][t]
        tt1[ (l['reason']['code'],n) ] += l["duration"]
        ll1[ (l['reason']['code'],n) ].append( l )
    for code, name in tt1.keys():
       self.tt2[name][code] = tt1[(code,name)]
       self.ll2[name][code] = ll1[(code,name)]

    self.ee = collections.defaultdict( dict )
    for code, name in cc.keys():
      self.ee[name][code] = cc[(code,name)]

  def rep1(self,name,code):
    this = self.ll2[name][code]
    for i in this:
      print i['file_date'],i['duration'],self._dt.utcfromtimestamp(i['datetime'])
      

s =Scan01()
