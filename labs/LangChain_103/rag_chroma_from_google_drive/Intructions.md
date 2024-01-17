
## Instructions

This directory contains the necessary files and instructions to set up and run the rag_chroma_from_google_drive project.

### Setting Google Credentials

To use Google services, such as Google Drive, you need to set up Google credentials. Follow these steps:

1. To set up Google credentials for your application, create a Google Service Account. Follow instructions here [Google Service Account Instructions](https://cloud.google.com/iam/docs/service-accounts-create)
2. This is necessary because we're using Docker to authenticate credentials and it's not possible to open a web browser when running containers. See this [GitHub issue](https://github.com/langchain-ai/langchain/issues/8755) for more info
3. A Google Service Account differs from OAuth 2.0 Client IDs. The latter are used when an application acts on behalf of a user and requires user consent and interactive login flows. Service Accounts are for server-to-server interactions where no user interaction is needed. They're suitable for automated processes running on servers, including Docker containers.
4. After creating a service account, you'll receive a key file with credentials for authentication. Rename it `keys.json` and save it in this path `~/.credentials/keys.json`
5. Important: Application-owned accounts can only access their own documents or those shared with them. If required documents are owned by a regular account, the service account won't list them. Use domain-wide delegation to allow your app to access files on behalf of other users in a Google Apps domain. If your `GoogleDriveLoader` returns an empty list, this is most likely why.

Before running the project, you need to set the following environment variables:

- `GOOGLE_APPLICATION_CREDENTIALS`: Set this variable to the path where you saved the `keys.json` file earlier. Make sure to call out the full path or you will get an error

### Running Docker Compose

Run the project using Docker Compose:

  ```bash
  docker-compose up --build
  ```

This will build and start the necessary containers.

### URLs

Access the project by opening a web browser and navigating to the specified URL

Streamlit app: http://localhost:8501/

Fast API Shema: http://localhost:8000/docs


