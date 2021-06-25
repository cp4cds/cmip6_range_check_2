
import shelve, glob, os, collections


class BaseUtils(object):

  def _boxFileSize(self,sz):
    """Create a discrete measure of file size, of from (x,n), where n is 1,2,5 and x is the length of the
    integer file size minus 1. The file size is above n * 10**x"""

    l1 = len( str(sz) )
    x = int(str(sz)[:1])
    this = 1
    for y in [2,5]:
      if y <= x:
        this = y
    return (l1-1,this)

class Aggreg(object):
  def __init__(self,activity):
    d1 = {'CMIP5':'sh', 'CMIP6':'sh6'}[activity]
    self._source = {'CMIP5':'model', 'CMIP6':'source_id'}[activity]
    l1 = glob.glob( '%s/*' % d1 )
    ss = set()
    for d in l1:
      dl2 = glob.glob( '%s/*' % d )
      for d2 in dl2:
        fl1 = glob.glob( '%s/*' % d2 )
        for f in fl1:
          ss.add(f)
    print '%s models, %s datasets' % (len(l1), len(ss))
    cc = collections.defaultdict( set )
    cci = collections.defaultdict( set )
    sz = 0
    for f in ss:
      sh = shelve.open(f,'r')
      this = sh['json']
      sz += this['size']
      m = str( this[self._source][0] )
      ##print this['variable'], m
      if 'variable' in this.keys():
        for v in this['variable']:
          cc[str(v)].add(m)
      else:
        print 'WARN.001: %s' % f
    for v in cc:
      cci[len(cc[v])].add(v)

    kk = sorted( cci.keys() )
    kk.reverse()
    for k in kk:
      print k, len(cci[k])
    print cci[ kk[0] ]
    self.cci = cci
    self.cc = cc
       
    print 'Size: %6.3fTB' % (sz*1.e-12)
