# Mobile GPS Tracker

WORK-IN-PROGRESS

## Notes

salt = bcrypt.gensalt(rounds=10, prefix=b'2a')
JWT_SECRET_KEY = openssl rand -hex 32

docker build -t gps/tracker

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <YOUR ACCT ID>.dkr.ecr.us-east-1.amazonaws.com
docker tag gps/tracker <YOUR ACCT ID>.dkr.ecr.us-east-1.amazonaws.com/<AN ECR REPOSITORY>:tracker
docker push <YOUR ACCT ID>.dkr.ecr.us-east-1.amazonaws.com/<AN ECR REPOSITORY>:tracker

```bash

cd ./cloudformation
sam build
sam deploy

````

```bash

sam delete

```


<p align="center">
  <img src="./assets/img/nw1.png" />
</p>