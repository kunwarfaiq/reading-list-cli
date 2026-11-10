"""Search Open Library for books by title or author."""

import requests

API_URL = "https://openlibrary.org/search.json"
USER_AGENT = "ReadingListCLI/1.0 (student project)"
RESULT_LIMIT = 10


def search_books(search_type, query):
    """Return up to ten Open Library book records for a title or author query."""
    params = {
        search_type: query,
        "fields": "title,author_name,first_publish_year,key",
        "limit": RESULT_LIMIT,
    }
    response = requests.get(
        API_URL,
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=10,
    )
    response.raise_for_status()
    return response.json().get("docs", [])


def print_results(books):
    """Print book search results as a numbered list."""
    if not books:
        print("No books found.")
        return

    for number, book in enumerate(books, start=1):
        title = book.get("title", "Unknown title")
        authors = ", ".join(book.get("author_name", [])) or "Unknown author"
        year = book.get("first_publish_year", "Year unknown")
        print(f"{number}. {title} - {authors} ({year})")


def main():
    """Ask the user what to search for and display matching books."""
    print("Search Open Library by:")
    print("1. Title")
    print("2. Author")
    choice = input("Choose 1 or 2: ").strip()
    if choice not in {"1", "2"}:
        print("Please choose 1 for title or 2 for author.")
        return

    search_type = "title" if choice == "1" else "author"
    query = input(f"Enter a book {search_type}: ").strip()
    if not query:
        print("Search text cannot be empty.")
        return

    print_results(search_books(search_type, query))


if __name__ == "__main__":
    main()
