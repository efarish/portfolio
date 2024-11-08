# Project: Access AWS Services From Docker

WORK IN PROGRESS

## Docker Build

Using the configuration and code in the `./server` folder, a very simple endpoint container is created. I used the commands below. I've removed the AWS account ID used for this project, but your AWS ECR URL should look similar to whats below.

```bash
docker build -t ecs1/server .
docker container run -d -p 9090:9090 ecs1/server
docker ps
```

There should now be a container running in Docker. Try to access the container endpoint in a browser using the URL `localhost:9090`. 

Now shutdown the container.


```bash
docker stop <container id>
```

And tag the Docker image as below.

```bash
docker tag ecs1/server <YOUR AWS ACCT ID>.dkr.ecr.us-east-1.amazonaws.com/ecs1:server
```


## Push Image to ECR

Below, the AWS CLI is used to push the Docker image to AWS ECR. The command below assumes the AWS CLI configuration has already been setup. 

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <YOUR ACCT ID>.dkr.ecr.us-east-1.amazonaws.com
docker push <YOUR AWS ACCT ID>.dkr.ecr.us-east-1.amazonaws.com/ecs1:server
```

## Provision ECS Cluster in AWS

I used AWS CloudFormation and SAM to provision a ECS cluster and a single task that references the image loaded to ECR.  The file `./template.yaml` has the CloudFormation configuration to provision the cluster. As I don't bother specifying a VPC to use for the cluster, the AWS account's default VPC will be used.

To build and deploy the cluster to AWS, I used the SAM CLI commands below. Be sure to run this commands in the `sam-app-ec1` directory as it has the template file.

```bash
sam build
sam deploy
```

## Run The ECS Cluster

In the AWS console, go the the ECS service, on Task Definitions screen select newly defined task, select `Deploy->Run`, on the create screen, select the `ECS2` cluster created for this project, and then deploy the task to cluster by clicking the create task button. 

A Public IP will be available on the cluster tasks configuration screen, try opening that in your browser. Be sure to use the port `9090` when access the public IP AWS has created for the task. 

