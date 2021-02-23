import glob, collections, os, shelve


def check_input_list(ifile='inputs_05/historical/x1_Amon_ps.txt' ):
  llm = []
  nv = 0
  kk = 0
  for l in open(ifile).readlines():
    kk+=1
    fs = l.rpartition('/')[-1].rpartition('.')[0]
    var,tab = fs.split('_')[:2]
    odir = 'out_05/%s.%s/' % (tab,var)
    if os.path.isfile( '%s%s' % (odir,fs) ):
      nv +=1
    else:
      llm.append( fs )
  return (nv,kk,llm)

def check_sh(ofile,verbosity=0):
  sfile = ofile.replace( 'out_', 'sh_' )
  if not os.path.isfile( sfile + '.dat' ):
     print ( 'ERROR: shelve not found: %s' % sfile )
     return False
  else:
     sh = shelve.open( sfile, 'r' )
     lk = len( sh.keys() )
     sh.close()
     if lk < 4:
       print ( 'ERROR: shelve file too short: %s' % sfile )
       return False
     if verbosity > 1:
       print ('%s: k=%s' % (sfile,lk) )

  return True


if __name__ == "__main__":
  import sys
  test=True
  opt=2
  if opt == 4:
    if check_sh( 'out_05/Amon.ps/ps_Amon_EC-Earth3-AerChem_historical_r1i1p1f1_gr_199701-199712', verbosity=2 ):
       print( 'shelve checked OK' )
    else:
       print ('Error in shelve ... ' )
  if opt == 0:
    nv,kk,llm = check_input_list()
    if nv == kk:
      print( 'TEST OK: %s found' % nv )
    else:
      print( 'Incomplete: %s -- %s' % (nv,kk) )

  elif opt == 1:
    fl = glob.glob( 'inputs_05/historical/*' )
    for f in sorted(fl):
      nv,kk,llm = check_input_list(ifile=f)
      if nv == kk:
        print( '%s: TEST OK: %s found' % (f,nv) )
      else:
        print( '%s: Incomplete: %s -- %s' % (f,nv,kk) )
    
  elif opt == 2:
    dl = glob.glob( 'inputs_05/*' )
    for d in dl:
      fl = glob.glob( '%s/*' % d )
      for f in sorted(fl):
        nv,kk,llm = check_input_list(ifile=f)
        if nv == kk:
          print( '%s: TEST OK: %s found' % (f,nv) )
        else:
          print( '%s: Incomplete: %s -- %s' % (f,nv,kk) )
    
