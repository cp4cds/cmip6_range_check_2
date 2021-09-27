
# Programmatic XHTML Validations in Python
# Martin Hepp and Alex Stolz
# mhepp@computer.org / alex.stolz@ebusiness-unibw.org

import urllib
import urllib2
import time, glob, os

URL = "http://validator.w3.org/check?uri=%s"
SITE_URL = "http://www.heppnetz.de"
SITE_URL = "http://test.clipc.eu"

# pattern for HEAD request taken from 
# http://stackoverflow.com/questions/4421170/python-head-request-with-urllib2

class Validate(object):
  def __init__(self,BASE):
    self.res = dict()
    self.base = BASE
    if os.path.isfile( 'validation_results.csv'):
      for l in open( 'validation_results.csv' ).readlines():
        u,t,e,w = l.strip().split( '\t' )
        self.res[u] = (t,e,w)

    self.omit_dirs = set()
    self.omit_files = set()
    ii = open( 'validation_omit.txt' ).readlines()
    for l in ii:
      this = l.strip().split()[0]
      print this
      if this[-1] == "/":
        self.omit_dirs.add( this )
      else:
        self.omit_files.add( this )
          

    self.run()
    oo = open( 'validation_results.csv', 'w' )
    for k in sorted( self.res.keys() ):
      oo.write( k + '\t' + '\t'.join( [str(x) for x in self.res[k]] ) + '\n' )
    oo.close()


  def run(self,nmax=24):
    lbase = '/home/ubuntu/mjuckes/Desktop/git/martinjuckes.github.io/_site'
    self.nn = 0
    for root,dirs,files in os.walk( lbase ):
    ##os.chdir( '/home/ubuntu/mjuckes/Desktop/git/martinjuckes.github.io/_site' ) 
      thisr = root[len(lbase):]
      for x in self.omit_dirs:
        if len(x) <= len(thisr) and thisr[:len(x)] == x:
            print 'OMITTING: %s' % thisr
            return
      
      nn0 = self.nn
      for f in files:
        if f[-5:] == '.html' or f[-4:] == '.htm':
          p = '%s/%s' % (thisr, f)
          if p in self.omit_files:
            print 'OMITTING: %s' % p
            return

          try:
            self.check( p )
          except:
            print 'SEVERE.001: %s: check crashed' % p
            self.res[p] = (int(time.time()), 'CRASH', 0)

          if self.nn > nmax:
            return
        if self.nn > nn0+4:
          break

  def check(self,path,nday=60):
    if path in self.res and (time.time() - float( self.res[path][0] ) ) < nday*86400:
      return

    url01 = '%s/%s' % (self.base,path)
    if url01 not in self.res or (time.time() - float( self.res[url01][0] ) ) > nday*86400:
      self.nn += 1
      request = urllib2.Request(URL % urllib.quote(url01))
      request.get_method = lambda : 'HEAD'
      response = urllib2.urlopen(request)

      valid = response.info().getheader('X-W3C-Validator-Status')
      if valid == "Valid":
          valid = True
      else:
          valid = False
      errors = int(response.info().getheader('X-W3C-Validator-Errors'))
      warnings = int(response.info().getheader('X-W3C-Validator-Warnings'))

      print "%s: %s: %s (Errors: %i, Warnings: %i) " % (self.nn,path, valid, errors, warnings)
      self.res[url01] = (int(time.time()), errors, warnings)


if __name__ == '__main__':
  v = Validate(SITE_URL)
