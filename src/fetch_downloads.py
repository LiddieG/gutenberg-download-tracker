import requests
import pandas as pd
import logging
from pathlib import Path

from logger import setup_logger

setup_logger()

logging.info("Fetching Gutenberg metadata")
logging.warning("No downloads found for this book")
logging.error("Request failed")

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
    Fetch download count for a Gutenberg book ID
    """
    url = f"https://gutendex.com/books/{book_id}"
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        logging.warning(f"Failed to fetch book {book_id}")
        return None

    data = response.json()
    return data.get("download_count")


def main():
    logging.info("Starting download count fetch")

    if not METADATA_FILE.exists():
        raise FileNotFoundError("metadata.csv not found. Run fetch_metadata.py first.")

    df = pd.read_csv(METADATA_FILE)

    downloads = []

    for _, row in df.iterrows():
        book_id = row["id"]
        title = row["title"]

        count = fetch_download_count(book_id)

        downloads.append({
            "id": book_id,
            "title": title,
            "downloads": count
        })

    result_df = pd.DataFrame(downloads)

    # Sanity checks
    assert result_df["downloads"].isnull().sum() == 0
    assert result_df["downloads"].min() >= 0

    result_df.to_csv(OUTPUT_FILE, index=False)
    logging.info(f"Saved download data to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

assert df["downloads"].min() >= 0
assert df["title"].isnull().sum() == 0
