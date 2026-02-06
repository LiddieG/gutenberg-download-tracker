import time
import logging
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
from logger import setup_logger

setup_logger()

logging.info("Starting Gutenberg metadata fetch")

# Paths
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = RAW_DIR / "metadata.csv"

GUTENBERG_TOP_100_URL = "https://www.gutenberg.org/browse/scores/top"

def parse_book_id(book_url: str) -> str:
    """Extract the Gutenberg book ID from an ebook URL."""
    return book_url.rstrip("/").split("/")[-1]

def fetch_top_books():
    """Fetch the Top 100 EBooks yesterday and return a list of books."""
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
        book_id = parse_book_id(book_url)
        books.append({
            "title": title,
            "book_url": book_url,
            "book_id": book_id
        })
    return books

def fetch_book_metadata(book_url: str) -> dict:
    """Fetch metadata for a single Gutenberg book."""
    response = requests.get(book_url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

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

def main():
    books = fetch_top_books()
    all_metadata = []

    for idx, book in enumerate(books, start=1):
        logging.info(f"[{idx}/{len(books)}] Fetching metadata for: {book['title']}")
        try:
            metadata = fetch_book_metadata(book["book_url"])
            metadata["book_id"] = book["book_id"]
            metadata["book_url"] = book["book_url"]
            all_metadata.append(metadata)
        except Exception as e:
            logging.error(f"Failed to fetch {book['book_url']}: {e}")
        time.sleep(0.1)  # shorter sleep for testing

    df = pd.DataFrame(all_metadata)
    df.to_csv(OUTPUT_FILE, index=False)
    logging.info(f"Saved metadata to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
