# CIS 4010 Cloud Computing

This repo contains the second of four assignments written for CIS 4010 Cloud Computing, a course first offered at the University of Guelph in 2020.

## Description

This assignment called for a set of scripts that could use the Azure and Amazon Web Service APIs to spin up EC2/AVM instances then install Docker containers on them, all according to input files.

`DeployAVM.py` and `DeployAWS.py` handle the creation of virtual machine instances based on the contents of `ConfigInstanceEC2.csv` and `ConfigInstanceAVM.csv`.

`DockerAVM.py` and `DockerAWS.py` handle the downloading, installation, and startup of Docker containers onto AVM or EC2 instances based on the contents of `ConfigDockerEC2.csv` and `ConfigDockerAVM.csv`.