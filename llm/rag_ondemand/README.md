# Project: RAG OnDemand

This project uses AWS services and LlamaIndex to create RAG agent API to answer questions about user provided PDFs. 

I found this [DeepLearning.AI](https://learn.deeplearning.ai/courses/building-agentic-rag-with-llamaindex/lesson/nfa5y/building-a-multi-document-agent) course very helpful. 

The workflow of this services is as follows:

1. Using an HTTP API Gateway, users create a session and upload a PDF document.
1. Users then request to build document indices.
1. Users submit queries about the document to the service and receive responses. 

The stack of AWS service and frameworks is below:

1. FastAPI - Used to implement the microservices. 
1. OpenAI - The o4-mini model provides LLM services.
1. Cloudformation/CodePipeline - Provides IaC and CI/CD services. 
1. VPC - A cloud to where the service is deployed.
1. API Gateway - The public API for the service. 
1. ECS - Where the FastAPI instance runs.
1. ECR - Where the ECS Docker images are stored.
1. S3 - Where the LlamaIndex indices are stored.
1. s3fs - A Python module that enables LlamaIndex to accessing S3 like a file system.

Below is an architecture diagram.

<p align="center">
  <img src="./assets/img/architecture.jpg" />
</p>

## Implementation Details

### Client

The `clients` folder contains a Jupyter notebook with examples of calling the HTTP AWS API Gateway.

This directory also contains a script to simulate user load on the service. The ECS cluster has been configured to auto-scale when the average CPU utilization exceeds a specified threshold. 

### The RAG Agent

The module `docker/lama_index_util.py` provides functions to interact with LlamaIndex. Two indices are built for documents uploaded by a user: An index for summary questions and another for detailed questions. These indices are wrapped using query engine tools and provided to a `FunctionAgent` instance whose agentic workflow determines which tool to use.

### LlamaIndex and S3

The service is stateless. To avoid having to rebuild them with each request, the indices are stored in AWS S3. When persisting files, LlamaIndex has alternatives to using the files system. It supports the [fsspec](https://filesystem-spec.readthedocs.io/en/latest/intro.html) standard which is an attempt to provide a common interface for files. The Python module [s3fs](https://github.com/s3fs-fuse/s3fs-fuse) provides an implementation of this standard for AWS S3.

### Framework Tokens

The `docker/.env` file contains the tokens needed for AWS and OpenAI. 


### Iac and CI/CD

The `cloudformation` directory contains three directories.

1. `create=app` - The IaC that defines the AWS stack.
1. `create-pipeline` - A CodePipeline used to build the Docker image and deploy the stack defined in `create-app`.
1. `update-pipeline` - A CodePipeline used to rebuild and deploy the Docker image to ECS.


## Lessons Learned

LlamaIndex makes it easy to develop RAG services. The limited load testing I did discovered bottlenecks I hadn't considered. In this case, the token rate limit for my OpenAI account limited the number of simultaneous requests I could make to the service.  





