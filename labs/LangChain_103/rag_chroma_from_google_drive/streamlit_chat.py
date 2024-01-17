import requests
import streamlit as st
import time


@st.cache_data
def get_response_from_llm(query):
    payload = {"input": query, "config": {}, "kwargs": {}}

    API_URL = "http://api:8080/rag-chroma/invoke"

    res = requests.post(API_URL, json=payload)

    if res.status_code == 200:
        return res.json()["output"]
    else:
        return f"Error: Received status code {res.status_code}"


st.title("Chat With Google Drive Files - Rag Chroma")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


prompt = st.chat_input("What is your query?")
if prompt:
    # Add user message to chat history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    response = get_response_from_llm(prompt)

    # Display bot response and add to chat history
    with st.chat_message("assistant"):
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
