# archivr
archive sys configuration files and provide means of comparing current system config files with archived versions of files

```
root@deskt0p:/data/scripts/archivr# python archivr.py 
usage: archivr.py [-h] [-a] [-c <archive>] [-e]

archive system config files for later integrity checks

optional arguments:
  -h, --help            show this help message and exit
  -a, --archive         archive defined cfg files
  -c <archive>, --check <archive>
                        check/compare archived files with system files
  -e, --email           email diffs to a configured address
```
