#!/usr/bin/env python
#
## archivr.py v0.9 | RN
#
# archive sys configuration files and provide means
# of comparing current system config files with 
# archived versions of files
# 

import os,sys,tarfile,datetime,socket,difflib,argparse

# list of configuration files to be archived
cflist="""
/etc/fstab
/etc/sudoers
/etc/resolv.conf
"""\
.split()

# smtp configuration section
smtpserver=""
sender=""
receivers=""

hname = socket.getfqdn()
ctimestamp = datetime.datetime.now()
ctimestamp = ctimestamp.strftime("%Y%m%d%H%M")
cfilename= "%s-archive.%s.tar" % (hname, ctimestamp)

class handling():
	""" usercheck/filecheck/err handling/print functions """
	def __init__(self):
		"self"
	def f_err(self,text):
		print "err: %s" % text 
	def f_ok(self,text):
		print "ok: %s" % text
	def f_filecheck(self,cflist):
			for cfile in cflist:
				try:
					os.path.isfile(cfile)
				except IOError:
					f_err("%s does not exist" %cfile)
	def f_usercheck(self):
		if os.getgid() != 0:
			handling().f_err("not root")
			sys.exit(1)

class archive():
	"""archive cflist - list of files"""
	def __init__(self):
		"self"
	def f_addfiles(self,cflist): # TODO with
		try:
			tar = tarfile.open(cfilename, "a")
		except (IOError, OSError):
			handling().f_err("cannot open archive %s" % cfilename)
			sys.exit(1)
		for cfile in cflist:
			try:
				tar.add(cfile)
			except (IOError, OSError):
				handling().f_err("%s not saved to archive" % cfile)
			handling().f_ok("file %s saved" % cfile)
		try:
			tar.close()
		except (IOError, OSError):
			handling().f_err("cannot close archive %s" % cfilename)

class check():
	""" compare archived files with system files """
	def __init__(self):
		"self"
	def f_compare(self,cflist,archive):
		archive=''.join(archive)
		# open archive && strip leading slash from each file path;
		# tar doesnt want to deal with that shit
		try:
			tar = tarfile.open(archive, "r")
		except (IOError,tarfile.ReadError):
			handling().f_err("%s not a valid tarfile" % archive)
			sys.exit(1)
		for cfile in cflist:
			# load archived file for comparison
			try:
				tfile = tar.extractfile(cfile[1:]).read().strip().splitlines()
			except KeyError:
				handling().f_err("%s not present in our archive" % cfile)
				continue
			# load system file for comparison
			try:
				sfile = open(cfile,"r").read().strip().splitlines()
			except IOError,tarfile.ReadError:
				handling().f_err("could not read %s system file" % sfile)
			# print "[ %s ]" % cfile
			# compare line by line; get rid of @@ -- and only print diffs & source file
			line=""
			for line in difflib.unified_diff(tfile, sfile, fromfile='archive', tofile=cfile, lineterm='\n', n=0):
				# if (not line.startswith('@@')) and (not line.startswith('+++')) and (not line.startswith('---')):
				if (not line.startswith('@@')) and (not line.startswith('---')):
					print line
					
	def f_email(self,cfile):
		message = ""
			
def f_start():
	parser = argparse.ArgumentParser(description='archive system config files for later integrity checks')
	parser.add_argument('-a', '--archive', action='store_true', help='archive defined cfg files')
	parser.add_argument('-c', '--check', nargs=1, metavar='<archive>', help='check/compare archived files with system files')
	parser.add_argument('-e', '--email', nargs=1, metavar='<email>', help='email diffs to an email address <email>'  )
	args = parser.parse_args()
	if len(sys.argv) < 2:
		parser.print_help()
		sys.exit(1)
	# am I uid 0?
	handling().f_usercheck()
	if args.archive: 
		archive().f_addfiles(cflist)

	if args.check:
		check().f_compare(cflist,args.check)
f_start()
