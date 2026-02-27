import datetime as dt
import logging
import typing

from app.utils import json_file_manager as jfm


class Book:
    def __init__(self, **kwargs):
        """
        The base class for the books
        """
        self.logger = logging.getLogger(__name__)
        self.kwargs = kwargs
        self.title = kwargs.get("title")
        self.authors = kwargs.get("authors")
        self.edition = kwargs.get("edition")
        self.summary = kwargs.get("summary")
        self.isbn = kwargs.get("isbn")
        self.cover_img_path = kwargs.get("cover_img_path")
        self.starting_read_date = kwargs.get("starting_read_date")
        self.end_read_date = kwargs.get("end_read_date")
        self.status = kwargs.get("status")
        self.tot_pages = kwargs.get("tot_pages", 1)
        self.alr_read_pages = kwargs.get("read_pages", 0)
        self.shelfs_ids = kwargs.get("shelfs_ids", [])
        self.internal_id = kwargs.get(
            "internal_id",
            str(dt.datetime.timestamp(dt.datetime.now())).replace(".", ""),
        )


class BooksHandler:
    def __init__(self, books: dict | None = None):
        """
        Handle and manage books data
        """
        self.logger = logging.getLogger(__name__)
        self.books = books if books else {}
        self.books_shelfs = {}
        self.changes_on_shelfs = []
        self.shelfs_updated = False

    def delete_book(self, book_id: str):
        book_id = book_id

        if book_id in self.books.keys():
            self.logger.info(f"Deleting book with id '{book_id}'")
            del self.books[book_id]

        else:
            self.logger.error(f"Unknown book id : {book_id}")

    def create_book(self, **kwargs):
        """
        Create a new instance of Book and return it
        """

        book = Book(**kwargs)
        self.add_book(book)
        return book

    def add_book(self, book_obj):
        self.logger.info(f"Adding new book with id : {book_obj.internal_id}...")

        for shelf_id in book_obj.shelfs_ids:
            if shelf_id in self.books_shelfs.keys():
                shelf = self.books_shelfs[shelf_id]
                shelf.add_book(book_obj)

            else:
                self.logger.warning(
                    f"Shelf with id {shelf_id} not found ! Perhaps it has been deleted ?"
                )

        self.books[book_obj.internal_id] = book_obj
        self.shelfs_updated = True

    def create_shelf(self, **kwargs):
        """
        Create a book shelf
        """
        self.logger.info(f"Creating book shelf '{kwargs.get('name', 'Unknown')}'...")
        shelf = Shelf(
            name=kwargs.get("name"), books=kwargs.get("books"), id=kwargs.get("id")
        )
        self.add_shelf(shelf)

    def add_shelf(self, book_shelf):
        """
        Add a book shelf

        book_shelf: an instance of a BookShelf object
        """

        if book_shelf.id not in self.books_shelfs.keys():
            self.logger.info(f"Adding book shelf '{book_shelf.name}'")
            self.books_shelfs[book_shelf.id] = book_shelf

            if book_shelf.id in self.books_shelfs.keys():
                self.shelfs_updated = True

            else:
                self.logger.warning(
                    f"Book shelf with id {book_shelf.id} doesn't exists ! Perhaps it has been deleted ?"
                )

        else:
            self.logger.warning(
                f"A book shelf with the id {book_shelf.id} already exists"
            )

    def remove_shelf(self, name: str):
        self.logger.info(f"Removing book shelf '{name}'")

        if name in self.books_shelfs.keys():
            del self.books_shelfs[name]

        else:
            self.logger.error(f"Unknown book shelf : {name}")

    def edit_book(self, event, book_id: str, new_book: Book):
        self.logger.info(f"Editing book with id {book_id}...")
        self.books[book_id] = new_book

        for shelf_id in new_book.shelfs_ids:
            if shelf_id in self.books_shelfs.keys():
                self.action_on_shelf(shelf_id, action="edited")

            else:
                self.logger.warning(
                    f"Book shelf with id {shelf_id} doesn't exists ! Perhaps it has been deleted ?"
                )

    def get_book(self, **kwargs):
        """
        Get all the books who matches with filters given as args and return them
        """
        filters = {}
        books_matchs = []

        for filter_name, filter in kwargs.items():
            if filter:
                filters[filter_name] = filter

        for book_obj in self.books.values():
            filter_matchs = []

            for filter_name, filter in filters.items():
                if hasattr(book_obj, filter_name):
                    if getattr(book_obj, filter_name).lower() == filter.lower():
                        filter_matchs.append(True)

                    else:
                        filter_matchs.append(False)

                else:
                    self.logger.warning(
                        f"Book shelf object with id <{book_obj.internal_id}> has not attribute <{filter_name}> !"
                    )

            if all(filter_matchs):
                books_matchs.append(book_obj)

        return books_matchs

    def get_shelf(self, **kwargs):
        """
        Get all the books who matches with filters given as args and return them
        """
        filters = {}
        books_matchs = []

        for filter_name, filter in kwargs.items():
            if filter:
                filters[filter_name] = filter

        for book_shelf in self.books_shelfs.values():
            filter_matchs = []

            for filter_name, filter in filters.items():
                if hasattr(book_shelf, filter_name):
                    if getattr(book_shelf, filter_name).lower() == filter.lower():
                        filter_matchs.append(True)

                    else:
                        filter_matchs.append(False)

                else:
                    self.logger.warning(
                        f"Book shelf object with id <{book_shelf.id}> has not attribute <{filter_name}> !"
                    )

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

    def save_shelfs(self, filepath: str):
        """
        Save the shelfs data in a file

        event: used if the function is called by the  handler. set it to None if you call this func manually
        filepath (str): the path of the file where the data will be saved
        """
        self.logger.info(f"Saving book shelf data at {filepath}")
        data = []

        for shelf in self.books_shelfs.values():
            if not shelf.name == "Tout les livres":
                data.append(
                    {
                        "name": shelf.name,
                        "id": shelf.id,
                        "books_ids": list(shelf.books.keys()),
                    }
                )

        jfm.write_json(filepath=filepath, data=data)

    def load_shelfs(self, filepath):
        self.logger.info(f"Loading shelf data from  {filepath}...")

        data = jfm.read_json(filepath)

        if data:
            for shelf_data in data:
                shelf_books = {}

                for book_id in shelf_data["books_ids"]:
                    if book_id in self.books:
                        book_obj = self.books[book_id]
                        shelf_books[book_id] = book_obj

                    else:
                        self.logger.warning(f"Book with id {book_id} doesn't exists !")

                self.create_shelf(
                    name=shelf_data["name"],
                    books=shelf_books,
                    id=shelf_data["id"],
                )

    def convert_book_id(self, books_ids: list | tuple):
        """
        Convert a list of books ids to a dict of books object

        books_id (list/tuple): the list/tuple of the ids
        """

        books_objs = {}

        for book_id in books_ids:
            book_obj = self.books[book_id]
            books_objs[book_id] = book_obj

        return books_objs

    def action_on_shelf(
        self, shelf_id: int, action: typing.Literal["created", "edited", "deleted"]
    ):
        self.changes_on_shelfs.append({"shelf_id": shelf_id, "action": action})

    def remove_action_on_shelf(self, index):

        if 0 <= index < len(self.changes_on_shelfs):
            del self.changes_on_shelfs[index]


class Session:
    def __init__(self, **kwargs):
        self.start_date = kwargs.get("start_date", None)
        self.end_date = kwargs.get("end_date", None)
        self.start_page = kwargs.get("start_date", 0)
        self.end_page = kwargs.get("end_page", 0)
        self.pages_read = self.end_page - self.start_page


class Shelf:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.logger = logging.getLogger(__name__)
        self.name = kwargs.get("name")
        self.books = kwargs.get("books", {})
        self.id = kwargs.get("id")

        for book_obj in self.books.values():
            if self.id not in book_obj.shelfs_ids:
                book_obj.shelfs_ids.append(self.id)

    def add_book(self, book: Book):

        if book.internal_id not in self.books.keys():
            self.logger.info(
                f"Adding book with id '{book.internal_id}' to book shelf '{self.name}'..."
            )
            self.books[book.internal_id] = book
            book.shelfs_ids = self.id

    def remove_book(self, book_id: str):
        self.logger.info(
            f"Removing book with id '{book_id}' from book shelf '{self.name}'..."
        )

        if book_id in self.books.keys():
            del self.books[book_id]

        else:
            self.logger.error(f"Unknown book id : {book_id}")
