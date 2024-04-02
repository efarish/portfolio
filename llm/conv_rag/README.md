# Projrct: RAG Chat 

The project implements a chat application using RAG to enhance queries from a user. The history of the chat is maintained but the RAG context used to help create the LLM response is not kept in the history. The is an attempt to limit the content submitted to the LLM. 

The number of words in the conversation in the conversation is counted with each request. If the count exceed a configurable limit, the chat history is trimmed from the beginning to get the conversation under the limit.  

The corpus used is the Bible NT and was created using this project. 

Project file descriptions are below:

- LLM_RAG_Conv.py: This wraps calls to OpenAI and Langchain APIs. A Chroma vector database is used. The documents in the database contain all the chapters for the Bible's New Testament. This vector database was created using in my project RAG1.
- app.py: This file provides a Streamlit front end.


## Demonstration

Below is a chat demonstrating that the history is maintained. It also demonstrates that if the context retrieved doesn't have the answer, the LLM will say so. An improvement to this behavior is Corrective RAG which I implemented a version of that here.


https://github.com/efarish/portfolio/assets/165571745/51822e9c-9082-4795-89aa-8a9df19bc396

## Technologies Used

- Streamlit for the frontend. 
- LangChain for the LLM framework.
- OpenAI 3.5 Turbo for the LLM model.
- Chroma vector datastore.


