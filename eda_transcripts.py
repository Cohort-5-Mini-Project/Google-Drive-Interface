from spellchecker import SpellChecker
import re
import pandas as pd
import os
import json

from google_drive_functions import (
    authenticate_google_drive,
    download_transcript_files,
)

# service = authenticate_google_drive()
# download_transcript_files(service)

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


def check_uk_misspellings(df, column_name):
    # Function to check and return misspellings
    def find_misspellings(text):
        misspelled_words = spell.unknown(text.split())
        # remove shefburger and fanta and oreo
        misspelled_words = [word for word in misspelled_words if word.lower() not in [
            "shefburger", "bbq", "erm", "sec", "ive", "mmm", "fourty", "sixtyfive", "plantbased", "cyeah", "okay", "sunday", "cyes", "ninetyeight", "realised", "ive", "thirtyeight", "eightyseven", "youll", "ive", "monday", "theyll", "shwippy", "shwippies", "flavour", "flavours", "fortyseven", "fiftyseven", "twentyseven", "fortyseven", "itll", "youve", "therell", "theyre", "youre", "im", "jesus", "theres", "weve", "youd", "thatll", "uhh", "cocacola", "im", "fanta", "oreo", "isnt", "thats", "dont", "cant", "wasnt", "wont", "havent", "hasnt", "didnt", "couldnt", "wouldnt", "shouldnt", "arent", "werent", "doesnt", "whats", "wheres", "whens", "whys", "whos", "hows", "whats", "wheres", "whens", "whys", "whos", "hows", "whats", "wheres", "whens", "whys", "whos", "hows", "whats", "wheres", "whens", "whys", "whos", "hows", "whats", "wheres", "whens", "whys", "whos", "hows", "whats", "wheres", "whens", "whys", "whos", "hows", "whats", "wheres", "whens", "whys", "whos", "hows", "whats", "wheres", "whens", "whys", "whos", "hows", "whats", "wheres", "whens", "whys", "whos", "hows", "whats", "wheres", "whens", "whys", "whos", "hows", "whats", "wheres", "whens", "whys", "whos", "hows"]]

        return ', '.join(misspelled_words) if misspelled_words else None

    # Apply the function to the specified column and store the results in a new column
    df['potential_misspellings'] = df[column_name].apply(
        lambda x: find_misspellings(x) if pd.notnull(x) else None)

    return df


df = pd.DataFrame({"transcript": transcripts, "annotator": annotators})
df["pounds_or_dollars"] = df["transcript"].str.count(
    r"\$|\£"
)
df["numbers"] = df["transcript"].str.count(r"\d")
df['contains_misspelt_number'] = df['transcript'].apply(
    check_misspelt_numbers)


df['clean_text'] = df['transcript'].str.replace(r'[^\w\s]', '', regex=True)

# remove all single C: and C: at the beginning of the text
df['clean_text'] = df['clean_text'].str.replace(
    r'C:', '', regex=True)
df['clean_text'] = df['clean_text'].str.replace(
    r'^C:', '', regex=True)

# remove all line breaks
df['clean_text'] = df['clean_text'].str.replace(
    r'\n', ' ', regex=True)


df_checked = check_uk_misspellings(df, 'clean_text')
# drop the clean_text column for clairty of output
df_checked = df_checked.drop(columns=['clean_text'])

df_checked.to_csv(os.path.join(
    TRANSCRIPTS_DIR, "transcripts.csv"), index=False)
