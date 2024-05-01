# LLM Graph Transformer

## Overview

[LLMGraphTransformer](https://python.langchain.com/docs/use_cases/graph/constructing/#llm-graph-transformer) allows you to extract [Knowledge Graphs](https://en.wikipedia.org/wiki/Knowledge_graph) from your context.  
This streamlit application demonstrates how you might utilize such a tool and gain interesting insights from your context.  

## Setup

While you can use any LLM that supports `with_structured_output()` function, this example uses [OllamaFunctions](https://python.langchain.com/docs/integrations/chat/ollama_functions/) to allow knowledge graph extraction using local LLMs.  
You will need to have access to an instance of [Ollama](https://ollama.com/) running either on your machine or within your network and have an LLM already download within Ollama.

Once Ollama is verified to be up and running, you may run the following commands within your terminal to launch the streamlit application.

```bash
git clone https://github.com/colinmcnamara/austin_langchain.git
cd austin_langchain/labs/LangChain_106/llm_graph_transformer
mkdir static
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

## Screenshot of the Streamlit Application

<img width="1159" alt="Screenshot 2024-05-01 at 12 28 47 AM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/db6fa5d8-c1fd-453e-89d6-cc62f54de610">

## Visualization of information represented as Knowledge Graph

![canvas](https://github.com/lalanikarim/austin_langchain/assets/1296705/b4f742a4-1204-40b6-bfbf-d1864ce468b7)
