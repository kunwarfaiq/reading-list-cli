# Reading List

Reading List is a Python command-line app for finding books in the Open Library
catalogue and keeping track of books you want to read. Search by title or
author, add a result to your list, view saved books, mark them read or unread,
and remove them.

Searches use the Open Library Search API and require an internet connection.
Your personal list is stored locally in `reading_list.json` in the project
folder. The file is created the first time you add a book.

## Requirements

- Python 3.8 or newer
- Internet access for book searches

## Install

Open a terminal in the project folder and create a virtual environment:

```powershell
py -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux, activate it with:

```bash
source .venv/bin/activate
```

Install the project dependency:

```bash
python -m pip install -r requirements.txt
```

## Run

From the project folder, with the virtual environment activated:

```bash
python app.py
```

Choose **Search for a book** and then search by title or author. Select a
number to add a result, or enter `0` to cancel. The other menu options let you
view, update, and remove books from your saved list.

## Sample session

The following is real terminal output from a title search against Open Library:

```text
Reading List
1. Search for a book
2. View my reading list
3. Mark a book read or unread
4. Remove a book
5. Quit
Choose an option: 1
Search Open Library by:
1. Title
2. Author
Choose 1 or 2: 1
Enter a book title: The Hobbit
1. The Hobbit - J.R.R. Tolkien (1937)
2. The Hobbit - Charles Dixon, Sean Deming, J.R.R. Tolkien (1990)
3. The Hobbit & The Lord of the Rings [collection/set] - J.R.R. Tolkien (1979)
4. The Hobbit - Jude Fisher (2012)
5. J.R.R. Tolkien's The hobbit - Patsey Gray (1968)
6. The Hobbit companion - David Day (1997)
7. The Hobbit - Unknown author (1975)
8. The hobbit - Patty Kempshall (2012)
9. The Hobbit, an unexpected journey - Brian Sibley (2012)
10. The Hobbit : The Desolation of Smaug - Brian Sibley (2013)
Choose a book number to select, or 0 to cancel: 0

Reading List
1. Search for a book
2. View my reading list
3. Mark a book read or unread
4. Remove a book
5. Quit
Choose an option: 5
Goodbye!
```
