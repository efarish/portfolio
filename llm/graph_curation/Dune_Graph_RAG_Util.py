import os
import re
from typing import List
import copy

import numpy as np
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser, PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Extra, Field
from langchain_openai import ChatOpenAI
from nltk.tokenize import word_tokenize
from numpy.linalg import norm
from neo4j import GraphDatabase
from yfiles_jupyter_graphs import GraphWidget

load_dotenv()

# Get neo4j credentials.
neo4j_url =      os.getenv("NEO4J_CONNECTION_URL")
neo4j_user =     os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

# Use neo4j credentials to set environment variables used by LangChain.
os.environ["NEO4J_URI"] =      neo4j_url
os.environ["NEO4J_USERNAME"] = neo4j_user
os.environ["NEO4J_PASSWORD"] = neo4j_password

def word_count(txt: str)->int:
    return len( word_tokenize(txt) ) 

def run_cypher(tx, stmt):
    """
    Function to run Cypher statements using neo4j.

    Parameters:

    tx: A ne04j transaction.
    stmt (str): A Cypher statement to execute.  
    """
    result = tx.run(stmt)
    return result.consume()

def execute_write(stmt):
    """
    Method to create graph db connection and execute write Cypher statements.
    
    Parameters:

    stmt (str): A Cypher statement to execute. 
    """
    driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))
    with driver.session(database="neo4j") as session:
        result_summary = session.execute_write(run_cypher, stmt)
    driver.close() 

def execute_query(query, parameters=None):
    driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))
    result = None
    try:
        with driver.session(database="neo4j") as session:
            result = list(session.run(query, parameters))
    except Exception as e:
        print(f'Failed query: {query}, Exception: {e}')
    finally:
        driver.close()
    return result 


class AnEntity(BaseModel):
    """
    Entity class used to extract data from text.
    """
    name: str = Field(description="Name of an entity")
    type: str = Field(description="Type of an entity")
    description: str = Field(description="Description of an entity")

    class Config:
        extra = Extra.allow

class Entities(BaseModel):
    """Container for entities."""
    entities: List[AnEntity] = Field(
        ...,
        description="All the entiteies appearing in the text",
    )

def create_docs(list_of_text: list[str]) -> list[Document]:
    """
    Utility function to create a list of LangChain documents 
      from a list of strings. 
    """
    docs = []
    for idx, chapter in enumerate(list_of_text):
        docs.append(Document(page_content=chapter, metadata={"chapter": idx+1}))
    return docs

def get_ss(v1, v2):
    """
    Calculate a similarity score between two vectors.
    """
    cosine = np.dot(v1,v2)/(norm(v1)*norm(v2))
    return cosine

def find_similar_entity(_entity, _entities, threshold=0.95):
    """
    Find the first entity in a list that is similar to an entity.

    Parameters:
    _entity (AnEntity): The being searched for.
    _entities (list): The list of entities being searched. 
    """
    for entity in _entities:
        cosine_sim = get_ss(_entity.embedding, entity.embedding)
        if cosine_sim >= threshold:
            return entity
    return None

def reset_similar_entities(_entities: list):
    """
    Reset the attributes of AnEntity instance.
    """
    for entity in _entities:
        entity.entity_alias = [] 
        entity.src_reference = set()

def update_entity_list(_source, _target):
    """
    Merge two lists of AnEntity instances. Similar entities are 
      added to similar entity's entity_alias attribute.
    """
    new_entities = []
    for entity in _source:
        similar_entity = find_similar_entity(entity, _target, 0.70)
        if similar_entity is None:
            new_entities.append(entity)
        else:
            #same_name_entity = find_entity_with_same_name(entity, similar_entity.entity_alias) 
            #if same_name_entity is None:
            similar_entity.entity_alias.append(entity)
            #else:
            #    same_name_entity.entity_alias.append(entity)    
    return _target + new_entities

def get_Dune_chapters(): 
    """
    Extract the chapters form the source corpus.
    """
    with open('dune.txt', 'r', encoding="utf-8") as f:
        text = f.read()
    # For this file, "= = = = = =" separates the chapters.
    text_split = text.split('= = = = = =')
    # Exclude appendicies and splits with less than 10 words.
    cleaned_text = []
    for idx, line in enumerate(text_split):
        if not re.search("Appendix .+:", line) and \
        not re.search('Terminology of the Imperium', line) and \
        len( word_tokenize(line.strip()) ) > 10:
            trimmed_line = line.strip()
            cleaned_text.append( trimmed_line )
    # This text file contains spaces before each paragraph extra line feeds.
    #  The code below cleans that up.
    for idx, chapter in enumerate(cleaned_text):
        cleaned_text[idx] = chapter.replace('\n    ', '\n').replace('\n\n','\n')
    # Create LangChain Document instances.
    lc_docs = create_docs(cleaned_text)
    return lc_docs

