## Creating Service Account to access Google Drive API
### 1. Go to [Google Cloud Console](https://console.cloud.google.com) and create a new project.  
   You can search for "new project" in the search bar and click `Create A Project`.
<img width="709" alt="Screenshot 2024-01-23 at 9 09 43 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/9af57c5c-6903-4ec3-af7c-cefdaf23d808">

### 2. Fill the `Project Name`.
<img width="579" alt="Screenshot 2024-01-23 at 9 10 04 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/28c672cd-3aef-4176-ba3b-280baf3ffb05">

### 3. Once the project is created, ensure that you've selected the correct project.
<img width="400" alt="Screenshot 2024-01-23 at 9 26 13 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/b272d8bc-2165-4278-9f82-fa1459d439ae">

### 4. Search for `Google Drive API` and select `Google Drive API` from the `Marketplace` section of the results.
<img width="707" alt="Screenshot 2024-01-23 at 9 10 43 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/c931ead0-f002-4855-90a2-59ab52a3b8fe">

### 5. Click `Enable` button on `Google Drive API` page to add it to your project.
<img width="640" alt="Screenshot 2024-01-23 at 9 10 55 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/39e93a04-2b0e-4ad8-80b9-ba0155177410">

### 6. Search for `Service Accounts` and select `Service Accounts` under `Products & Pages` section of the results.
<img width="712" alt="Screenshot 2024-01-23 at 9 11 31 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/1cf6a5d1-2417-4435-8c27-a7d1f571e18b">

### 7. On `Service Accounts` page, click `+ Create Service Account` button.
<img width="955" alt="Screenshot 2024-01-23 at 9 11 46 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/ba159a33-0886-42b1-b708-cc91c5cfede4">

### 8. Fill out the `Service Account Details` form and click `Done`.
<img width="955" alt="Screenshot 2024-01-23 at 9 12 39 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/5d09afe4-19f8-46bf-ac99-696db85cc3ec">

### 9. On the `Service Accounts` page, you should see your newly created service account. Click actions menu and select `Manage Keys` from the options.
<img width="1001" alt="Screenshot 2024-01-23 at 9 13 11 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/9262944d-93e4-4777-9d07-122aaeeca683">

### 10. On the `Keys` tab, click `Add Key` and select `Create New Key`.
<img width="1001" alt="Screenshot 2024-01-23 at 9 13 27 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/540edd3e-5b8e-4a26-88f0-fe527248f3db">

### 11. Select `JSON` as the key type and click `Create`.
<img width="567" alt="Screenshot 2024-01-23 at 9 13 38 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/c8d5d6a9-9933-4138-ae86-4b1c02a08a87">

### 12. This will also download the service account credentials in `json` format. You will need this file later.

### 13. On the `Service Accounts` page, click the actions menu and select `Manage Details` from the options.
<img width="1001" alt="Screenshot 2024-01-23 at 9 13 11 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/892ccf54-f526-47c6-8d5a-daca47dc244f">

### 14. On the `Details` tab, copy the `email address` under the `Service Account Details` section. You will need to share your Google Drive folder with this email address in later steps.
<img width="644" alt="Screenshot 2024-01-23 at 9 15 15 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/a47e64b3-7f3e-4ee3-a180-b5c7c138ccb0">

## Associating Service Account with Google Drive
### 1. On your Google Drive, create a new folder.

### 2. Right click on the new folder, and create a Share.
<img width="686" alt="Screenshot 2024-01-23 at 9 42 09 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/2e4993bd-a83f-49ce-ae9f-0eb8dfd9a821">

### 3. In the `Create Share` settings, add the service account email address from step 14 above as `Viewer` and uncheck `Notify people`. 
<img width="532" alt="Screenshot 2024-01-23 at 9 14 57 PM" src="https://github.com/lalanikarim/austin_langchain/assets/1296705/fc0d707d-ef10-4cb8-a0ef-4f831758baf2">

## Your Google Service Account set up and Google Drive Share should now be complete.
