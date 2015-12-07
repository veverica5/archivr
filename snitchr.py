#!rusr/bin/env python
#
## archivr.py v0.9 | RN
#
# archive sys configuration files and provide means
# of comparing current system config files with 
# archived versions of files
# 

import os,sys,tarfile,datetime,socket,difflib,argparse,smtplib

# list of configuration files to be archived
cflist="""
/etc/hosts
/etc/fstab
/etc/sudoers
/etc/resolv.conf
/etc/lvm/lvm.conf
"""\
.split()

# smtp configuration 
smtpserver="smtp1.emea.omc.hp.com"
sender="archivr <archivr-noreply@hpe.com>"
receivers=','.join(["richard.nedbalek@hpe.com"])
subject="archivr report | "+socket.getfqdn()
# archive location
archpath="/var/log/archivr"+"/"

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
	def f_createarchdir(self,archpath):
		if os.path.isdir(archpath):
			pass
		else:
			try: 
				self.f_ok("directory does not exist, creating")
				os.mkdir(archpath,0700)
			except:
				self.f_err("cannot create %s, check manually" % archpath)
				sys.exit(1)
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
# end of class 'handling'
class archive():
	global archloc
	archloc=archpath+cfilename
	handling().f_createarchdir(archpath)
	"""archive cflist - list of files"""
	def __init__(self):
		"self"
	def f_addfiles(self,cflist): # TODO with
		try:
			tar = tarfile.open(archloc, "a")
		except (IOError, OSError):
			handling().f_err("cannot open archive %s" % archloc)
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
			handling().f_err("cannot close archive %s" % archloc)
# end of class 'archive'
class check():
	""" compare archived files with system files """
	def __init__(self):
		"self"
        def f_email(self,message):# TODO: exceptions
		header="From: %s \n" % sender
		header+="To: %s \n" % receivers
		header+="Subject: %s \n" % subject
		msg=()
		for key,value in message.iteritems():
			msg+=key,value+("\n\n")
                server = smtplib.SMTP(smtpserver)
		# create a tuple from string variable 'header' and merge with 'msg' - send that
                server.sendmail(sender, receivers, ''.join(((header,)+msg)))
                server.quit()
	def f_compare(self,cflist,archive):
		diffdict={}
		archive=''.join(archive)
		archive=archpath+archive
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
			# compare line by line; get rid of @@ -- +++ and fill in dictionary with differences 
			line=""
			filediff=""
			for line in difflib.unified_diff(tfile, sfile, fromfile='archive', tofile=cfile, lineterm='\n', n=0):
				if (not line.startswith('@@')) and (not line.startswith('+++')) and (not line.startswith('---')):
					filediff+="\n"
					filediff+=line
			if filediff:
				cfile="""[ %s ]""" % cfile
				diffdict[cfile]=filediff
		for key, value in diffdict.iteritems():
			print key,value
			print ""
		if args.email:
			self.f_email(diffdict)
# end of class 'check'
parser = argparse.ArgumentParser(description='archive system config files for later integrity checks')
# some options are exclusive. like check and archive and automatic
me1=parser.add_mutually_exclusive_group()
me1.add_argument('-a', '--archive', action='store_true', help='archive defined cfg files')
me1.add_argument('-c', '--check', nargs=1, metavar='<archive>', help='check/compare archived files with system files')
parser.add_argument('-e', '--email', action='store_true', help='email diffs to a configured address')
me1.add_argument('-t', '--automatic', action='store_true', help='autonomous mode - create a new archive snapshot and check last archived files in one go')
parser.add_argument('-l', '--location', action='store_true', help='archive output location; default: /var/log/archivr ')

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
if args.automatic:
	print "todo"
if args.location:
	print "todo"
