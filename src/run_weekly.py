from fetch_metadata import fetch_top_books
from pprint import pprint



def main():
    books = fetch_top_books()
    print(f"Weekly scrape complete. Collected {len(books)} books.\n")

    if books:
        print("First record:")
        pprint(books[0])


if __name__ == "__main__":
    main()

