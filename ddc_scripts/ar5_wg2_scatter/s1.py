

import collections, json

f1 = 'summary_cmip3-5_scatter_data_precip.txt'
f2 = 'summary_cmip3-5_scatter_data_temp.txt'

class ch14Ex(object):
  def __init__(self):
     ee = dict()
     fn = 'ch14ExtremesR.csv'
     self.cc = dict()
     cols = 'n, T, pr, stat, Scenario, Region, Label, Mask, Season, Year,'
     ii = open(fn).readlines()
     for l in ii[1:]:
       _T, _pr, stat, scenario, region, label, mask, season, _Year = [x.strip() for x in l.split(',')][1:10]
       ee[label] = (region,mask)
       t = float( _T )
       pr = float( _pr )
       year = int( _Year )
## region, season, model, scenario, mask, statistic, year
       self.cc[ (label, season, scenario, mask, stat, year) ] = (t,pr)
     dlabs = ['Region','Season','Scenario','Mask','Statistic','Year']
     dims = collections.defaultdict( set )
     for t in self.cc.keys():
       for i in range(len(dlabs)):
         dims[ dlabs[i] ].add( t[i] )
     self.dims = dict()
     for k in dims:
        self.dims[k] = sorted( list( dims[k] ) )

     oo = open( 'regions.json', 'w')
     json.dump( ee, oo, indent=4, sort_keys=True )
     oo.close()
     self.ee =ee
     

def flattenOn( cc, n ):
   cco = collections.defaultdict( dict )
   for t in cc:
     l = list(t)
     k = l.pop( n )
     cco[ tuple(l) ][k] = ( cc[t] )
   return cco

#RCP2.6   4.    6.0    8.5
#CMIP3ModelName    SRES   b1    a1b    a2


#CMIP3ModelName
class scan(object):
  def __init__(self,fn,regions):
    print fn
    ii = [l.strip() for l in open(fn).readlines()]
    self.cc = dict()
    lrec = 5
    cmip = 'CMIP5'
    scenarios = {'CMIP5':['RCP26','RCP45','RCP60','RCP85'],
           'CMIP3':['B1','A1B','A2'] }
    for l in ii[1:]:
      if len(l) in [9,11]:
        print l
      elif len(l) == 7:
        region,season = l.split( ' ' )
        if region not in regions:
          print 'INFO.region.00001:',region,season
      else:
        bits = l.split( )
        if bits[0] == 'CMIP3ModelName':
          cmip = 'CMIP3'
          lrec = 4
        else:
          assert len(bits) == lrec, 'Bad record: %s' % l
          for k in range(lrec-1):
            if bits[k+1] != 'NaN':
              v = float( bits[k+1] )
## era, region, season, model, scenario
              self.cc[ (cmip, region, season, bits[0], scenarios[cmip][k]) ] = v

    dlabs = ['Era','Region', 'Season','Model','Scenario']
    dims = collections.defaultdict( set )
    for t in self.cc.keys():
       for i in range(len(dlabs)):
         dims[ dlabs[i] ].add( t[i] )
    self.dims = dict()
    for k in dims:
        self.dims[k] = sorted( list( dims[k] ) )
    self.cc1 = flattenOn( self.cc, 3 )

class dump(object):
  def __init__(self,ofile,temp,pr,regions):
    self.cc = dict()
    self.cc2 = collections.defaultdict(dict)
    col1 = collections.defaultdict(set)
    ks = set( temp.keys() ).union( set( pr.keys() ) )
    for k in ks:
       #('CMIP3', 'ALA', 'DJF', 'A2')
       era, region, season, scenario = k
       dt = temp.get( k, {} )
       dp = pr.get( k, {} )
       models = set( dt.keys() ).union( set( dp.keys() ) )
       for model in models:
         thist = str( dt.get(model,'NA') )
         thisp = str( dp.get(model,'NA') )
         ##thist = '%5.2f' % dt.get(model,None)
         ##thisp = '%5.2f' % dp.get(model,None)
         rec = [thist, thisp, model, era, scenario, regions[region][0], region, regions[region][1], season, '2085']
         col1[era].add(model)
         thisk = (era,scenario,model,region,season)
         assert thisk not in self.cc, 'Duplicate: %s' % thisk
         self.cc2[(era,scenario,model,regions[region][0], region, regions[region][1])][season] = (thist,thisp)
         self.cc[ thisk ] = rec
    oo = open( ofile,'w' )
    oo.write( ','.join( ['n','T','pr','Model','Activity','Scenario','Region','Label','Mask','Season','Year'] ) + ',\n' )
    n = 0
    for k in sorted( self.cc.keys() ):
      oo.write( '%s,' % n + ','.join( self.cc[k] ) + ',\n' )
      n += 1
    oo.close()
    oo = open( 'var_' + ofile,'w' )
    for k in sorted( self.cc2.keys() ):
      part1 = ','.join(k) + ', '
      part2 = ','.join( [ self.cc2[k].get(x,['na',''])[0] for x in ['ANN','DJF','MAM','JJA','SON'] ] ) + ', '
      part3 = ','.join( [ self.cc2[k].get(x,['','na'])[1] for x in ['ANN','DJF','MAM','JJA','SON'] ] ) + ', '
      oo.write( part1 + part2 + part3 + '\n' )
    oo.close()
    print col1
    print col1['CMIP3'].intersection( col1['CMIP5'] )
         
    

ex = ch14Ex()
a1 = scan(f1,ex.ee)
a2 = scan(f2,ex.ee)

d = dump('IPCC-AR5-WGII-Chap21SM_scatter.csv',a1.cc1,a2.cc1,ex.ee)
      
