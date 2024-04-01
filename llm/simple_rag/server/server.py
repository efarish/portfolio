#!/usr/bin/env python
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.runnables.base import RunnableParallel
from flask import Flask
from flask import request
import logging

app = Flask(__name__)

load_dotenv()

TEMPLATE_FORMAT = """
#You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
Question: {question}
Context: {context}
Answer:
"""
embeddings = OpenAIEmbeddings()
db = Chroma(persist_directory=os.environ['VECTOR_DB_SRC'], embedding_function=embeddings)
chat_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.25)
qa = RetrievalQA.from_chain_type(llm=chat_model, 
                                    chain_type="stuff", 
                                    retriever=db.as_retriever(search_kwargs={"k": 1}), 
                                    return_source_documents=True)

@app.route('/')
def do_rag_query() -> str:
    query = request.args.get("query","").strip()
    if len( query ) == 0:
        return "No query provided."
    else:
        logging.info(f'Query submitted: {query}')

    result = qa.invoke( query )
    meta_src = " ".join( [f'Book: {doc.metadata["book"]}, Chapter: {doc.metadata["chapter"]}' for doc in result['source_documents']] ) 
    response = result['result']
    logging.info(f'Reponse: {response}')
    logging.info(f'Content source: {meta_src}')

    return response + f' \nSource - {meta_src}.'
    
if __name__ == "__main__":
    #result = do_rag_query("Where was Jesus born?") 
    app.run(host='0.0.0.0', port=os.environ.get("FLASK_SERVER_PORT", 9090), debug=True)