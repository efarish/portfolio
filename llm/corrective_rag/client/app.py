""""
A Steamlit script the uses the CRAGService to implement a
  corrective RAG requests.
"""

import json
import logging
import os

import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_chat import message

logging.getLogger().setLevel(logging.INFO)

load_dotenv()

if "conv_llm" not in st.session_state:
    st.session_state["conv_llm"] = None
if "API_Key" not in st.session_state:
    st.session_state["API_Key"] = ""
if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.set_page_config(page_title="Corrective-RAG", page_icon=":question:")
st.markdown(
    "<h3 style='text-align: center;'>Enter a search</h3>", unsafe_allow_html=True
)


st.sidebar.markdown(
    "<h2 style='text-align: center;'>Corrective-RAG</h2>", unsafe_allow_html=True
)
st.sidebar.markdown(
    """
    This search will:\n
    - Search an archive of RAG papers.\n
    - Reformulate the question if no documents are found.\n
    - Generate an answer to the question use a LLM.
    """
)
reformulation_attempts = st.sidebar.radio(
    'Questions reformulation attempts?',
    ('1', '2'),
    index=0)

response_container = st.container()
container = st.container()


def json_to_dictionary(_json: str) -> dict:
    return json.loads(_json)


def do_request(_query: str, _openai_key: str):
    server = os.environ['SERVER_HOST']
    port = os.environ['SERVER_PORT']
    response = requests.get('http://' + server + ':' + port + '/?question=' + _query + '&attempts=' +
                            reformulation_attempts).text
    response_dict = json_to_dictionary(response)
    messages = st.session_state["messages"]
    messages.append(("user", _query))
    questions_asked = response_dict["generated_questions"]
    if len(questions_asked) > 0:
        questions_asked.insert(0, ("ai", "No documents found for question. Using alternate formulations..."))
    messages = messages + [msg for msg in questions_asked if msg[0] == 'ai']
    messages.append(("ai", response_dict["answer"]))
    st.session_state["messages"] = messages

def render_conversation():
    messages = st.session_state["messages"]
    with response_container:
        for idx, msg in enumerate(messages):
            if msg[0] == "user":
                message(
                    msg[1],
                    is_user=True,
                    key=str(idx) + "_user",
                    avatar_style="adventurer",
                )
            else:
                message(
                    msg[1],
                    key=str(idx) + "_AI",
                    avatar_style="initials",
                    seed="AI",
                )


with container:
    with st.form(key="my_form", clear_on_submit=True):
        user_input = st.text_area("Enter a question:", key="input", height=10)
        submit_button = st.form_submit_button(label="Send")
        if submit_button:
            if len(user_input.strip()) > 0:
                do_request(user_input.strip(), st.session_state["API_Key"])
                render_conversation()
            else:
                render_conversation()
                st.sidebar.markdown(
                    "<h4 style='text-align:left;color:red'>Empty search string.</h4>",
                    unsafe_allow_html=True,
                )
        elif reformulation_attempts:
            render_conversation()

