#!/usr/bin/env python
#
## archivr.py v0.9 | RN
#
# archive sys configuration files and provide means
# of comparing current system config files with 
# archived versions of files
# 

import os,sys,tarfile,datetime,socket,difflib,argparse

cflist="""
/etc/sudoers
/etc/fstab
/etc/resolva.conf
"""\
.split()

hname = socket.getfqdn()
ctimestamp = datetime.datetime.now()
ctimestamp = ctimestamp.strftime("%Y%m%d%H%M")
cfilename= "%s-archive.%s.tar" % (hname, ctimestamp)

class handling():
	""" usercheck/filecheck/err handling/print functions """
	def __init__(self):
		"self"
	def f_usage(self):
		print "usage:"
		print sys.argv[0],"archive"
		print sys.argv[0],"check <archive.tar>"
		sys.exit(1)
	def f_err(self,text):
		print "err: %s" % text 
		sys.exit(1)
	def f_ok(self,text):
		print "ok: %s" % text
	def f_filecheck(self,cfile):
		try:
			os.path.isfile(cfile)
			# handling().f_ok("%s exists" % cfile)
		except IOError:
			f_err("%s does not exist" %cfile)
	def f_usercheck(self):
		if os.getgid() != 0:
			handling().f_err("not root")

class archive():
	"""archive cflist - list of files"""
	def __init__(self):
		"self"
	def f_addfile(self,cfile): # TODO with
		try:
			tar = tarfile.open(cfilename, "a")
		except (IOError, OSError):
			handling().f_err("cannot open archive %s" % cfilename)
		try:
			tar.add(cfile)
		except (IOError, OSError):
			handling().f_err("%s not saved to archive" % cfile)
		try:
			tar.close()
		except (IOError, OSError):
			handling().f_err("cannot close archive %s" % cfilename)
		handling().f_ok("file %s saved" % cfile)

class check():
	""" compare archived files with system files """
	def __init__(self):
		"self"
	def f_compare(self,cfile):
		# load file from archive for comparison
		# strip leading slash; tar doesnt want to deal with that shit
		try:
			tar = tarfile.open(sys.argv[2], "r")
		except IOError:
			handling().f_err("%s not a valid tarfile" % cfilename)
		try:
			tfile = tar.extractfile(cfile[1:]).read().strip().splitlines()
		except KeyError:
			handling().f_err("%s not present in our archive" % cfilename)
		# load system file for comparison
		try:
			sfile = open(cfile,"r").read().strip().splitlines()
		except IOError:
			handling().f_err("could not read %s system file" %sfile)
		print "[ %s ]" % cfile
		# compare line by line; get rid of @@ ++ -- and only print diffs
		for line in difflib.unified_diff(tfile, sfile, fromfile='archive', tofile='system', lineterm='\n', n=0):
			if (not line.startswith('@@')) and (not line.startswith('+++')) and (not line.startswith('---')):
				print line
			
def f_start():
	parser = argparse.ArgumentParser(description='archive system config files for later integrity checks')
	parser.add_argument('-a', '--archive', action='store_true', help='archive defined cfg files')
	parser.add_argument('-c', '--check', nargs=1, metavar='<archive>', help='check archived files with system files')
	args = parser.parse_args()
	# am I uid 0?
	handling().f_usercheck()
	if args.archive: 
		for cfile in cflist:
			handling().f_filecheck(cfile)
			archive().f_addfile(cfile)
	if args.check: 
		for cfile in cflist:
			 check().f_compare(cfile)
f_start()
