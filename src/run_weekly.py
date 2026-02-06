from fetch_metadata import fetch_book_metadata, fetch_top_books
from pathlib import Path
from datetime import date
import shutil
import pandas as pd
from pprint import pprint
import logging
from logger import setup_logger

# Setup logger
setup_logger()

# Paths
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
HISTORY_DIR = DATA_DIR / "history"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

DOWNLOADS_FILE = PROCESSED_DIR / "downloads.csv"

def main():
    # Fetch top books
    books = fetch_top_books()
    first_book = books[0]

    print("Top book:")
    pprint(first_book)

    print("\nMetadata:")
    metadata = fetch_book_metadata(first_book["book_url"])
    pprint(metadata)

    # Copy downloads.csv to history if it exists
    today = date.today().isoformat()
    if DOWNLOADS_FILE.exists():
        dest_file = HISTORY_DIR / f"downloads_{today}.csv"
        shutil.copy(DOWNLOADS_FILE, dest_file)
        logging.info(f"Copied downloads.csv to {dest_file}")
    else:
        logging.warning(f"{DOWNLOADS_FILE} not found. Skipping history copy.")

if __name__ == "__main__":
    main()
