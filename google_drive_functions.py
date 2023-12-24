import io
import os
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Constants and Configuration
SCOPES = ["https://www.googleapis.com/auth/drive"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"
DRIVE_ID = "0AMC2Evk8hvfdUk9PVA"
DATA_DIR = "./data/recordings"


def create_directory(path):
    """Create directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def find_or_create_folder(service, folder_name, parent_id=None, drive_id=None):
    """Find a folder by name or create it if it doesn't exist."""
    query = f'mimeType="application/vnd.google-apps.folder" and name="{folder_name}"'
    if parent_id:
        query += f' and "{parent_id}" in parents'

    response = (
        service.files()
        .list(
            q=query,
            spaces="drive",
            corpora="drive",
            driveId=drive_id,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
        )
        .execute()
    )
    folder = response.get("files")

    if not folder:
        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id] if parent_id else [],
        }
        folder = (
            service.files()
            .create(
                body=folder_metadata,
                # drive_id=drive_id,
                supportsAllDrives=True,
                fields="id",
            )
            .execute()
        )
        return folder.get("id")

    return folder[0].get("id")


def download_files(service, date_prefix, file_type):
    """
    Download files from Google Drive with a specific prefix and type.
    """
    try:
        file_path = f"{DATA_DIR}/{date_prefix}/{file_type}/"
        create_directory(file_path)
        query = (
            f"name contains '{date_prefix}' and not name contains 'chunk' and not name contains 'transcribed' and mimeType = 'audio/wav'"
            if file_type == "Audio"
            else f"name contains 'export_{date_prefix[:4]}-{date_prefix[4:6]}-{date_prefix[6:8]}' and mimeType = 'application/json'"
        )
        results = (
            service.files()
            .list(
                q=query,
                corpora="drive",
                driveId=DRIVE_ID,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                spaces="drive",
                fields="nextPageToken, files(id, name)",
            )
            .execute()
        )
        items = results.get("files", [])

        if not items:
            print("No files found.")
            return

        for item in items:
            if item["name"].startswith("."):
                continue

            print(f"{item['name']} ({item['id']})")
            request = service.files().get_media(fileId=item["id"])
            with io.FileIO(f'{file_path}{item["name"]}', "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}%.")
    except Exception as e:
        print(f"An error occurred: {e}")


def authenticate_google_drive():
    """
    Authenticate with Google Drive and return the service object.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def upload_files(service, date_prefix, file_type, drive_id=DRIVE_ID, model="base"):
    """Upload files to a specific path in Google Drive."""
    base_folder_id = find_or_create_folder(service, "Recording Prep", drive_id=drive_id)
    pilot_folder_id = find_or_create_folder(
        service, "Pilot recordings", parent_id=base_folder_id, drive_id=drive_id
    )
    session_folder_id = find_or_create_folder(
        service, "Recording Sessions", parent_id=pilot_folder_id, drive_id=drive_id
    )
    date_folder_id = find_or_create_folder(
        service,
        f"{date_prefix[6:8]}_{date_prefix[4:6]}_{date_prefix[:4]}",
        parent_id=session_folder_id,
        drive_id=drive_id,
    )
    text_folder_id = find_or_create_folder(
        service, "Text", parent_id=date_folder_id, drive_id=drive_id
    )
    run_folder_id = find_or_create_folder(
        service, f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{model}", parent_id=text_folder_id, drive_id=drive_id)
 
    upload_path = f"{DATA_DIR}/{date_prefix}/{file_type}/"

    for file_name in os.listdir(upload_path):
        file_path = os.path.join(upload_path, file_name)
        if os.path.isfile(file_path):
            print(f"Uploading {file_name}...")
            file_metadata = {"name": file_name, "parents": [run_folder_id]}

            media = MediaFileUpload(file_path, mimetype="text/plain")
            file = (
                service.files()
                .create(
                    body=file_metadata,
                    supportsAllDrives=True,
                    media_body=media,
                    fields="id",
                )
                .execute()
            )
            print(f"Uploaded file with ID: {file.get('id')}")
