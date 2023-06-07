#!/bin/bash
# to install docker
sudo yum update
sudo yum install docker -y
sudo usermod -a -G docker ec2-user
id ec2-user
newgrp docker
sudo systemctl enable docker.service
sudo systemctl start docker.service

# to pull the api docker images from the ecr
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# DO NOT uncomment the below. This is for illustration purposes when it comes
# to what you need to execute next once you are in the ec2 instance
# first authenticate yourself so that you can pull the docker image
# aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <id>.dkr.ecr.<region>.amazonaws.com
# docker pull <id>.dkr.ecr.<region>.amazonaws.com/polygon-claim-rent:latest
# docker run polygon-claim-rent:latest
