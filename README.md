# snitchr
snapshot system configuration files and provide means of comparing current system config files with archived versions of files

```
root@deskt0p:/data/scripts/snitchr$ python snitchr.py 
usage: snitchr.py [-h] [-s] [-c <snapshot>] [-e] [-a]

snapshot system config files for later integrity checks

optional arguments:
  -h, --help            show this help message and exit
  -s, --snapshot        snapshot cfg files; default location /var/log/snitchr
  -c <snapshot>, --check <snapshot>
                        check/compare archived files with system files
  -e, --email           email diffs to a configured address
  -a, --autonomous      autonomous mode - check last archived files & create a
                        new snapshot in one go
```
