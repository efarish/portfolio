# Project:  Simple RAG

## Introduction

This project implements a simple retrieval augmented generation (RAG) application. I developed this application using VS Code, Python, LangChain, and Docker. The corpus indexed is the Bible. The indexing was done by the chapters of each book in the Bible.

## Demonstration

Below is a demo of the appliaction. To simulate a production environment, the code was deployed to AWS using the following resources: 

- Elastic Container Repository (ECR) - This repository is where the custom Docker images were uploaded.
- Elastic Container Service (ECS) - Both the client and service endpoints were deployed to AWS's ECS.
- Application Load Balancer - A load balancer was created to control access to the the Streamlit frontend client.   

https://github.com/efarish/portfolio/assets/165571745/7bbe358c-acb8-4b4b-9a29-80fdbf003e90

## Architecture

A simple microservices architecture is used. The Client and Server are deployed to two different endpoints. The application has four components: a corpus, a vector datastore, a service endpoint, and a frontend client. 

### Corpus

The source corpus used for indexing by the vector DB was the New International Version (NIV) translation of the Bible. Each chapter was used for indexing with its source book and chapter being stored in the metadata. The XML file containing the corpus can be found in /server/data folder.

### Vector Database

The open-source vector database Chroma is used to index the corpus. To simplify using Chroma, the LangChain framework was used.

### Service

A Python class manages call to an Open AI 3.5 Turbo LLM model. LangChain was also used to access the OpenAI model. This class also manages access to the vector DB which is built once and then loaded from a directory after the first request. 

### Client

A Streamlit frontend is used for submitting request to the RAG service. 

## Technology Summary


- Streamlit for the frontend. 
- LangChain for the LLM framework.
- OpenAI 3.5 Turbo for the LLM model.
- Chroma vector datastore.





