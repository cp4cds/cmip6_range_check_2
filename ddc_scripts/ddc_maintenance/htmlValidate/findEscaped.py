import re, os, collections


def getFiles():
  oo = []
  for root,dirs,files in os.walk( '/home/ubuntu/mjuckes/Desktop/git/martinjuckes.github.io/_site/' ):
    base = root[2:]
    ##if len(base) == 0 or base[0] not in ['_','.']:
    for f in files:
        if f[-5:] == '.html':
          oo.append( '%s/%s' % (root,f) )
  return oo


class Fesc(object):
  def __init__(self):
    self.re_esp = dict()
    self.re_esp['p'] = re.compile( '&lt;[P|p]&gt;' )
    self.re_esp['h'] = re.compile( '&lt;[H|h]' )
    self.re_esp['div'] = re.compile( '&lt;(div|/div)' )
    self.re_esp['span'] = re.compile( '&lt;(span|/span)' )

    files = getFiles()
    for f in files:
      self.run(f)


  def run(self,f):
    msg = []
    nm = collections.defaultdict( int )
    nn = 0
    fn = f.split('/')[-1]
    for l in open(f).readlines():
      for k in self.re_esp:
        matches = self.re_esp[k].findall( l )
        if len(matches) > 0:
          nm[k] += len(matches)
          nn += len(matches)
    if nn > 0:
      msg = '%s: ' % f
      for k in sorted( nm.keys() ):
        msg += ' %s escaped <%s ; ' % (nm[k],k)
      print (msg)


if  __name__ == "__main__":
  f = Fesc()
        
    
