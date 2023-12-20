"""Take an audiofile and transcibe it to text using Whisper API."""
import glob
import whisper
import json
from tqdm import tqdm


def translate_audio(file_path, date, model):
    """Translate audio to text."""
    result = model.transcribe(file_path, language="en", fp16=False, verbose=True)
    print(file_path)
    print(result["text"])
    with open(f"./data/recordings/{date}/Text/{file_path.split('/')[-1].split('.')[0]}.json", "w") as file:
        file.write(json.dumps(result))
    

def transcribe(date):
    """Transcribe audio to text."""
    print(f"Transcribing {date}...")
    model = whisper.load_model("base")
    # Get a list of all audio files in the directory
    audio_files = glob.glob(f"./data/recordings/{date}/Audio/*.wav")
    print(f"Found {len(audio_files)} audio files.")
    for file in tqdm(audio_files):
        translate_audio(file, model=model, date=date)


