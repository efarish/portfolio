# Project: Building An ECS Stack

This project demonstrates using Docker, ECS, and CloudFormation to deploy a very simple microservice.

Below is a summary of the AWS resources provisioned for this this stack:

- A VPC with two public and private subnets and supporting gateways.
- Fargate Task Definition, Cluster, and Service deployed to the private subnets. 
- An internal facing Application Load Balancer.
- An API Gateway along with a VPC link to the private Application Load Balancer.

**NOTE**: The charges for this stack can accumulate quickly. In particular, the ELB and NAT Gateways. Be sure to delete the stack when done. See [section 'AWS Cleanup'](#cleanup) for options to delete the stack.  

Below are a couple options for reducing the cost of this stack:

1. Remove the VPC created and the references to it and use the AWS account default VPC.
1. Reduce the number of public/private subnets and the NAT Gateway that connects them.
1. Git rid of the public subnets and the Internet/NAT Gateways and use AWS Private Links to the services needed by the container app (S3) and ECS (EDR and Secrets Manager).
1. Reduce the number of tasks created by the ECS.
1. Use AWS Cloud Map instead of an application load balancer to integrate the API Gateway and ECS.  

Below are the steps to:

- Build and test the Docker image and deploy it to AWS ECR.
- Create the ECS stack using CloudFormation.  

The Docker container exposes a FastAPI endpoint that copies posted files to S3.

This project demonstrates two use cases of providing AWS credentials to the Docker container to access AWS services (e.g. AWS S3):

- When testing the Docker container locally. 
- When running the Docker container in AWS ECS.

You'll need the following to run this project:

- Configured AWS and SAM command line clients.
- Docker

I found these CloudFormation examples useful:

- [API Gateway Integrations examples](https://github.com/aws-samples/aws-apigw-http-api-private--integrations/blob/main/templates/APIGW-HTTP-private-integration-ALB-ecs.yml) 
- [Fargate Example](https://containersonaws.com/pattern/sam-fargate)

# The App

In the `./server` directory are the files to build the Docker image. The `main.py` script contains an endpoint that supports GET and POST requests. The POST copies files to AWS S3. The web framework FastAPI is used to implement the endpoint.  

NOTE: The `.env` file included with this distribution needs to be updated to reference a valid AWS S3 bucket in the AWS account used for this project.

# Docker Build

Using the Docker file in the `./server` folder, run the commands below. 

```bash
docker build -t ecs1/server .
docker container run -d -p 9090:9090 ecs1/server
docker ps
```

In your local docker instance, there should now be a container listed in the output of the `docker ps` command above. Try to access the container endpoint at `http://localhost:9090` in a web browser or using the client Jupyter notebook in this distribution's `client` directory. 

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

# Provision A CloudFormation Stack in AWS

I used AWS CloudFormation and SAM to provision the stack defined in `./sam-app-ecs1/template.yaml` and `./sam-app-ecs1/vpc.yml`. 

To build and deploy the cluster to AWS, use the SAM CLI commands below. Be sure to run this commands in this distribution's `sam-app-ec1` directory as thats where the SAM template files are.

```bash
sam build
sam deploy
```

The deployment will take a few minutes. Status messages will appear in the console as deployment progresses. The deployment can also be monitored in CloudFormation.

When the deployment completes, the API Gateway URL will be printed to the console by the SAM CLI. The following AWS endpoint routes should now be available:

1. http://< URL >/ - A health check use by the load balancer.
1. http://< URL >/getInfo - A simple GET method.
1. http://< URL >/upload - A POST method to which files can be posted and copied to S3.   

The GET methods can be access through a browser. The notebook in the `./client` folder can be used to POST a sample image. 

# AWS Clean Up <a id='cleanup'></a>

To avoid unwanted AWS charges, the CloudFormation stack for this project must be deleted. 

Go to CloudFormation in the AWS console, find the stack with the name `sam-app-ecs1` and delete it.

**--OR--**

At the command line in the `./sam-app-ecs1` directory, run `sam delete`.

After doing either of these, do a sanity check to make sure the ECS cluster, VPC, and application load balancer are deleted.

# Conclusion

Using CloudFormation and SAM greatly expedites the creation of AWS applications.

# TODO 
1. Create a version that uses AWS Cloud Map instead of an ALB to avoid the costs.
1. Add Authentication/Authorization.
