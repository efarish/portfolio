import streamlit as st
from streamlit_chat import message
from LLM_RAG_Conv import *
import logging
import os
from dotenv import load_dotenv

load_dotenv()

SIMILARITY_SEARCH_K=int( os.environ['SIMILARITY_SEARCH_K'] ) 
LLM_TEMPERATURE=float( os.environ['LLM_TEMPERATURE']  ) 
MAX_CONTENT_SIZE=int( os.environ['MAX_CONTENT_SIZE'] )
MAX_TOKENS=int( os.environ['MAX_TOKENS'] )
SYSTEM_CONTENT=os.environ['SYSTEM_CONTENT']
LLM_MODEL=os.environ['LLM_MODEL']
VECTOR_DB_PATH=os.environ['VECTOR_DB_PATH']

if 'conv_llm' not in st.session_state:
    st.session_state['conv_llm'] = None 
if 'API_Key' not in st.session_state:
    st.session_state['API_Key'] =''

# Setting page title and header
st.set_page_config(page_title="RAG Conversation", page_icon=":robot_face:")
st.markdown("<h1 style='text-align: center;'>Lets talk.</h1>", unsafe_allow_html=True) 

st.sidebar.title("RAG Conversataion")
st.session_state['API_Key'] = st.sidebar.text_input("OpenAI key:",type="password")

response_container = st.container()
container = st.container()

def get_response(_query: str, _openai_key: str) -> str:
    """" Query the LLM using the wrapper class LLM_RAG_Conv. """
    if  st.session_state['conv_llm'] == None:
        logging.warning("Creating a new llm.")
        st.session_state['conv_llm'] = LLM_RAG_Conv(LLM_MODEL, 
                                                    VECTOR_DB_PATH, 
                                                    st.session_state['API_Key'])    
    model = st.session_state['conv_llm']
    model.invoke( _query )
    return model.get_messages()[-1]
    
with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("Enter a question:", key='input', height=10)
        submit_button = st.form_submit_button(label='Send')
        if submit_button:
            if len( user_input.strip() ) > 0:
                response = get_response(user_input.strip(), st.session_state['API_Key'])
                with response_container:
                    messages = st.session_state['conv_llm'].get_messages()
                    logging.warning(f'Length of messages: {len( messages )}')
                    for i in range(1, len( messages ) ):
                        if (i % 2) > 0:
                            message(messages[i].content, avatar_style="no-avatar",  is_user=True, key=str(i) + '_user')
                        else:
                            message(messages[i].content, avatar_style="no-avatar", key=str(i) + '_AI')


        




