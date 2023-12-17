# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Install system packages required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the Streamlit Python script into the container
COPY streamlit_app.py /app

# Install required dependencies
RUN pip install streamlit requests

# Expose the port that Streamlit will run on
EXPOSE 8501

# Run the Streamlit app when the container starts
CMD ["streamlit", "run", "streamlit_app.py"]

