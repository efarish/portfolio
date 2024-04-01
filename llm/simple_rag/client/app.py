import streamlit as st
import requests
from urllib.parse import quote
import logging
import os

st.set_page_config(page_title="Bible RAG Questions")
st.sidebar.title("Bible RAG Questions")
st.sidebar.markdown(
"""
Model notes:
- The corpus used is the Bible NT.
- Streamlit is providing this frontend.
- The RAG service consists of:
    - OpenAI embeddings and LLM 3.5 Turbo
    - Chroma Vector DB 
    - LangChain
"""
)

form = st.form(key='my-form')
txt = form.text_input('Enter a prompt')
submit = form.form_submit_button('Submit') 
    
if submit:
    with st.spinner('Processing...'):
        st.markdown("<h4 style='text-align: left;'>Response:</h4>", unsafe_allow_html=True)
        ta = st.empty() 
        query = quote( txt )
        logging.warn(f'localhost request...')
        generated_text = requests.get('http://' + os.environ['API_HOST'] + ':9090/?query=' + query).text
        ta.write( generated_text )
