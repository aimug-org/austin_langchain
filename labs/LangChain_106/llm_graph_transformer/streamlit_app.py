import copy
import uuid
from typing import List, Optional

import streamlit as st
from langchain_community.graphs.graph_document import GraphDocument
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_experimental.graph_transformers.llm import LLMGraphTransformer
from langchain_experimental.graph_transformers.llm import default_prompt
from pyvis.network import Network
from requests import request
import streamlit.components.v1 as components
import pandas as pd

models = []

example = """
    Use the following example as reference. Especially note now the relationships is structured:

    example input: Bob is a Software Engineer. Bob is married to Alice, who is a business services manager.
    response: {{"tool": "DynamicGraph","tool_input": {{"nodes": [{{"id":"Bob", "type":"PERSON"}},{{"id":"Alice","type":"PERSON"}},{{"id":"Software Engineer":"type":"PROFESSION"}},{{"id":"Business Services Manager":"type":"PROFESSION"}}],"relationships": [{{"source_node_id":"Bob","source_node_type":"PERSON","target_node_id":"Alice","target_node_type":"PERSON","type":"SPOUSE"}},{{"source_node_id":"Bob","source_node_type":"PERSON","target_node_id":"Software Engineer","target_node_type":"PROFESSION","type":"OCCUPATION"}},{{"source_node_id":"Alice","source_node_type":"PERSON","target_node_id":"Business Services Manager","target_node_type":"PROFESSION","type":"OCCUPATION"}},]}}}}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""You are an expert knowledge graph extractor. Analyze the input and extract "Nodes" and "Relationships".
    Nodes represent entities and concepts.
    Relationships represent connections between entities or concepts.

    {example}
    """,
        ),
        (
            "human",
            "Be sure to extract both Nodes as well as Relationships. "
            "Use the given format to extract information from the following input: {input}",
        ),
    ]
)

modified_prompt = copy.deepcopy(default_prompt)
modified_prompt.messages[0].prompt.template += example

prompts = {"one shot": modified_prompt, "new prompt": prompt}

if 'ollama_api_host' not in st.session_state:
    st.session_state['ollama_api_host'] = "http://localhost:11434"

if 'models' not in st.session_state:
    st.session_state['models'] = []

if 'model' not in st.session_state:
    st.session_state['model'] = None

models = st.session_state.models
model = st.session_state.model


@st.cache_data
def get_models(api_host: str) -> List[str]:
    resp = request(url=f"{api_host}/api/tags", method="get").json()
    model_names = []
    if 'models' in resp:
        model_names = ([details['name']
                        for details in resp["models"]
                        if 'name' in details and details['details']['family'] == 'llama'])
    return model_names


@st.cache_resource
def get_llm(api_host: str, model_name: str, prompt: str):
    return LLMGraphTransformer(
        llm=OllamaFunctions(
            model=model_name,
            temperature=0.0,
            base_url=api_host,
        ),
        prompt=prompts[prompt]
    )


def filter_graph(graph: GraphDocument):
    nodes = [node.id for node in graph.nodes]
    relationships = [
        rel
        for rel in graph.relationships
        if rel.source.id in nodes and rel.target.id in nodes
    ]
    rel_nodes = [[rel.source.id, rel.target.id] for rel in relationships]
    nodes = [node for rel_node in rel_nodes for node in rel_node]

    return nodes, relationships


def draw_pyvis(graph: GraphDocument) -> Optional[str]:
    nodes, relationships = filter_graph(graph)
    if len(nodes) == 0:
        return None
    g = Network(notebook=False, directed=True, cdn_resources="remote")
    for node in nodes:
        g.add_node(node)
    for rel in relationships:
        g.add_edge(rel.source.id, rel.target.id, label=rel.type)
    filename = f"static/{uuid.uuid4()}.html"
    g.write_html(filename)
    return filename


st.set_page_config(page_title="LLM Graph Transformer")
st.title("LLM Graph Transformer")

with st.sidebar:
    ollama_api_host = st.text_input(label="Ollama API Server", value="http://localhost:11434")
    if st.button(label="Get Models"):
        models = get_models(ollama_api_host)
        st.session_state.models = models

    if len(models) > 0:
        model = st.selectbox(label="Select Model", options=models)

        if st.button(label="Set Model"):
            st.session_state.model = model

        if st.session_state.model is not None:
            prompt_choice = st.selectbox(label="Prompt to use", options=prompts)

if st.session_state.model is not None:
    st.write(f"Model:", st.session_state.model, "Prompt:", prompt_choice)
    llm = get_llm(ollama_api_host, model, prompt_choice)

    user_input = st.text_area(label="Text to extract knowledge from")
    if st.button(label="Generate Graph"):
        graph_documents = llm.convert_to_graph_documents([Document(page_content=user_input)])
        graph = graph_documents[0]
        nodes = graph.nodes
        relationships = graph.relationships
        df_nodes = pd.DataFrame.from_records([{"Entity": node.id, "Type": node.type} for node in nodes])
        df_relationships = pd.DataFrame.from_records([{"Source": rel.source.id, "Type": rel.type, "Target": rel.target.id} for rel in relationships])
        col1, col2 = st.columns(2)
        with col1:
            st.text("Entities")
            st.dataframe(df_nodes, hide_index=True)
        with col2:
            st.text("Relationships")
            st.dataframe(df_relationships, hide_index=True)
        filename = draw_pyvis(graph)
        if filename is not None:
            HtmlFile = open(filename, "r", encoding="utf-8")
            source_code = HtmlFile.read()
            st.text("Knowledge Graph")
            components.html(source_code, height=1000, width=800)
