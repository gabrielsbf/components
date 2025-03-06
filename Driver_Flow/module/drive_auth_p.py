# import the required libraries
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Define the self.SCOPES. If modifying it,
# delete the token.pickle file.
class Drive_Manager:
    def __init__(self, token_path, cred_path) -> None:
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.token_path = token_path
        self.cred_path = cred_path
        self.service = self.return_drive_service()

    def return_drive_service(self):
        # Variable creds will store the user access token.
        # If no valid token found, we will create one.
        creds = None

        # The file token.pickle stores the
        # user's access and refresh tokens. It is
        # created automatically when the authorization
        # flow completes for the first time.

        # Check if file token.pickle exists
        if os.path.exists(self.token_path):

            # Read the token from the file and
            # store it in the variable creds
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials are available,
        # request the user to log in.
        if not creds or not creds.valid:
            # If token is expired, it will be refreshed,
            # else, we will request a new one.
            if creds and creds.expired and creds.refresh_token:
                print("entering in refresh")
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.cred_path, self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the access token in token.pickle
            # file for future usage
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        # Connect to the API service
        service = build('drive', 'v3', credentials=creds)
        print("Servico Google Drive autenticado com sucesso!")
        return service
    # Create a function getFileList with
    # parameter N which is the length of
    # the list of files.
    def getFileList(self, N, driveId = "", query= "", fields="files(id, name)"):
        
        resource = self.service.files()
        result = resource.list(pageSize=N, fields=fields, q=query, driveId=driveId).execute()
        # return the result dictionary containing
        # the information about the files
        return result


    def create_drive_file(self, file_type, parent_folder_id, file_name):
        file= self.service.files().create(
            body={
                'mimeType': "application/vnd.google-apps." + file_type,
                "parents": [parent_folder_id],
                "name" : file_name
                },
            enforceSingleParent=False,
            keepRevisionForever=None,
            media_body=None,
            useContentAsIndexableText=None,
            supportsTeamDrives=True,
            ocrLanguage=None,
            ignoreDefaultVisibility=None,
            supportsAllDrives=True,
            media_mime_type=None
        ).execute()
        return file

    def duplicate_drive_file(self, file_id, parent_folder, file_name):
        file= self.service.files().copy(
            fileId=file_id,
            body={
                "parents": [parent_folder],
                "name" : file_name
                },
            supportsTeamDrives=True,
            ocrLanguage=None,
            supportsAllDrives=True,
        ).execute()
        return file