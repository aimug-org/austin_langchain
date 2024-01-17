import requests
import streamlit as st

API_BASE = "http://api:8000"
state = st.session_state


class ChatManager:
    def add_message(self, role, content):
        if state.selected_path not in state.chat_histories:
            state.chat_histories[state.selected_path] = []

        message = {
            "role": role,
            "content": content,
        }
        state.chat_histories[state.selected_path].append(message)

        with st.chat_message(role):
            st.write(content)

    def display_chat_history(self):
        # Display chat messages from history for the selected path
        if state.selected_path in state.chat_histories:
            for message in state.chat_histories[state.selected_path]:
                with st.chat_message(message["role"]):
                    st.write(message["content"])


def initialize_state():
    if "chat_histories" not in state:
        state.chat_histories = {}
    if "selected_path" not in state:
        state.selected_path = ""
    if "folder_routes" not in state:
        state.folder_routes = []


@st.cache_data
def get_response_from_llm(query, path):
    payload = {"input": query, "config": {}, "kwargs": {}}
    res = requests.post(f"{API_BASE}{path}", json=payload)
    if res.status_code == 200:
        return res.json()["output"]
    else:
        return f"Error: Received status code {res.status_code}"


def get_folder_routes():
    response = requests.get(f"{API_BASE}/list-folder-routes")
    if response.status_code == 200:
        folder_routes = response.json()
        state.folder_routes = folder_routes
    else:
        st.error(f"{response.status_code} Error: Failed to retrieve folder routes")


def add_new_folder_config(name, folder_id):
    response = requests.post(
        f"{API_BASE}/initialize-chain", json={"folder_id": folder_id, "name": name}
    )
    if response.status_code == 200:
        path = response.json().get("path")
        state.folder_routes.append(path)
        select_config(path)
    else:
        error_detail = response.json().get("detail")

        if "File not found" in error_detail:
            user_friendly_error = "Invalid folder ID, please try again."
        else:
            user_friendly_error = error_detail

        st.error(f"{response.status_code} Error: {user_friendly_error}")


def select_config(path):
    state.selected_path = path

    if path not in state.chat_histories:
        state.chat_histories[path] = []


def handle_folder_configs():
    if state.folder_routes == []:
        get_folder_routes()

    with st.sidebar:
        st.header("Folder Configurations")
        folder_id = st.text_input("Enter Google Drive Folder ID")
        config_name = st.text_input("Enter a name for this configuration")
        if st.button(
            "Add New Configuration",
        ):
            add_new_folder_config(config_name, folder_id)

        if state.folder_routes:
            st.sidebar.header("Select Drive to Chat With")

            for path in state.folder_routes:
                if st.button(path):
                    select_config(path)


st.title("Chat With Google Drive Files - Rag Chroma")

initialize_state()
chat_manager = ChatManager()

handle_folder_configs()

if state.selected_path:
    chat_manager.display_chat_history()

    if prompt := st.chat_input("What is your query?"):
        chat_manager.add_message("user", prompt)

        response = get_response_from_llm(prompt, state.selected_path)

        chat_manager.add_message("assistant", response)
