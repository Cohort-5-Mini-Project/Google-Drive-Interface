from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import io
import argparse

from wspr_transcribe import transcribe

# Constants and Configuration
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'
DRIVE_ID = '0AMC2Evk8hvfdUk9PVA'
DATA_DIR = "./data/recordings"


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

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


def create_directory(path):
    """Create directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def download_files(service, date_prefix, file_type):
    """
    Download files from Google Drive with a specific prefix and type.
    """
    try:
        file_path = f"{DATA_DIR}/{date_prefix}/{file_type}/"
        create_directory(file_path)

        query = f"name contains '{date_prefix}'" if file_type == "Audio" else f"'export_{date_prefix[0:4]}-{date_prefix[4:6]}-{date_prefix[6:8]}'"
        results = service.files().list(q=query, corpora='drive', driveId=DRIVE_ID, 
                                       supportsAllDrives=True, includeItemsFromAllDrives=True,
                                       spaces='drive', fields='nextPageToken, files(id, name)').execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return

        for item in items:
            if item['name'].startswith('.'):
                continue

            print(f"{item['name']} ({item['id']})")
            request = service.files().get_media(fileId=item['id'])
            with io.FileIO(f'{file_path}{item["name"]}', 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}%.")
    except Exception as e:
        print(f"An error occurred: {e}")


def validate_date(input_date):
    """Validate and format date input."""
    try:
        month, day, year = input_date.split("/")
        month = int(month)
        day = int(day)
        year = int(year)
        return f"{year}{day}{month}"
    except ValueError:
        return None


def main():

    parser = argparse.ArgumentParser(description="Process and handle audio files.")
    parser.add_argument("--date", help="The date of the recordings in dd/mm/yyyy format", required=True)
    parser.add_argument("--download", help="Download files", action="store_true")
    parser.add_argument("--transcribe", help="Transcribe files", action="store_true")
    parser.add_argument("--upload", help="Upload files", action="store_true")
    parser.add_argument("--whispermodel", help="Version of whisper model to use", type=str)
    
    args = parser.parse_args()

    date_input = args.date
    date_prefix = validate_date(date_input)
    if not date_prefix:
        print("Invalid date format. Please enter the date in dd/mm/yyyy format.")
        return

    service = None
    if args.download or args.upload:
        service = authenticate_google_drive()

    # if args.download:
    #     download_files(service, date_prefix, "Audio")
    #     download_files(service, date_prefix, "Logs")
    #     print(f"Download completed for date: {date_prefix}")

    if args.transcribe:
        create_directory(f"{DATA_DIR}/{date_prefix}/Text")
        if args.whispermodel:
            transcribe(date_prefix, args.whispermodel)
        else:
            transcribe(date_prefix)

    if args.upload:
        # Implement upload functionality here
        pass

    print("Operation completed.")


if __name__ == "__main__":    
    main()
