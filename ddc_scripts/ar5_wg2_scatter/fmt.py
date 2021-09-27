
import s1

ee = dict()

for m,r,seas,scen in s1.a1.cc1:
  d1 = s1.a1.cc1[(m,r,seas,scen)]
  d2 = s1.a2.cc1[(m,r,seas,scen)]
  models = sorted( list( set( d1.keys() ).union( d2.keys() ) ) )
  for mm in models:
    t = d1.get( mm, None )
    p = d2.get( mm, None )
    ee[ (m,scen,r,seas,mm) ] = (t,p)

oo = open( 'test.csv', 'w' )
for k in sorted( ee.keys() ):
  oo.write( '\t'.join( list(k) ) + '\t' + '\t'.join( ['%s' % x for x in ee[k]] ) + '\n' )
oo.close()
  
