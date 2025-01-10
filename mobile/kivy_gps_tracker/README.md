# Mobile GPS Tracker

WORK-IN-PROGRESS

This project focuses on implementing a REST API using FastAPI and AWS ECS. To make it more interesting, a Kivy mobile application client is also implemented. Furthermore, to reduce the cost of the resources deployed on AWS, reliability and scalability considerations are ignored. Therefore, a single low capacity Fargate launch type is used.

## Notes

salt = bcrypt.gensalt(rounds=10, prefix=b'2a')
JWT_SECRET_KEY = openssl rand -hex 32

docker build -t gps/tracker .

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS ACCT ID>.dkr.ecr.us-east-1.amazonaws.com

docker tag gps/tracker <AWS ACCT ID>.dkr.ecr.us-east-1.amazonaws.com/ecs1:tracker

docker push <AWS ACCT ID>.dkr.ecr.us-east-1.amazonaws.com/ecs1:tracker

```bash

cd ./cloudformation
sam build
sam deploy

````

```bash

sam delete

```

```bash
sam build --template template_pipeline_stack.yaml --config-file samconfig_pipeline.toml

sam build --template template_app_stack.yaml --config-file samconfig.toml

```

<p align="center">
  <img src="./assets/img/nw1.png" />
</p>

# Customizations

1. template_pipeline_stack.yaml -> GitHubConnectionArn
2. update-pipeline->buildspec.yml->ECS_CONTAINER_NAME must match create-app->service-tracker->TaskDefinition:ContainerDefinition:Name

## Clean Up 

### CloudFormation Stacks

In the AWS CloudFormation console, delete the stacks created for this project in the following order. Let the deletion of each stack finish before deleting the next.

**NOTE: The order of stack deletion is very important.** Deleting the pipeline stacks before the app-stack will cause you many problems. IAM roles created by the pipeline stacks are needed to delete app-stack. Deletion of the app-stack from the Cloudformation console or command line will fail without those roles. So be sure to delete the `ecs-create-pipeline-v1-app-stack` first, then the pipeline stacks.  

1. ecs-create-pipeline-v1-app-stack - This is the root stack of the VPC, API Gateway, and ECS cluster stacks created by the Create ECS Pipeline. Deleting this stack will delete the other three.
2. TODO

### ECR Images

The Docker images in the `ecs1` repository (or whatever repository you used) created for this project need to be deleted.

### S3 Bucket

Delete the bucket created for the pipelines.

### Github Code Connection

Delete the AWS Developer Tools Code Connections to Github created for this project.

# Conclusion

The extra up-front effort of implementing CI/CD pipelines and IaC templates vastly reduces the effort involved with repeatable deployments.