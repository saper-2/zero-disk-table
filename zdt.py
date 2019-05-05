#!/usr/bin/env python3

import subprocess
import sys
import re
import argparse
import os

# global variables
devs = {}



# ###################################################################
# #  Run command and return it's output or False on error.
def do_proc(proc_cmd):
	pr = subprocess.Popen(proc_cmd, shell=True, stdout=subprocess.PIPE)
	(outp, errp) = pr.communicate()
	
	prs = pr.wait()
	
	if (pr.returncode != 0):
		print("\033[31mCommand\033[1m {}\033[0m\033[31m failed: \033[91m {} \033[93m {} \033[0m".format(proc_cmd,errp,outp))
		return False

	return outp.decode()

# ##################################################################
# #  Populate disk device list
def get_disk_list():
	global devs
	# -------------- Get disk informations -----------------------
	# -----------------------------------------------------------
	
	# get disk list and size in MiB
	devl1 = do_proc("parted -s /dev/sda unit mib print devices")
	devlt1 = []
	if (devl1 == False):
		print("Getting devices list failed. Command failed.")
		sys.exit("[ERROR:DEV_LIST_TEMP_1]")
	else:
		#print("\033[33mOutput:\033[0m")
		devlt1 = devl1.splitlines() #split('\n')
		#print(devlt1)
		#print("\033[33mResult:\033[0m")
		for a in devlt1:
			x = re.findall("(/dev/(sd[a-z]{1}))(\ .)(([0-9]+)([MB|GB|MiB|GiB]+))", a)
			#print(x)
			devs[x[0][0]] = { "dev": x[0][0], "sz":int(x[0][4]), "szu": x[0][5] }
	
	# get each disk sector count
	#devl2 = do_proc("parted -s /dev/sda unit s print devices")
	#devlt2 = []
	#if (devl2 == False):
	#        print("Getting devices list 2 failed. Command failed.")
	#        sys.exit("[ERROR:DEV_LIST_TEMP_2]")
	#else:
	#	#print("\033[33mOutput:\033[0m")
	#	devlt2 = devl2.splitlines() #split('\n')
	#	#print(devlt2)
	#	#print("\033[92mResult:\033[0m")
	#	for a in devlt2:
	#		x = re.findall("(/dev/(sd[a-z]{1}))(\ .)(([0-9]+)s)",a)
	#		#print(x)
	#		devs[x[0][1]]["sec"] = x[0][4]
	
	# get physical block sizes
	for d in devs:
		bcnt = do_proc("blockdev --getsz {}".format(d))
		if (bcnt == False):
			print("Getting device {} block count failed. Command failed.".format(d))
			sys.exit("[ERROR:DEV_BLK_COUNT({})]".format(d))
		else:
			devs[d]["bc"] = int(bcnt)
	# end func: get_disk_ist
	return
	

def print_devs():
	#devs
	print(" ")
	print("\033[93mAvailable disk devices are:\033[0m")
	print("\033[34m---- Device ---- \033[32m--- Size --- \033[90m--- Size ---  \033[36m- Sectors(512bytes) -\033[0m")
	#/dev/sdb          111.8GiB  120.0GB    234441648s
	for d in devs:
		gb = devs[d]["sz"] * 1048576.0;
		gb = gb / 1000000000.0;
		print("\033[94m{0:16} \033[92m{1:9.1f}{2}  \033[37m{3:9.1f}{4} \033[96m{5:21d}s\033[0m".format(devs[d]['dev'], (devs[d]['sz']/1024.0), "GiB", gb, "GB", devs[d]["bc"]))
		#print(d)
	return

def delete_temp(tfp):
	if (tfp != "/dev/zero"):
		if os.path.isfile(tfp):
			os.remove(tfp)
	# end delete_temp



