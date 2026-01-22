
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
        self.logger = logging.getLogger(__name__)
        self.kwargs = kwargs
        self.title = kwargs.get("title", "Unknown")
        self.authors = kwargs.get("authors", None)
        self.edition = kwargs.get("edition", None)
        self.summary = kwargs.get("summary", None)
        self.isbn = kwargs.get("isbn", None)
        self.start_read_date = kwargs.get("start_read_date", None)
        self.end_read_date = kwargs.get("end_read_date", None)
        self.status = kwargs.get("status", None)
        self.tot_pages = kwargs.get("tot_pages", 1)
        self.alr_read_pages = kwargs.get("read_pages", 0)
        self.books_shelfs = kwargs.get("books_shelfs", [])
        self.series = kwargs.get("series", None)
        self.internal_id = kwargs.get("internal_id", str(dt.datetime.timestamp(dt.datetime.now())).replace(".", ""))


class BooksHandler:

    def __init__(self, events_handler, books: dict|None=None):
        """
        Handle and manage books data
        """
        self.logger = logging.getLogger(__name__)
        self.events_handler = events_handler
        self.events_handler.create_event(name="BookDeletionRequest", book_id=None)
        self.events_handler.add_listener("BookDeletionRequest", self.delete_book)
        self.events_handler.create_event(
            name="BookCreationRequest", 
            title=None, 
            authors=None, 
            edition=None,
            isbn=None, 
            summary=None,
            start_read_date=None,
            end_read_date=None,
            status=None,tot_pages=None,
            alr_read_pages=None,
            books_shelfs=None,
            series=None,
            internal_id=None
            )
        self.events_handler.add_listener("BookCreationRequest", self.add_book)
        self.events_handler.create_event("BookEditionRequest", book_id=None, new_book=None)
        self.events_handler.add_listener("BookEditionRequest", self.edit_book)
        self.events_handler.create_event("BookShelfUpdated", book_shelf_name=None)
        self.books = books if books else {}
        self.books_shelfs = {}
        self.history = []

    def delete_book(self, event=None, book_id: str|None=None):

        if event:
            book_id = event.kwargs.get("book_id")

        if book_id in self.books.keys():
            self.logger.info(f"Deleting book with id '{book_id}'")
            del self.books[book_id]

        else:
            raise ValueError(f"Unknown book id : {book_id}")

    def create_book_shelf(self, name: str, books: dict):
        """
        Create a book shelf

        name (str): the name for the book shelf
        books (dict): the books handled by the book shelf
        """

        self.logger.info(f"Creating book shelf '{name}'...")
        books_shelf = BooksShelf(name, books)
        self.add_book_shelf(books_shelf)

    def add_book_shelf(self, book_shelf):
        """
        Add a book shelf

        book_shelf: an instance of a BookShelf object
        """

        if not book_shelf.name in self.books_shelfs.keys():
            self.logger.info(f"Adding book shelf '{book_shelf.name}'...")
            self.books_shelfs[book_shelf.name] = book_shelf

        else:
            self.logger.error(f"Book shelf with name '{book_shelf.name}'")
            raise ValueError("A book shelf with this name already exists !")

    def remove_book_shelf(self, name: str):
        self.logger.info(f"Removing book shelf '{name}'")

        if name in self.books_shelfs.keys():
            del self.books_shelfs[name]

        else:
            raise ValueError(f"Unknown book shelf : {name}")

    def add_book(self, event, **kwargs):
        book_obj = Book(**event.kwargs)
        self.logger.info(f"Adding new book with id : {book_obj.internal_id}...")
        self.books[book_obj.internal_id] = book_obj

        for book_shelf_name in book_obj.books_shelfs:
            book_shelf = self.books_shelfs[book_shelf_name]
            book_shelf.add_book(book_obj)
            self.events_handler.raise_event("BookShelfUpdated", book_shelf_name=book_shelf_name)

        return book_obj
    
    def edit_book(self, book_id: str, new_book: Book):
        self.logger.info(f"Editing book with id {book_id}...")
        self.books[book_id] = new_book

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

class BooksShelf:

    def __init__(self, name, books: dict|None=None):
        self.logger = logging.getLogger(__name__)
        self.name = name
        self.books = books if books else {}

    def add_book(self, book: Book):
        self.logger.info(f"Adding book with id '{book.internal_id}' to book shelf '{self.name}'...")
        self.books[book.internal_id] = book

    def remove_book(self, book_id: str):
        self.logger.info(f"Removing book with id '{book_id}' from book shelf '{self.name}'...")

        if book_id in self.books.keys():
            del self.books[book_id]

        else:
            self.logger.error(f"Unknown book id : {book_id}")
            raise ValueError(f"Unknown book id : {book_id}")
