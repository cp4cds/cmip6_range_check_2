

import collections
import s1
import matplotlib.pyplot as plt

plt.figure(0)

x = []
y = []
for r in s1.a2.dims['Region']:
  t,pr=s1.ex.cc[(r,'Annual','rcp60','land','Max',2100)]
  t2 = max(  [ v for k,v in s1.a2.cc1[('CMIP5',r,'ANN','RCP60')].items() ] )

  x.append(t)
  y.append( t2 )

plt.scatter(x,y,
            # the marker as
            marker='o',
            # the color
            color='r',
            # the alpha
            alpha=0.7,
            # with size
            s = 124,
            # labelled this
            label='Year 299')

##plt.show()
plt.savefig('cmip5_rcp60_wg1_wg2_extremes.png')

plt.figure(1)

x = collections.defaultdict( list )
y = collections.defaultdict( list )
markers = {'B1':'o', 'A1B':'^', 'A2':'s', 'RCP26':'+', 'RCP45':'+', 'RCP60':'+', 'RCP85':'+'}
markerc = {'B1':'gray', 'A1B':'gray', 'A2':'gray', 'RCP26':'navy', 'RCP45':'cyan', 'RCP60':'orange', 'RCP85':'red'}
ss = {'CMIP3':['B1', 'A1B', 'A2'], 'CMIP5':['RCP26', 'RCP45', 'RCP60' ,'RCP85']}
for m in ['CMIP3','CMIP5']:
 for scen in ss[m]:
  d1 = s1.a1.cc1[(m,'SSA','ANN',scen)]
  d2 = s1.a2.cc1[(m,'SSA','ANN',scen)]
  kk = set( d1.keys() ).intersection( d2.keys() )
  for k in sorted( list( kk ) ):
    x[scen].append( d1[k] )
    y[scen].append( d2[k] )

  plt.scatter(y[scen],x[scen],
            # the marker as
            marker=markers[scen],
            # the color
            color=markerc[scen],
            # the alpha
            alpha=0.7,
            # with size
            s = 124,
            # labelled this
            label='Year 299')
plt.savefig('cmip5_rcp60_wg2_ssa_ann_rcp60.png')

