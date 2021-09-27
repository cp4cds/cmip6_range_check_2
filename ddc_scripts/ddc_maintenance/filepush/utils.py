
import os, netrc


class Netrc(object):
  def __init__(self,machine,rc=None):
    """Read the NETRC file to extract user & password for given machine id."""
    HOME = os.environ[ 'HOME' ]
    if rc == None:
      rc = os.environ.get( 'NETRC', '.netrc')

    if rc[0] != '/':
      rc = "%s/%s" % (HOME,rc)

    rcmode = oct(os.stat ( rc ).st_mode)[-2:]
    assert  rcmode == '00', 'File permissions on %s are unsafe: please fix' % rc
    nn = netrc.netrc( rc )
    assert machine in nn.hosts, 'Machine not found in %s: %s' % (rc, sorted( nn.hosts.keys() ) )
    self.__user__ = nn.hosts[ machine ][0]
    self.__pwd__ = nn.hosts[ machine ][2]

    
if __name__ == "__main__":
  n = Netrc('89.187.86.6')
