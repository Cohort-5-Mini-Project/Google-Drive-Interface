""" 
This module provides functions for transcribing audio files using the LemonFox API.

Functions:
- get_files_to_transcribe(date_prefix): Get a list of audio files to transcribe.
- transcribe_audio(date_prefix, auth_token): Transcribe audio files using the LemonFox API.

Usage:
1. Set the configuration in the 'config.json' file.
2. Call the 'transcribe_audio' function with the desired date prefix and authentication token.
3. The function will transcribe the audio files and save the transcriptions as JSON files in the 
   'Text' directory.

Note: The 'config.json' file should contain the 'data_dir' key specifying the directory where the 
audio and text files are stored.
"""

import json
import os
import time

import requests

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

DATA_DIR = config["data_dir"]


def get_files_to_transcribe(date_prefix):
    """
    Get a list of files to transcribe.
    """
    audio_dir = os.path.join(DATA_DIR, date_prefix, "Audio")
    text_dir = os.path.join(DATA_DIR, date_prefix, "Text")

    files_to_transcribe = [
        os.path.join(audio_dir, file)
        for file in os.listdir(audio_dir)
        if file.endswith(".wav") and not file.startswith("prechunked")
    ]

    transcribed_files = {
        os.path.splitext(file)[0]
        for file in os.listdir(text_dir)
        if file.endswith(".json") and file.startswith("transcribed_api")
    }

    files_to_transcribe = [
        file
        for file in files_to_transcribe
        if os.path.splitext(os.path.basename(file))[0] not in transcribed_files
    ]

    return files_to_transcribe


def transcribe_audio(date_prefix, auth_token):
    """
    Transcribe audio files using the LemonFox API.

    Parameters
    ----------
    date_prefix : str
        The date prefix for the files to transcribe.
        auth_token : str
        The authentication token for the LemonFox API.
    """
    files_to_transcribe = get_files_to_transcribe(date_prefix)
    url = "https://api.lemonfox.ai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {auth_token}"}
    data = {"language": "english", "response_format": "verbose_json"}

    for file_path in files_to_transcribe:
        time.sleep(10)

        with open(file_path, "rb") as audio_file:
            files = {"file": audio_file}
            response = requests.post(
                url, headers=headers, files=files, data=data, timeout=600
            )
            if response.status_code == 200:
                print(f"Transcription completed for {file_path}")
                file_name = file_path.split("/")[-1].split(".")[0]
                with open(
                    f"./data/recordings/{date_prefix}/Text/transcribed_api_{file_name}.json",
                    "w",
                    encoding="utf-8",
                ) as file_obj:
                    file_obj.write(response.text)
            else:
                print(f"Transcription failed for {file_path}")
                print(response.text)
