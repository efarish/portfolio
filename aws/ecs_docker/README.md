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

NOTE: The `.env` file included with this distribution needs to be updated to reference a valid AWS S3 bucket for the account used for this project.

# Docker Build

Using the Docker file in the `./server` folder, a very simple endpoint container is created. 

```bash
docker build -t ecs1/server .
docker container run -d -p 9090:9090 ecs1/server
docker ps
```

There should now be a container running in Docker. Try to access the container endpoint at `http://localhost:9090` in a web browser or using the client Jupyter notebook in this distribution's `client` directory. 

Now shutdown the container.

```bash
docker stop <container id>
```

Tag the Docker image as below. I've removed the AWS account ID used for this project, but your AWS ECR URL should look similar to whats below

```bash
docker tag ecs1/server <YOUR AWS ACCT ID>.dkr.ecr.us-east-1.amazonaws.com/ecs1:server
```

# Test Locally

Since the endpoint will use the AWS S3 service, credentials will need to be provided. An easy way to do this is by providing the credentials through environment variables when the container is started. Below is an example.

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

I used AWS CloudFormation and SAM to provision the stack defined in `./sam-app-ecs1/template.yaml`. This file specifies the following resources to be created in AWS.

- A VPC with two public subnets
- Fargate Task Definition
- Fargate Cluster
- Fargate Service
- An Application Load Balancer

To build and deploy the cluster to AWS, use the SAM CLI commands below. Be sure to run this commands in this distribution's `sam-app-ec1` directory as thats where the SAM template file is.

```bash
sam build
sam deploy
```

The deployment will take a few minutes. Status messages will appear in the console and deployment progresses. The deployment can also be monitored in CloudFormation.

When the deployment completes, the load balance URL should be printed out by the SAM CLI. The following AWS endpoint routes should now be available:

1. http://< LB URL >/ - A health check use by the load balancer.
1. http://< LB URL >/getInfo - A simple GET method.
1. http://< LB URL >/upload - A POST method to which files can be posted and copied to S3.   

The GET methods can be access through a browser. The notebook in the `./client` folder can be used to post a sample image. 

## Container Access to AWS service

In the SAM `./sam-app-ecs1/template.yaml` file, the role `ECSTaskRole` is created and is assigned to the `TaskDefinition` resources's `TaskRoleArn` property. This configuration gives the container created by the service and task definitions access to S3 and CloudWatch logs. Any other AWS service needed by the endpoint can be added to the `ECSTaskRole` element `Policies`->`PolicyDocument`->`Statement`->`Affect`->`Action`.  

# AWS Clean Up

To avoid unwanted AWS charges, the CloudFormation stack for this project must be deleted. Go to CloudFormation in the AWS console, find the stack with the name `sam-app-ecs1` and delete it.

Finally, in the AWS console go to the ECR screen screen and remove the Docker image used for this project.

# Conclusion

Using CloudFormation and SAM greatly expedites the creation of AWS applications. This simple project demonstrated accessing AWS services from a Docker container run locally and in AWS ECS.   

TODO 
1. Add Api Gateway 
1. Add Authentication/Authorization

