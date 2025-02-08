# Project: Mobile Device Tracker

THIS IS A WORK-IN-PROGRESS

This project demonstrates using Python, AWS, and Kivy (a cross-platform GUI framework for Python) to implement a mobile device tracker. The AWS highlights include a RESTFul API web service implemented using CloudFormation, CodePipeline, API Gateway, a Lambda Authorizer, ECS, FastAPI, and SQLAlchemy. A mobile client app is implemented using Kivy. Once installed, the app calls the web service to report its GSP location and to retrieve the locations of any other mobile device logged into the appliacation. The device locations are then displayed on an interactive map. 

I made some architecture decisions to reduce the cost of deploying this app to AWS: 

* Cloud Map instead of an ALB is used integrate API Gateway and ECS.
* A single ECS task is provisioned.
* SQLite is used for data storage. 
* To avoid the expense of a NAT Gateway, all resources are deployed to a single public subnet. 

A couple of additional notes:

* Lambdas deployed to a public subnet have no internet access so a VPC Interface Endpoint is used to access AWS services.
* The ECS service is secured by using its security group to restrict inbound access to API Gateway, Cloud Map, and Lambda.   
* Some of the AWS services used were for self-didactic teaching. For example, a Lambda Authorizer was included to experiment with securing an API Gateway. ECS and FastAPI are used to implement the endpoints instead of Lambda Fucntions. 
 
A final note on costs. For small ECS clusters, the AWS cost for public IPs and VPC endpoints is less than that of NAT gateways. Furthermore, an application load balancer is more expensive than Cloud Map. For larger clusters, this is probably not true.

The architecture diagram is below.

<p align="center">
  <img src="./assets/img/nw1.png" />
</p>

# Test Suite

A PyTest suite can be run using the `./docker/test/TestSuite.py` script.

# AWS Deployment

Three AWS CodePipelines are created to deploy and maintain this application.

- Create Pipeline: Runs the CloudFormation templates found in the directory `./create-app` to create the application.
- Update Lambda Pipeline: Update the Lambda with the latest code. 
- Update Pipeline: Update the AWS ECS task with the latest code. 

As soon as any of these pipeline are deployed to AWS, it executes. Therefore, be sure to run the `Create Pipeline` first, and the other two after that. The following SAM CLI commands were used to build and deploy the pipelines.

```bash

sam build
sam deploy

```

Three AWS resources are not provisioned by `create-pipeline` and need to be manually created before running any of the pipelines:

1. The AWS Developer Tools GitHub Connection referenced by the `GitHubConnectionArn` property in the pipeline templates will need to be manually created in any AWS account trying to run these pipelines. The connection needs to point to where this code is stored and its ARN used to update the pipeline templates property. For this project, the code was stored in the Git Hub repository `https://github.com/efarish/portfolio`. 
2. An AWS ECR repository with the name `ecs1` is assumed to exist. This repository is referenced by the CloudFormation templates and the pipeline `buildspec.yml` files.
3. CodePipeline requires an S3 bucket. To run these pipelines, replace the `S3ArtifactBucket` values in the template files with a bucket from the AWS account the pipelines are run in.

# Kivy Android Deployment

I've done another project that goes into the details of setting up a Kivy Android deployment environment using Buildozer. Please see [this](https://github.com/efarish/portfolio/tree/main/mobile/kivy_img_post) project for details. 

# Kivy IOS Deployment

To deploy the Kivy app to an IOS device, I used a Mac workstation and the [kivy-ios](https://github.com/kivy/kivy-ios) framework. I found these resource useful in setting it up.

* [This](https://www.youtube.com/watch?v=6gLGyrlgqCU) Youtube video to set up the environment.
* The [Kivy-ios](https://github.com/kivy/kivy-ios) documentation for reference.

## Addition Configuration

1. I ran the following Toolchain commands:
  - python toolchain.py pip install httpx
  - python toolchain.py pip install git+https://github.com/kivy/plyer.git@master
  - python toolchain.py pip install httpcore
  - python toolchain.py pip install anyio
  - python toolchain.py pip install certifi
  - python toolchain.py pip install idna
  - python toolchain.py pip install h11
  - python toolchain.py pip install openssl
2. The Kivy Garden MapView code appears to have a bug when running on IOS. The code attempts to create a cache for the map images to a directory it doesn't have permission to. I cloned the project from GitHub and made the following change to the `kivy_garden/mapview/constants.py` to put the cache in directory the app would have access to:
```bash
if platform == 'ios': 
  root_folder = App().get_running_app().user_data_dir
  CACHE_DIR = os.path.join(root_folder, 'cache')
else:
  CACHE_DIR = "cache"
```   
Use the command below to install the modified MapView package, 
```bash
python toolchain.py pip install $<PATHJ TO THE CLONED MAPVIEW DIRECTOYR>
```
3. When using Xcode to deploy to a IOS device, I had to edit the Xcode projects's Info.plist (in this project the file was called gps_tracker-Info.plist) with the following entry to the <dict> element. This allows the target device to access the GPS location: 
<key>NSLocationWhenInUseUsageDescription</key>
<string>${PRODUCT_NAME}</string>

 




# Clean Up 

### CloudFormation Stacks

In the AWS CloudFormation console, delete the root stacks created for this project in the following order. 

1. tracker-create-pipeline-app-stack
2. gps-tracker-lambda-update
3. gps-tracker-update-pipeline
4. gps-tracker-create-pipeline

Let the deletion of each stack finish before deleting the next.

**NOTE: The order of stack deletion is very important.** Deleting the pipeline stacks before the app stack will cause many problems. The IAM role created by the Create Pipeline stack is needed to delete the application stack. Delete the application root stack first, then delete the pipeline stacks. If the pipeline stacks are mistakenly deleted first, deleting the application stack will fail with an error stating a certain role cannot be assumed. To fix, manually create an IAM role with the same name using the policy defined in the `create-pipeline` template.  

### ECR Images

The Docker images in the `ecs1` repository created for this project need to be deleted.

### S3 Bucket

Delete the bucket created for the pipelines.

### Github Code Connection

Delete the AWS Developer Tools Code Connections to Github created for this project.

# Conclusions

* The costs of demonstration projects can be significantly reduced with a few architecture decisions,
* The up-front effort of implementing CI/CD pipelines and IaC templates reduces development time.

# TODO

1. Add a CloudFormation template for the ECR repository.
1. In the Kivy buildozer.spec, needed to reference kivy plyer as: git+https://github.com/kivy/plyer.git@master for the latest code. 
