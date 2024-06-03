Creating a simple web service using Streamlit in Google Cloud Run, with authentication and proxying by Google Identity-Aware Proxy (IAP), involves several steps. Here is a step-by-step guide:

### 1. Set Up Your Development Environment
Ensure you have the following installed:
- Python
- Streamlit
- Google Cloud SDK
- Docker

### 2. Create Your Streamlit Application
Create a simple Streamlit application (`app.py`). For example:
```python
import streamlit as st

st.title("Simple Streamlit App")
st.write("Hello, World!")
```

### 3. Create a Dockerfile
Create a `Dockerfile` to containerize your Streamlit application.
```Dockerfile
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install the dependencies
RUN pip install streamlit

# Expose the port Streamlit is running on
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
```

### 4. Build and Push the Docker Image
Build the Docker image and push it to Google Container Registry (GCR).

```sh
# Authenticate with Google Cloud
gcloud auth login

# Set your Google Cloud project
gcloud config set project YOUR_PROJECT_ID

# Build the Docker image
docker build -t gcr.io/YOUR_PROJECT_ID/streamlit-app .

# Push the Docker image to GCR
docker push gcr.io/YOUR_PROJECT_ID/streamlit-app
```

### 5. Deploy to Google Cloud Run
Deploy your container to Google Cloud Run.

```sh
gcloud run deploy streamlit-app \
  --image gcr.io/YOUR_PROJECT_ID/streamlit-app \
  --platform managed \
  --region YOUR_PREFERRED_REGION \
  --allow-unauthenticated
```

### 6. Set Up Google Identity-Aware Proxy (IAP)
1. **Enable IAP and Configure OAuth Consent Screen**
   - Go to the [IAP page in the Google Cloud Console](https://console.cloud.google.com/security/iap).
   - Enable IAP for your project.
   - Configure the OAuth consent screen in the [OAuth consent screen page](https://console.cloud.google.com/apis/credentials/consent).
   - Create OAuth 2.0 credentials in the [Credentials page](https://console.cloud.google.com/apis/credentials).
   - Add the OAuth 2.0 Client ID to the IAP configuration.

2. **Restrict Access to Your Cloud Run Service**
   - Go to the [Cloud Run page](https://console.cloud.google.com/run) and click on your service.
   - Click on the "Permissions" tab and then "Add member".
   - Add the IAP-secured Web App User role to the email addresses of the users who should have access.

3. **Configure IAP**
   - Go to the [IAP page](https://console.cloud.google.com/security/iap) and enable IAP for your Cloud Run service.

### 7. Test Your Application
Visit the URL provided by Cloud Run. You should be prompted to log in with your Google account due to the IAP protection.

### Complete Example
Here is a complete example of the commands you will run and the files you will create:

**app.py**
```python
import streamlit as st

st.title("Simple Streamlit App")
st.write("Hello, World!")
```

**Dockerfile**
```Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install streamlit
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
```

**Commands**
```sh
# Authenticate with Google Cloud
gcloud auth login

# Set your Google Cloud project
gcloud config set project YOUR_PROJECT_ID

# Build the Docker image
docker build -t gcr.io/YOUR_PROJECT_ID/streamlit-app .

# Push the Docker image to GCR
docker push gcr.io/YOUR_PROJECT_ID/streamlit-app

# Deploy to Cloud Run
gcloud run deploy streamlit-app \
  --image gcr.io/YOUR_PROJECT_ID/streamlit-app \
  --platform managed \
  --region YOUR_PREFERRED_REGION \
  --allow-unauthenticated

# Set up IAP and configure OAuth consent screen as described in steps 6 and 7.
```

This should result in a simple Streamlit app deployed on Google Cloud Run with authentication managed by Google IAP.