FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install the dependencies
RUN pip install streamlit

# Expose the port that Streamlit uses
EXPOSE 8080

# Run Streamlit and use the PORT environment variable
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
