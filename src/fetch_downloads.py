import requests
import pandas as pd
import logging
from pathlib import Path
from logger import setup_logger
import time

# Setup logger
setup_logger()
logging.info("Starting Gutenberg download count fetch")

# Paths
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

METADATA_FILE = RAW_DIR / "metadata.csv"
OUTPUT_FILE = PROCESSED_DIR / "downloads.csv"

def fetch_download_count(book_id):
    """
    Fetch download count for a Gutenberg book ID from Gutendex API.
    """
    url = f"https://gutendex.com/books/{book_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("download_count", 0)
    except Exception as e:
        logging.warning(f"Failed to fetch downloads for book {book_id}: {e}")
        return 0

def main():
    if not METADATA_FILE.exists():
        raise FileNotFoundError(f"{METADATA_FILE} not found. Run fetch_metadata.py first.")

    df = pd.read_csv(METADATA_FILE)

    downloads = []

    for idx, row in df.iterrows():
        book_id = row["book_id"]
        title = row["title"]
        logging.info(f"[{idx+1}/{len(df)}] Fetching downloads for: {title} (ID: {book_id})")
        count = fetch_download_count(book_id)
        downloads.append({
            "book_id": book_id,
            "title": title,
            "downloads": count
        })
        time.sleep(0.1)  # prevent overloading API

    result_df = pd.DataFrame(downloads)

    # Fill missing downloads with 0 just in case
    result_df["downloads"] = result_df["downloads"].fillna(0)

    result_df.to_csv(OUTPUT_FILE, index=False)
    logging.info(f"Saved download data to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
