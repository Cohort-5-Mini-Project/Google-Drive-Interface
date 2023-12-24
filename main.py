"""
This script handles the downloading, transcribing and uploading of audio files 
from google drive and using whisper model
"""
import os
import io
import argparse
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from wspr_transcribe import transcribe, get_duration_wave
import wave
import math

# Constants and Configuration
SCOPES = ["https://www.googleapis.com/auth/drive"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"
DRIVE_ID = "0AMC2Evk8hvfdUk9PVA"
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

        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


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
        query = (
            f"name contains '{date_prefix}'"
            if file_type == "Audio"
            else f"name contains 'export_{date_prefix[:4]}-{date_prefix[4:6]}-{date_prefix[6:8]}'"
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
                driveid=drive_id,
                supportsAllDrives=True,
                fields="id",
            )
            .execute()
        )
        return folder.get("id")

    return folder[0].get("id")


def upload_files(service, date_prefix, file_type, drive_id):
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

    upload_path = f"{DATA_DIR}/{date_prefix}/{file_type}/"

    for file_name in os.listdir(upload_path):
        file_path = os.path.join(upload_path, file_name)
        if os.path.isfile(file_path):
            print(f"Uploading {file_name}...")
            file_metadata = {"name": file_name, "parents": [text_folder_id]}

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


def split_audio_into_chunks(audio_file, chunk_size=30):
    """Split audio file into chunks of 30 seconds."""
    # Open the audio file
    with wave.open(audio_file, 'rb') as audio:
        # Get the sample rate and number of frames
        sample_rate = audio.getframerate()
        num_frames = audio.getnframes()

        # Calculate the duration of each chunk in seconds
        chunk_duration = chunk_size * sample_rate

        # Calculate the total number of chunks
        num_chunks = math.ceil(num_frames / chunk_duration)

        # Create a list to store the chunk file names
        chunk_files = []

        # Split the audio into chunks
        for i in range(num_chunks):
            # Calculate the start and end frames of the chunk
            start_frame = i * chunk_duration
            end_frame = min((i + 1) * chunk_duration, num_frames)

            # Set the file name for the chunk
            chunk_file = f"{audio_file}_chunk_{i}.wav"

            # Create a new wave file for the chunk
            with wave.open(chunk_file, 'wb') as chunk:
                # Set the parameters for the chunk
                chunk.setparams(audio.getparams())

                # Set the number of frames for the chunk
                chunk.setnframes(end_frame - start_frame)

                # Set the position of the audio file to the start frame of the chunk
                audio.setpos(start_frame)

                # Read the frames from the audio file and write them to the chunk file
                chunk.writeframes(audio.readframes(end_frame - start_frame))

            # Add the chunk file name to the list
            chunk_files.append(chunk_file)

    return chunk_files

def delete_zero_byte_files(date_prefix):
    """Delete zero byte wav files."""
    for file in os.listdir(f"{DATA_DIR}/{date_prefix}/Audio"):
        if os.path.getsize(f"{DATA_DIR}/{date_prefix}/Audio/{file}") == 0:
            os.remove(f"{DATA_DIR}/{date_prefix}/Audio/{file}")

def main():
    """
    Main function to handle command line arguments and call other functions.
    """
    parser = argparse.ArgumentParser(description="Process and handle audio files.")
    parser.add_argument(
        "--date", help="The date of the recordings in dd/mm/yyyy format", required=True
    )
    parser.add_argument("--download", help="Download files", action="store_true")
    parser.add_argument("--transcribe", help="Transcribe files", action="store_true")
    parser.add_argument("--upload", help="Upload files", action="store_true")
    parser.add_argument(
        "--whispermodel", help="Version of whisper model to use", type=str
    )
    args = parser.parse_args()

    date_input = args.date
    date_prefix = validate_date(date_input)
    if not date_prefix:
        print("Invalid date format. Please enter the date in dd/mm/yyyy format.")
        sys.exit()

    service = authenticate_google_drive() if args.download or args.upload else None

    delete_zero_byte_files(date_prefix)

    for audio_file in os.listdir(f"{DATA_DIR}/{date_prefix}/Audio"):
        # check if the file is > 30 second
        # if yes, split it into chunks of 30 seconds
        # else, skip
        audio_length = get_duration_wave(f"{DATA_DIR}/{date_prefix}/Audio/{audio_file}")
        if audio_length <= 30:
            continue
        print(f"Splitting {audio_file} into chunks...")
        split_audio_into_chunks(f"{DATA_DIR}/{date_prefix}/Audio/{audio_file}")

    if args.download:
        download_files(service, date_prefix, "Audio")
        download_files(service, date_prefix, "Logs")
        print(f"Download completed for date: {date_prefix}")

    if args.transcribe:
        create_directory(f"{DATA_DIR}/{date_prefix}/Text")
        if args.whispermodel:
            transcribe(date_prefix, args.whispermodel)
        else:
            transcribe(date_prefix)

    if args.upload:
        upload_files(service, date_prefix, "Text", drive_id=DRIVE_ID)

    print("Operation completed.")


if __name__ == "__main__":
    main()
