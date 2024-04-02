# Project: Corrective RAG

This project implements a variant of the Corrective RAG as described in the paper [Corrective Retrieval Augmented Generation](https://arxiv.org/pdf/2401.15884.pdf?ref=blog.langchain.dev)

The features of Corrective RAG implemented are:
- Evaluating the content retrieved from the vector database for relevance. 
- Rewritting the search query if no documents were found or the documents found were deemed irrelevant. 
- If the rewritten query does not find relevant documents, I inform the user no relevant documents were found. 

In the paper, a Google search was done to find content in the event not relevant documents are found. I decided not to do that as I thought it more appropriate to restrict the reponse to a corpus of documents I trust. 

The corpus indexed for the RAG were three papers on RAG:

- [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)
- [Corrective Retrieval Augmented Generation](https://arxiv.org/pdf/2401.15884.pdf?ref=blog.langchain.dev)
- [SELF-RAG: LEARNING TO RETRIEVE, GENERATE, AND CRITIQUE THROUGH SELF-REFLECTION](https://arxiv.org/pdf/2310.11511.pdf?ref=blog.langchain.dev)

The application will be able to answer questions on these topics with a degree of accuracy. 

## Demonstration

Below is a demo of the application. I used OpenAI's ChatGPT website to first do a query on Corrective RAG. Since this is a new use case for LLMs, nothing relevant is found. I then use the application I wrote deployed to AWS EKS to anwser the question. 

<video src='assets/vid/crag1.mp4' width=320 controls/>


# Implementation Details 

Technologies used for implementation:

- Streamlit for the frontend. 
- LangChain for the LLM framework.
- OpenAI 3.5 Turbo for the LLM model.
- LangGraph for Corrective RAG conditional behavior. 
- FAISS vector datastore.

# Architecture

A microservice architecture was used where the frontend Streamlit client and LLM service were deployed to different endpoints.

# Deployment

To simulate a production deployment for the demonstration above, I deployed the application to AWS EKS.

