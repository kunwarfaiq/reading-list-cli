"""Search Open Library for books by title or author."""

import json
from pathlib import Path

import requests

API_URL = "https://openlibrary.org/search.json"
USER_AGENT = "ReadingListCLI/1.0 (student project)"
RESULT_LIMIT = 10
READING_LIST_FILE = Path("reading_list.json")


def is_valid_book_record(book):
    """Check fields used by the app without rejecting optional API fields."""
    title = book.get("title", "Unknown title")
    authors = book.get("author_name", [])
    year = book.get("first_publish_year")
    key = book.get("key")
    return (
        isinstance(title, str)
        and isinstance(authors, list)
        and all(isinstance(author, str) for author in authors)
        and (year is None or isinstance(year, (int, str)))
        and (key is None or isinstance(key, str))
        and isinstance(book.get("read", False), bool)
    )


def load_reading_list(path=READING_LIST_FILE):
    """Load saved books, returning an empty list if no file exists yet."""
    try:
        with path.open(encoding="utf-8") as file:
            books = json.load(file)
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"{path} contains invalid JSON or text.") from error
    except OSError as error:
        raise OSError(f"Could not read {path}: {error}") from error

    if not isinstance(books, list):
        raise ValueError(f"{path} must contain a JSON list of books.")
    for number, book in enumerate(books, start=1):
        if not isinstance(book, dict):
            raise ValueError(f"Book entry {number} in {path} must be a JSON object.")
        if not is_valid_book_record(book):
            raise ValueError(f"Book entry {number} in {path} has invalid fields.")
    return books


def save_reading_list(books, path=READING_LIST_FILE):
    """Save reading-list books as formatted JSON, reporting file errors."""
    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(books, file, indent=2, ensure_ascii=False)
    except OSError as error:
        print(f"Could not save {path}: {error}")
        return False
    return True


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
    """Return up to ten books, or None after reporting an API error."""
    if search_type not in {"title", "author"}:
        print("Search type must be title or author.")
        return None

    params = {
        search_type: query,
        "fields": "title,author_name,first_publish_year,key",
        "limit": RESULT_LIMIT,
    }
    try:
        response = requests.get(
            API_URL,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        print("The search timed out. Check your connection and try again.")
        return None
    except requests.exceptions.ConnectionError:
        print("Could not connect to Open Library. Check your internet connection.")
        return None
    except requests.exceptions.HTTPError as error:
        print(f"Open Library returned an error: {error}")
        return None
    except ValueError:
        print("Open Library returned a response that was not valid JSON.")
        return None
    except requests.exceptions.RequestException as error:
        print(f"The search request failed: {error}")
        return None

    if not isinstance(data, dict) or not isinstance(data.get("docs"), list):
        print("Open Library returned an unexpected search response.")
        return None
    if any(
        not isinstance(book, dict) or not is_valid_book_record(book)
        for book in data["docs"]
    ):
        print("Open Library returned an invalid book record.")
        return None
    return data["docs"][:RESULT_LIMIT]


def print_results(books):
    """Print book search results as a numbered list."""
    if not books:
        print("No books found.")
        return

    for number, book in enumerate(books, start=1):
        title = book.get("title", "Unknown title")
        author_names = book.get("author_name", [])
        authors = (
            ", ".join(author_names)
            if isinstance(author_names, list)
            and all(isinstance(author, str) for author in author_names)
            else ""
        ) or "Unknown author"
        year = book.get("first_publish_year", "Year unknown")
        print(f"{number}. {title} - {authors} ({year})")


def print_reading_list(books):
    """Print saved books and whether each has been read."""
    if not books:
        print("Your reading list is empty.")
        return

    for number, book in enumerate(books, start=1):
        status = "Read" if book.get("read", False) else "Unread"
        title = book.get("title", "Unknown title")
        author_names = book.get("author_name", [])
        authors = (
            ", ".join(author_names)
            if isinstance(author_names, list)
            and all(isinstance(author, str) for author in author_names)
            else ""
        ) or "Unknown author"
        year = book.get("first_publish_year") or "Year unknown"
        print(f"{number}. {title} - {authors} ({year}) [{status}]")


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


def select_reading_list_book(books):
    """Prompt for a saved book number and return that book, or None."""
    if not books:
        print("Your reading list is empty.")
        return None

    print_reading_list(books)
    choice = input("Choose a book number, or 0 to cancel: ").strip()
    if not choice.isdigit():
        print("Please enter a number from the list, or 0 to cancel.")
        return None

    number = int(choice)
    if number == 0:
        return None
    if number > len(books):
        print("That number is not in your reading list.")
        return None
    return books[number - 1]


def update_read_status(books):
    """Mark a selected saved book as read or unread and persist the change."""
    book = select_reading_list_book(books)
    if book is None:
        return

    print("1. Mark as read")
    print("2. Mark as unread")
    choice = input("Choose an option: ").strip()
    if choice not in {"1", "2"}:
        print("Please choose 1 or 2.")
        return

    previous_status = book.get("read", False)
    book["read"] = choice == "1"
    if not save_reading_list(books):
        book["read"] = previous_status
        return
    status = "read" if book["read"] else "unread"
    print(f"Marked as {status}: {book.get('title', 'Unknown title')}")


def remove_book(books):
    """Remove a selected saved book and persist the change."""
    book = select_reading_list_book(books)
    if book is None:
        return

    index = books.index(book)
    books.pop(index)
    if not save_reading_list(books):
        books.insert(index, book)
        return
    print(f"Removed: {book.get('title', 'Unknown title')}")


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
    if books is None:
        return
    print_results(books)
    selected = select_result(books)
    if selected:
        title = selected.get("title", "Unknown title")
        if add_book(reading_list, selected):
            if save_reading_list(reading_list):
                print(f"Added to your reading list: {title}")
            else:
                reading_list.pop()


def main():
    """Run the search menu until the user chooses to quit."""
    try:
        reading_list = load_reading_list()
    except (OSError, ValueError) as error:
        print(f"Could not load your reading list: {error}")
        return
    while True:
        print("\nReading List")
        print("1. Search for a book")
        print("2. View my reading list")
        print("3. Mark a book read or unread")
        print("4. Remove a book")
        print("5. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            search_flow(reading_list)
        elif choice == "2":
            print_reading_list(reading_list)
        elif choice == "3":
            update_read_status(reading_list)
        elif choice == "4":
            remove_book(reading_list)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Please choose a number from 1 to 5.")


if __name__ == "__main__":
    main()
