
The hddump package dumps information about a CMIP6 file from the handle registry


USAGE
=====

hddump [-h|-v|-t|-f <file_name>|-id <tracking id>] [-V]

 -h: print this message;
 -v: print version;
 -t: run a test
 -f <file name>: examine file, print path to replacement if this file is obsolete, print path to sibling files (or replacements).
 -id <tracking id>: examine handle record of tracking id.
 -V: verbose
 --debug: Debug


CHANGES
=======

0.1.06: 

 - Fixed uncaught exception caused when file has no replicas;
 - Fixed "hddump -v" to print true package version.


