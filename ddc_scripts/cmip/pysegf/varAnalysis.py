import collections
import xlrd
from dreqPy import dreq

class CMIP5IMPORT(object):
  def __init__(self):
    oo = open( 'data/cmip5_varlist.csv', 'w' )
    wb = xlrd.open_workbook( 'data/CMIP5_standard_output2014.xls' )
    self.sns = wb.sheet_names()
    for s in self.sns:
      if s not in ['general','dims','other input','CFMIP output']:
          this = wb.sheet_by_name( s )
          for k in range(this.nrows):
            r = this.row(k)
            xx = [str(x.value).strip() for x in r]
            if xx[0] in ['1','2','3','1.0','2.0','3.0']:
              oo.write( '%s\t%s\t%s\n' % (xx[0][0],s,xx[5]) )
            else:
              print xx[:7]
    oo.close()

class CMIP6IMPORT(object):
  def __init__(self):
    oo = open( 'data/cmip6_varlist.csv', 'w' )
    dq = dreq.loadDreq()
    for i in dq.coll['CMORvar'].items:
      if 'requestVar' in dq.inx.iref_by_sect[i.uid].a:
        pp = []
        for j in dq.inx.iref_by_sect[i.uid].a['requestVar']:
          pp.append( dq.inx.uid[j].priority )
        p = min( pp )
        t = i.mipTable
        v = i.label
        s = dq.inx.uid[ i.stid ].label
        oo.write( '%s\t%s\t%s\t%s\n' % (p,t,v,s) )
    oo.close()
    
class Vpar(object):
  """Analyse variables submitted to the archive.
     self.indx [defaultdict(set)]: key: count of models which have supplied variables, value: set of (table,label) pairs identifying variables;
     self.vs [dictionary] {era=CMIP6 only}: structure label associated with each variable. key: (table,label) pair identifying variables.
  """
  
  def __init__(self,pmax=1,era='CMIP6'):
    self.era = era
    self.pmax = pmax
    self._readVarList()
    self._readCmip5()
    kk = sorted( self.indx.keys() )
    kk.reverse()
    print len(self.mm)
    cc1 = collections.defaultdict( set )
    for n in [59,58,57,56]:
      cc1 = collections.defaultdict( set )
      if n in self.indx:
        for t,v in self.indx[n]:
          this = [m for m in self.mm if m not in self.cc[(t,v)] ]
          for m in this:
            cc1[m].add( '%s.%s' % (t,v) )
        print 'models not in %s:: %s' % (n,' '.join( sorted(list(cc1)) ) )

    for k in kk[:5]:
      print '--------------- %s [%s] -------------' % (k,len(self.indx[k]))
      print self.indx[k]
      if self.era == 'CMIP6':
        ss = set( [self.vs[x] for x in self.indx[k]] )
        print sorted( list( ss ) )
    for k in kk[-4:]:
      print '--------------- %s [%s] -------------' % (k,len(self.indx[k]))
      print self.indx[k]
      if self.era == 'CMIP6':
        ss = set( [self.vs[x] for x in self.indx[k]] )
        print sorted( list( ss ) )

    nn = 0
    ss = collections.defaultdict( list )
    ss2 = collections.defaultdict( list )
    ss3 = set()
    for k in kk:
      nn += len(self.indx[k])
      for t,v in self.indx[k]:
        this = [m for m in self.mm if m not in self.cc[(t,v)] ]
        for m in this:
          ss3.add(m)
      print '%s, %s, %s {%s}' % (k,len(self.indx[k]),nn, len( [m for m in self.mm if m not in ss3]) )
      if k >= 30:
        for v in self.indx[k]:
          ss[ v[0] ].append( v[1] )
      elif k <= 3:
        for v in self.indx[k]:
          ss2[ v[0] ].append( v[1] )

    for t in sorted( ss.keys() ):
      print '%16s [%3s]:: %s' % (t, len( ss[t] ), ' '.join( sorted( ss[t] ) ) )

    print '----- Low use variables -------'
    for t in sorted( ss2.keys() ):
      print '%16s [%3s]:: %s' % (t, len( ss2[t] ), ' '.join( sorted( ss2[t] ) ) )


    oo = open( 'freq.csv', 'w' )
    oo.write( 'Models,Variables,N\n' )
    nn = 0
    for k in kk:
      nn += len(self.indx[k])
      oo.write( ','.join( [str(x) for x in [k,len(self.indx[k]),nn]] ) + '\n' )
    oo.close()
    
    
  def _readVarList(self):
    if self.era == 'CMIP5':
      ii = open( 'data/cmip5_varlist.csv' )
    else:
      ii = open( 'data/cmip6_varlist.csv' )

    self.vlist = {}
    self.vs = {}
    self.pk = collections.defaultdict( int )
    self.slist = collections.defaultdict( int )

    for l in ii.readlines():
      tt = l.strip().split( '\t' )
      if len(tt) == 3:
        p,t,v = tt
        p = int(p)
        self.vlist[ (t,v) ] = p
      elif len(tt) == 4:
        p,t,v,s = tt
        p = int(p)
        self.vlist[ (t,v) ] = p
        self.vs[ (t,v) ] = s
        self.slist[ (s,p) ] += 1
      else:
        print 'short record: %s' % l

    for k,p in self.vlist.items():
        self.pk[p] += 1

    print self.pk

  def _readCmip5(self,opt='old'):
    self.cc = collections.defaultdict( set )
    self.mm = set()
    self.indx = collections.defaultdict( set )
    if opt == 'new':
      ii = open( 'data/%s_mtv.csv' % self.era, 'r' )
      for l in ii.readlines():
        m, t, var = l.strip().split( '\t' )
        self.mm.add(m)
        v = (t,var)
        if self.vlist.get( v, 0 ) == 1:
          self.cc[ v ].add( m )
    else:
      ii = open( 'data/variableLevelList_20150706.txt' )
      for l in ii.readlines():
        bits = l.strip().split( '/' )
        self.mm.add(bits[2])
        v = (bits[6],bits[-1])
        if self.vlist.get( v, 10 ) <= self.pmax:
          self.cc[ v ].add( bits[2] )

    for k in self.cc.keys():
        self.indx[ len( self.cc[k] ) ].add( k )

    for v in self.vlist:
      if self.vlist[v] <= self.pmax and v not in self.cc:
        self.indx[0].add( v )
##

v = Vpar(pmax=1, era='CMIP5')
#c = CMIP5IMPORT()
#c = CMIP6IMPORT()
