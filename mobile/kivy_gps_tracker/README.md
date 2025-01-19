# Project: RESTful API Application

WORK-IN-PROGRESS

This project demonstrates using Python and AWS services to implement a RESTful API. Highlights include the use of CloudFormation, CodePipeline, API Gateway, Lambda Authorizer, ECS, FastAPI, and SQLAlchemy. I made some architecture decisions to reduce the cost of deploying this app to AWS: 

* Cloud Map instead of an ALB is used integrate API Gateway and ECS.
* Since only a single ECS task is provisioned, SQLite is used for data storage. 
* To avoid the expense of a NAT Gateway, all resources are deployed to a single public subnet. 

For reliability and scalability, the architecture supports increasing the size of the ECS cluster and adding addition subnets with minimal changes:

* To service the cluster, one of AWS's relational database services would be needed. However, since SQLAlchemy is used for ORM, the effort of swapping out SQLite is minimal.
* The Cloud Map configuration used for the ECS service will automatically pickup the additional tasks instances and use round-robin for request distribution.

A couple of additional notes:

* Lambdas deployed to a public subnet have no internet access so a VPC Interface Endpoint is used to access AWS services.
* The ECS service is secured by using its security group to restrict inbound access to API Gateway, Cloud Map, and Lambda.   
* Some of the AWS resources provisioned were included for personal didactic teaching. For example, the Lambda Authorizer was included to experiment with securing an API Gateway. ECS is used to implement the endpoints instead of Lambda. Also, using an AWS account's default VPC would also have been cheaper, but less interesting.
 
A final note on costs. For small ECS clusters, the AWS cost for public IPs and VPC endpoints is less than that of NAT gateways. Furthermore, an application load balancer is more expensive than Cloud Map. For larger clusters, this is probably not true.

The architecture diagram is below.

<p align="center">
  <img src="./assets/img/nw1.png" />
</p>

# Deployment

Three AWS CodePipelines are created to deploy and maintain this application.

- Create Pipeline: Runs the CloudFormation templates found in the directory `./create-app` to create the application.
- Update Lambda Pipeline: Update the Lambda with the latest code. 
- Update Pipeline: Update the AWS ECS tasks with the latest code. 

As soon as any of these pipeline are deployed to AWS, it executes. Therefore, be sure to run the `Create Pipeline` first, and the other two after that. The following SAM CLI commands were used to build and deploy the pipelines.

```bash

sam build
sam deploy

```

Three AWS resources are not provisioned by `create-pipeline` and need to be manually created before running any of the pipelines:

1. The AWS Developer Tools GitHub Connection referenced by the `GitHubConnectionArn` property in the pipeline templates will need to be manually created in any AWS account trying to run these pipelines. The connection needs to point to where this code is stored and its ARN used to update the pipeline templates property. For this project, the code was stored in the Git Hub repository `https://github.com/efarish/portfolio`. 
2. An AWS ECR repository with the name `ecs1` is assumed to exist. This repository is referenced by the CloudFormation templates and the pipeline `buildspec.yml` files.
3. CodePipeline requires an S3 bucket. To run these pipelines, replace the `S3ArtifactBucket` values in the template files with a bucket from the AWS account the pipelines are run in.

# Clean Up 

### CloudFormation Stacks

In the AWS CloudFormation console, delete the root stacks created for this project in the following order. 

<< TODO >> 

Let the deletion of each stack finish before deleting the next.

**NOTE: The order of stack deletion is very important.** Deleting the pipeline stacks before the app stack will cause many problems. The IAM role created by the Create Pipeline stack is needed to delete the application stack. Delete the application stack first, then delete the pipeline stacks. If the pipeline stacks are mistakenly deleted first, deleting the application stack will fail with an error stating a certain role cannot be assumed. To fix, manually create an IAM role with the same name using the policy defined in the `create-pipeline` template.  

### ECR Images

The Docker images in the `ecs1` repository created for this project need to be deleted.

### S3 Bucket

Delete the bucket created for the pipelines.

### Github Code Connection

Delete the AWS Developer Tools Code Connections to Github created for this project.

# Conclusions

* The costs of demonstration projects can be significantly reduced with a few architecture decisions,
* The up-front effort of implementing CI/CD pipelines and IaC templates reduces development time.

# Enhancements

1. Replace ECS endpoints with Lambda.

# TODO

1. Develop Kivy model frontend app.
1. Add CloudFormation template for the ECR repository.