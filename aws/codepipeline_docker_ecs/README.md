# Project: AWS CodePipeline, Docker, ECS, and CloudFormation

This project demonstrates using Amazon's CI/CD CodePipeline service to deploy and update an AWS ECS cluster. Two pipelines are created:

1. A pipeline to create a AWS ECS using a CloudFormation template.
1. A pipeline to update the containers in the ECS stack.

The SAM CLI and CloudFormation templates are used to create the pipelines.

A couple of **WARNINGS**:

1. This projects creates AWS resources that cost money. Specifically, API Gateway and ECS resources are deployed into a VPC created for the project. The VPC consists of a one public subnet, one private subnet, an Internet gateway, and a NAT gateway. Be sure to execute the [Clean Up](#Clean-Up) section when done.
1. As soon as a pipeline is created in CodePipeline using the SAM CLI, it executes. For example, when the ECS pipeline is created in the steps below, it will immediately execute. 

## The Endpoint Deployed

The `docker` directory contains a simple FastAPI implementation of GET and POST endpoints. This Docker image will be deployed as part of the the lone task in the ECS cluster.   

## Prerequisites

1. This project assumes the AWS and SAM CLIs are are installed and configured. 
2. The following resources need to be created manually:
    1. A S3 bucket used to by the pipelines. Set your bucket at the `S3ArtifactBucket` parameter in the `cloudformation/ecs-create-pipeline/templage_pipeline.yaml` and the `cloudformation/ecs-update-pipeline/templage.yaml` CloudFormation templates.
    2. A ECR repository called `ecs1` needs to be created. The `buildspec.yml` files and pipeline templates assume this repository exists.
    3. An ARN for a AWS Developer Tools Code Connections to Github. Set the Github connection at the `GitHubConnectionArn` parameter in the `cloudformation/ecs-create-pipeline/template_pipeline.yaml` and the `cloudformation/ecs-update-pipeline/template.yaml` CloudFormation templates with the ARN of the Github Code Connection you create. When creating the Code Connection, you'll be prompted to referenced a IAM role. Below are the IAM Trust relationships and permissions policy needed for this project. The permissions are overly broad and would need to be refined for production use.
        1. Trust Relationships:
        ```
        {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "ecs-tasks.amazonaws.com",
                        "cloudformation.amazonaws.com",
                        "codebuild.amazonaws.com",
                        "codedeploy.amazonaws.com",
                        "codepipeline.amazonaws.com"
                    ]
                },
                "Action": "sts:AssumeRole"
            }
        ```
        2. Permissions Policy:
        ```
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "codestar-connections:UseConnection",
                        "codebuild:BatchGetBuilds",
                        "codebuild:StartBuild",
                        "codebuild:BatchGetBuildBatches",
                        "codebuild:StartBuildBatch",
                        "apigateway:*",
                        "cloudformation:*",
                        "cloudwatch:*",
                        "ec2:*",
                        "ecs:*",
                        "ecr:*",
                        "logs:*",
                        "route53:*",
                        "s3:*",
                        "servicediscovery:*",
                        "iam:DeleteRolePolicy",
                        "iam:DetachRolePolicy",
                        "iam:DeleteRole",
                        "iam:CreateRole",
                        "iam:PutRolePolicy",
                        "iam:AttachRolePolicy",
                        "iam:PassRole"
                    ],
                    "Resource": "*"
                }
            ]
        }
        ```

## Creating the Pipeline Stacks

Create the pipelines in the order below. Let the execution of each pipeline complete before proceeding.

I've configured the pipelines to run on demand. Meaning after the initial pipeline execution after install, the pipelines will only execute again when done manually through the command line or AWS CodePipeline console. 

### The Create ECS Stack Pipeline

To deploy and execute the pipeline that creates the ECS cluster, at the command line in the `cloudformation/ecs-create-pipeline` directory, execute the following:

```bash
sam build --template-file template_pipeline.yaml
sam deploy
```

As mentioned above, the pipeline will start executing once its created. **Let the pipeline finish before proceeding**.

Once the pipeline completes, two CloudFormation stacks will have been created: 

1. The `ecs-create-pipeline-v1` CodePipeline stack.  
2. The `ecs-create-pipeline-v1-app-stack` created by the `ecs-create-pipeline-v1` pipeline. The resources in this stack include the ECS cluster and an API Gateway to access the cluster's endpoint. 

If the CloudFormation `ecs-create-pipeline-v1-app-stack` is ever deleted, the `ecs-create-pipeline-v1` pipeline can be used to re-create it. 

Once the pipeline completes, use the Jupyter notebook in the `client` directory to verify the endpoint has been deployed successfully. In the AWS CodePipeline console, find the created pipeline. View the details of the `Deploy` action in the `Deploy` stage. The `Output` tab will have teh URL of the API Gateway.     

### The Update ECS Stack Pipeline

The pipeline created in this stack can be used to update the containers in the ECS cluster. It re-builds the Docker image in the `docker` directory and updates the container in the cluster. In the `cloudformation/ecs-update-pipeline` directory, run the following commands:

```bash
sam build 
sam deploy
```

This creates a CloudFormation CodePipeline stack called `ecs-update-pipeline-v1`. As mentioned above, the pipeline will start executing once its created. **Let the pipeline finish before proceeding**.

This pipeline uploads a new Docker image to ECR and updates the ECS Service task to reference that image. No other resource provisioned by the ECS Create Stack Pipeline are impacted. 

After this pipeline executes, the container will reflect the latest code in the `docker/main.py` script. This pipeline can be re-run to deploy changes made to the Docker image. The deployment can be verified by opening the AWS ECS console, navigating to the service created for this project, and viewing the "Deployments" tab. There should now be a new `Service revision`.

## Clean Up 

### CloudFormation Stacks

In the AWS CloudFormation console, delete the stacks created for this project in the following order. Let the deletion of each stack finish before deleting the next.

**NOTE: The order of stack deletion is very important.** Deleting the pipeline stacks before the app-stack will cause you many problems. IAM roles created by the pipeline stacks are needed to delete app-stack. Deletion of the app-stack from the Cloudformation console or command line will fail without those roles. So be sure to delete the `ecs-create-pipeline-v1-app-stack` first, then the pipeline stacks.  

1. ecs-create-pipeline-v1-app-stack - This is the root stack of the VPC, API Gateway, and ECS cluster stacks created by the Create ECS Pipeline. Deleting this stack will delete the other three.
2. ecs-update-pipeline-v1
3. ecs-create-pipeline-v1

### ECR Images

The Docker images in the `ecs1` repository created for this project need to be deleted.

### S3 Bucket

Delete the bucket created for the pipelines.

### Github Code Connection

Delete the AWS Developer Tools Code Connections to Github created for this project.

# Conclusion

The extra up-front effort of implementing CI/CD pipelines and IaC templates vastly reduces the effort involved with repeatable deployments.
