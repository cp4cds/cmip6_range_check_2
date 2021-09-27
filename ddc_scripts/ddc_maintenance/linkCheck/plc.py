
import sys

itml = []
kk = 0
thisitem = None

k404 = []
kslow = []

if len(sys.argv) > 1:
  lf = sys.argv[1]
else:
  lf = 'lc_out_mon.txt'

other = []

nu=0
##for l in map( string.strip, open( lf ).readlines()):
for l in [ x.strip() for x in open( lf ).readlines() ]:

  if l[:3] == 'URL':
    nu +=1
    if thisitem != None:
      itml.append( [thisitem, ct, res, parent, other] )
      kk += 1
    thisitem =l.split()[-1]
    other = []
    ct = None
    res = None
    parent = None
  elif l[:10] == 'Check time':
    ct = float( l.split()[2] )
    if ct > 15:
      kslow.append( kk )
  elif l[:6] == 'Result':
    res = l[11:]
    if res.find( '404' ) != -1:
      k404.append(kk)
  elif l[:10] == 'Parent URL':
    parent = l[11:]
  else:
    other.append(l)


oo = open( 'broken.csv', 'w' )
print ('Broken links')
for k in k404:
  print ('############################################')
  print (itml[k][0])
  print (itml[k][3])
  print (itml[k][1])
  print (itml[k][2])
  a,b,c = itml[k][3].split( ',' )
  d = ':'.join( [x.split()[-1] for x in [b,c]] )
  oo.write( '%s\t%s\t%s\n' % (itml[k][0],a,d) )
oo.close()
for k in kslow:
  print ('%s [%s]' % (itml[k][0], itml[k][1]))

print (nu)
