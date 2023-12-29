""" 
This module provides functions for transcribing audio files using the LemonFox API.

The Lemonfox API is cheaper than using the Whisper API, and you can supply files
>100mb, however, I cannot seem to get the prompt working with it! 
I have emailed the owner of the API to see if its possible. 

It cannot also utilise "initial_prompt" parameter.

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
import random
import time

import requests

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

DATA_DIR = config["data_dir"]


def get_files_to_transcribe(date_prefix, api):
    """
    Get a list of files to transcribe.
    """
    audio_dir = os.path.join(DATA_DIR, date_prefix, "Audio")
    text_dir = os.path.join(DATA_DIR, date_prefix, "Text")

    files_to_transcribe = [
        os.path.join(audio_dir, file)
        for file in os.listdir(audio_dir)
        if file.endswith(".wav") and "chunk" in file
    ]

    transcribed_files = {
        os.path.splitext(file)[0]
        for file in os.listdir(text_dir)
        if file.endswith(".json") and file.startswith("transcribed_api")
    }

    transcribed_files = [s.replace("transcribed_api_", "") for s in transcribed_files]

    files_to_transcribe = [
        s for s in files_to_transcribe if all(sub not in s for sub in transcribed_files)
    ]

    if api == "lemonfox":
        prechunked_files = [
            os.path.join(audio_dir, file)
            for file in os.listdir(audio_dir)
            if file.endswith(".wav") and file.startswith("under_api_")
        ]

        files_to_transcribe.extend(prechunked_files)

    return files_to_transcribe


def exponential_backoff_decorator(max_retries, base_delay):
    """
    Decorator that adds retry functionality to a function.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.

    Raises:
        Exception: If the maximum number of retries is reached and the operation still fails.

    Examples:
        >>> @decorator
        ... def my_function():
        ...     # Function implementation
        ...
        >>> my_function()
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    result_func = func(*args, **kwargs)
                    return result_func
                except Exception as e:
                    print(f"Attempt {retries + 1} failed: {e}")
                    retries += 1
                    delay = base_delay * 2**retries + random.uniform(0, 1)
                    print(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
            raise Exception("Max retries reached, operation failed.")

        return wrapper

    return decorator


@exponential_backoff_decorator(max_retries=5, base_delay=1)
def send_request(url, headers, files, data):
    """
    Send a request to the Transcription API."""
    return requests.post(url, headers=headers, files=files, data=data, timeout=600)


def new_transcribe(date_prefix, api_type, auth_token):
    """
    Transcribes audio files using different APIs based on the specified API type.

    Args:
        date_prefix (str): The date prefix used to identify the files to transcribe.
        api_type (str): The type of API to use for transcription.
        auth_token (str): The authentication token for API authorization.

    Raises:
        ValueError: If the specified API type is not supported.

    Examples:
        >>> new_transcribe("2022-01-01", "lemonfox", "my_auth_token")
    """

    files_to_transcribe = get_files_to_transcribe(date_prefix, api_type)

    if api_type == "lemonfox":
        url = config["lemonfoxAPIURL"]
        data = {
            "language": "en",
            "initial_prompt": config["audio_prompt"],
            "response_format": "verbose_json",
        }
    elif api_type == "whisper":
        url = config["whisperAPIURL"]
        data = {
            "language": "en",
            "initial_prompt": config["audio_prompt"],
            "response_format": "verbose_json",
            "model": "whisper-1",
        }
    else:
        raise ValueError("Unsupported API type")

    headers = {"Authorization": f"Bearer {auth_token}"}

    for file_path in files_to_transcribe:
        with open(file_path, "rb") as audio_file:
            files = {"file": audio_file}
            try:
                response = send_request(url, headers, files, data)
            except Exception as e:
                print("Operation failed:", e)
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
