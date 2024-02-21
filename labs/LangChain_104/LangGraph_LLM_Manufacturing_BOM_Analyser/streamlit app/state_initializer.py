import streamlit as st
from bom_handler import BOMGraph


def initialize_state():
    state = st.session_state
    if "messages" not in state:
        state["messages"] = []

    if "uploaded_file" not in state:
        state["uploaded_file"] = None

    if "BOMGraph" not in state:
        state["BOMGraph"] = BOMGraph()
    if "locals" not in state:
        state["locals"] = {}
