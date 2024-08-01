# Project: Knowledge Graph Curation

This project uses LangChain, OpenAI, Neo4j, Pydantic, and yWorks to demonstrate NER (named entity recognition) NLP and examples of curating data prior to creating elements of a knowledge graph (KG).  

The first couple chapters of Frank Herbert's 1965 novel Dune will is the source text.

The approach used will:

1. Load the source text and split it into chunks.
2. Perform NER on the text splits.
3. For the entities found, extract relationships between the entities.  
4. Persist the entities and relationships into a graph database.

Along the way, the data will be curated to increase the usefulness of the KG. As an LLM is used, its necessary to review the indeterminate extraction results produced. 

An open information extraction approach will be used for creating the KG. This means the knowledge graph will not have a pre-defined schema. The node labels and edges defined will be created by the LLM.

The purpose of this experiment is to demonstrate simple curation steps that can be taken when relying on a LLM to create a graph database. The steps taken could easily be implemented by a much more capable curation application.

The results of the project can be viewed in the Jupyter Notebook file "Dune_Graph_Curating.ipynb".
