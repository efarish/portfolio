import streamlit as st
from transformers import AutoModelForCausalLM, GPT2Tokenizer, StoppingCriteria, StoppingCriteriaList
from transformers import TextIteratorStreamer
from threading import Thread
import torch
import random   

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
PROJECT_MODEL = "RickMartel/GPT2_FT_By_NT_RAND_v11"
model = AutoModelForCausalLM.from_pretrained(PROJECT_MODEL)
model = model.to( device )
model.eval()
tokenizer = GPT2Tokenizer.from_pretrained(PROJECT_MODEL)

class StoppingCriteriaSub(StoppingCriteria):
    def __init__(self, stops = [], encounters=1):
        super().__init__()
        self.stops = [stop.to( device ) for stop in stops]
        self.encounters = encounters

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor):
        last_tkn = input_ids[0][-1]
        stop_word_found = False
        for stop in self.stops:
            if sum( input_ids[0] == stop ) >= self.encounters: 
                stop_word_found = True
        return stop_word_found and self.stops[0] == last_tkn

# The StoppingCriteriaSub assumes period is the first token id.
stop_words = ['.']
stop_words_ids = [tokenizer(stop_word, return_tensors='pt', add_special_tokens=False)['input_ids'].squeeze() for stop_word in stop_words]
stopping_criteria = StoppingCriteriaList([StoppingCriteriaSub(stops=stop_words_ids,
                                                              encounters=3)])
st.set_page_config(page_title="GPT2 4 Bible")
st.sidebar.title("GPT2 4 Bible")
st.sidebar.markdown(
"""
Model notes:
- This is a fine-tuned Hugging Face distilgpt2 model.  
- The dataset used was the Christian New Testament.
- This Space uses a CPU only. So, the app is slow.
- This is a document completion model. Not a Q&A. Input prompts like, "Jesus said".
"""
)

form = st.form(key='my-form')
txt = form.text_input('Enter a prompt')
submit = form.form_submit_button('Submit') 
    
if submit:
    with st.spinner('Processing...'):
        st.markdown("<h4 style='text-align: left;'>Response:</h4>", unsafe_allow_html=True)
        ta = st.empty() 
        input = tokenizer([tokenizer.bos_token + txt], return_tensors="pt")
        streamer = TextIteratorStreamer( tokenizer )
        generation_kwargs = dict(input, streamer=streamer, 
                                 stopping_criteria=stopping_criteria,
                                 do_sample=True,
                                 max_new_tokens=200,)
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()
        generated_text = ""
        for new_text in streamer:
            generated_text += new_text.replace('"', "").replace(tokenizer.bos_token,"")
            ta.write( generated_text )
