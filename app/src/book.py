
import json
import logging
import datetime as dt

from app.utils import paths
from app.utils import json_file_manager as jfm

class Book:

    def __init__(self, **kwargs):
        """
        The base class for the books
        """
        self.kwargs = kwargs
        self.logger = logging.getLogger(__name__)
        self.title = kwargs.get("title", "Unknown")
        self.authors = kwargs.get("authors", None)
        self.edition = edition = kwargs.get("edition", None)
        self.summary = kwargs.get("summary", None)
        self.isbn = kwargs.get("isbn", None)
        self.start_read_date = kwargs.get("start_read_date", None)
        self.end_read_date = kwargs.get("end_read_date", None)
        self.status = kwargs.get("status", None)
        self.internal_id = str(dt.datetime.timestamp(dt.datetime.now())).replace(".", "")


class BooksHandler:

    def __init__(self, books: dict|None=None):
        """
        Handle and manage books data
        """
        self.logger = logging.getLogger(__name__)
        self.books = books if books else {}
        self.history = []

    def add_books(self, title: str, **kwargs):
        book = Book(title=title, **kwargs)
        self.logger.info(f"Adding new book with id : {book.internal_id}...")
        self.books[book.internal_id] = book

    def get_book(self, **kwargs):
        title = kwargs.get("title", None)
        title = title.lower() if title else title
        author = kwargs.get("authors", None)
        author = author.lower() if author else author
        isbn = kwargs.get("isbn", None)

        title_correspondance = []
        author_correspondance = []
        isbn_correspondance = []

    def save_books(self, filepath: str):
        self.logger.info(f"Saving books data at {filepath}...")
        data = []

        for book in self.books.values():
            data.append({**book.kwargs})

        jfm.write_json(filepath, data)

    def load_books(self, filepath: str):
        self.logger.info(f"Loading books data from {filepath}...")

        data = jfm.read_json(filepath)

        if data:

            for book_data in data:
                book = Book(**book_data)
                self.books[book.internal_id] = book

class Session:

    def __init__(self, **kwargs):
        self.start_date = kwargs.get("start_date", None)
        self.end_date = kwargs.get("end_date", None)
        self.start_page = kwargs.get("start_date", 0)
        self.end_page = kwargs.get("end_page", 0)
        self.pages_read = self.end_page - self.start_page
