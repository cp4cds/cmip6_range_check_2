
from ftplib import FTP
ftp = FTP('89.187.86.6')
print( 'PASSWORD ENTRY NOT IMPLEMENTED' )
ftp.login( user='home@ipcc-data.org', passwd='*****' )
ii = open( 'dlist.txt' ).readlines()
for d in ii:
    this = d[1:].strip()
    ftp.cwd(this)
    fl = ftp.nlst()
    fl1 = [x for x in fl if x[-3:] == '.sh' ]
    if len(fl1) > 0:
      print (this,len(fl),len(fl1))
      print (fl1)
      for mdf in fl1:
          ftp.delete( mdf )