def get_entity_llm():
    """
    Create a LangChain pipeline to perform NER on text documents.
    """

    #parser = JsonOutputParser(pydantic_object=Entities)
    parser = PydanticOutputParser(pydantic_object=Entities)

    # Define the map prompt template
    summary_template = """You extract people, organizations, planets, and family houses that appear in a text. Use the document below:
    ------------
    {context}
    ------------
    From the document above, extract all people, organizations, planets, and family houses.
    For each entity found, provide entity type and a description. Entity examples are below:
    ------------
    name: Barry Allan
    type: Person
    description: Barry Allan is the fasters man alive.

    name: Earth
    type: Planet
    description: Earth is a planet where all humans come frome.

    name: John Cunnington
    type: Person
    description: John Cunnington is a lord in Westerose.

    name: Central Inteligence Agency
    type: Organization
    description: The Centtral Inteligence Agency is a spy agency on earth.
    ------------
    Helpful Answer:\n{format_instructions}"""
    summary_prompt = PromptTemplate(template=summary_template,
                                    input_variables=["context"],
                                    partial_variables={"format_instructions": parser.get_format_instructions()},)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-1106") #gpt-3.5-turbo-1106 gpt-4o
    summary_chain = summary_prompt | llm | parser

    return summary_chain

def initialize_entities(_entities: list, _embedder, _src_refernce):
    """
    Initialize AnEntity instances.    
    """

    for entity in _entities:
        embed = _embedder.encode(entity.name + "|" + entity.type)
        entity.embedding = embed
        entity.entity_alias = [] 
        entity.src_reference = set()
        entity.src_reference.add(_src_refernce)
    #return _entities

def combine_similar_entities(_entities: list):
    """
    For the AnEntity instances identified as aliases, combine the source references and descriptions.
    """

    _entities = copy.deepcopy( _entities )

    for entity in _entities:
        if len(entity.entity_alias) > 0:
            for se in entity.entity_alias:
                if entity.name.lower() == se.name.lower():
                    entity.src_reference.update( se.src_reference )
                entity.description += ' ' + se.description    

    summary_template = """Summarize the entity description below:
    {context}
    """
    summary_prompt = PromptTemplate.from_template(template=summary_template)
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-1106") #gpt-3.5-turbo-1106 gpt-4o
    summary_chain = summary_prompt | llm | StrOutputParser()

    for entity in _entities:
        if len(entity.entity_alias) > 0:
            desc_before = entity.description
            desc_after = summary_chain.invoke([desc_before])
            entity.description = desc_after

    return _entities

def cypher_entity_create(e: AnEntity)->str:
    """
    Use an AnEntity instance to create a CREATE Cypher statement.
    """
    stmt = '\n' + f"CREATE (:{e.type.replace(' ','_')} {{name: '{e.name.replace("'","\\'")}', \
        chapters:'{''.join(['['+str(chpt)+']' for chpt in e.src_reference])}', \
        description: '{e.description.replace("'","\\'")}' }})"
    return stmt

def cypyer_entity_alias(e_alias: AnEntity, e: AnEntity)->str:

    stmt = (f"MATCH (p1 {{name: '{e.name.replace("'","\\'")}'}}) "
            f"MERGE (p2 {{name: '{e_alias.name.replace("'","\\'")}', chapters:'{''.join(['['+str(chpt)+']' for chpt in e.src_reference])}' }}) "
            f"MERGE (p2)-[r:also_known_as]->(p1);" )

    return stmt

def create_nodes(_entities: list):
    """
    Create entity nodes in a neo4j knowledge graph.
    """
    for e in _entities:
        try:
            stmt = cypher_entity_create(e)
            execute_write(stmt)
            for se in e.entity_alias:
                if se.name.lower() != e.name.lower():
                    try:
                        stmt = cypyer_entity_alias(se, e)
                        execute_write(stmt)
                    except Exception as e:
                        print(f'Failed Similar Node Create: {stmt}, {e}')
        except Exception as e:
            print(f'Failed Main Node Create: {stmt}, {e}')


def get_relationship_llm():
    """
    Create an LLM to extract relationships for a set of entities.

    NOTE: it is not expected that the only relationships returned will be for the entities provided for the prompt.
      The purpose of providing the entities is to bias the response to the entities identified in the text.
    """

    template = """You extract key entity relationships from text. Use the document below:
    ------------
    {context}
    ------------
    Extract key relationships for the entities below:
    ------------
    {entities}
    ------------
    Respond with a list of triplets. Examples are below:
    ------------
    Barry Allen:MARRIED_TO:Iris West
    Batman:MEMBER_OF:The Justice League
    Carol Davners:LOCATED_ON:Hala
    The Flash:ALSO_KNOWN_AS:Barry Allen
    Dick Grayson:ASSOCIATE_OF:Bruce Wayne
    Tom:ENEMY_OF:Jerry
    Nicholas Bradford:CHILD_OF:Tom Bradford 
    ------------
    Directions:
    Add no extra text.

    Helpful Answer:\n"""
    summary_prompt = PromptTemplate.from_template(template=template)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-1106") #gpt-3.5-turbo-1106 gpt-4o
    summary_chain = summary_prompt | llm | StrOutputParser()

    return summary_chain

# directly show the graph resulting from the given Cypher query
default_cypher = "MATCH (s)-[r]->(t) RETURN s,r,t LIMIT 100"

def showGraph(cypher: str = default_cypher):
    """
    Function to use yWork graph widget to visualize 
      graph database.
    """
    driver = GraphDatabase.driver(
        uri = os.environ["NEO4J_URI"],
        auth = (os.environ["NEO4J_USERNAME"],
                os.environ["NEO4J_PASSWORD"]))
    session = driver.session()
    widget = GraphWidget(graph = session.run(cypher).graph())
    widget.node_label_mapping = 'name'
    #display(widget)
    return widget




