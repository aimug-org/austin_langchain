# run this file using
# streamlit run streamlit_app.py

import streamlit as st
import requests

# Define the API URL
api_url = "http://localhost:8080/pirate-speak/invoke"

# Create a Streamlit UI
st.title("Ticket Lingo Converter")  # Updated title
st.write("Enter a text to convert to Ticket Lingo:")  # Updated description

# Input text box
input_text = st.text_area("Enter text:", "")

# Button to trigger API call
if st.button("Convert to Ticket Lingo"):  # Updated button label
    if input_text:
        # Prepare the request payload in JSON format
        payload = {"input": {"text": input_text}, "config": {}, "kwargs": {}}

        # Make a POST request to the API
        response = requests.post(api_url, json=payload)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Display the Ticket Lingo conversion
            result = response.json()["output"]["content"]
            st.success(f"Ticket Lingo Conversion: {result}")  # Updated success message
        else:
            st.error("API request failed. Please check the input and try again.")
    else:
        st.warning("Please enter some text to convert.")
