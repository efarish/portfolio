# Project: GraphQL API

A WORK-IN-PROGRESS

This project implements a Query and Mutation GraphQL API using AWS service. The AWS stack was implemented using the following services and frameworks.

* API Gateway Http API - The public face interface to the app.
* Lambda Functions - Provides compute resources for application and API Gateway authorization.
* DynamoDB - Used for persistence.
* JSON Web Token (JWT) - Used limit app access to logged in users.
* CodePipeline - Provides CD/CI services.  
* CloudFormation - Provides IaC services. 
* PyTest - Used for Python code unit tests.

The architecture diagram is below.

<p align="center">
  <img src="./assets/img/architecture1.jpg" />
</p>

This app supports 2 GraphQL queries and 1 mutation types of .

1. Create User - Creating a user.
1. Login - Logging into the application and receiving a JWT.
2. Get User - Using the JWT form the login, get user information.

Examples of making calling these endpoints can be found in the Jupyter notebook found in the `client` folder of this project. 

# TODO

1. Implement GraphQL Subscription. 



