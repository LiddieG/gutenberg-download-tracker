import requests
from bs4 import BeautifulSoup


GUTENBERG_TOP_100_URL = "https://www.gutenberg.org/browse/scores/top"


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

        books.append({
            "title": title,
            "book_url": book_url
        })

    return books


if __name__ == "__main__":
    data = fetch_top_books()
    print(f"Fetched {len(data)} books")
