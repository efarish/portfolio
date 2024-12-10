# This is a Work-In-Progress

# Project: AWS CodePipeline, Docker, ECS, and CloudFormation

This project demonstrates using Amazon's CI/CD CodePipeline service to deploy and update an AWS ECS cluster. Two pipelines are used:

1. A pipeline to create a AWS ECS using a CloudFormation template.
1. A pipeline to update the containers in the ECS stack.

The SAM CLI and CloudFormation templates are used to create the pipelines.

A couple of **WARNINGS**:

1. This projects creates AWS resources that cost money. Be sure to execute the [Clean Up](#Clean-Up) section when done.
1. As soon as a pipeline is created using the SAM CLI, it executes. 

## The Endpoint Deployed

The `docker` directory contains a simple FastAPI endpoint implementation GET and POST FastAPI endpoints. This Docker image will be deployed as the lone task in the ECS cluster.   

## Prerequisites

1. This project assumes the AWS and SAM CLIs are are installed and configured. 
2. The following resources need to be created manually:
    1. A S3 bucket used to by the pipelines. Set you bucket at the `S3ArtifactBucket` parameter in the `cloudformation/ecs-create-pipeline/templage_pipeline.yaml` and the `cloudformation/ecs-update-pipeline/templage.yaml` CloudFormation templates.
    2. An ARN for a AWS Developer Tools Code Connections. Set the Github connection in the `GitHubConnectionArn` parameter in the `cloudformation/ecs-create-pipeline/template_pipeline.yaml` and the `cloudformation/ecs-update-pipeline/template.yaml` CloudFormation templates. 
    3. A ECR repository called `ecs1` needs to be created. The `buildspec.yml` and pipeline templates assume this repository exists.

## Creating the Pipeline Stacks

Create the pipelines in the order below. Let the execution of each stack completes before proceeding.

### The ECS Stack Pipeline

In the `cloudformation/ecs-create-pipeline` directory, run the following commands:

```bash
sam build --template-file template_pipeline.yaml
sam deploy
```

As mentioned above, the pipeline will start executing once its created. **Let the pipeline finish before proceeding**.

Once the pipeline completes, two stacks will have been created: 

1. The `ecs-create-pipeline-v1` CodePipeline stack. This pipeline creates the application AWS resources.
2. The `ecs-create-pipeline-v1-app-stack` created by the `ecs-create-pipeline-v1` pipeline. The resources in this stack include the ECS cluster and an API Gateway to access the cluster's endpoint. 

Once the pipeline completes, use the Jupyter notebook in the `client` directory to verify the endpoint has been deployed successfully.   

### The ECS Update Pipeline

This pipeline can be used to update the containers in the ECS cluster. It re-builds the Docker image in the `docker` directory and updates the containers in the created cluster. 

In the `cloudformation/ecs-update-pipeline` directory, run the following commands:

```bash
sam build 
sam deploy
```

This creates a CloudFormation CodePipeline stack called `ecs-update-pipeline-v1`. As mentioned above, the pipeline will start executing once its created. **Let the pipeline finish before proceeding**.

After this pipeline executes, the container will reflect the latest code in the `docker/main.py` script. The `ecs-update-pipeline-v1` can be re-run to deploy changes made to the Docker image.

## Clean Up 

In the AWS CloudFormation console, delete the stacks created for this project in the following order. Let the deletion of each stack finish before deleting the next.

1. ecs-create-pipeline-v1-app-stack
2. ecs-update-pipeline-v1
3. ecs-create-pipeline-v1

