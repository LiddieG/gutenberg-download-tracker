from fetch_metadata import fetch_top_books


def main():
    books = fetch_top_books()
    print(f"Weekly scrape complete. Collected {len(books)} books.")


if __name__ == "__main__":
    main()
