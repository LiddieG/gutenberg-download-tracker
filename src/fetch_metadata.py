from pathlib import Path
import pandas as pd

OUTPUT_PATH = Path("src/data/processed/metadata.csv")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


import logging
from logger import setup_logger

setup_logger()

logging.info("Fetching Gutenberg metadata")
logging.warning("No downloads found for this book")
logging.error("Request failed")


import requests
from bs4 import BeautifulSoup

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "gutenberg-download-tracker/1.0 (educational project)"
    })

    retries = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


GUTENBERG_TOP_100_URL = "https://www.gutenberg.org/browse/scores/top"

def parse_book_id(book_url: str) -> str:
    """
    Extract the Gutenberg book ID from an ebook URL.
    Example: https://www.gutenberg.org/ebooks/1342 -> 1342
    """
    return book_url.rstrip("/").split("/")[-1]


def fetch_top_books():
    """
    Fetch the Project Gutenberg Top 100 ebooks page
    and return structured data for the weekly top downloads.
    """
    session = create_session()
    response = session.get(GUTENBERG_TOP_100_URL, timeout=30)
    response.raise_for_status()
    

    soup = BeautifulSoup(response.text, "lxml")

    # Find the "Top 100 EBooks yesterday" section
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
    """
    Fetch metadata for a single Gutenberg book page.
    """
    session = create_session()
    response = session.get(book_url, timeout=30)
    response.raise_for_status()
    ...


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
    logging.info(f"Fetched {len(books)} books")

    all_metadata = []

    for book in books:
        try:
            metadata = fetch_book_metadata(book["book_url"])
            metadata["book_id"] = book["book_id"]
            metadata["book_url"] = book["book_url"]

            all_metadata.append(metadata)

        except Exception as e:
            logging.error(
                f"Failed to fetch metadata for {book['book_url']}: {e}"
            )

    df = pd.DataFrame(all_metadata)
    df.to_csv(OUTPUT_PATH, index=False)

    logging.info(f"Saved metadata to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
