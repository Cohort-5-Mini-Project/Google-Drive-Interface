"""
This script handles the downloading, transcribing and uploading of audio files 
from google drive and using whisper model.

The script provides the following functionalities:
- Downloading audio files from Google Drive.
- Splitting audio files into chunks of 30 seconds.
- Transcribing audio files using the Whisper model or the Whisper API.
- Uploading transcribed text files to Google Drive.

The script requires a configuration file named "config.json" in the same directory,
which contains the API key and data directory path.

Usage:
    python main.py --date <date> [--download] [--transcribe] [--upload] [--whispermodel <model>] [--split <seconds>] [--api <api_key>]

Arguments:
    --date: The date of the recordings in dd/mm/yyyy format. (required)
    --download: Download audio files from Google Drive.
    --transcribe: Transcribe audio files.
    --upload: Upload transcribed text files to Google Drive.
    --whispermodel:> Version of the Whisper model to use for transcription.
    --split: Split audio files into chunks of specified seconds.
    --api: Use the Whisper API for transcription.

Example:
    python main.py --date 01/01/2022 --download --transcribe --upload --whispermodel large --split 30 --api <api_key>

Notes: whispermodel and split arguments are optional, if not specified, the script will use the default values.
Whispermodel cannot be changed when using the whisper API, it defaults to large-v3.
"""

import argparse
import math
import os
import sys
import wave
import json

from google_drive_functions import (
    authenticate_google_drive,
    create_directory,
    download_files,
    upload_files,
)
from whisper_api import transcribe_audio
from wspr_transcribe import get_duration_wave, transcribe

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

API_KEY = config["api_key"]
DATA_DIR = config["data_dir"]


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


def split_audio_into_chunks(audio_file, chunk_size=30, date_prefix=None):
    """Split audio file into chunks of 30 seconds."""
    with wave.open(audio_file, "rb") as audio:
        sample_rate = audio.getframerate()
        num_frames = audio.getnframes()
        chunk_duration = chunk_size * sample_rate
        num_chunks = math.ceil(num_frames / chunk_duration)
        chunk_files = []

        for i in range(num_chunks):
            start_frame = i * chunk_duration
            end_frame = min((i + 1) * chunk_duration, num_frames)

            chunk_file = f"{DATA_DIR}/{date_prefix}/Audio/{audio_file.split('/')[-1].split('.')[0]}_chunk_{i}.wav"
            with wave.open(chunk_file, "wb") as chunk:
                chunk.setparams(audio.getparams())

                chunk.setnframes(end_frame - start_frame)

                audio.setpos(start_frame)

                chunk.writeframes(audio.readframes(end_frame - start_frame))

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
    args, split, date_prefix, openai_api = parse_args()

    service = authenticate_google_drive() if args.download or args.upload else None

    if args.download:
        download_files(service, date_prefix, "Audio")
        download_files(service, date_prefix, "Logs")
        print(f"Download completed for date: {date_prefix}")
    delete_zero_byte_files(date_prefix)

    if split:
        for audio_file in os.listdir(f"{DATA_DIR}/{date_prefix}/Audio"):
            audio_length = get_duration_wave(
                f"{DATA_DIR}/{date_prefix}/Audio/{audio_file}"
            )
            if audio_length >= split:
                print(f"Splitting {audio_file} into chunks...")
                split_audio_into_chunks(
                    f"{DATA_DIR}/{date_prefix}/Audio/{audio_file}", split, date_prefix
                )
                os.rename(
                    f"{DATA_DIR}/{date_prefix}/Audio/{audio_file}",
                    f"{DATA_DIR}/{date_prefix}/Audio/prechunked_{audio_file}",
                )
    if args.transcribe:
        create_directory(f"{DATA_DIR}/{date_prefix}/Text")
        if args.api:
            transcribe_audio(date_prefix, openai_api)
        elif args.whispermodel:
            transcribe(date_prefix, args.whispermodel)
        else:
            transcribe(date_prefix)

    if args.upload:
        upload_files(service, date_prefix, "Text", model=args.whispermodel)

    print("Operation completed.")


def parse_args():
    """
    Parse command line arguments.

    Returns:
        args: command line arguments
        split: split audio files into chunks
        date_prefix: date in yyyymmdd format
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
    parser.add_argument(
        "--split",
        help="Usage --split 30, Split audio files into seconds, 30 or under required for whisper API",
    )
    parser.add_argument("--api", help="Use whisper API", type=str)
    args = parser.parse_args()

    date_input = args.date or None
    split = int(args.split) if args.split else None
    openai_api = args.api or None
    date_prefix = validate_date(date_input)
    if not date_prefix:
        print("Invalid date format. Please enter the date in dd/mm/yyyy format.")
        sys.exit()

    if openai_api and not split:
        print(
            "Split value is required to use whisper API as only 100mb or lower sized files are accepted."
        )
        sys.exit()

    if openai_api and args.whispermodel:
        print(
            "Whisper model cannot be changed when using the whisper API, it defaults to large-v3."
        )
        sys.exit()
    return args, split, date_prefix, openai_api


if __name__ == "__main__":
    main()
