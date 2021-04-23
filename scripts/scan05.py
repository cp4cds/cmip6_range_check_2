
import json, glob, collections


def scan():
  fl = sorted( list( glob.glob( 'json_05/Lmon.mrro/mrro_Lmon_*' ) ) )
  sm = collections.defaultdict(set)
  sss = set()
  s1 = set()
  s2 = set()
  for f in fl:
    ee = json.load( open( f ) )
    ss = ee['data']['summary']
    drs = ss['drs']
    mx = ss['basic'][1]
    if mx > 0.001065:
      sm[drs[3]].add( ss['quantiles'][0] )
      fn = f.rpartition('/')[-1]
      s1.add( ss['quantiles'][0] )
      s2.add( ss['quantiles'][1] )
      if ss['quantiles'][0] > 0.001065:
        sss.add(fn)
      print( fn, '%6.4f, (%6.4f, %6.4f)' % (mx,*ss['quantiles'][:2]) )
  print( sm.keys() )
  print( sss )
  print( max(s1), max(s2) )

def scano():
  fl = sorted( list( glob.glob( 'json_05/Omon.sos/sos_*' ) ) )
  sm = collections.defaultdict(set)
  sss = set()
  s1 = set()
  s2 = set()
  for f in fl:
    ee = json.load( open( f ) )
    ss = ee['data']['summary']
    drs = ss['drs']
    mx = ss['basic'][1]
    mn = ss['basic'][0]
    if mn < 0.0:
      fn = f.rpartition('/')[-1]
      s1.add( ss['quantiles'][0] )
      s2.add( ss['quantiles'][1] )
      print( fn, '%6.4f, (%6.4f, %6.4f)' % (mn,*ss['quantiles'][-4:-2]) )

def scanp():
  fl = sorted( list( glob.glob( 'json_05/Amon.hur/hur_Amon_*' ) ) )
  ff= collections.defaultdict(list)
  for f in fl:
    fn = f.rpartition('/')[-1]
    sid = fn.split('_')[2]
    ff[sid].append(f)
  

  for sid in sorted( list( ff.keys() ) ):
    cc = collections.defaultdict(set)
    sss = set()
    s1 = set()
    s2 = set()
    for f in ff[sid]:
      ee = json.load( open( f ) )
      ss = ee['data']['summary']
      drs = ss['drs']
      for k,r in ee['data']['records'].items():
        mx = r['basic'][1]
        mn = r['basic'][0]
        lev = int( k.rpartition('-')[-1] )
        cc[lev].add(mn)
      ee = dict()
      for lev in sorted( list( cc.keys() ) ):
        ee[lev] = min( cc[lev] )
      vm = [ee[k] for k in range(19)]
      print( sid, min(vm[:16]), vm[16:] )

scanp()
