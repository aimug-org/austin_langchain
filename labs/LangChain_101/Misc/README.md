# Overview

1. [101-1-streamlit_llamacpp_mistral.ipynb](101-1-streamlit_llamacpp_mistral.ipynb)  
This notebook is a variation on the original [101-1-streamlit_streaming.ipynb](../101-1-streamlit_streaming.ipynb)  
It uses an alternative model called Mistral 7b locally instead of making api  
calls to OpenAI.
2. [101-1-mistral-chatbot](101-1-mistral-chatbot)  
This is a standalone python application and doesn't require a notebook to run. You may run this locally on your  
computer with or without a GPU. Note that your mileage may vary when running solely on a CPU. The chatbot is created  
with ease of deployment in mind and can be deployed in a "production" environment with very little effort.
3. [101-1-streamlit_ollama_streaming.ipynb](101-1-streamlit_ollama_streaming.ipynb)
This notebook demonstrates an alternate approach to running and using LLMs locally.  
Instead of using LLama.Cpp, it uses [Ollama](https://ollama.ai) Inference Engine as a webservice,  
making the development process very similar to using 3rd party AI services like OpenAI etc.
4. [101-1-streamlit_ollama_llava.ipynb](101-1-streamlit_ollama_llava.ipynb)
This notebook takes the Ollama game to the next level by letting you do multimodal inferencing using images.  
This modified notebook uses the `bakllava` model which is `mistral-7b` model modified to incorporate `llava-v1.5`  
architecture, which gives it `image to text` capabilities. Using this notebook, you can now upload an image file  
and ask the LLM to describe it to you.
