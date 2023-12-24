"""
This script handles the downloading, transcribing and uploading of audio files 
from google drive and using whisper model
"""
import os
import argparse
import sys
from google_drive_functions import authenticate_google_drive, create_directory, download_files, upload_files
from wspr_transcribe import transcribe, get_duration_wave
import wave
import math

# Constants and Configuration
SCOPES = ["https://www.googleapis.com/auth/drive"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"
DRIVE_ID = "0AMC2Evk8hvfdUk9PVA"
DATA_DIR = "./data/recordings"






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
    parser.add_argument("--split", help="Split audio files into seconds, 30 or under required for whisper API")
    args = parser.parse_args()

    date_input = args.date if args.date else None
    split = int(args.split) if args.split else None
    date_prefix = validate_date(date_input)
    if not date_prefix:
        print("Invalid date format. Please enter the date in dd/mm/yyyy format.")
        sys.exit()

    service = authenticate_google_drive() if args.download or args.upload else None

    if args.download:
        download_files(service, date_prefix, "Audio")
        download_files(service, date_prefix, "Logs")
        print(f"Download completed for date: {date_prefix}")
    delete_zero_byte_files(date_prefix)

    if split:
        for audio_file in os.listdir(f"{DATA_DIR}/{date_prefix}/Audio"):
            audio_length = get_duration_wave(f"{DATA_DIR}/{date_prefix}/Audio/{audio_file}")
            if audio_length <= split:
                continue
            else:
                print(f"Splitting {audio_file} into chunks...")
                split_audio_into_chunks(f"{DATA_DIR}/{date_prefix}/Audio/{audio_file}", split)
                # rename the original file
                os.rename(f"{DATA_DIR}/{date_prefix}/Audio/{audio_file}", f"{DATA_DIR}/{date_prefix}/Audio/prechunked_{audio_file}_original")
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
