import base64
import io
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account


class MyGDrive:
    def __init__(self, service_account_json_key):
        scope = ['https://www.googleapis.com/auth/drive']
        # service_account_json_key = 'service-account-key.json'
        credentials = service_account.Credentials.from_service_account_file(
                                      filename=service_account_json_key,
                                      scopes=scope)
        self.service = build('drive', 'v3', credentials=credentials)

    def get_files(self):
        results = (
                self.service.files()
                .list(pageSize=1000,
                      fields="nextPageToken, "
                      "files(id, name, mimeType, size, modifiedTime, parents)",
                      q='mimeType != "application/vnd.google-apps.folder"')
                .execute()
                )
        # get the results
        return results.get('files', [])

    def get_file_contents(self, fileId: str, encoded: bool = True):
        try:
            request_file = self.service.files().get_media(fileId=fileId)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request_file)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            file_retrieved = file.getvalue()
            if encoded:
                return base64.b64encode(file_retrieved).decode()
            else:
                return file_retrieved
        except HttpError as error:
            print(F'An error occurred: {error}')
