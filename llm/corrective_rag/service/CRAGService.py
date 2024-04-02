"""
Wrapper class for OpenAI api.

"""

from langgraph.graph import END
from langgraph.graph import StateGraph
from flask import Flask
from flask import request
import logging
import json
import re
from waitress import serve

from graph_functions import *

load_dotenv()

app = Flask(__name__)



def get_model():
    """
    Create LangGraph graph.
    """
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("start_node", start_node)  # initialize state
    workflow.add_node("retrieve", retrieve)  # retrieve
    workflow.add_node("grade_documents", grade_documents)  # grade documents
    workflow.add_node("generate", generate)  # generatae
    workflow.add_node("transform_query", transform_query)  # transform_query
    workflow.add_node("failure", failure)  # create failure response

    # Build graph
    workflow.set_entry_point("start_node")
    workflow.add_edge("start_node", "retrieve")
    workflow.add_edge("retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "transform_query": "transform_query",
            "generate": "generate",
            "failure": "failure",
        },
    )
    workflow.add_edge("transform_query", "retrieve")
    workflow.add_edge("failure", END)
    workflow.add_edge("generate", END)

    # Compile
    app = workflow.compile()

    return app


def dictionary_to_json(_dict: dict) -> str:
    """
    Create str from dict.
    @rtype: str
    """
    return json.dumps(_dict)


def json_to_dictionary(_json: str) -> dict:
    """
    Creata dict from str.
    """
    return json.loads(_json)


class CRAGService:
    """
    Wrapper for LLM calls to OpenAI to implement a Corrective RAG requests.
    The workflow is:
    1. Each document found is evaluated for relevance. Its possible the documents found in the
      similarity search of the vector database will not be relevant.
    2. If no relevant documents are found in the vector datastore, the query is rewritten using a
      LLM request and the document query tried again.
    3. If after one query rewrite no documents are found, a message indicating this is
      returned to the client.

    A cache of message is maintained for chat applications.
    """

    def __init__(self, openai_key=None):
        if openai_key is None:
            openai_key = os.environ.get("OPENAI_API_KEY", None)
        assert openai_key is not None, "Missing OpenAI API key."
        os.environ["OPENAI_API_KEY"] = openai_key
        self.model = get_model()
        self.messages = []

    def invoke(self, query: str, attempts: int) -> (list, str):
        """
        Call the model, and update the message cache.
        """
        inputs = {"keys": {"question": query, "attempts": attempts}}
        response = self.model.invoke(inputs)
        state = response["keys"]
        questions = state["questions"]
        for idx in range(len(questions)):
            if idx == 0:
                self.messages.append(("user", questions[idx]))
            else:
                self.messages.append(("ai", f"Alternate Question: {questions[idx]}"))
        self.messages.append(("ai", state["generation"]))
        return state["questions"], state["generation"]

    def get_messages(self):
        """
        Get the conversation between this instance and client.
        """
        return self.messages


@app.after_request
def add_hostname_header(response):
    env_host = str(os.environ.get('HOSTNAME'))
    hostname = re.findall('[a-z]{3}-\d$', env_host)
    if hostname:
        response.headers["SP-LOCATION"] = hostname
    return response


@app.route('/')
def do_request() -> str:
    question = request.args.get("question", "").strip()
    attempts = int(request.args.get("attempts", "1").strip())
    if len(question) != 0:
        svc = CRAGService()
        questions, answer = svc.invoke(question, attempts)
        return dictionary_to_json({"answer": answer,
                                   "generated_questions": [('ai', str(idx) + ": " + q) for idx, q in
                                                           enumerate(questions) if idx > 0]})
    return dictionary_to_json({"answer": "Empty question.", "questions": [question]})


if __name__ == "__main__":
    serve(app, listen='*:9090')
