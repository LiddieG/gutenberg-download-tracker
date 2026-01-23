from fetch_metadata import fetch_book_metadata, fetch_top_books
from pprint import pprint



def main():
    books = fetch_top_books()
    first_book = books[0]

    print("Top book:")
    pprint(first_book)

    print("\nMetadata:")
    metadata = fetch_book_metadata(first_book["book_url"])
    pprint(metadata)

if __name__ == "__main__":
    main()

