
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
        self.events_handler.add_listener("System.Books.ShelfCreationRequest", self.create_book_shelf)
        self.events_handler.add_listener("System.Books.BookDeletionRequest", self.delete_book)
        self.events_handler.add_listener("System.Books.BookCreationRequest", self.add_book)
        self.events_handler.add_listener("System.Books.BookEditionRequest", self.edit_book)
        self.events_handler.add_listener("System.Books.SaveShelfsData", self.save_shelfs)
        self.events_handler.add_listener("System.Books.LoadShelfsData", self.load_shelfs)
        self.events_handler.add_listener("System.Books.CreateBaseShelf", self.create_base_shelf)
        self.books = books if books else {}
        self.books_shelfs = {}
        self.history = []

    def delete_book(self, event, book_id: str):
        book_id = book_id

        if book_id in self.books.keys():
            self.logger.info(f"Deleting book with id '{book_id}'")
            del self.books[book_id]

        else:
             self.logger.error(f"Unknown book id : {book_id}")

    def create_book_shelf(self, event, shelf_name: str, shelf_books: dict, shelf_id: str):
        """
        Create a book shelf

        name (str): the name for the book shelf
        books (dict): the books handled by the book shelf
        """
        self.logger.info(f"Creating book shelf '{shelf_name}'...")
        books_shelf = BooksShelf(name=shelf_name, books=shelf_books, id=shelf_id)
        self.add_book_shelf(books_shelf)
        self.events_handler.raise_event("System.Books.ShelfCreated")
        self.events_handler.raise_event("System.Ui.ShelfFrameCreationRequest", shelf=books_shelf)

    def add_book_shelf(self, book_shelf):
        """
        Add a book shelf

        book_shelf: an instance of a BookShelf object
        """

        if not book_shelf.name in self.books_shelfs.keys():
            self.logger.info(f"Adding book shelf '{book_shelf.name}'...")
            self.books_shelfs[book_shelf.id] = book_shelf

        else:
            self.logger.error(f"A book shelf with name '{book_shelf.name} arleady exists !'")

    def remove_book_shelf(self, name: str):
        self.logger.info(f"Removing book shelf '{name}'")

        if name in self.books_shelfs.keys():
            del self.books_shelfs[name]

        else:
            self.logger.error(f"Unknown book shelf : {name}")

    def add_book(self, event, **kwargs):
        book_obj = Book(**kwargs)
        self.logger.info(f"Adding new book with id : {book_obj.internal_id}...")
        self.books[book_obj.internal_id] = book_obj
        book_obj.kwargs["books_shelfs"] = {}

        for shelf_id in book_obj.books_shelfs:
            shelf_obj = self.get_shelf(event=None, id=shelf_id)[0]
            shelf_obj.add_book(book_obj)
            self.events_handler.raise_event("System.Books.ShelfUpdated", shelf=shelf_obj)

        return book_obj
    
    def edit_book(self, event, book_id: str, new_book: Book):
        self.logger.info(f"Editing book with id {book_id}...")
        self.books[book_id] = new_book

    
    def create_base_shelf(self, event):
        all_books_shelf_books = {}

        for book_id, book_obj in self.books.items():
            all_books_shelf_books[book_id] = book_obj

        self.create_book_shelf(event=None, shelf_name="Tout les livres", shelf_books=all_books_shelf_books, shelf_id=str(dt.datetime.timestamp(dt.datetime.now())).replace(".", ""))

    def get_book(self, **kwargs):
        """
        Get all the books who matches with filters given as args and return them
        """
        title = kwargs.get("title", None)
        author = kwargs.get("authors", None)
        id = kwargs.get("internal_id", None) 
        filters = {}
        books_matchs = []

        for filter_name, filter in kwargs.items():

            if filter:
                filters[filter_name] = filter

        for book_obj in self.books.values():
            filter_matchs = []

            for filter_name, filter in filters.items():

                if book_obj.kwargs[filter_name].lower() == filter.lower():
                    filter_matchs.append(True)

                else:
                    filter_matchs.append(False)

            if all(filter_matchs):
                books_matchs.append(book_obj)

        return books_matchs
    
    def get_shelf(self, event, **kwargs):
        """
        Get all the books who matches with filters given as args and return them
        """
        name = kwargs.get("name", None)
        id = kwargs.get("id", None) 
        filters = {}
        books_matchs = []

        for filter_name, filter in kwargs.items():

            if filter:
                filters[filter_name] = filter

        for book_shelf in self.books_shelfs.values():
            filter_matchs = []

            for filter_name, filter in filters.items():

                if book_shelf.kwargs[filter_name].lower() == filter.lower():
                    filter_matchs.append(True)

                else:
                    filter_matchs.append(False)

            if all(filter_matchs):
                books_matchs.append(book_shelf)

        return books_matchs


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
                book_obj = Book(**book_data)
                self.books[book_obj.internal_id] = book_obj

    def save_shelfs(self, event, filepath: str):
        """
        Save the shelfs data in a file

        event: used if the function is called by the events handler. set it to None if you call this func manually
        filepath (str): the path of the file where the data will be saved
        """
        self.logger.info(f"Saving book shelf data at {filepath}")
        data = []

        for shelf in self.books_shelfs.values():

            if not shelf.name == "Tout les livres":
                data.append({"name":shelf.name, "id":shelf.id, "books_ids":list(shelf.books.keys())})

        jfm.write_json(filepath=filepath, data=data)

    def load_shelfs(self, event, filepath):
        self.logger.info(f"Loading shelf data from  {filepath}...")

        data = jfm.read_json(filepath)

        if data:

            for shelf_data in data:
                shelf_books = self.convert_book_id(event=None, books_ids=shelf_data["books_ids"])
                self.create_book_shelf(event=None, shelf_name=shelf_data["name"], shelf_books=shelf_books, shelf_id=shelf_data["id"])

    def convert_book_id(self, event, books_ids: list|tuple):
        """
        Convert a list of books ids to a dict of books object

        event: used if the function is called by the events handler. set it to None if you call this func manually
        books_id (list/tuple): the list/tuple of the ids
        """

        books_objs = {}

        for book_id in books_ids:
            book_obj = self.books[book_id]
            books_objs[book_id] = book_obj

        return books_objs

        
class Session:

    def __init__(self, **kwargs):
        self.start_date = kwargs.get("start_date", None)
        self.end_date = kwargs.get("end_date", None)
        self.start_page = kwargs.get("start_date", 0)
        self.end_page = kwargs.get("end_page", 0)
        self.pages_read = self.end_page - self.start_page

class BooksShelf:

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.logger = logging.getLogger(__name__)
        self.name = kwargs.get("name")
        self.books = kwargs.get("books", {})
        self.id = kwargs.get("id")

    def add_book(self, book: Book):
        self.logger.info(f"Adding book with id '{book.internal_id}' to book shelf '{self.name}'...")
        self.books[book.internal_id] = book

    def remove_book(self, book_id: str):
        self.logger.info(f"Removing book with id '{book_id}' from book shelf '{self.name}'...")

        if book_id in self.books.keys():
            del self.books[book_id]

        else:
            self.logger.error(f"Unknown book id : {book_id}")
            
