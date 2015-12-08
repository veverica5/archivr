#!/usr/bin/env python
##
### snitchr.py v1.0 | RN
##
# snapshot system configuration files and provide means
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
smtpserver="smtp.server.example"
sender="snitchr <snitchr-noreply@example.com>"
receivers=','.join(["jane.doe@example.com"])
subject="snitchr report | "+socket.getfqdn()

# snapshot location
snappath="/var/log/snitchr"+"/"

hname = socket.getfqdn()
ctimestamp = datetime.datetime.now()
# timestamp is very relevant to automatic sorting function!
ctimestamp = ctimestamp.strftime("%Y%m%d%H%M")
cfilename= "%s-snapshot.%s.tar" % (hname, ctimestamp)

class handling():
	""" usercheck/filecheck/err handling/print functions """
	def __init__(self):
		"self"
	def f_err(self,text):
		print "err: %s" % text 
	def f_ok(self,text):
		print "ok: %s" % text
	def f_inf(self,text):
		print "inf: %s" % text
	def f_createsnapdir(self,snappath):
		if os.path.isdir(snappath):
			pass
		else:
			try: 
				self.f_inf("directory does not exist, creating")
				os.mkdir(snappath,0700)
			except:
				self.f_err("cannot create %s, check manually" % snappath)
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
class snapshot():
	"""snapshot cflist - list of files"""
	def __init__(self):
		"self"
	def f_createsnap(self,cflist): # TODO with && compression
		global snaploc
		snaploc=snappath+cfilename
		handling().f_createsnapdir(snappath)
		try:
			tar = tarfile.open(snaploc, "a")
		except (IOError, OSError):
			handling().f_err("cannot open snapshot %s" % snaploc)
			sys.exit(1)
		for cfile in cflist:
			try:
				tar.add(cfile)
			except (IOError, OSError):
				handling().f_err("%s not saved to snapshot" % cfile)
			handling().f_ok("file %s saved" % cfile)
		try:
			tar.close()
		except (IOError, OSError):
			handling().f_err("cannot close snapshot %s" % snaploc)
# end of class 'snapshot'
class check():
	""" compare archived files with system files """
	def __init__(self):
		"self"
	def f_sortsnapshots(self):
		snaplist=os.listdir(snappath)
		snaplist=sorted(snaplist, key = lambda x: x.split('.')[-2])
		return(snaplist)
        def f_email(self,message):# TODO: exceptions && style for emails
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
	def f_compare(self,cflist,snapshot):
		diffdict={}
		snapshot=''.join(snapshot)
		snapshot=snappath+snapshot
		# open tar snapshot && strip leading slash from each file path;
		# tar doesnt want to deal with that shit
		try:
			tar = tarfile.open(snapshot, "r")
		except (IOError,tarfile.ReadError):
			handling().f_err("%s not a valid tarfile" % snapshot)
			sys.exit(1)
		for cfile in cflist:
			# load archived file for comparison
			try:
				tfile = tar.extractfile(cfile[1:]).read().strip().splitlines()
			except KeyError:
				handling().f_err("%s not present in our snapshot" % cfile)
				continue
			# load system file for comparison
			try:
				sfile = open(cfile,"r").read().strip().splitlines()
			except IOError,tarfile.ReadError:
				handling().f_err("could not read %s system file" % sfile)
			# compare line by line; get rid of @@ -- +++ and fill in dictionary with differences 
			line=""
			filediff=""
			for line in difflib.unified_diff(tfile, sfile, fromfile='snapshot', tofile=cfile, lineterm='\n', n=0):
				if (not line.startswith('@@')) and (not line.startswith('+++')) and (not line.startswith('---')):
					filediff+="\n"
					filediff+=line
			# if difference is found; fill dictionary
			if filediff:
				cfile="""[ %s ]""" % cfile
				diffdict[cfile]=filediff
		for key, value in diffdict.iteritems():
			print key,value
			print ""
		# if email flag is set & diffdict is not empty; send out owls
		if args.email and diffdict:
				self.f_email(diffdict)
# end of class 'check'
parser = argparse.ArgumentParser(description='snapshot system config files for later integrity checks')
# some options are exclusive. like check, snapshot & automatic
me1=parser.add_mutually_exclusive_group()
me1.add_argument('-s', '--snapshot', action='store_true', help='snapshot cfg files; default location /var/log/snitchr')
me1.add_argument('-c', '--check', nargs=1, metavar='<snapshot>', help='check/compare archived files with system files')
parser.add_argument('-e', '--email', action='store_true', help='email diffs to a configured address')
me1.add_argument('-a', '--autonomous', action='store_true', help='autonomous mode - check last archived files & create a new snapshot in one go')

args = parser.parse_args()
if len(sys.argv) < 2:
	parser.print_help()
	sys.exit(1)
# am I uid 0?
handling().f_usercheck()
if args.snapshot:
	snapshot().f_createsnap(cflist)
if args.check:
	check().f_compare(cflist,args.check)
if args.autonomous:
	# order of [check & create] is very important here. sorting function delivers latest available snapshot
	# for comparison and so first we must check and only then can we create a new snapshot; otherwise, in reversed 
	# order, latest snapshot is the one we created in a previous function miliseconds ago,thus checking system this snapshot makes very little sense
	snaplist=check().f_sortsnapshots()
	check().f_compare(cflist,snaplist[-1])
	snapshot().f_createsnap(cflist)

## end of snitchr.py
