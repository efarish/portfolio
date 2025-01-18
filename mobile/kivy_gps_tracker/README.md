# Application

WORK-IN-PROGRESS

This project focuses on implementing a RESTful API using AWS API Gateway, ECS, FastAPI, SQLAlchemy, and supporting AWS infrastructure. To reduce the cost of the resources deployed on AWS, reliability and scalability considerations are ignored. Therefore...

* A single low capacity Fargate launch type is used.
* The VPC created has only one public subnet.
* Cloud Map (instead of an ALB) is used to integrate API Gateway and ECS.   

The application is simple. It provisions a RESTful API to store data in a SQLite database stored on a single ECS task. The REST API is made available using an API Gateway integrated with an ECS service running tasks FastAPI endpoints.  

TODO: architecture details.

The architecture diagram is below.

<p align="center">
  <img src="./assets/img/nw1.png" />
</p>

# Deployment

Three AWS CodePipelines were created to deploy and maintain this applications.

- Create Pipeline: Runs the CloudFormation templates found in the directory `./create-app` to create the application.
- Update Lambda Pipeline: For the AWS Lambda function deployed with this application, update the Lambda with the latest code. 
- Update Pipeline: Update the AWS ECS tasks with the latest code. 

NOTE: as soon as a pipeline is deployed to AWS, it runs. 

Two AWS resource not provisioned by the `create-pipeline` and need to be manually created before running and of the pipelines. 

1. is the AWS Developer Tools GitHub Connection referenced by the `GitHubConnectionArn` property in the pipeline templates. The resource will need to be manually created in any AWS account trying to run these pipelines. The connection needs to point to where this code is stored and its ARN used to update the pipeline templates. For this project, the code was stored in the Git Hub repository `https://github.com/efarish/portfolio`. 
2. An AWS ECR repository with the name `ecs1`. This repository is referenced by the CloudFormation templates and the pipeline `buildspec.yml` files.

The following commands were used to build and deploy the pipelines.

```bash

sam build
sam deploy

```

# Clean Up 

### CloudFormation Stacks

In the AWS CloudFormation console, delete the stacks created for this project in the following order. Let the deletion of each stack finish before deleting the next.

**NOTE: The order of stack deletion is very important.** Deleting the pipeline stacks before the app-stack will cause you many problems. IAM roles created by the pipeline stacks are needed to delete the application stack. Delete the application stack first, then delete the pipeline stacks.

### ECR Images

The Docker images in the `ecs1` repository (or whatever repository you used) created for this project need to be deleted.

### S3 Bucket

Delete the bucket created for the pipelines.

### Github Code Connection

Delete the AWS Developer Tools Code Connections to Github created for this project.

# Conclusion

The extra up-front effort of implementing CI/CD pipelines and IaC templates vastly reduces the effort involved with repeatable deployments.

# Notes Yet To Be incorporated

* salt = bcrypt.gensalt(rounds=10, prefix=b'2a')
* JWT_SECRET_KEY = openssl rand -hex 32
