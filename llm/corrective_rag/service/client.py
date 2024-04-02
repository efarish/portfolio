"""
A client for the CRAGService.py

"""
from CRAGService import *
import requests
import logging
from dotenv import load_dotenv

logging.getLogger().setLevel(logging.INFO)

load_dotenv()


def talk_to_instance():
    app = CRAGService()
    questions, answer = app.invoke("What is Chain-of-Thought Prompting?")
    # questions, answer = app.invoke("What is a unicorn?")
    for idx, query in enumerate(questions, 1):
        print(f"Query {idx}: {query}")
    print(f"Response: {answer}")
    print(f"Chat history:")
    history = app.get_messages()
    for msg in history:
        print(msg)


def talk_to_flask(_question: str) -> str:
    response = requests.get('http://localhost:' + os.environ['FLASK_SERVER_PORT'] + '/?question=' + _question).text
    return response


if __name__ == "__main__":
    #query = "What is a unicorn?"
    #query = "Who wrote the paper on Corrective RAG?"
    query = "What is a unicorn?"
    response = talk_to_flask(query)
    logging.info(response)