def do_the_job(tmp_file, tmp_file_sz, dev):
	global devs
	# math
	dev_sectors = devs[dev]["bc"]
	file_sec_count = int(tmp_file_sz*1024/512)
	end_sec_start = dev_sectors-1-file_sec_count
	dev_sz = devs[dev]["sz"]*1048576.0; # size in MiB
	gib = dev_sz / (1048576.0*1024.0);
	gb = dev_sz / 1000000000.0;
	tmp_file_sz_mib = (tmp_file_sz * 1024.0) / 1048576.0;
	print("\033[97mConfirm erasing configuration:\033[0m")
	print("Device:\033[93m {}\033[0m".format(dev))
	print("  Size:\033[34m {0:9.1f}{1}\033[0m \\ \033[96m{2:9.1f}{3}\033[0m".format(gb,"GB",gib,"GiB"))
	print("  Sectors:\033[95m{0:21d}\033[0m (* 512 bytes)".format(dev_sectors))
	print("  Sector range:\033[94m{0:15d}\033[0m .. \033[96m{1:15d}\033[0m".format(0,dev_sectors-1))
	print("Following sector ranges will be erased:")
	print("  - \033[97mBEGIN: \033[0m[\033[94m{0:15.0f}\033[0m .. \033[96m{1:15.0f}\033[0m]".format(0,file_sec_count))
	print("  - \033[97m  END: \033[0m[\033[94m{0:15.0f}\033[0m .. \033[96m{1:15.0f}\033[0m]".format(end_sec_start,dev_sectors-1))
	print("Fill file size: \033[96m{0:6.1f}MiB\033[0m = \033[95m{1:9.0f}\033[0m sectors (512 bytes) \033[90m(file: {2} )\033[0m".format(tmp_file_sz_mib, file_sec_count,tmp_file))
	print()
	answ = input("Type 'yes' to confirm erase settings and start erasing disk: ")
	if (answ == "yes"):
		# do the JOB
		print()
		# begin
		print("\033[97mErasing beggining of disk '{}'\033[90m".format(dev))
		#pr1 = "ok" # for debug
		pr1 = do_proc('dd if={0} of={1} bs=512 count={2}'.format(tmp_file,dev,int(file_sec_count)))
		print("\033[0m")
		if (pr1 == False):
			print("Erasing first {} sectors from disk {} failed.".format(file_sec_count,dev))
			return 1 #delete_temp(tmp_file)
			#sys.exit("[ERROR:BEGIN_ERASE]")
		#end
		print("\033[97mErasing end of disk '{}' seek={} \033[90m".format(dev,int(end_sec_start)))
		#pr2 = "ok" # for debug
		pr2 = do_proc('dd if={0} of={1} bs=512 count={2} seek={3}'.format(tmp_file,dev,int(file_sec_count),int(end_sec_start)))
		print("\033[0m")
		if (pr2 == False):
			print("Erasing last {} sectors from disk {} failed.".format(file_sec_count,dev))
			return 2 #delete_temp(tmp_file)
			#sys.exit("[ERROR:END_ERASE]")
		# cleanup
		print("\033[92mBegin and end part of disk erased.\033[0m")
		print()
		print("Now to create new partition table on disk ose one of following commands:")
		print(" - MS-DOS (old/classic): \033[93mparted -s {} mktable msdos\033[0m ".format(dev))
		print(" - GPT (new/UEFI)      : \033[96mparted -s {} mktable gpt\033[0m ".format(dev))
		print(" ")
	else:
		print("You must type exactly 'yes' (case sensitive!).")
		return 3
	
	
	#print("Cleanup...")
	#delete_temp(tmp_file)
	
	# end function: do_the_job(tmp_file, tmp_file_sz, dev)	
	return 0
	

	
