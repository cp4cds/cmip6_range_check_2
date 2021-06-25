import collections
import matplotlib.pyplot as plt
import numpy

class AR4(object):
  def __init__(self, dir='../../data/ar4/obs_gm/' ):
    self.dir = dir
    self.data = dict()

  def load(self):
    self.crutem()
    self.noaa()
    self.lugina()
    self.giss()
    self.time_range = [max( [self.data[x][0][0] for x in self.data.keys()] ),
                       min( [self.data[x][0][-1] for x in self.data.keys()] ) ]
    tt = []
    yy = []
    for y in range( self.time_range[0], self.time_range[1]+1):
      t = 0
      for k in self.data.keys():
        t += self.data[k][1][ self.data[k][0].index( y ) ]
      tt.append(t*0.25)
      yy.append(y)
    self.mean = (yy,tt)
 

  def crutem(self, fn='crutem3gl.txt'):
    ii = open( '%s%s' % (self.dir,fn) ).readlines()
    nn = len(ii)
    yy = []
    tt = []
    for i in range(nn/2):
      bits = ii[i*2].strip().split()
      y = int( bits[0] )
      t = float( bits[-1] )
      yy.append(y)
      tt.append(t)
    self.data['crutem'] = (yy,tt)

  def noaa(self, fn='annual.land_ocean.90S.90N.df_1901-2000mean.dat'):
    ii = open( '%s%s' % (self.dir,fn) ).readlines()
    nn = len(ii)
    yy = []
    tt = []
    for i in range(nn):
      bits = ii[i].strip().split()
      y = int( bits[0] )
      t = float( bits[1] )
      if t > -990:
        yy.append(y)
        tt.append(t)
    self.data['noaa'] = (yy,tt)

  def giss(self, fn='GLB.Ts.txt'):
    ii = open( '%s%s' % (self.dir,fn) ).readlines()
    nn = len(ii)
    yy = []
    tt = []
    for l in ii:
      if l[0] in ['1','2']:
        this = l.replace( '****', ' ***' )
        bits = this.strip().split()
        if bits[13].find( '*' ) == -1:
          y = int( bits[0] )
          t = int( bits[13] )*0.01
          yy.append(y)
          tt.append(t)
    self.data['giss'] = (yy,tt)

  def lugina(self, fn='90N-60S.dat'):
    ii = open( '%s%s' % (self.dir,fn) ).readlines()
    nn = len(ii)
    yy = []
    tt = []
    for l in ii:
      if l[0] in ['1','2']:
          bits = l.strip().split()
          y = int( bits[0] )
          t0 = [float(x) for x in bits[1:]]
          t = sum(t0)/12.
          yy.append(y)
          tt.append(t)
    self.data['lugina'] = (yy,tt)


class AR5(object):
  def __init__(self, dir='../../data/ar5/land/' ):
    self.dir = dir
    self.data = dict()


  def load(self):
    self.crutem()
    self.noaa()
    self.berkley()
    self.giss()
    self.time_range = [max( [self.data[x][0][0] for x in self.data.keys()] ),
                       min( [self.data[x][0][-1] for x in self.data.keys()] ) ]
    tt = []
    yy = []
    for y in range( self.time_range[0], self.time_range[1]+1):
      t = 0
      for k in self.data.keys():
        t += self.data[k][1][ self.data[k][0].index( y ) ]
      tt.append(t*0.25)
      yy.append(y)
    self.mean = (yy,tt)

  def crutem(self, fn='CRUTEM.4.1.1.0.global_n+s.txt'):
    ii = open( '%s%s' % (self.dir,fn) ).readlines()
    nn = len(ii)
    yy = []
    tt = []
    for i in range(nn):
      bits = ii[i].strip().split()
      y = int( bits[0] )
      t = float( bits[1] )
      yy.append(y)
      tt.append(t)
    self.data['crutem'] = (yy,tt)

  def noaa(self, fn='aravg.ann.land.90S.90N.v3.5.2.201301.asc'):
    ii = open( '%s%s' % (self.dir,fn) ).readlines()
    nn = len(ii)
    yy = []
    tt = []
    for i in range(nn):
      bits = ii[i].strip().split()
      y = int( bits[0] )
      t = float( bits[1] )
      if t > -990:
        yy.append(y)
        tt.append(t)
    self.data['noaa'] = (yy,tt)

  def giss(self, fn='GISS_Land_from_Sato.txt'):
    ii = open( '%s%s' % (self.dir,fn) ).readlines()
    cc = collections.defaultdict( float )
    for l in ii:
      if l[0] in ['1','2']:
          bits = l.strip().split()
          y = int( bits[0].split('.')[0] )
          t = float( bits[1] )
          cc[y] += t 

    yy = []
    tt = []
    for y in sorted( cc.keys() ):
          yy.append(y)
          tt.append(cc[y]/12.)
    self.data['giss'] = (yy,tt)

  def berkley(self, fn='Full_Database_TAVG_summary.txt'):
    ii = open( '%s%s' % (self.dir,fn) ).readlines()
    nn = len(ii)
    yy = []
    tt = []
    for l in ii:
      this = l.strip()
      if len(this) > 0 and this[0] in ['1','2']:
          bits = this.split()
          y = int( bits[0] )
          t = float( bits[1] )
          yy.append(y)
          tt.append(t)
    self.data['berkley'] = (yy,tt)


class Plot(object):
  def __init__(self,targ='AR5'):
    if targ == 'AR5':
      era = AR5()
      era.load()
      fig, ax = plt.subplots()
      kk = 0
      for this in ['noaa','giss','berkley','crutem']:
        ax.plot( era.data[this][0], era.data[this][1], color=['green','blue','red','cyan'][kk] )
        kk += 1
      plt.show()
    elif targ == 'mean':
      ar4 = AR4()
      ar4.load()
      ar5 = AR5()
      ar5.load()
      fig, ax = plt.subplots()
      kk = 0
      for era in [ar4,ar5]:
        ax.plot( era.mean[0], era.mean[1], color=['green','blue','red','cyan'][kk] )
        kk += 1
      plt.show()
    
