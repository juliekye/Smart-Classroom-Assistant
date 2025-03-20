docker image rm 504326962860.dkr.ecr.us-east-1.amazonaws.com/awsomeppl:cse546p2
docker build -t 504326962860.dkr.ecr.us-east-1.amazonaws.com/awsomeppl:cse546p2 .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 504326962860.dkr.ecr.us-east-1.amazonaws.com
docker push 504326962860.dkr.ecr.us-east-1.amazonaws.com/awsomeppl:cse546p2

