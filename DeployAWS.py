
''' Program that creates VM instances based on a CSV file.

:author: 	Christopher Oehler
:email: 	coehler@uoguelph.ca
'''

import csv
import sys
import os
import boto3

client = boto3.client("ec2")

allowed_instances = [ # For us-east-2 (Ohio)

	"ami-0e38b48473ea57778",	# Amazon Linux 2 AMI (HVM), SSD Volume Type (64-bit x86)
	"ami-0998bf58313ab53da",	# Amazon Linux AMI 2018.03.0 (HVM), SSD Volume Type
	"ami-0520e698dd500b1d1",	# Red Hat Enterprise Linux 8 (HVM), SSD Volume Type
	"ami-04c5bab51cc146925",	# SUSE Linux Enterprise Server 15 SP1 (HVM), SSD Volume Type
	"ami-0fc20dd1da406780b"		# Ubuntu Server 18.04 LTS (HVM), SSD Volume Type
]

allowed_types = [

	"t2.micro"

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
			storage 		= row[3]
			storage_type 	= row[4]
			storage_size 	= row[5]
			key 			= row[6]

			if name not in allowed_instances:

				print (red + "*** Error: no instance of type " + name + xxx)
				continue

			response = client.describe_instances(Filters = [

					{
						"Name": "tag:Name",

						"Values": [instance]

					}
				]
			)

			if response["Reservations"] == []: # If no instance with this name already exists.

				print("Creating " + blu + name + xxx + " instance called " + blu + instance + xxx)

				print("\t CPU: " + size_cpu)

				if storage == "Y":

					print("\t Storage: " + storage_size + " GB of " + storage_type)

				else:

					print("\t No storage")

				print("\t SSH key name: " + key)

				try:

					response = client.describe_key_pairs(KeyNames = [key])

					print("\t Key pair " + blu + key + xxx + " already exists")

				except:

					print("\t Generating 2048-bit RSA key pair " + blu + key + xxx)

					ec2_key = client.create_key_pair(KeyName = key) # Create a 2048-bit RSA key pair.

					with open("./" + key + ".pem", 'w') as file:
						
						file.write(ec2_key["KeyMaterial"])

					os.chmod(key + ".pem", 0o400)

					print(grn + "\t Successfully generated" + xxx)

				''' Create an EC2 instance
		
				:author:	adapted from Boto 3 Docs 1.12.0.
				'''
				
				client.run_instances(

					ImageId = name, # revert to name in final

					MinCount = 1,

					MaxCount = 1,

					InstanceType = size_cpu,

					KeyName = key,

					TagSpecifications = [

						{

							"ResourceType": "instance",

							"Tags": [

								{"Key": "Name", "Value": instance }

							]

						}

					]
				)
				
				print(grn + "\t Successfully created " + instance + xxx)

				success_count += 1

			else:

				print (red + "*** Error: an instance called " + instance + " already exists" + xxx)
				continue

		line_count += 1

	print("Created " + str(success_count) + " instances")