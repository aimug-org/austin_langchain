import warnings
import streamlit as st
import pandas as pd
from langchain_core.messages import HumanMessage
from state_initializer import initialize_state
from chat_manager import ChatManager
from bom_agent_graph import BomAgentGraph
from moc_data.fake_data_df import fake_data_df

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.title("BOM Analysis Assistant")

state = st.session_state
chat_manager = ChatManager()

initialize_state()
chat_manager.display_chat_history()

if not state.messages:
    chat_manager.add_message(
        "assistant",
        """
        This tool is designed to demonstate how we can use LangGraph LLM agents to analyze manufacturing / supply chain Bill of Material (BOM) data.
        You can think of BOMs as directed graphs where each node represents a part number and each edge represents a parent-child relationship. We can use this graph to answer questions like:
        - What parts are used in a given assembly?
        - What assemblies use a given part?
        - What are the top-level assemblies?
        - What are the lowest-level parts?
        """,
    )

with st.sidebar:
    uploaded_file = st.file_uploader(
        "Upload Excel file",
        type="xlsx",
    )

    if uploaded_file:
        state["uploaded_file"] = uploaded_file


df = pd.DataFrame(fake_data_df)
st.dataframe(df, hide_index=True)

if prompt := st.chat_input("What is your query?"):

    chat_manager.add_message("user", prompt)

    # Create an instance of BomAgentGraph
    bom_agent_graph = BomAgentGraph()

    # Compile the graph
    app = bom_agent_graph.compile()

    # Prepare your inputs: a list of messages and a DataFrame
    messages = [HumanMessage(content=prompt)]
    df = []

    if state["uploaded_file"]:
        df = pd.read_excel(state["uploaded_file"])
    else:
        df = pd.DataFrame(fake_data_df)

    st.dataframe(
        df,
        hide_index=True,
    )

    inputs = {"messages": messages, "dataframe": df}

    for output in app.stream(inputs):

        for key, value in output.items():
            chat_manager.add_message(key, value)
