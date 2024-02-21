"""
This script processes the transcripts from the recordings and checks for misspellings and other issues.
"""
import json
import os
import re
from datetime import datetime, timedelta

import pandas as pd
from spellchecker import SpellChecker

from google_drive_functions import authenticate_google_drive, download_transcript_files

# Constants
TRANSCRIPTS_FOLDER = "data/recordings/transcripts"
LAST_DOWNLOADED_FILE = os.path.join(TRANSCRIPTS_FOLDER, "last_downloaded.txt")
CONFIG_FILE = "config.json"

# Initialize SpellChecker
spell = SpellChecker()
correct_numbers = [
    spell.correction(word)
    for word in [
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
        "eleven",
        "twelve",
        "thirteen",
        "fourteen",
        "fifteen",
        "sixteen",
        "seventeen",
        "eighteen",
        "nineteen",
        "twenty",
        "thirty",
        "forty",
        "fifty",
        "sixty",
        "seventy",
        "eighty",
        "ninety",
        "hundred",
    ]
]
common_misspellings = [
    "shefburger",
    "bbq",
    "erm",
    "sec",
    "ive",
    "mmm",
    "fourty",
    "sixtyfive",
    "plantbased",# Function to check and return misspellings
    "cyeah",
    "syeah",
    "twentyeight",
    "ninethree",
    "seventyeight",
    "thatd",
    "ok",
    "okay",
    "sunday",
    "cyes",
    "ninetyeight",
    "realised",
    "ive",
    "thirtyeight",
    "eightyseven",
    "youll",
    "ive",
    "monday",
    "theyll",
    "shwippy",
    "shwippies",
    "flavour",
    "flavours",
    "fortyseven",
    "fiftyseven",
    "twentyseven",
    "fortyseven",
    "itll",
    "youve",
    "therell",
    "theyre",
    "youre",
    "im",
    "jesus",
    "theres",
    "weve",
    "youd",
    "thatll",
    "uhh",
    "cocacola",
    "im",
    "fanta",
    "oreo",
    "isnt",
    "thats",
    "dont",
    "cant",
    "wasnt",
    "wont",
    "havent",
    "hasnt",
    "didnt",
    "couldnt",
    "wouldnt",
    "shouldnt",
    "arent",
    "werent",
    "doesnt",
    "whats",
    "wheres",
    "whens",
    "whys",
    "whos",
    "hows",
    "whats",
    "wheres",
    "whens",
    "whys",
    "whos",
    "hows",
    "whats",
    "wheres",
    "whens",
    "whys",
    "whos",
    "hows",
    "whats",
    "wheres",
    "whens",
    "whys",
    "whos",
    "hows",
    "whats",
    "wheres",
    "whens",
    "whys",
    "whos",
    "hows",
    "whats",
    "wheres",
    "whens",
    "whys",
    "whos",
    "hows",
    "whats",
    "wheres",
    "whens",
    "whys",
    "whos",
    "hows",
    "whats",
    "wheres",
    "whens",
    "whys",
    "whos",
    "hows",
    "whats",
    "wheres",
    "whens",
    "whys",
    "whos",
    "hows",
    "whats",
    "wheres",
    "whens",
    "whys",
    "whos",
    "hows",
    "whats",
    "wheres",
    "whens",
    "whys",
    "whos",
    "hows",
]


def load_config(config_path=CONFIG_FILE):
    """Load the configuration file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_uk_misspellings(df, column_name):
    """Check for misspellings in the UK English language."""
    def find_misspellings(text):
        """Find misspelled words in the UK English language."""
        misspelled_words = spell.unknown(text.split())
        misspelled_words = [
            word for word in misspelled_words if word.lower() not in common_misspellings
        ]
        return ", ".join(misspelled_words) if misspelled_words else None

    df["potential_misspellings"] = df[column_name].apply(
        lambda x: find_misspellings(x) if pd.notnull(x) else None
    )

    return df


def download_latest_transcripts(force_download=False):
    """Download the latest transcripts from Google Drive."""
    if not os.path.exists(TRANSCRIPTS_FOLDER):
        print("No transcripts found. Downloading...")
        force_download = True
    else:
        try:
            with open(LAST_DOWNLOADED_FILE, "r") as f:
                last_downloaded = pd.to_datetime(f.read().strip())
            if datetime.utcnow() - last_downloaded > timedelta(days=1):
                print("Transcripts older than 24 hours. Downloading...")
                force_download = True
        except Exception:
            print("Error checking last download date. Downloading...")
            force_download = True

    if force_download:
        service = authenticate_google_drive()
        download_transcript_files(service)
        with open(LAST_DOWNLOADED_FILE, "w") as f:
            f.write(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))


def clean_and_tokenize(text):
    """Clean the text and tokenize it."""
    text = re.sub(r"[^\w\s]", "", text)
    return text.split()


def check_misspelt_numbers(transcript):
    """Check for misspelled numbers in the transcript."""
    words = clean_and_tokenize(transcript)
    for word in words:
        if word.lower() in correct_numbers:
            continue
        if spell.unknown([word]):
            corrected = spell.correction(word)
            if corrected in correct_numbers:
                return word
    return False


def process_transcripts(data_dir):
    """Process the transcripts and return a DataFrame."""
    transcripts_dir = os.path.join(data_dir, "transcripts")
    transcripts = []
    annotators = []
    for file in os.listdir(transcripts_dir):
        if file.endswith(".jsonl"):
            annotator = file.split("_")[0]
            with open(os.path.join(transcripts_dir, file), "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    transcripts.append(data["transcript"])
                    annotators.append(annotator)
    return pd.DataFrame({"transcript": transcripts, "annotator": annotators})


def main():
    """Main function to process the transcripts."""
    download_latest_transcripts()
    config = load_config()
    DATA_DIR = config["data_dir"]

    df = process_transcripts(DATA_DIR)
    print(f"Transcripts: {df.shape[0]}")
    print(f"Annotators: {df['annotator'].nunique()}")
    print("Finding misspellings...")
    df["pounds_or_dollars"] = df["transcript"].str.count(r"\$|\£")
    df["numbers"] = df["transcript"].str.count(r"\d")
    df["contains_misspelt_number"] = df["transcript"].apply(check_misspelt_numbers)

    df["clean_text"] = df["transcript"].str.replace(r"[^\w\s]", "", regex=True)

    # remove all single C: and C: at the beginning of the text
    df["clean_text"] = df["clean_text"].str.replace(r"C:", "", regex=True)
    df["clean_text"] = df["clean_text"].str.replace(r"^C:", "", regex=True)

    # remove all line breaks
    df["clean_text"] = df["clean_text"].str.replace(r"\n", " ", regex=True)

    df_checked = check_uk_misspellings(df, "clean_text")
    # drop the clean_text column for clairty of output
    df_checked = df_checked.drop(columns=["clean_text"])

    df_checked.to_csv(os.path.join(TRANSCRIPTS_FOLDER, "transcripts.csv"), index=False)
    print("misspellings checked and saved to transcripts.csv")

if __name__ == "__main__":
    main()
 