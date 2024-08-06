import streamlit as st
import requests
import json
import time
import datetime
from streamlit_chat import message as st_message

BASE_URL = "http://localhost:52864"

# Helper functions for API calls
def api_call(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        if response.status_code == 204:  # No content, typically for successful DELETE
            return True
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None
    except json.JSONDecodeError:
        if response.status_code in [200, 201, 202, 204]:  # Successful status codes
            return True
        st.error(f"API returned invalid JSON. Status code: {response.status_code}")
        return None

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_assistants():
    return api_call('POST', '/assistants/search', {"graph_id": "memory", "limit": 100})

def send_message():
    user_message = st.session_state.chat_user_input.strip()
    if user_message:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.chat_history.append({"role": "user", "content": f"{user_message}\n\n_{timestamp}_", "timestamp": timestamp})
        st.session_state.chat_user_input = ""

        # Create a run
        with st.spinner("Assistant is thinking..."):
            run_response = api_call('POST', f'/threads/{st.session_state.thread_id}/runs', 
                                    {
                                        "assistant_id": st.session_state.assistant_id,
                                        "input": {"messages": [{"role": "user", "content": user_message}]}
                                    })
            
            if run_response:
                run_id = run_response['run_id']
                
                while True:
                    status_response = api_call('GET', f'/threads/{st.session_state.thread_id}/runs/{run_id}')
                    if status_response and status_response['status'] in ['success', 'error']:
                        break
                    time.sleep(1)
                
                if status_response and status_response['status'] == 'success':
                    state_response = api_call('GET', f'/threads/{st.session_state.thread_id}/state')
                    if state_response and 'values' in state_response:
                        messages = state_response['values'].get('messages', [])
                        for message in reversed(messages):
                            if message.get('type') == 'ai':
                                content = message.get('content', [])
                                if content and isinstance(content[0], dict):
                                    assistant_message = content[0].get('text', '')
                                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    st.session_state.chat_history.append({"role": "assistant", "content": f"{assistant_message}\n\n_{timestamp}_", "timestamp": timestamp})
                                    break
                        else:
                            st.error("No assistant message found in the response.")
                    else:
                        st.error("Failed to retrieve assistant's response.")
                else:
                    st.error(f"Run failed to complete successfully. Status: {status_response['status'] if status_response else 'Unknown'}")
            else:
                st.error("Failed to start a new run.")

def chat_with_assistant_page():
    st.header("Chat with an Assistant")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'selected_assistant' not in st.session_state:
        st.session_state.selected_assistant = None

    # Get list of assistants
    assistants = get_assistants()

    # Let user select an assistant
    assistant_options = {f"{a['metadata'].get('name', 'Unnamed')} ({a['assistant_id']})": a['assistant_id'] for a in assistants}
    selected_assistant = st.selectbox("Choose an Assistant", list(assistant_options.keys()), key="chat_assistant_select")
    
    if selected_assistant != st.session_state.selected_assistant:
        st.session_state.selected_assistant = selected_assistant
        st.session_state.chat_history = []
        st.session_state.thread_id = None

    if selected_assistant:
        st.session_state.assistant_id = assistant_options[selected_assistant]
        
        # Create or retrieve a thread
        if 'thread_id' not in st.session_state or not st.session_state.thread_id:
            thread_response = api_call('POST', '/threads', {})
            if thread_response:
                st.session_state.thread_id = thread_response['thread_id']
            else:
                st.error("Failed to create a new thread.")
                return

        st.info(f"Current Thread ID: {st.session_state.thread_id}")

        # Chat interface
        st.subheader("Chat")
        chat_container = st.container()
        
        with chat_container:
            for i, chat in enumerate(st.session_state.chat_history):
                if chat['role'] == 'user':
                    st_message(chat['content'], is_user=True, key=f"chat_{i}_user", avatar_style="thumbs")
                else:
                    st_message(chat['content'], key=f"chat_{i}_assistant", avatar_style="bottts")

        user_input = st.text_input("Type your message...", key="chat_user_input", on_change=send_message)
        col1, col2, col3 = st.columns([1, 1, 5])
        send_button = col1.button("Send", on_click=send_message)
        clear_button = col2.button("Clear Chat")

        if clear_button:
            st.session_state.chat_history = []
            st.experimental_rerun()

        st.markdown("---")
        st.markdown("💡 **Tip**: Press Enter to send your message quickly!")

        # Auto scroll to the bottom
        st.markdown(
            """
            <script>
            var chat_container = window.parent.document.querySelector("div[data-testid='stVerticalBlock'] > div:nth-child(3) > div:nth-child(2)");
            if (chat_container) {
                chat_container.scrollTop = chat_container.scrollHeight;
            }
            </script>
            """,
            unsafe_allow_html=True
        )

def create_assistant_page():
    st.header("Create a New Assistant")
    
    if 'new_assistant' not in st.session_state:
        st.session_state.new_assistant = None
    
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0

    with st.form(key=f"create_assistant_form_{st.session_state.form_key}"):
        assistant_name = st.text_input("Assistant Name", key=f"create_assistant_name_{st.session_state.form_key}")
        description = st.text_area("Description", key=f"create_assistant_description_{st.session_state.form_key}")
        config = st.text_area("Configuration (JSON)", "{}", key=f"create_assistant_config_{st.session_state.form_key}")
        submitted = st.form_submit_button("Create Assistant")
        if submitted:
            try:
                config_dict = json.loads(config)
                result = api_call('POST', '/assistants', {
                    "graph_id": "memory",
                    "config": config_dict,
                    "metadata": {"name": assistant_name, "description": description}
                })
                if result:
                    st.session_state.new_assistant = result
                    st.session_state.assistants = []  # Clear the assistants list to force a refresh
                    st.session_state.form_key += 1  # Increment the form key
                    st.experimental_rerun()
                else:
                    st.error("Failed to create assistant. Please try again.")
            except json.JSONDecodeError:
                st.error("Invalid JSON in configuration. Please check your input.")

    if st.session_state.new_assistant:
        st.success("Assistant created successfully!")
        st.write("New Assistant Details:")
        st.json(st.session_state.new_assistant)
        if st.button("Clear", key=f"clear_button_{st.session_state.form_key}"):
            st.session_state.new_assistant = None
            st.session_state.form_key += 1  # Increment the form key
            st.experimental_rerun()

def search_assistants_page():
    st.header("Search Assistants")
    
    if 'assistants' not in st.session_state:
        st.session_state.assistants = []

    search_term = st.text_input("Search by name", key="search_assistants_term")
    if st.button("Search", key="search_assistants_button") or st.session_state.assistants:
        response = api_call('POST', '/assistants/search', {
            "graph_id": "memory",
            "limit": 100,
            "metadata": {"name": search_term} if search_term else {}
        })
        if response:
            st.session_state.assistants = response
            st.write("Search Results:")
            for i, assistant in enumerate(st.session_state.assistants):
                with st.expander(f"Assistant: {assistant['metadata'].get('name', 'Unnamed')}", expanded=False):
                    st.write(f"ID: {assistant['assistant_id']}")
                    st.write(f"Description: {assistant['metadata'].get('description', 'No description')}")
                    if st.button(f"Delete {assistant['metadata'].get('name', 'Unnamed')}", key=f"delete_assistant_{i}"):
                        delete_response = api_call('DELETE', f"/assistants/{assistant['assistant_id']}")
                        if delete_response is True:
                            st.success(f"Assistant {assistant['metadata'].get('name', 'Unnamed')} deleted successfully.")
                            st.session_state.assistants = [a for a in st.session_state.assistants if a['assistant_id'] != assistant['assistant_id']]
                            st.experimental_rerun()
                        else:
                            st.error("Failed to delete assistant.")
        else:
            st.write("No assistants found or error occurred.")

def manage_threads_page():
    st.header("Manage Threads")
    
    if 'threads' not in st.session_state:
        st.session_state.threads = []

    # Search for threads
    st.subheader("Search Threads")
    
    col1, col2 = st.columns(2)
    with col1:
        limit = st.number_input("Limit", min_value=1, max_value=100, value=10, key="thread_limit")
        status = st.selectbox("Status", ["All", "idle", "busy", "interrupted"], key="thread_status")
    with col2:
        offset = st.number_input("Offset", min_value=0, value=0, key="thread_offset")
        sort_by = st.selectbox("Sort by", ["created_at", "updated_at"], key="thread_sort_by")

    sort_order = st.radio("Sort order", ["descending", "ascending"], key="thread_sort_order")

    # Metadata search
    st.subheader("Metadata Search")
    metadata_key = st.text_input("Metadata Key", key="thread_metadata_key")
    metadata_value = st.text_input("Metadata Value", key="thread_metadata_value")

    if st.button("Search Threads", key="thread_search_button") or st.session_state.threads:
        search_params = {
            "limit": limit,
            "offset": offset,
            "metadata": {metadata_key: metadata_value} if metadata_key and metadata_value else {},
        }
        if status != "All":
            search_params["status"] = status

        threads = api_call('POST', '/threads/search', search_params)
        
        if threads:
            # Sort threads
            threads.sort(key=lambda x: x[sort_by], reverse=(sort_order == "descending"))
            st.session_state.threads = threads
            
            for i, thread in enumerate(st.session_state.threads):
                with st.expander(f"Thread {thread['thread_id']}", expanded=False):
                    st.write(f"Created at: {thread['created_at']}")
                    st.write(f"Updated at: {thread['updated_at']}")
                    st.write(f"Status: {thread['status']}")
                    st.write(f"Metadata: {thread.get('metadata', {})}")
                    
                    # Get thread state
                    thread_state = api_call('GET', f"/threads/{thread['thread_id']}/state")
                    if thread_state:
                        st.write("Thread State:")
                        st.json(thread_state)
                    
                    # Get recent runs
                    runs = api_call('GET', f"/threads/{thread['thread_id']}/runs")
                    if runs:
                        st.write("Recent Runs:")
                        for run in runs[:5]:  # Display only the 5 most recent runs
                            st.write(f"Run ID: {run['run_id']}, Status: {run['status']}, Created at: {run['created_at']}")
                    
                    if st.button(f"Delete Thread {thread['thread_id']}", key=f"delete_thread_{i}"):
                        delete_response = api_call('DELETE', f"/threads/{thread['thread_id']}")
                        if delete_response is True:
                            st.success(f"Thread {thread['thread_id']} deleted successfully.")
                            # Remove the deleted thread from the session state
                            st.session_state.threads = [t for t in st.session_state.threads if t['thread_id'] != thread['thread_id']]
                            st.experimental_rerun()
                        else:
                            st.error("Failed to delete thread.")
        else:
            st.write("No threads found or error occurred.")

    # Create a new thread
    st.subheader("Create New Thread")
    new_thread_metadata = st.text_area("Thread Metadata (JSON)", "{}", key="new_thread_metadata")
    if st.button("Create Thread", key="create_thread_button"):
        try:
            metadata_dict = json.loads(new_thread_metadata)
            new_thread = api_call('POST', '/threads', {"metadata": metadata_dict})
            if new_thread:
                st.success(f"New thread created with ID: {new_thread['thread_id']}")
                # Refresh the thread list
                st.session_state.threads = []
                st.experimental_rerun()
            else:
                st.error("Failed to create new thread.")
        except json.JSONDecodeError:
            st.error("Invalid JSON in metadata")

def main():
    st.title("AI Assistant Interface")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Chat with Assistant", "Create Assistant", "Search Assistants", "Manage Threads"], key="navigation")

    # Page content
    if page == "Chat with Assistant":
        chat_with_assistant_page()
    elif page == "Create Assistant":
        create_assistant_page()
    elif page == "Search Assistants":
        search_assistants_page()
    elif page == "Manage Threads":
        manage_threads_page()

if __name__ == "__main__":
    main()
