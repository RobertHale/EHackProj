import subprocess

if __name__ == "__main__":
	cmd = "nmap -sV 1.1.1.1"
	proc = subprocess.Popen(cmd.split())
