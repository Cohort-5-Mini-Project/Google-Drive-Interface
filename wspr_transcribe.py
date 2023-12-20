"""Take an audiofile and transcibe it to text using Whisper API."""
import glob
import json
import whisper
from tqdm import tqdm


def translate_audio(file_path, date, model):
    """Translate audio to text."""
    result = model.transcribe(file_path, language="en", fp16=False, verbose=True)
    print(file_path)
    print(result["text"])
    with open(
        f"./data/recordings/{date}/Text/{file_path.split('/')[-1].split('.')[0]}.json",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(json.dumps(result))


def transcribe(date, model_size="base"):
    """Transcribe audio to text.    
    Args:
        date (str): Date of the recordings to transcribe.
        model_size (str, optional): Size of the model to use, options "base, medium, large" Defaults to "base".

    """
    print(f"Transcribing {date}...")
    model = whisper.load_model(model_size)
    audio_files = glob.glob(f"./data/recordings/{date}/Audio/*.wav")
    print(f"Found {len(audio_files)} audio files.")
    for file in tqdm(audio_files):
        translate_audio(file, model=model, date=date)
