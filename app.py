"""Search Open Library for books by title or author."""

import json
from pathlib import Path

import requests

API_URL = "https://openlibrary.org/search.json"
USER_AGENT = "ReadingListCLI/1.0 (student project)"
RESULT_LIMIT = 10
READING_LIST_FILE = Path("reading_list.json")


def load_reading_list(path=READING_LIST_FILE):
    """Load saved books, returning an empty list if no file exists yet."""
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_reading_list(books, path=READING_LIST_FILE):
    """Save reading-list books as formatted JSON."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(books, file, indent=2, ensure_ascii=False)


def book_identity(book):
    """Build a stable identity from a work key or title and authors."""
    if book.get("key"):
        return book["key"].casefold()

    title = " ".join(book.get("title", "").casefold().split())
    authors = ", ".join(book.get("author_name", [])).casefold()
    if title or authors:
        return f"{title}|{authors}"
    return None


def add_book(books, book):
    """Add a book once, storing only the fields needed by the app."""
    identity = book_identity(book)
    if identity and any(book_identity(saved) == identity for saved in books):
        print("That book is already in your reading list.")
        return False

    books.append(
        {
            "title": book.get("title", "Unknown title"),
            "author_name": book.get("author_name", []),
            "first_publish_year": book.get("first_publish_year"),
            "key": book.get("key"),
            "read": False,
        }
    )
    return True


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


def select_result(books):
    """Prompt for a result number and return that book, or None to cancel."""
    if not books:
        return None

    choice = input("Choose a book number to select, or 0 to cancel: ").strip()
    if not choice.isdigit():
        print("Please enter a number from the list, or 0 to cancel.")
        return None

    number = int(choice)
    if number == 0:
        return None
    if number > len(books):
        print("That number is not in the results.")
        return None
    return books[number - 1]


def search_flow(reading_list):
    """Search by title or author and add the selected book."""
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

    books = search_books(search_type, query)
    print_results(books)
    selected = select_result(books)
    if selected:
        title = selected.get("title", "Unknown title")
        if add_book(reading_list, selected):
            save_reading_list(reading_list)
            print(f"Added to your reading list: {title}")


def main():
    """Run the search menu until the user chooses to quit."""
    reading_list = load_reading_list()
    while True:
        print("\nReading List")
        print("1. Search for a book")
        print("2. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            search_flow(reading_list)
        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("Please choose 1 or 2.")


if __name__ == "__main__":
    main()
