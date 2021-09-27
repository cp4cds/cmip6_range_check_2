
import glob, os, stat, re, string, filecmp

## usage: filekit.getFlist().go( '-f', [ 'filekit.py', 'd2', 'd3'] )
## returns (flist, unused_args)

def dan( s ):
  bits = string.split(s, ',' )
  assert len( bits) in [1,2], 'Unrecognised sub-string format: %s' % s
  if len(bits) == 1:
    return 1
  elif len(bits) == 2:
    return int( bits[1] ) - int( bits[0] ) + 1

def ryn( msg, deflt='y' ):
      x = None
      kt = 0
      while x not in ['y','n']:
        assert kt < 4, 'Too many tries'
        print msg
        x = string.strip(sys.stdin.readline())
        if x == '':
            x = deflt
        kt += 1
      return x

###
### this class deals with command line arguments specifying a file, a list of files, or directories of files.
##
## 
class getFlist:

  def __init__(self, checkExist=True, fileSelSuffix='.nc'):
      self.checkExist = checkExist
      self.fileSelSuffix=fileSelSuffix

  def go(self, next, args):

      fts = ['-f','-ff','-d','-D']
      assert next in fts, 'Option %s not recognised' % next
   
      flist = []
      if next == '-f':
        flist =   [args.pop(0),]
      elif next == '-ff':
        while len(args) > 0:
          flist.append( args.pop(0) )
      elif next == '-d':
        fdir = args.pop(0)
        flist = glob.glob( '%s/*%s' % (fdir,self.fileSelSuffix)  )
      elif next == '-D':
        fdir = args.pop(0)
        lfs = len( self.fileSelSuffix )
        for root, dirs, files in os.walk( fdir ):
          for f in files:
            fpath = '%s/%s' % (root,f)
            if lfs > 0:
              if os.path.isfile( fpath ) and f[-lfs:] == self.fileSelSuffix:
                flist.append( fpath )
              elif os.path.isfile( fpath ):
                flist.append( fpath )
                
      if len(args) > 0:
        fts.pop(fts.index(next))
        for t in fts:
          assert t not in args, 'ERROR: duplicate file specification arguments %s %s' % (next,t)
      if next in ['-f','-ff'] and self.checkExist:
        for f in flist:
          assert os.path.isfile( f ), 'File %s not found' % f
        
      return (flist, args)


class fileInfo:

   def __init__(self,f1,f2):
     self.f1 = f1
     self.f2 = f2
     self.re_diff = None
     self.fktmp = '%s/ddcpub_filekit.tmp' % os.getenv( 'HOME' )
     assert os.path.isfile( f1), 'File %s not found' % f1

   def isunique(self):
     return not os.path.isfile(self.f2)

   def isnewer(self):
     return os.stat( self.f1 )[stat.ST_CTIME] > os.stat( self.f2 )[stat.ST_CTIME]

   def isolder(self):
     return os.stat( self.f1 )[stat.ST_CTIME] < os.stat( self.f2 )[stat.ST_CTIME]

   def isdiff(self):
     return filecmp.cmp( self.f1, self.f2 )

   def diffSummary(self):
     if os.path.isfile( self.fktmp ):
       os.unlink( self.fktmp )
     os.popen( 'diff %s %s > %s;' % ( self.f2, self.f1,self.fktmp ) ).readlines()
     if self.re_diff == None:
       self.re_diff = re.compile( '([0-9,]*)([acd])([0-9,]*)' )
     nn = 0
     no = 0
     ee = { 'a':0, 'd':0, 'c1':0, 'c2':0 }
     for l in open( self.fktmp ).readlines():
       if l[0] == '>':
         no += 1
       elif l[0] == '<':
         nn += 1
       else:
         m = self.re_diff.findall( string.strip(l) )
         if len(m) > 0:
            tag = m[0][1]
            val = m[0][2]
            if tag == 'a':
              ee[tag] += dan( val )
            elif tag == 'd':
              ee[tag] += dan( m[0][0] )
            elif tag == 'c':
              ee['c1'] += dan( m[0][0] )
              ee['c2'] += dan( m[0][2] )
         
     ##print 'New or changed in new file: %s lines\nNew or changed in old file: %s lines' % (nn,no)
     ##print 'Added: %s, deleted: %s, changed: (%s,%s)' % tuple( map( lambda x: ee[x], ('a','d','c1', 'c2') ) )
     self.cmesg = 'Added: %s, deleted: %s, changed: (%s,%s)' % tuple( map( lambda x: ee[x], ('a','d','c1', 'c2') ) )
     self.ee = ee
     self.nchange = sum( map( lambda x: ee[x], ('a','d','c1', 'c2') ) )
     self.nchange = max( [self.nchange, no+nn] )
     return self.nchange
     
