#!/bin/bash
# the below is for illustrative purposes, but those are the commands to push
# the image to ecr
docker build -t polygon-claim-rent.latest .
aws ecr get-login-password --profile <aws profile> | docker login --username AWS --password-stdin <id>.dkr.ecr.<region>.amazonaws.com
docker tag <image just built above> <id>.dkr.ecr.<region>.amazonaws.com/polygon-claim-rent:latest
docker push <id>.dkr.ecr.<region>.amazonaws.com/polygon-claim-rent:latest
