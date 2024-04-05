# Project: Corrective RAG

This project implements a variant of the Corrective RAG as described in the paper [Corrective Retrieval Augmented Generation](https://arxiv.org/pdf/2401.15884.pdf?ref=blog.langchain.dev).

The features of Corrective RAG implemented are:
- Evaluating the content retrieved from the vector database for relevance. 
- Rewritting the search query if no documents were found or the documents found were deemed irrelevant. 
- If the rewritten query does not find relevant documents, I inform the user no relevant documents were found. 

In the paper, a Google search was done to find content in the event no relevant documents are found. I decided not to do that as I thought it more appropriate to restrict the reponse to a corpus of documents I trust. If no relevant context is found in the indexed corpus, the user is informed of this.

The corpus indexed for the RAG were three papers on RAG:

- [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)
- [Corrective Retrieval Augmented Generation](https://arxiv.org/pdf/2401.15884.pdf?ref=blog.langchain.dev)
- [SELF-RAG: LEARNING TO RETRIEVE, GENERATE, AND CRITIQUE THROUGH SELF-REFLECTION](https://arxiv.org/pdf/2310.11511.pdf?ref=blog.langchain.dev)

The application will be able to answer questions on these topics with a degree of accuracy. 

## Demonstration

Below is a demo of the application. I use OpenAI's ChatGPT website to first do a query on Corrective RAG. Since this is a new use case for LLMs, nothing relevant is found. I then use the application I wrote (deployed to AWS EKS) to anwser the question. The source paper is cited at the end of the response. I first enter questions that can be answered by documents contained in the corpus. I then ask a question that cannot be answered from the corpus to demonstrate the app's ability to evaluate relevant content.

https://github.com/efarish/portfolio/assets/165571745/e26d7865-940a-4a66-b755-4efafe983801

# Implementation Details 

Technologies used for implementation:

- Streamlit for the frontend. 
- LangChain for the LLM framework.
- OpenAI 3.5 Turbo for the LLM model.
- LangGraph for Corrective RAG conditional behavior. 
- FAISS vector datastore.

# Architecture

To simulate a production deployment for the demonstration above, I deployed the application to AWS EKS.

A microservice architecture was used where the frontend Streamlit client and LLM service were deployed to different endpoints. These endpoints were deployed to AWS EKS with a NGINX ingress controller providing endpoint access and routing.

