import re
"""Code to parse ISO8601 compliant date strings, with extensions;
   extended years are allowed, but only in the form +-YYYYYYY-MM-DD: months and days must be specified and separator must be used.
   These restrictions ensure that there can be no ambiguity regarding YYYYMMDD and YYYYDDD forms of the date in the core specification.
   For backward compatibility, dates of the form Y-M-D aere also accepted;

  Updated from those posted in github discussion to make '-' optional in week format;
           - remove spurious brackets in core-ymd;
           - allow weeks 001-009 (blocked in previous form);
"""

class ParseOne(object):
    def __init__(self, ex, lab, ttl):
      self.ex = ex
      self.lab = lab
      self.ttl = ttl
      self.m = re.compile( self.ex ).match

    def __call__(self,ss):
      r = self.m(ss)
      if r == None:
        return None
      else:
        return r.groups()

class ParseSet(object):
  r1 = '^([1-9][0-9]{0,3})(?:-(1[0-2]|0[1-9]|[0-9])(?:-(3[01]|0[1-9]|[12][0-9]|[0-9]))?)?$'
  r2 = '^([-+]?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])$'
  r3 = '^([1-9][0-9]{3})(?:(-)?(1[0-2]|0[1-9])(?:(?(2)-|)(3[01]|0[1-9]|[12][0-9]))?)?$'
  r4 = '^([1-9][0-9]{3})(?:-?([0-2][0-9][1-9]))$'
  r5 = '^([1-9][0-9]{3})(?:(-)?W(5[0-3]|0[1-9]|[1-4][0-9])(?:(?(2)-|)([1-7]))?)?$'

  rd = {'core-ymd':(r3, 'Core ISO 8601 Date',['1999-01-01','19990101','1999-10'],['19999-01-01','1999-1-1','-1999-01-01']),
      'single':(r1, 'Non-ISO8601 extension for single digit months', ['1999-1-1','1-11-1','1-1'],['19990101','-1999-1-1']),
      'long':(r2, 'ISO8601 extension for extended years', ['-101999-01-01','+1999-11-01'],['19990101','-1999-1-1']),
      'core-yjd':(r4, 'Core ISO 8601 Date in Year-Julian day format',['1999-011','1999011'],['19999-011','199911','19990101']),
      'core-ywd':(r5, 'Core ISO 8601 Date in Year-week-day format',['1999-W11','1999W114'],['19999-W11','1999W1','1999W518'])
     }


  def __init__(self):

    self.ee = {}
    for k in self.rd.keys():
      self.ee[k] = ParseOne( self.rd[k][0], k, self.rd[k][1] )

  def __call__(self,s):
    for k in ['core-ymd','long','single','core-yjd','core-ywd']:
      x = self.ee[k](s)
      if x != None:
        if k in ['core-ymd','core-ywd']:
           x = (x[0],x[2],x[3])
        x = [ {None:'01'}.get(i,i) for i in x]
        return (k,x)
    return None

  def test(self):
    ee = self.ee
    rd = self.rd
    for k in rd.keys():
      for s in rd[k][2]:
        x = ee[k](s)
        if x == None:
          print ('Testing valid %s string %s: FAIL' % (k,s) )
        else:
          print ('Testing valid %s string %s: OK' % (k,s) )
      for s in rd[k][3]:
        x = ee[k](s)
        if x == None:
          print ('Testing invalid %s string %s: OK (no match)' % (k,s) )
        else:
          print ('Testing invalid %s string %s: FAIL (erroneous match)' % (k,s) )
  

p = ParseSet()
p.test()
