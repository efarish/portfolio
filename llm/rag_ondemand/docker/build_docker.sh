#!/bin/bash

PROJECT_NAME=rag_ondemand # Used build path to source files.
ECR_REPO=ecs1                 # Name of ECR image repository.
DOCKER_IMAGE_NAME=rag_ondemand     # Name of Tracker Docker image.
ECR_IMG_NAME=${ECR_REPO}:${DOCKER_IMAGE_NAME}
#ECR_MAIN_URI="${AWS_ACCT}.dkr.ecr.${AWS_REGION}.amazonaws.com"
#ECR_IMAGE_URI=${ECR_MAIN_URI}/${ECR_REPO}:${DOCKER_IMAGE_NAME}

#aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_MAIN_URI}
docker build -t ${ECR_IMG_NAME} ./
#docker build --platform linux/amd64 -t ${ECR_IMG_NAME} ./
#aws cloudformation package --template ./llm/${PROJECT_NAME}/cloudformation/create-app/template.yaml --s3-bucket a-unique-artifact-bucket-name --output-template-file packaged-template.yaml
#docker tag ${ECR_IMG_NAME} ${ECR_IMAGE_URI}
#docker push ${ECR_IMAGE_URI}

#docker container run -p 80:80 $ECR_IMG_NAME