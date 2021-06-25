
import os, re, collections, socket
from bs4 import BeautifulSoup, Comment

linkregex = re.compile('href=[\'|"](.*?)[\'|"]')

SITE='/home/ubuntu/mjuckes/Desktop/git/martinjuckes.github.io/_site/'
SITE='/home/mjuckes/Repositories/git/mine/ipcc_ddc_site/_site/' 

def getFiles():
  oo = []
  for root,dirs,files in os.walk( SITE ):
    base = root[2:]
    ##if len(base) == 0 or base[0] not in ['_','.']:
    for f in files:
        if f[-5:] == '.html':
          oo.append( '%s/%s' % (root,f) )
  return oo


files = sorted( getFiles() )
links = set()
links2 = set()
for f in files:
  this = '\n'.join( open(f).readlines() )
##  soup = BeautifulSoup( this )
  ##comments = soup.findAll(text=lambda text:isinstance(text, Comment))
  ##[comment.extract() for comment in comments]
  ##page = str( soup )
  page = this
  isdkrz = (page.find( 'DKRZ_Logo_281x127_2014.png' ) != -1) and (page.find( 'ceda_logo_transp_black_h188.png' ) == -1)
  print ( f, isdkrz )
  ##page = ' '.join(page.split())
  ##print page
  msg = linkregex.findall( page )
  for l in msg:
    l = l.strip().strip('/')
    if isdkrz:
      links2.add( l )
    else:
      links.add( l )

oo = open('test.html','w')
oode = open('testde.html','w')
oo.write( '<html><body>\n' )
oode.write( '<html><body>\n' )
for l in sorted( links ):
  if l[:4] in ['http','ftp:']:
    if l.find( 'www.dkrz.de' ) != -1:
      oode.write( '<a href="%s">%s</a>\n' % (l,l) )
    else:
      oo.write( '<a href="%s">%s</a>\n' % (l,l) )

oo.write( '</html></body>\n' )
oode.write( '</html></body>\n' )
oo.close()
oode.close()

oo = open( 'links.csv', 'w' )
oo1 = open( 'domains.csv', 'w' )
sp = set()
sd = set()
for l in sorted( links ):
  if l.find( '://' ) != -1:
    p,xx = l.split( '://' )
    sp.add(p)
    if xx.find( '/' ) != -1:
      dom,path = xx.split('/',1)
      sd.add(dom)
      oo.write( '\t%s\t%s\t%s\n' % (p,dom,path) )
    else:
      oo.write( '\t%s\t%s\t%s\n' % (p,xx,'') )
oo.close()
for d in sorted( sd ):
  try:
    ip = socket.gethostbyname(d)
  except:
    print( 'GETHOST Failed  ',d )
  os.popen( 'whois %s > _whois.txt' % ip )
  ii = open( '_whois.txt' ).readlines()
  org = ''
  for l in ii:
    if l[:13] == 'organisation:' or l[:13] == 'Organization:':
      org = l.strip().split(':',1)[1].strip()
    elif l[:24] == 'Registrant Organization:':
      org = l.strip().split(':',1)[1].strip()
   
  oo1.write( '%s\t%s\t%s\n' % (d,ip,org) )
oo1.close()
