# Project: Train GPT2 LLM using Hugging Face models and APIs.

This notebook fine-tunes a pre-trained Hugging Face GPT2 `distilgpt2` model using the Bible as the corpus. The purpose of this is to better enable the model to generate document completion queries such as, "Jesus was born in".

For training, the corpus will be chunked up into training data of 500 tokens per example.

The training was done usign Colab on a A100. GPU RAM usage peaked at around 28 gigs.

This project has the following files:

- GPT2_FineTune.ipynb: A notebook used to load and pre-process the training data.
- Inference.ipynb: A notebook used to experiment with stoping criteria and streaming tokens while a response is being created.
- The `app` directory contains a Streamlit application used to submit requests to the fine-tuned model.

