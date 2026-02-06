import logging
from pathlib import Path
from datetime import date
from pprint import pprint
import shutil
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from logger import setup_logger

# ---------------------------
# Setup
# ---------------------------
setup_logger()
logging.info("Starting weekly runner")

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
HISTORY_DIR = DATA_DIR / "history"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

METADATA_FILE = RAW_DIR / "metadata.csv"
DOWNLOADS_FILE = PROCESSED_DIR / "downloads.csv"

GUTENBERG_TOP_100_URL = "https://www.gutenberg.org/browse/scores/top"

# ---------------------------
# Functions
# ---------------------------
def parse_book_id(book_url: str) -> str:
    return book_url.rstrip("/").split("/")[-1]

def fetch_top_books():
    response = requests.get(GUTENBERG_TOP_100_URL, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    header = soup.find("h2", string="Top 100 EBooks yesterday")
    if not header:
        raise ValueError("Top 100 section not found")

    book_list = header.find_next("ol")
    books = []
    for item in book_list.find_all("li"):
        link = item.find("a")
        if not link:
            continue
        title = link.text.strip()
        book_url = "https://www.gutenberg.org" + link["href"]
        books.append({
            "title": title,
            "book_url": book_url,
            "book_id": parse_book_id(book_url)
        })
    return books

def fetch_book_metadata(book_url: str) -> dict:
    try:
        response = requests.get(book_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
    except Exception as e:
        logging.error(f"Error fetching {book_url}: {e}")
        return {}

    metadata = {
        "title": None,
        "author": [],
        "language": None,
        "subjects": [],
        "bookshelves": []
    }

    table = soup.find("table", class_="bibrec")
    if not table:
        return metadata

    for row in table.find_all("tr"):
        header = row.find("th")
        value = row.find("td")
        if not header or not value:
            continue
        label = header.text.strip()
        text = value.text.strip()
        if label == "Title":
            metadata["title"] = text
        elif label == "Author":
            metadata["author"].append(text)
        elif label == "Language":
            metadata["language"] = text
        elif label == "Subject":
            metadata["subjects"].append(text)
        elif label == "Bookshelf":
            metadata["bookshelves"].append(text)
    return metadata

def save_metadata(books):
    all_metadata = []
    for book in books:
        metadata = fetch_book_metadata(book["book_url"])
        metadata["book_id"] = book["book_id"]
        metadata["book_url"] = book["book_url"]
        all_metadata.append(metadata)
        time.sleep(0.5)  # be gentle with Gutenberg

    df = pd.DataFrame(all_metadata)
    df.to_csv(METADATA_FILE, index=False)
    logging.info(f"Saved metadata to {METADATA_FILE}")
    return df

def fetch_download_count(book_id):
    url = f"https://gutendex.com/books/{book_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            logging.warning(f"Failed to fetch book {book_id}")
            return None
        return response.json().get("download_count")
    except Exception as e:
        logging.error(f"Error fetching downloads for {book_id}: {e}")
        return None

def save_downloads(df_metadata):
    downloads = []
    for _, row in df_metadata.iterrows():
        book_id = row["book_id"]
        title = row["title"]
        count = fetch_download_count(book_id)
        downloads.append({"book_id": book_id, "title": title, "downloads": count})
        time.sleep(0.3)  # gentle on API

    df_downloads = pd.DataFrame(downloads)
    df_downloads["downloads"] = df_downloads["downloads"].fillna(0)
    df_downloads.to_csv(DOWNLOADS_FILE, index=False)
    logging.info(f"Saved downloads to {DOWNLOADS_FILE}")
    return df_downloads

def save_history():
    today = date.today().isoformat()
    if DOWNLOADS_FILE.exists():
        dest_file = HISTORY_DIR / f"downloads_{today}.csv"
        shutil.copy(DOWNLOADS_FILE, dest_file)
        logging.info(f"Copied downloads.csv to {dest_file}")
    else:
        logging.warning(f"No downloads.csv to copy for history.")

# ---------------------------
# Main Runner
# ---------------------------
def main():
    books = fetch_top_books()
    df_metadata = save_metadata(books)
    df_downloads = save_downloads(df_metadata)
    save_history()

    # Optional: show top book
    pprint(books[0])
    pprint(df_metadata.iloc[0].to_dict())
    pprint(df_downloads.iloc[0].to_dict())

if __name__ == "__main__":
    main()
