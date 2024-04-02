"""
Utility methods used to CRAGService.
"""
import logging
from typing import Dict
from typing import TypedDict

from langchain.output_parsers.openai_tools import PydanticToolsParser
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.output_parsers import StrOutputParser
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.pydantic_v1 import Field
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_openai import ChatOpenAI

from manage_vector_db import *

VECTOR_DB_GET_PAPER_K = int(os.environ["VECTOR_DB_GET_PAPER_K"])
VECTOR_DB_GET_DOCS_K = int(os.environ["VECTOR_DB_GET_DOCS_K"])
VECTOR_DB_GET_DOCS_FETCH_K = int(os.environ["VECTOR_DB_GET_DOCS_FETCH_K"])
OPENAI_LLM_MODEL = os.environ["OPENAI_LLM_MODEL"]
QUERY_TRANSFORM_LIMIT = int(os.environ["QUERY_TRANSFORM_LIMIT"])


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        keys: A dictionary where each key is a string.
    """

    keys: Dict[str, any]


### Nodes ###


def start_node(state):
    """
    Initialize the state object.
    Args:
        state (dict): The current graph state
    Returns:
        state (dict): New key added to state: retriever.
    """
    state_dict = state["keys"]
    state_dict["query_transforms"] = 0
    state_dict["questions"] = []
    state_dict["questions"].append(state_dict["question"])
    state_dict["vector_db"] = create_vector_db()
    return state


def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    state_dict = state["keys"]
    question = state_dict["questions"][-1]
    logging.warning(f"Query: {question}")
    db = state_dict["vector_db"]
    papers = db.similarity_search_with_score(
        question,
        filter=dict(page=0),
        k=VECTOR_DB_GET_PAPER_K,
        distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE,
    )
    logging.warning(f"Meta data: {[doc.metadata for doc, _ in papers]}")
    logging.warning(f"Scores: {[score for _, score in papers]}")
    documents = []
    if len(papers) > 0:
        source_filter = papers[0][0].metadata["source"]
        state_dict["doc_meta_data"] = papers[0][0].metadata
        documents = db.similarity_search_with_score(
            question,
            filter=dict(source=source_filter),
            k=VECTOR_DB_GET_DOCS_K,
            fetch_k=VECTOR_DB_GET_DOCS_FETCH_K,
            distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE,
        )
        documents.sort(key=lambda item: item[0].metadata["page"], reverse=False)
        logging.warning(f"Meta data: {[doc.metadata for doc, _ in documents]}")
        logging.warning(f"Scores: {[score for _, score in documents]}")
    state_dict["documents"] = documents
    return state


def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    state_dict = state["keys"]
    question = state_dict["questions"][-1]
    documents = state_dict["documents"]

    # The template came from LangChain hub prompt rlm/rag-prompt.
    prompt = PromptTemplate(
        template="""You are an assistant for question-answering tasks. \n
        Use the following pieces of retrieved context to answer the question. \n
        If you don't know the answer, just say that you don't know. \n
        Keep the answer concise.
        \n
        Question: {question} 
        \n
        Context: {context} 
        \n
        Answer: """,
        input_variables=["question", "context"],
    )

    # LLM
    llm = ChatOpenAI(model_name=OPENAI_LLM_MODEL, temperature=0, streaming=False)

    # Post-processing
    def format_docs(_documents):
        return "\n\n".join(doc.page_content for doc in _documents)

    context = format_docs(documents)

    # Chain
    rag_chain = prompt | llm | StrOutputParser()

    # Run
    generation = rag_chain.invoke({"context": context, "question": question})
    state_dict["generation"] = (
        generation + "\nSource: " + state_dict["doc_meta_data"]["source"]
    )

    return state


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with relevant documents
    """

    print("---CHECK RELEVANCE---")
    state_dict = state["keys"]
    question = state_dict["questions"][-1]
    documents = state_dict["documents"]

    if len(documents) == 0:
        return state

    # Data model
    class grade(BaseModel):
        """Binary score for relevance check."""

        binary_score: str = Field(description="Relevance score 'yes' or 'no'")

    # LLM
    model = ChatOpenAI(temperature=0, model=OPENAI_LLM_MODEL, streaming=False)

    # Tool
    grade_tool_oai = convert_to_openai_tool(grade)

    # LLM with tool and enforce invocation
    llm_with_tool = model.bind(
        tools=[grade_tool_oai],
        tool_choice={"type": "function", "function": {"name": "grade"}},
    )

    # Parser
    parser_tool = PydanticToolsParser(tools=[grade])

    # Prompt
    prompt = PromptTemplate(
        template="""You are a grader assessing relevance of a retrieved document to a user question. \n 
        Here is the retrieved document: \n\n {context} \n\n
        Here is the user question: {question} \n
        If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.""",
        input_variables=["context", "question"],
    )

    # Chain
    chain = prompt | llm_with_tool | parser_tool

    # Score
    filtered_docs = []
    search = "No"  # Default do not opt for web search to supplement retrieval
    for d, _ in documents:
        score = chain.invoke({"question": question, "context": d.page_content})
        grade = score[0].binary_score
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            search = "Yes"
            continue
    state_dict["documents"] = filtered_docs

    return state


def transform_query(state):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    state_dict = state["keys"]
    question = state_dict["questions"][-1]

    # Create a prompt template with format instructions and the query
    prompt = PromptTemplate(
        template="""You are generating questions that is well optimized for retrieval. \n 
        Look at the input and try to reason about the underlying sematic intent / meaning. \n 
        Here is the initial question:
        \n ------- \n
        {question} 
        \n ------- \n
        Formulate an improved question: """,
        input_variables=["question"],
    )

    # Grader
    model = ChatOpenAI(temperature=0, model=OPENAI_LLM_MODEL, streaming=True)

    # Prompt
    chain = prompt | model | StrOutputParser()
    better_question = chain.invoke({"question": question})
    state_dict["questions"].append(better_question)
    state_dict["query_transforms"] = state_dict["query_transforms"] + 1

    return state


def failure(state):
    """
    Terminal node in the event not relevant documents are found.

    Args:
       state (dict): The current graph state

    Returns:
       state (dict): Updates question key with a re-phrased question
    """
    state["keys"]["generation"] = "Failed to find any relevant documents."
    return state


### Edges


def decide_to_generate(state):
    """
    Determines whether to generate an answer or re-generate a question for web search.

    Args:
        state (dict): The current state of the agent, including all keys.

    Returns:
        str: Next node to call
    """

    print("---DECIDE TO GENERATE---")
    state_dict = state["keys"]

    if state_dict["query_transforms"] >= QUERY_TRANSFORM_LIMIT\
            or state_dict["query_transforms"] >= state_dict["attempts"]:
        return "failure"
    elif len(state_dict["documents"]) == 0:
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print("---DECISION: TRANSFORM QUERY and RUN WEB SEARCH---")
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"