class publish:

  def __init__(self, root1, root2, levNoChange=0, levChange=1, queryChange=True):
    for r in (root1,root2):
      assert os.path.isdir( r ), 'Directory %r not found' % r
    if root1[-1] != '/':
      root1 += '/'
    if root2[-1] != '/':
      root2 += '/'

    self.root1 = root1
    self.root2 = root2
    self.lr1 = len(root1)

    self.levNoChange=levNoChange
    self.levChange=levChange
    self.queryChange=queryChange

  def getTarg( self, p1 ):
    fp1 = os.path.realpath( p1 )
    assert fp1[:self.lr1] == self.root1, 'Mismatch between real path and root1: %s  %s' (fp1,self.root1)
    return self.root2 + fp1[self.lr1:]

  def push(self, p1, p2 ):
    assert os.path.isfile(p1),'Attempt to push non-existent file: %s' % p1
    self.p1 = p1
    self.p2 = p2
    tdir = string.join( string.split( p2, '/' )[:-1], '/' )
    fn =  string.split( p2, '/' )[-1]

    if not os.path.isdir( tdir ):
      tsdir = string.join( string.split( p2, '/' )[:-2], '/' )
      if os.path.isdir( tsdir ):
        msg = 'Create subdirectory %s for file %s? (y/n [y])' % (tdir,fn)
      else:
        msg = 'Create directory tree %s for file %s? (y/n [y])' % (tdir,fn)

      x = ryn( msg )
      if x == 'y':
          if os.path.isdir( tsdir ):
             os.mkdir( tdir )
          else:
             os.popen( 'mkdir -p %s' % tdir )
      else:
          return (-1,'Target directory not found' )

    f = fileInfo( p1, p2 )
    if f.isunique():
      print 'Pushing %s' % fn
      self._copy_()
    else:
      x = f.diffSummary()
      n = f.isnewer()
      o = f.isolder()
      if x > 0:
        if self.levChange > 0:
            print f.cmesg
        if not n:
          if o: 
            print 'WARNING: target file is different and newer %s %s' % (p1,p2)
          else:
            print 'WARNING: target file is different and has same time stamp %s %s' % (p1,p2)
          x = ryn( 'Push file (y/n)? [n]', deflt='n' )
        else:
          if self.queryChange:
            x = ryn( 'Push file (y/n)? [y]' )
          else:
            x = 'y'

        if x == 'y':
            self._copy_()
        else:
            print 'File not changed'
      
      else:
        if self.levNoChange > 0:
          print '%s not changed' % self.p1

  def _copy_(self):
    os.popen( 'cp %s %s' % (self.p1, self.p2) ).readlines()
    assert filecmp.cmp( self.p1, self.p2, shallow=0 ), 'File copy failed: %s %s' % (self.p1,self.p2)
    
d1 = '/home/martin/python/wrk/dev/'
d2 = '/home/martin/python/wrk/live/'
import sys
fn = sys.argv[1]
force = False
if fn == "-f":
  force = True
  fn = sys.argv[2]
fp = os.path.realpath( fn )
print fp
validSrc = "/var/www/ipccddc_devel/html/"
target = "/var/www/ipccddc_site/html/"
ls = len( validSrc)
assert fp[:ls] == validSrc, 'Requested file is not in the valid directory tree %s' % validSrc

pfn = fp[ls:]

p = publish( validSrc, target, levNoChange=1, queryChange=not force )
targ = p.getTarg( fn )
print targ
p.push( fn, targ )
