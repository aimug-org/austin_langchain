## Instructions

This directory contains the necessary files and instructions to set up and run the rag_chroma_from_google_drive project.

### Setting Google Credentials

To use Google services, such as Google Drive, you need to set up Google credentials. Follow these steps:

1. To set up Google credentials for your application, create a Google Service Account. Follow instructions here [Google Service Account Instructions](https://cloud.google.com/iam/docs/service-accounts-create)
2. This is necessary because we're using Docker to authenticate credentials and it's not possible to open a web browser when running containers. See this [GitHub issue](https://github.com/langchain-ai/langchain/issues/8755) for more info
3. A Google Service Account differs from OAuth 2.0 Client IDs. The latter are used when an application acts on behalf of a user and requires user consent and interactive login flows. Service Accounts are for server-to-server interactions where no user interaction is needed. They're suitable for automated processes running on servers, including Docker containers.
4. After creating a service account, you'll receive a key file with credentials for authentication. Rename it `keys.json` and save it in this path `~/.credentials/keys.json` (see below section "Creating Service Account to Access Google Drive API with keys.json File")
5. Important: Application-owned accounts can only access their own documents or those shared with them. If required documents are owned by a regular account, the service account won't list them. Use domain-wide delegation to allow your app to access files on behalf of other users in a Google Apps domain. If your `GoogleDriveLoader` returns an empty list, this is most likely why.

Before running the project, you need to set the following environment variables:

- `GOOGLE_APPLICATION_CREDENTIALS`: Set this variable to the path where you saved the `keys.json` file earlier. Make sure to call out the full path or you will get an error
- `OPENAI_API_KEY`

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

### Creating Service Account to Access Google Drive API with keys.json File
#### 1. Go to [Google Cloud Console](https://console.cloud.google.com) and create a new project.
   You can search for "new project" in the search bar and click `Create A Project`.
<img width="709" alt="Screenshot 2024-01-23 at 9 09 43 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/9af57c5c-6903-4ec3-af7c-cefdaf23d808">

#### 2. Fill the `Project Name`.
<img width="579" alt="Screenshot 2024-01-23 at 9 10 04 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/28c672cd-3aef-4176-ba3b-280baf3ffb05">

#### 3. Once the project is created, ensure that you've selected the correct project.
<img width="400" alt="Screenshot 2024-01-23 at 9 26 13 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/b272d8bc-2165-4278-9f82-fa1459d439ae">

#### 4. Search for `Google Drive API` and select `Google Drive API` from the `Marketplace` section of the results.
<img width="707" alt="Screenshot 2024-01-23 at 9 10 43 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/c931ead0-f002-4855-90a2-59ab52a3b8fe">

#### 5. Click `Enable` button on `Google Drive API` page to add it to your project.
<img width="640" alt="Screenshot 2024-01-23 at 9 10 55 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/39e93a04-2b0e-4ad8-80b9-ba0155177410">

#### 6. Search for `Service Accounts` and select `Service Accounts` under `Products & Pages` section of the results.
<img width="712" alt="Screenshot 2024-01-23 at 9 11 31 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/1cf6a5d1-2417-4435-8c27-a7d1f571e18b">

#### 7. On `Service Accounts` page, click `+ Create Service Account` button.
<img width="955" alt="Screenshot 2024-01-23 at 9 11 46 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/ba159a33-0886-42b1-b708-cc91c5cfede4">

#### 8. Fill out the `Service Account Details` form and click `Done`.
<img width="955" alt="Screenshot 2024-01-23 at 9 12 39 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/5d09afe4-19f8-46bf-ac99-696db85cc3ec">

#### 9. On the `Service Accounts` page, you should see your newly created service account. Click actions menu and select `Manage Keys` from the options.
<img width="1001" alt="Screenshot 2024-01-23 at 9 13 11 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/9262944d-93e4-4777-9d07-122aaeeca683">

#### 10. On the `Keys` tab, click `Add Key` and select `Create New Key`.
<img width="1001" alt="Screenshot 2024-01-23 at 9 13 27 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/540edd3e-5b8e-4a26-88f0-fe527248f3db">

#### 11. Select `JSON` as the key type and click `Create`.
<img width="567" alt="Screenshot 2024-01-23 at 9 13 38 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/c8d5d6a9-9933-4138-ae86-4b1c02a08a87">

#### 12. This will download the service account credentials in `json` format. You need to name it `keys.json` and save it in this path `~/.credentials/keys.json`

#### NOTE: The path `~/.credentials/keys.json` refers to a file located in a directory on a Unix-like system (like Linux or macOS). Here's a breakdown:

* `~ `: This is a shorthand for the home directory of the current user. For example, if the current user's username is john, this could translate to `/home/johnsmith` on Linux or `/Users/johnsmith` on macOS.

* `/.credentials/`: This is a hidden directory in the user's home directory. It's hidden because its name starts with a dot (.).

* `keys.json` : This is the name of the file.

So, `~/.credentials/keys.json` is the full path to the keys.json file located in the .credentials directory in the user's home directory. This would be equivalent to something like `/Users/john/.credentials/keys.json`

#### 13. Save the entire full path of your `keys.json` file as an environment variable in your system. If you are using a Unix-like operating system, you can do this by accessing your profile with the command `vim ~/.bash_profile` in your command line and saving the path to the environment variable like this:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/Users/johnsmith/.credentials/keys.json"
```

