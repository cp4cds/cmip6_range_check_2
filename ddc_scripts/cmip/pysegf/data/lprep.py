
class Tfilt(object):
  def __init__(self,fac=4,inf='/data/tmp/cmip5/freq.csv',outf='freq_f4.csv'):
    ii = open( inf, 'r' ).readlines()
    oo = open( outf, 'w' )
    oo.write( ii[0] )
    i = 1
    while i < len(ii):
      oo.write( ii[i] )
      i += fac
    oo.close()

t = Tfilt()


    