argp = argparse.ArgumentParser(description='Zero/FF-ing disk partition(s) tables(s)')
argp.add_argument('-l','--list', help="List available disks", required=False, action='store_true')
argp.add_argument('-d','--device', nargs=1, required=False, help="Specify device (e.g.: '/dev/sdc')")
argp.add_argument('-f','--fill-ff', required=False, default=False, action='store_true', help="Fill sectors with 0xff")
argp.add_argument('-0','--fill-00', required=False, default=False, action='store_true', help="Fill sectors with 0x00")
args = argp.parse_args()

#print("Zero/FF-ing disk partition(s) table(s) tool by")
print("Author: \033[37mPrzemyslaw W.\033[0m (c)2019")
print("License: Free")
print(" ")
#print("SYS.ARGV={}".format(sys.argv))
#print("ARGS PARSED: {}".format(args))
#print("list={} device={} fill-ff={} fill-00={}".format(args.list,args.device,args.fill_ff, args.fill_00))

# ------- device list
if (args.list == True):
	get_disk_list()
	print_devs()
# ------- Erase with 0xFF
elif (args.fill_ff == True and args.fill_00 == False):
	# file size
	tmp_file_sz = 32768 # [KiB]
	# create temp file
	tmp_file = "/tmp/fill-ff"
	# this is slow...
	#with open(tmp_file, "wb") as f:
	#	ff = 0xffffffff
	#	ffb = (ff).to_bytes(4, byteorder="big")
	#	for i in range(0, (1024*tmp_file_sz), 4):
	#		f.write(ffb)
	# check device
	if (args.device is None):
		print("No disk specified.")
		sys.exit("[ERROR:NO_DEVICE_SPECIFIED]")
	
	dev = args.device[0]
	
	# collect disk info
	get_disk_list()
	# check if device exists
	if (dev not in devs):
		print("Specified device '{}' do not exists.".format(dev))
		sys.exit("[ERROR:DEVICE_NOT_FOUND]")
	
	# dd is much faster...
	print("\033[97mPreparing 0xFF filed file...\033[90m")
	pre = do_proc('dd if=/dev/zero ibs=1k count={1} | tr "\\000" "\\377" > {0}'.format(tmp_file,tmp_file_sz))
	print("\033[0m")
	if (pre == False):
		print("Generating temp file failed (`{}`).".format(tmp_file))
		sys.exit("[ERROR:TEMP_FILE_CREATE]")
	
	ret = do_the_job(tmp_file, tmp_file_sz, dev)
	if (ret == 0):
		print(" ")
	elif (ret == 1):
		print(" ")
	elif (ret == 2):
		print(" ")
	elif (ret == 3):
		print(" ")
	else:
		print("do_the_job.return={}".format(ret))
	
	print("\033[90mCleanup...\033[0m")
	delete_temp(tmp_file)

# ---------- Erase with 0x00 ( /dev/zero )
elif (args.fill_00 == True and args.fill_ff == False):	
	# size of erase
	f_sz = 32768 #KiB
	f_name = "/dev/zero"
	# check ev
	if (args.device is None):
		print("No disk specified.")
		sys.exit("[ERROR:NO_DEVICE_SPECIFIED]")
	
	dev = args.device[0]
	# collect disk info
	get_disk_list()
	# check if device exists
	if (dev not in devs):
		print("Specified device '{}' do not exists.".format(dev))
		sys.exit("[ERROR:DEVICE_NOT_FOUND]")
	# run erase	
	ret = do_the_job(f_name, f_sz, dev)
	if (ret == 0):
		print(" ")
	elif (ret == 1):
		print(" ")
	elif (ret == 2):
		print(" ")
	elif (ret == 3):
		print(" ")
	else:
		print("do_the_job.return={}".format(ret))

# -------------- DAFAQ? SRSLY? -_-
elif (args.fill_00 == True and args.fill_ff == True):
	print(" ")
	print("\033[91mYou can not use both -0/--fill-00 and -f/--fill-ff at the same time. Choose only one.\033[0m")
# ------------ just print usage....
else:
	argp.print_help(sys.stdout)


sys.exit()	
