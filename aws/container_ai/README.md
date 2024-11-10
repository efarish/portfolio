# Project: Access AWS Services From Docker

This project demonstrates using AWS services within a docker container which AWS makes very easy to do.

Below are the steps to build and test the Docker image locally, deploy it to AWS ECR, create the ECS cluster, and run a ECS task. 

To demonstrate accessing AWS services, the Docker container copies to S3 files posted to an FastAPI endpoint.

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

Since the endpoint will use the AWS S3 services, credentials will need to be provided. An easy way to do this is provide the credentials through environment variables when the container is started. Below is an example.

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

I used AWS CloudFormation and SAM to provision an ECS cluster and a single task definition that references the image loaded to ECR.  The file `./template.yaml` has the CloudFormation configuration to provision the cluster. A couple notes on the template file.

1. The `Image` property needs to be customized to reference the ECR Docker image uploaded previously. 
1. The `TaskRoleArn` property needs to reference an AWS account role that gives access to whatever AWS services your endpoint will need. Below is an example policy that provides access to CloudWatch logs, S3, and Rekognition (AWS's cloud-based image and video analysis service). 
```
{
	"Statement": [
		{
			"Action": [
				"logs:*"
			],
			"Resource": "arn:aws:logs:*:*:*",
			"Effect": "Allow"
		},
		{
			"Action": [
				"s3:GetObject",
				"s3:PutObject"
			],
			"Resource": "arn:aws:s3:::*",
			"Effect": "Allow"
		},
		{
			"Action": [
				"rekognition:DetectLabels"
			],
			"Resource": "*",
			"Effect": "Allow"
		}
	]
}
```
1. The `ExecutionRoleArn` property needs to reference a role available in the AWS account that contains the policy `AmazonECSTaskExecutionRolePolicy`. 

To build and deploy the cluster to AWS, use the SAM CLI commands below. Be sure to run this commands in this distribution's `sam-app-ec1` directory as it has the template file.

```bash
sam build
sam deploy
```

# Run The ECS Cluster in AWS

In the AWS console, go the the ECS service, on Task Definitions screen select newly defined task, select `Deploy->Run`, on the create screen, select the `ecs1` cluster created for this project, and then deploy the task to the cluster by clicking the create task button. 

A public IP will be available on the cluster task's configuration screen. Use that IP and the Jupyter notebook in this distribution's `client` directory to test the endpoint. 

# AWS Clean Up

At this point you'll have a task running in the ECS cluster created for this project. To avoid unwanted AWS charges, the task must be terminated. Go to the AWS ECS console, click on the cluster created for this project, open the `Tasks` tab, and stop the task. 

Next, to remove the resources created for this project: go to CloudFormation in the AWS console, find the stack with the name `sam-app-ecs1` and delete it.

Finally, in the AWS console go to the ECR screen screen and remove the Docker image used for this project.

# Conclusion

This simple project demonstrated accessing AWS services from a Docker container running locally and in AWS ECS.   



