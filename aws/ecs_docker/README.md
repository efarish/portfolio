# Project: Access AWS Services From Docker

WORK IN PROGRESS

This project demonstrates using AWS services within a docker container which AWS makes very easy to do.

Below are the steps to build and test the Docker image locally, deploy it to AWS ECR, and create a ECS cluster. 

To demonstrate accessing AWS services, the Docker container exposes a FastAPI endpoint that copies posted files to S3.

This project demonstrates providing AWS credentials to a Docker container in two cases:

1. When testing the Docker container locally. 
1. When running the Docker container in AWS ECS.

# The App

In the `./server` directory are the files to build the Docker image. The `main.py` script contains an endpoint that supports GET and POST requests. The POST copies files to S3. The web framework FastAPI is used to implement the endpoint.  

NOTE: The `.env` file included with this distribution need to be updated to reference a valid AWS S3 bucket for the account used for this demonstration.

# Docker Build

Using the Docker configuration in the `./server` folder, a very simple endpoint container is created. 

```bash
docker build -t ecs1/server .
docker container run -d -p 9090:9090 ecs1/server
docker ps
```

There should now be a container running in Docker. Try to access the container endpoint using the client Jupyter notebook in this distribution's `client` directory. 

Now shutdown the container.

```bash
docker stop <container id>
```

Tag the Docker image as below. I've removed the AWS account ID used for this project, but your AWS ECR URL should look similar to whats below

```bash
docker tag ecs1/server <YOUR AWS ACCT ID>.dkr.ecr.us-east-1.amazonaws.com/ecs1:server
```

# Test Locally

Since the endpoint will use the AWS S3 service, credentials will need to be provided. An easy way to do this is provide the credentials through environment variables when the container is started. Below is an example.

```bash
docker container run -p 9090:9090 -e AWS_ACCESS_KEY_ID='YOUR AWS ACCT ID' -e AWS_SECRET_ACCESS_KEY='YOUR AWS ACCT KEY' ecs1/server  
```

# Push Docker Image to ECR

Below, the AWS CLI is used to push the Docker image to AWS ECR. The command below assumes the AWS CLI configuration has already been setup. 

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <YOUR ACCT ID>.dkr.ecr.us-east-1.amazonaws.com
docker push <YOUR AWS ACCT ID>.dkr.ecr.us-east-1.amazonaws.com/ecs1:server
```

# Provision ECS Cluster in AWS

I used AWS CloudFormation and SAM to provision an ECS cluster and a single task definition that references the image loaded to ECR.  The file `./template.yaml` has the CloudFormation configuration to provision the cluster. A couple note(s) on the template file.

1. The `Image` property needs to be customized to reference the ECR Docker image uploaded previously. 

To build and deploy the cluster to AWS, use the SAM CLI commands below. Be sure to run this commands in this distribution's `sam-app-ec1` directory as it has the template file.

```bash
sam build
sam deploy
```

At this point, an AWS ECS cluster should be deployed. Within it will be a service and a single task. In the task's configuration screen, find the public IP. Use that IP and the notebook in this distribution's `./client` folder to test the ECS endpoint.

# AWS Clean Up

To avoid unwanted AWS charges, the CloudFormation stack for this project must be deleted. Go to CloudFormation in the AWS console, find the stack with the name `sam-app-ecs1` and delete it.

Finally, in the AWS console go to the ECR screen screen and remove the Docker image used for this project.

# Conclusion

This simple project demonstrated accessing AWS services from a Docker container running locally and in AWS ECS.   

TODO 
1. Add App Load Balancer (maybe VPC?)
1. Add Api Gateway 
1. Add Authentication/Authorization

