"""
This file contains a class used to wrap calls to ChatOpenAI and matain a history of chat messages. 
"""
import os

import nltk
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from nltk.tokenize import word_tokenize

nltk.download('punkt')

from dotenv import load_dotenv

load_dotenv()

SIMILARITY_SEARCH_K=int( os.environ['SIMILARITY_SEARCH_K'] ) 
LLM_TEMPERATURE=float( os.environ['LLM_TEMPERATURE']  ) 
MAX_CONTENT_SIZE=int( os.environ['MAX_CONTENT_SIZE'] )
MAX_TOKENS=int( os.environ['MAX_TOKENS'] )
SYSTEM_CONTENT=os.environ['SYSTEM_CONTENT']

class LLM_RAG_Conv:
    """
    A class used to wrap calls to ChatOpenAI and matain a history of chat messages. 
    """

    def __init__(self, model_name, vector_dir, openai_key):
        if(len(model_name.strip())==0): raise Exception("Missing model name.")
        if(len(vector_dir.strip())==0): raise Exception("Missing vector db directory.")
        if(len(openai_key.strip())==0): raise Exception("Missing OpenAI key.") 
        if not os.path.exists( vector_dir ): raise Exception("Vector db directory does not exist.") 
    
        os.environ["OPENAI_API_KEY"] = openai_key
        self.embeddings = OpenAIEmbeddings()
        self.db = Chroma(persist_directory=vector_dir, 
                         embedding_function=self.embeddings)
        self.chat_model = ChatOpenAI(model_name=model_name, 
                                     temperature=LLM_TEMPERATURE)
        self.messages = [
            SystemMessage(content=SYSTEM_CONTENT),
            ]

    def get_messages(self):
        return self.messages
    
    def augment_human_prompt(self, _query: str):
        """
        Augment the query with context from the vectory database.
        """
        # get docs knowledge base
        results = self.db.similarity_search(_query, k=SIMILARITY_SEARCH_K)
        # get the text from the results
        source_knowledge = "\n".join([x.page_content for x in results])
        # feed into an augmented prompt
        # The answer should be concise.
        augmented_prompt = f"""Using the contexts below, answer the query. 

        Contexts:
        {source_knowledge}

        Query: {_query}"""
        return HumanMessage(content=augmented_prompt)

    def get_conversation_lenght(self):
        return sum( [len( word_tokenize(msg.content) ) for msg in self.messages] )

    def invoke(self, _query: str):
        """ Execute the query supplying context for the query and the chat history so far."""
        self.messages.append( self.augment_human_prompt(_query) )
        #If the number of words in the context is larger that the maximum context size, 
        #  remove some of the prior chat history.
        while self.get_conversation_lenght() > MAX_CONTENT_SIZE - MAX_TOKENS:
            self.messages.pop(1) #remove the first message and the system message.
        response = self.chat_model.invoke( self.messages )
        self.messages.pop()
        self.messages.append( HumanMessage(content=_query) )
        self.messages.append( AIMessage(content=response.content) )
        return response.content, response.response_metadata

