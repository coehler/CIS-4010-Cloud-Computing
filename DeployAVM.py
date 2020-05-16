''' Program that creates VM instances based on a CSV file.

:author: 	Christopher Oehler
:email: 	coehler@uoguelph.ca
'''

import csv
import sys
import os
import os.path
import subprocess
import json

allowed_instances = [

	"UbuntuLTS",	# Ubuntu Server 16.04 LTS
	"RHEL",			# Red Hat Enterprise Linux 7.4 
	"Debian",		# Debian 10 "Buster"

]

allowed_types = [

	"Standard_B1ls"

]

template = ""

blu = "\033[94m"
grn = "\033[92m"
red = "\033[91m"
xxx = "\033[0m"

if len(sys.argv) > 0:

	print("Using " + str(sys.argv[1]) + " as CSV deployment template.")
	template = str(sys.argv[1]);

else:

	quit()


print("Parsing CSV deployment template.")

with open(template) as csv_file:

	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0
	success_count = 0

	for row in csv_reader:

		if line_count != 0:

			instance 		= row[0]
			name 			= row[1]
			size_cpu 		= row[2]
			key 			= row[3]

			if name not in allowed_instances:

				print (red + "*** Error: no instance of type " + name + xxx)
				continue

			result = subprocess.run(["az", "vm", "list"], stdout=subprocess.PIPE)

			vm_list = json.loads(result.stdout.decode('utf-8'))

			exists = False

			for vm in vm_list:

				if vm["name"] == instance:

					exists = True
					break
				
			if exists:
				
				print (red + "*** Error: an instance called " + instance + " already exists" + xxx)
				continue

			print("Creating " + blu + name + xxx + " instance called " + blu + instance + xxx)

			print("\t CPU: " + size_cpu)

			print("\t SSH key name: " + key)

			if os.path.isfile(key) and os.path.isfile(key + ".pub"):
				
				print("\t Key pair " + blu + key + xxx + " & " + blu + key + ".pub" + xxx + " already exists")

			else:

				print("\t Key pair " + blu + key + xxx + " could not be found")

				result = subprocess.run(["ssh-keygen",

					"-m", "PEM",

					"-f", key,

					"-P", "",

					"-t", "rsa",

					"-b", "4096"

				], stdout=subprocess.PIPE)

				print(grn + "\t Successfully created key pair " + key + " & " + key + ".pub" + xxx)

			# Create Azure VM

			result = subprocess.run(["az", "vm", "create",

				"--resource-group", "coehler-RG",

				"--name", instance,

				"--image", name,

				"--admin-username", "avm-user",

				"--ssh-key-value", key + ".pub"

				], stdout=subprocess.PIPE)
			
			print(grn + "\t Successfully created " + instance + xxx)

			success_count += 1

		line_count += 1

	print("Created " + str(success_count) + " instances")