# archivr
archive sys configuration files and provide means of comparing current system config files with archived versions of files

```
root@wrk:/data/scripts/archivr# python archivr.py 
usage: archivr.py [-h] [-a] [-c <archive>] [-e] [-t] [-l]

archive system config files for later integrity checks

optional arguments:
  -h, --help            show this help message and exit
  -a, --archive         archive defined cfg files
  -c <archive>, --check <archive>
                        check/compare archived files with system files
  -e, --email           email diffs to a configured address
  -t, --automatic       autonomous mode - create a new archive snapshot and
                        check last archived files in one go
  -l, --location        archive output location; default: /var/log/archivr
```
