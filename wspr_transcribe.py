"""Take an audiofile and transcibe it to text using Whisper API."""
import glob
import json
import wave

import whisper
from tqdm import tqdm

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


DATA_DIR = config["data_dir"]
PROMPT = config["audio_prompt"]


def translate_audio(file_path, date, model):
    """Translate audio to text."""
    result = model.transcribe(
        file_path, initial_prompt=PROMPT, language="en", fp16=False, verbose=True
    )
    print(file_path)

    with open(
        f"{DATA_DIR}/{date}/Text/transcribed_{file_path.split('/')[-1].split('.')[0]}.json",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(json.dumps(result))


def get_duration_wave(file_path):
    """Get duration of wave file."""
    with wave.open(file_path, "r") as audio_file:
        frame_rate = audio_file.getframerate()
        n_frames = audio_file.getnframes()
        return n_frames / float(frame_rate)


def transcribe_audio_whisper_local(date, model_size="base"):
    """Transcribe audio to text.
    Args:
        date (str): Date of the recordings to transcribe.
        model_size (str, optional): Size of the model to use, options "base, medium, large"
        Defaults to "base".

    """
    print(f"Transcribing {date}...")
    model = whisper.load_model(model_size)
    audio_files = glob.glob(f"{DATA_DIR}/{date}/Audio/*.wav")
    audio_files = [file for file in audio_files if "prechunked" not in file]
    print(f"Found {len(audio_files)} audio files.")
    for file in tqdm(audio_files):
        translate_audio(file, model=model, date=date)
