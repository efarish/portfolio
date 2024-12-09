# This is a Work-In-Progress

# Project: AWS CodePipeline, Docker, ECS, and CloudFormation

This project demonstrates using Amazon's CI/CD service CodePipeline to deploy and update an AWS ECS cluster.

## Create CodePipeLine

The directory `docker` directory contains a simple FastAPI endpoint implementation GET and POST FastAPI endpoints. The The resources are deployed into a VPC created by the template.   

The `cloudformation/ecs` directory has a CloudFormation template to deploy an API Gateway connected to an ECS cluster containing a single task. The task's Docker container exposes simple GET and POST FastAPI endpoints. The The resources are deployed into a VPC created by the template.   

## Update CodePipeline

CloudFormation 

Template Parameters: 

1. PipeLineName: A uniques name for your pipeline.
1. SourceRepository: The GitHub repository used by the pipeline in the format: <GitHub Owner>/<Repository Name>.
1. ECSClusterName: The name of the ECS cluster created above.
1. ECSServiceName: The name of the ECS Service created above.
1. GitHubConnectionArn: The ARN of an existing AWS Development Tools Connection used to connect to GitHub.  
1. S3BucketName: An existing S3 bucket name that will be used by CodePipeline to store artifacts.

## Deploy



## Test

## Cleanup

## TODO 

Two resources are crated outside of the CloudFormation templates:

1. The S3 bucket used by CodePipeline.
1. The Development Tools Connection to GitHub.
1. Put the creation of the AWS ECS cluster in a pipeline.

Additional work could be done to manage these resources within CloudFormation.