import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

LLM_MODEL = None
if os.environ.get("LLM_MODEL", None) is None:
    load_dotenv()
    LLM_MODEL = os.environ["LLM_MODEL"]
else: LLM_MODEL = os.environ["LLM_MODEL"]

def get_llm_model():
    """
    A place to the the LLM model.

    Returns:
        ChatOpenAI
    """
    return ChatOpenAI(model=LLM_MODEL, temperature=0)
