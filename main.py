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
import json
import math
import os
import sys
import wave

from pydub import AudioSegment
from pydub.utils import make_chunks, mediainfo

from google_drive_functions import (
    authenticate_google_drive,
    create_directory,
    download_files,
    upload_files,
)
from transcribe_api import new_transcribe
from wspr_transcribe import transcribe_audio_whisper_local

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

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


def split_wav_by_size(file_path, target_size_mb, date_prefix):
    """
    Splits a WAV file into multiple parts, each with a size approximately equal to target_size_mb megabytes.

    :param file_path: Path to the input WAV file.
    :param target_size_mb: Desired maximum size of each split file in megabytes.
    :return: None
    """

    target_size_bytes = target_size_mb * 1024 * 1024

    with wave.open(file_path, "rb") as wav_file:
        frame_rate = wav_file.getframerate()
        n_channels = wav_file.getnchannels()
        sampwidth = wav_file.getsampwidth()
        duration_in_seconds = wav_file.getnframes() / float(wav_file.getframerate())
        bit_rate = int(mediainfo(file_path)["bits_per_sample"])

        print("sample_width=", sampwidth)
        print("channel_count=", n_channels)
        print("duration_in_sec=", duration_in_seconds)
        print("frame_rate=", frame_rate)
        print("bit_rate=", bit_rate)

        wav_file_size = (frame_rate * bit_rate * n_channels * duration_in_seconds) / 8
        print("wav_file_size = ", wav_file_size)

        print("")
        audio = AudioSegment.from_file(file_path, "wav")

        total_chunks = wav_file_size // target_size_bytes
        chunk_length_in_sec = math.ceil(
            (duration_in_seconds * target_size_bytes) / wav_file_size
        )
        chunk_length_ms = chunk_length_in_sec * 1000
        chunks = make_chunks(audio, chunk_length_ms)

        file_name = os.path.splitext(os.path.basename(file_path))[0]
        for i, chunk in enumerate(chunks):
            chunk_name = (
                f"{DATA_DIR}/{date_prefix}/Audio/{date_prefix}_chunk{i}_{file_name}.wav"
            )
            print("exporting", chunk_name)
            chunk.export(chunk_name, format="wav")
        print("Total chunks = ", total_chunks)


def delete_zero_byte_files(date_prefix):
    """Delete zero byte wav files."""
    for file in os.listdir(f"{DATA_DIR}/{date_prefix}/Audio"):
        if os.path.getsize(f"{DATA_DIR}/{date_prefix}/Audio/{file}") == 0:
            os.remove(f"{DATA_DIR}/{date_prefix}/Audio/{file}")


def main():
    """
    Main function to handle command line arguments and call other functions.
    """
    args, date_prefix, API_KEY = parse_args()

    service = authenticate_google_drive() if args.download or args.upload else None

    if args.download:
        download_files(service, date_prefix, "Audio")
        download_files(service, date_prefix, "Logs")
        print(f"Download completed for date: {date_prefix}")
    delete_zero_byte_files(date_prefix)

    create_directory(f"{DATA_DIR}/{date_prefix}/Text")
    if args.whisper:
        transcribe_audio_whisper_local(date_prefix)
    if args.whisperapi:
        chunk_for_api("whisper_api_file_size_limit", date_prefix)
        new_transcribe(date_prefix, "whisper", API_KEY)
    if args.lemonfoxapi:
        chunk_for_api("lemonfox_api_file_size_limit", date_prefix)
        new_transcribe(date_prefix, "lemonfox", API_KEY)

    if args.upload:
        upload_files(service, date_prefix, "Text", model=args.whispermodel)

    print("Operation completed.")


def chunk_for_api(config_param, date_prefix):
    file_limit = config[config_param]
    print(
        f"Splitting audio files into sizes of {file_limit}mb as per whisper API requirements."
    )
    chunk_files(date_prefix, file_limit)


def chunk_files(date_prefix, file_limit):
    for audio_file in os.listdir(f"{DATA_DIR}/{date_prefix}/Audio"):
        audio_length = (
            os.path.getsize(f"{DATA_DIR}/{date_prefix}/Audio/{audio_file}")
            / 1024
            / 1024
        )

        if audio_length > file_limit:
            print(f"Splitting {audio_file} into chunks...")
            split_wav_by_size(
                f"{DATA_DIR}/{date_prefix}/Audio/{audio_file}", file_limit, date_prefix
            )
        else:
            os.rename(
                f"{DATA_DIR}/{date_prefix}/Audio/{audio_file}",
                f"{DATA_DIR}/{date_prefix}/Audio/under_api_{audio_file}",
            )




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
    parser.add_argument(
        "--whisper", help="Transcribe files using local whisper", action="store_true"
    )
    parser.add_argument("--upload", help="Upload files", action="store_true")
    parser.add_argument(
        "--whispermodel", help="Version of whisper model to use", type=str
    )
    parser.add_argument(
        "--lemonfoxapi", help="Use LemonFox's whisper API", action="store_true"
    )
    parser.add_argument("--whisperapi", help="Use Whisper API", action="store_true")
    args = parser.parse_args()

    date_input = args.date or None
    date_prefix = validate_date(date_input)

    if not date_prefix:
        print("Invalid date format. Please enter the date in dd/mm/yyyy format.")
        sys.exit()
    if args.lemonfoxapi and args.whisperapi:
        print("Cannot use both Lemonfox and Whisper API.")
        sys.exit()
    if args.lemonfoxapi and args.whispermodel:
        print(
            "Whisper model cannot be changed when using the Lemonfox whisper API, it defaults to large-v3."
        )
        sys.exit()
    if args.whisper and args.whisperapi or args.lemonfoxapi and args.whisper:
        print("Cannot transcribe using both local whisper model and API.")
        sys.exit()

    if args.lemonfoxapi:
        API_KEY = config["lemonfox_api_key"]
    elif args.whisperapi:
        API_KEY = config["whisper_api_key"]
    return args, date_prefix, API_KEY


if __name__ == "__main__":
    main()
