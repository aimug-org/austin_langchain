import streamlit as st
import pandas as pd


state = st.session_state


class ChatManager:
    """
    A class that manages the chat messages and history in a chat application. Since we work a lot with chat messagesm, this class will be reused a lot across our tutorials
    """

    def add_message(self, role, content, use_expander=False, copyable_content=None):
        """
        Adds a new message to the chat history.

        Parameters:
        - role (str): The role of the message sender.
        - content (str): The main content of the message.
        - use_expander (bool): Whether to use an expander to display the message.
        - copyable_content (str): The copyable content of the message.

        Returns:
        None
        """

        message = {
            "role": role,
            "content": content,
            "copyable_content": copyable_content,
        }
        state.messages.append(message)

        with st.chat_message(role):
            if use_expander:
                with st.expander("""**Click to view steps to generate report**"""):
                    st.markdown(content)
            else:
                st.markdown(content)

            if copyable_content is not None:
                st.code(copyable_content)

    def display_chat_history(self):
        """
        Displays the chat history.

        Parameters:
        None

        Returns:
        None
        """
        for message in state.messages:
            with st.chat_message(message["role"]):

                if message["copyable_content"]:
                    st.markdown(message["content"])
                    st.code(message["copyable_content"])
                else:
                    st.markdown(message["content"])
