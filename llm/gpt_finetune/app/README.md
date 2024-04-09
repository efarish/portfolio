---
title: GPT2 4 Bible
emoji: 🌍
colorFrom: gray
colorTo: red
sdk: streamlit
sdk_version: 1.31.1
app_file: app.py
pinned: false
license: mit
---

A Streamlit frontend using a GPT2 model fine-tuned using the Christain New Testament as a corpus. 

Model notes:
- This is a fine-tuned Hugging Face distilgpt2 model.  
- The dataset used was the Christian New Testament.
- This is a document completion model. Not a Q&A. Input prompts like, "Jesus said".
