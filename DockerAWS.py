
''' Program that installs Docker containers on EC2 instances based on a CSV file.

:author: 	Christopher Oehler
:email: 	coehler@uoguelph.ca
'''

import os.path
import csv
import sys
import boto3
import botocore
import paramiko

client = boto3.client("ec2")

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

			if container not in allowed_containers:

				print(red + "*** Error: container " + container + " is not allowed" + xxx)
				continue

			# Collect data on EC2 Instance

			response = client.describe_instances(Filters = [

					{
						"Name": "tag:Name",

						"Values": [instance]

					}
				]
			)

			if response["Reservations"] == []:

				print(red + "*** Error: no instance with the name " + instance + " exists" + xxx)
				continue

			public_ip = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]

			print("Attempting SSH connection to " + blu + instance + xxx + " at public IP " + blu + public_ip + xxx)

			path = response["Reservations"][0]["Instances"][0]["KeyName"]

			if os.path.isfile(path + ".pem"):

				print("\t Located " + blu + path + ".pem" + xxx)

			else:

				print(red + "\t *** Error: RSA private key with name " + path + ".pem could not be found" + xxx)
				continue

			user_name = "ec2-user"

			image_id = response["Reservations"][0]["Instances"][0]["ImageId"]

			if image_id != "ami-0fc20dd1da406780b":
			
				print("\t Image ID is " + blu + image_id + xxx + " and SSH user name is " + blu + user_name + xxx)

			else:

				user_name = "ubuntu"

				print("\t Image ID is " + blu + image_id + xxx + " and SSH user name is " + blu + user_name + xxx)

			# Attempt SSH connection

			key = paramiko.RSAKey.from_private_key_file(path + ".pem")

			ssh_client = paramiko.SSHClient()

			ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

			try:
				
				ssh_client.connect(hostname = public_ip, username = user_name, pkey = key) # Establish SSH connection

				if image_id == "ami-0e38b48473ea57778" or image_id == "ami-04c5bab51cc146925": # if Amazon Linux 2 or SUSE Linux use ...

					print (pur + "\t " + user_name + "@" + str(public_ip) + "$ " + xxx + "sudo amazon-linux-extras install docker")
					stdin, stdout, stderr = ssh_client.exec_command("sudo amazon-linux-extras install docker")
					stdout.read()

				elif image_id == "ami-0fc20dd1da406780b": # if Ubuntu Linux use ...

					print (pur + "\t " + user_name + "@" + str(public_ip) + "$ " + xxx + "curl -fsSL https://get.docker.com -o get-docker.sh")
					stdin, stdout, stderr = ssh_client.exec_command("curl -fsSL https://get.docker.com -o get-docker.sh")
					stdout.read()

					print (pur + "\t " + user_name + "@" + str(public_ip) + "$ " + xxx + "sudo sh get-docker.sh")
					stdin, stdout, stderr = ssh_client.exec_command("sudo sh get-docker.sh")
					stdout.read()					
					
				else:

					print (pur + "\t " + user_name + "@" + str(public_ip) + "$ " + xxx + "sudo yum -y install docker")
					stdin, stdout, stderr = ssh_client.exec_command("sudo yum -y install docker")
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