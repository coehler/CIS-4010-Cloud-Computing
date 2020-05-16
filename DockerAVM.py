
''' Program that installs Docker containers on AVM instances based on a CSV file.

:author: 	Christopher Oehler
:email: 	coehler@uoguelph.ca
'''

import os.path
import csv
import sys
import paramiko
import subprocess
import json

allowed_containers = [

	"golang",
	"gcc",
	"swift",
	"julia",

]

template = ""

blu = "\033[94m"
grn = "\033[92m"
red = "\033[91m"
pur = "\033[95m"
xxx = "\033[0m"

if len(sys.argv) > 0:

	print("Using " + str(sys.argv[1]) + " as CSV deployment template.")
	template = str(sys.argv[1]);

else:

	quit()

print("Parsing CSV container template.")

with open(template) as csv_file:

	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0
	success_count = 0

	for row in csv_reader:

		if line_count != 0:

			instance 	= row[0]
			container 	= row[1]
			start 		= row[2]
			key_file	= row[3]

			if container not in allowed_containers:

				print(red + "*** Error: container " + container + " is not allowed" + xxx)
				continue

			# Check if VM exists

			result = subprocess.run(["az", "vm", "list"], stdout=subprocess.PIPE)

			vm_list = json.loads(result.stdout.decode('utf-8'))

			exists = False

			for vm in vm_list:

				if vm["name"] == instance:

					exists = True
					break
				
			if not exists:
				
				print(red + "*** Error: no instance with the name " + instance + " exists" + xxx)
				continue			

			# Get VM public IP address

			result = subprocess.run(["az", "vm", "list-ip-addresses"], stdout=subprocess.PIPE)

			vm_ip_list = json.loads(result.stdout.decode('utf-8'))

			public_ip = ""

			for vm in vm_ip_list:

				if vm["virtualMachine"]["name"] == instance:

					public_ip = vm["virtualMachine"]["network"]["publicIpAddresses"][0]["ipAddress"]

			print("Attempting SSH connection to " + blu + instance + xxx + " at public IP " + blu + public_ip + xxx)

			# Get private key pair

			if os.path.isfile(key_file):

				print("\t Located RSA private key " + blu + key_file + xxx)

			else:

				print(red + "\t *** Error: RSA private key with name " + key_file + " could not be found" + xxx)
				continue

			user_name = "avm-user"

			key = paramiko.RSAKey.from_private_key_file(key_file)

			ssh_client = paramiko.SSHClient()

			ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

			try:
				
				ssh_client.connect(hostname = public_ip, username = user_name, pkey = key) # Establish SSH connection

				print (pur + "\t " + user_name + "@" + str(public_ip) + "$ " + xxx + "curl -fsSL https://get.docker.com -o get-docker.sh")
				stdin, stdout, stderr = ssh_client.exec_command("curl -fsSL https://get.docker.com -o get-docker.sh")
				stdout.read()

				print (pur + "\t " + user_name + "@" + str(public_ip) + "$ " + xxx + "sudo sh get-docker.sh")
				stdin, stdout, stderr = ssh_client.exec_command("sudo sh get-docker.sh")
				stdout.read()					

				print (pur + "\t " + user_name + "@" + str(public_ip) + "$ " + xxx + "sudo service docker start")
				stdin, stdout, stderr = ssh_client.exec_command("sudo service docker start")
				stdout.read()

				print (pur + "\t " + user_name + "@" + str(public_ip) + "$ " + xxx + "sudo docker pull " + container)
				stdin, stdout, stderr = ssh_client.exec_command("sudo docker pull " + container)
				stdout.read()

				if start == "Y":

					print (pur + "\t " + user_name + "@" + str(public_ip) + "$ " + xxx + "sudo docker run -i -t -d " + container)
					stdin, stdout, stderr = ssh_client.exec_command("sudo docker run -i -t -d " + container)
					stdout.read()

				print(grn + "\t Successfully installed " + container + " on " + str(public_ip) + xxx)

				ssh_client.close()

			except Exception as e:

				print(red + "\t *** Error: " + str(e) + xxx)

				
		line_count += 1