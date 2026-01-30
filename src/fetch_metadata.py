import logging
from logger import setup_logger

setup_logger()

logging.info("Fetching Gutenberg metadata")
logging.warning("No downloads found for this book")
logging.error("Request failed")


import requests
from bs4 import BeautifulSoup


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
    response = requests.get(GUTENBERG_TOP_100_URL, timeout=30)
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


if __name__ == "__main__":
    data = fetch_top_books()
    print(f"Fetched {len(data)} books")

def fetch_book_metadata(book_url: str) -> dict:
    """
    Fetch metadata for a single Gutenberg book page.
    """
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
