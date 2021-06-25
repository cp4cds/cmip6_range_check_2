
import re

re_start = re.compile( '<div[ |>]' )
re_end = re.compile( '</div[ |>]' )

class Fedit(object):
  def __init__(self,fin,fout):
    ii = open(fin).readlines()
    jj = []
    nst = nen = 0
    skipped = False
    force = False
    msg1 = ''
    n=0
    for l in ii:
      skip = False
      n+= 1
      if re_start.match( l ):
         nst += 1
      if re_end.match( l ):
         nen += 1
         if nen > nst:
            if l.strip() != "</div>":
              print 'WARNING [%s]: skipping %s' % (fin,l.strip())
            skip = True

      if not skip or force:
         jj.append( l )
      else:
         nen += -1
         ##print 'REMOVING Line: %s' % n
         msg1 = 'Removed: %s' % n
         skipped = True

    oo = open( fout, 'w' )
    for l in jj:
      oo.write( l )
    oo.close()
    err = ''
    if nen != nst:
      err = 'ERROR.001: %s:%s ::' % (nst,nen)
    

    if skipped:
      print '%sEDITTED: %s: %s' % (err,fin,msg1)
    else:
      print '%sNO CHANGE: %s' % (err,fin)

if __name__ == '__main__':
  import sys
  fin = sys.argv[1]
  if fin == '_all_':
    import glob
    fl = glob.glob( '*.md' )
    for fn in fl:
      fout = 'pmd_out/%s' % fn
      f = Fedit( fn, fout )
  else:
    fout = 'pmd_out/%s' % fin
    f = Fedit( fin, fout )
