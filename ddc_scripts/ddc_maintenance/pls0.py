import re, collections

rea = re.compile( '@' )

ii = open( 'ls0' )
cc = collections.defaultdict( int )
dd = collections.defaultdict( int )
ff = collections.defaultdict( dict )

for l in ii.readlines():
 ll = l.strip()
##-rw-rw-r-- 1 prototype byacl    111 2007-12-03 16:39 gcalberto@yahoo.com
 if ll.find( 'prototype' ) == -1 and ll.find( 'webuser' ) == -1:
   print '0001:: ',ll
 else:
   m = rea.findall( ll )
   if len(m) != 1:
     print '???:::',ll
   else: 
     bits = ll.split()
     yy = bits[5].split('-')[0]
     cc[yy] += 1
     dom = bits[-1].split('@')[1]
     dd[(yy,dom)] += 1
     

for yy,dom in dd.keys():
  ff[yy][dom] = dd[(yy,dom)]

oo = open( 'ddc_domains.txt', 'w' )
for k in sorted( cc.keys() ):
  print k,cc[k]
  for d in sorted( ff[k].keys() ):
    oo.write( '%s %32s:: %s\n' % (k,d,ff[k][d]) )
oo.close()
