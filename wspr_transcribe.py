"""Take an audiofile and transcibe it to text using Whisper API."""
import glob
import json
import wave
import whisper
from tqdm import tqdm


def translate_audio(file_path, date, model):
    """Translate audio to text."""
    result = model.transcribe(file_path, language="en", fp16=False, verbose=True)
    print(file_path)
    print(result["text"])
    with open(
        f"./data/recordings/{date}/Text/transcribed_{file_path.split('/')[-1].split('.')[0]}.json",
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


def create_details_file(date, model_size="large-v3"):
    """Create a details file for the date."""
    audio_files = glob.glob(f"./data/recordings/{date}/Audio/*.wav")
    total_duration = sum(get_duration_wave(file) for file in audio_files)
    total_duration = round(total_duration, 2)
    details = {
        "date": date,
        "total_duration_seconds": total_duration,
        "total_duration_minutes": round(total_duration / 60, 2),
        "audio_files": glob.glob(f"./data/recordings/{date}/Audio/*.wav"),
        "text_files": glob.glob(f"./data/recordings/{date}/Text/*.json"),
        "whisper_model": model_size,
    }
    with open(
        f"./data/recordings/{date}/Text/details.json", "w", encoding="utf-8"
    ) as file:
        file.write(json.dumps(details))


def transcribe(date, model_size="base"):
    """Transcribe audio to text.
    Args:
        date (str): Date of the recordings to transcribe.
        model_size (str, optional): Size of the model to use, options "base, medium, large"
        Defaults to "base".

    """
    print(f"Transcribing {date}...")
    model = whisper.load_model(model_size)
    audio_files = glob.glob(f"./data/recordings/{date}/Audio/*.wav")
    audio_files = [
        file for file in audio_files if "prechunked" not in file
    ]
    print(f"Found {len(audio_files)} audio files.")
    for file in tqdm(audio_files):
        translate_audio(file, model=model, date=date)
    create_details_file(date, model_size=model_size)
