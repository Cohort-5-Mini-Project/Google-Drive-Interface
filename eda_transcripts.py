from spellchecker import SpellChecker
import re
import pandas as pd
import os
import json

from google_drive_functions import (
    authenticate_google_drive,
    download_transcript_files,
)

service = authenticate_google_drive()
download_transcript_files(service)

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

DATA_DIR = config["data_dir"]
TRANSCRIPTS_DIR = os.path.join(DATA_DIR, "transcripts")

annotators = {}
for file in os.listdir(TRANSCRIPTS_DIR):
    if file.endswith(".jsonl"):
        annotator = file.split("_")[0]
        annotators[annotator] = annotators.get(annotator, 0) + 1
transcripts = []
annotators = []
for file in os.listdir(TRANSCRIPTS_DIR):
    if file.endswith(".jsonl"):
        annotator = file.split("_")[0]
        with open(os.path.join(TRANSCRIPTS_DIR, file), "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                an_lines = json.loads(line)
                text = an_lines["transcript"]
                transcripts.append(text)
                annotators.append(annotator)

spell = SpellChecker()
correct_numbers = [spell.correction(word) for word in ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen',
                                                       'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety', 'hundred']]


def check_misspelt_numbers(transcript):
    words = transcript.split()
    words = [re.sub(r'[^\w\s]', '', word) for word in words]
    for word in words:
        if word.lower() in correct_numbers:
            continue
        misspelled = spell.unknown([word])
        for mis in misspelled:
            if spell.correction(mis) in correct_numbers:
                return mis
    return False


df = pd.DataFrame({"transcript": transcripts, "annotator": annotators})
df["pounds_or_dollars"] = df["transcript"].str.count(
    r"\$|\£"
)
df["numbers"] = df["transcript"].str.count(r"\d")
df['contains_misspelt_number'] = df['transcript'].apply(
    check_misspelt_numbers)
df.to_csv(os.path.join(TRANSCRIPTS_DIR, "transcripts.csv"), index=False)
