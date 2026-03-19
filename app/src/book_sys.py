import datetime as dt
import logging

from app.utils import json_file_manager as jfm
from app.utils import my_exceptions


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
            str(dt.datetime.timestamp(dt.datetime.now())),
        )


class BooksHandler:
    def __init__(self, books: dict | None = None):
        """
        Handle and manage books data
        """
        self.logger = logging.getLogger(__name__)
        self.books = books if books else {}
        self.books_shelfs = {}
        self.shelfs_updated = False
        self.default_shelf = Shelf(name="All", books=self.books)

    def delete_book(self, book_id: str):
        book_id = book_id

        if book_id in self.books.keys():
            self.logger.debug(f"Deleting book with ID '{book_id}'...")
            del self.books[book_id]
            return True

        else:
            self.logger.warning(
                f"Couldn't delete book with ID '{book_id}' : book doesn't exists !"
            )
            return False

    def create_book(self, **kwargs):
        """
        Create a new instance of Book and return it
        """

        book = Book(**kwargs)
        return book

    def new_book(self, **kwargs):
        """Create and add an instance of Book" to the books handler"""
        book_obj = self.create_book(**kwargs)
        self.add_book(book_obj)

    def add_book(self, book_obj: Book):
        for shelf_id in book_obj.shelfs_ids:
            if shelf_id in self.books_shelfs.keys():
                if book_obj.internal_id not in self.books.keys():
                    shelf = self.books_shelfs[shelf_id]
                    shelf.add_book(book_obj)

            else:
                self.logger.warning(
                    f"Couldn't to add book to shelf with the ID {shelf_id} : Shelf doesn't exists !"
                )

        self.books[book_obj.internal_id] = book_obj
        self.shelfs_updated = True

    def create_shelf(self, **kwargs):
        """
        Create a Shelf object and return it
        """
        shelf = Shelf(**kwargs)
        return shelf

    def new_shelf(self, **kwargs):
        """
        Create a Shelf object and add it to the current handler
        """
        shelf = self.create_shelf(**kwargs)
        self.add_shelf(shelf)

    def edit_default_shelf(self, **kwargs):
        """
        Edit the attributes of the default shelf.
        """
        for arg_name, arg_value in kwargs.items():
            if hasattr(self.default_shelf, arg_name):
                setattr(self.default_shelf, arg_name, arg_value)

            else:
                self.logger.warning(
                    f"Couldn't set attribute {arg_name} of the default shelf: Unknown attribute !"
                )

    def add_shelf(self, book_shelf):
        """
        Add a book shelf

        book_shelf: an instance of a BookShelf object
        """
        self.logger.info(
            f"Adding shelf with ID '{book_shelf.id}' to books_handler '{self}'"
        )

        if book_shelf.id not in self.books_shelfs.keys():
            self.books_shelfs[book_shelf.id] = book_shelf

        else:
            self.logger.warning(
                f"Failed to add book shelf with ID : '{book_shelf.id}' to books_handler '{self}' : ID arleady exists !"
            )

    def remove_shelf(self, id: str):
        self.logger.debug(f"Removing book shelf with ID : '{id}'...")

        if id in self.books_shelfs.keys():
            del self.books_shelfs[id]

        else:
            self.logger.warning(
                f"Couldn't delete book shelf with ID '{id}' : Book shelf doesn't exists"
            )
            raise my_exceptions.BooksShelfNotFoundError(id)

    def edit_book(self, book_id: str, new_book: Book):
        self.logger.info(f"Editing book with id {book_id}...")

        if book_id != new_book.internal_id:
            raise my_exceptions.BookNotFoundError(book_id)

        else:
            self.books[book_id] = new_book

        for shelf_id in new_book.shelfs_ids:
            if shelf_id in self.books_shelfs.keys():
                self.books_shelfs[shelf_id] = new_book

            else:
                self.logger.warning(
                    f"Failed to add on editing book with id '{new_book.internal_id}' to shelf with ID '{shelf_id}' : Shelf doesn't exists !"
                )

    def edit_shelf(self, shelf_id: str, new_shelf):

        if shelf_id in self.books_shelfs.keys():
            new_shelf.id = shelf_id
            self.books_shelfs[shelf_id] = new_shelf

        else:
            raise my_exceptions.BooksShelfNotFoundError(shelf_id)

    def get_book(self, **kwargs):
        """
        Get all the books which matches with filters
        Each argument must following this syntax :
            <filter_name> = <(filter_value, full_match, case_sensitive)>
        - filter_name: an attribute of the Book class
        In the tuple:
            - filter_value: the value to check
            - full_match (bool, optionnal): if True, then match is allowed if filter_value partially match, else match is allowed only if filter_value full match. default to True.
            - case_sensitive (bool, optionnal): if filter_value is a string and this parameter is set to True, then the match is case sensitive. default to False.
        """

        def compare(value_a, value_b, full_match: bool):
            """
            Arguments:

            - value_a: the value to compare to value_b

            - value_b: the value against which value_b is compared

            - full_match: (Boolean): indicates whether a partial match is allowed

            Compare value_a to value_b.

            If complete_match is set to True:

            - True is returned if value_a is equal to value_b, otherwise False

            If complete_match is set to False:

            - True is returned if value_a is present in value_b, otherwise False
            """

            if full_match:
                if value_a == value_b:
                    return True

                else:
                    return False

            elif not full_match:
                if value_a in value_b:
                    return True

                else:
                    return False

        filters = {}
        books_matchs = []

        for filter_name, filter_infos in kwargs.items():
            if filter_infos:
                filters[filter_name] = filter_infos

        for book_obj in self.books.values():
            filter_matchs = []

            for filter_name, filter_infos in filters.items():
                if hasattr(book_obj, filter_name):
                    filter_value = filter_infos[0]
                    full_match = filter_infos[1] if len(filter_infos) > 1 else True
                    case_sensitive = filter_infos[2] if len(filter_infos) > 2 else False

                    if type(getattr(book_obj, filter_name)) is type(filter_value):
                        if type(filter_value) is str and not case_sensitive:
                            filter_value = filter_value.lower()

                        if compare(
                            filter_value,
                            getattr(book_obj, filter_name)
                            if case_sensitive
                            else (
                                getattr(book_obj, filter_name).lower()
                                if type(filter_value) is str
                                else getattr(book_obj, filter_name)
                            ),
                            full_match,
                        ):
                            filter_matchs.append(True)

                        else:
                            filter_matchs.append(False)

                else:
                    raise AttributeError(
                        f"Couldn't perform comparison: Book (id='{book_obj.internal_id}') has no attribute '{filter_name}'."
                    )

            if len(filter_matchs) == len(filters):
                if all(filter_matchs):
                    books_matchs.append(book_obj)

        return books_matchs

    def save_books(self, filepath: str):
        self.logger.info(f"Saving books data at {filepath}...")
        data = []

        for book in self.books.values():
            data.append(book.kwargs)

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
            data.append(shelf.kwargs)

        jfm.write_json(filepath=filepath, data=data)

    def load_shelfs(self, filepath):
        self.logger.info(f"Loading shelf data from  {filepath}...")

        data = jfm.read_json(filepath)

        if data:
            for shelf_data in data:
                books_ids = []

                for book_id in shelf_data.get("books_ids", []):
                    if book_id in self.books:
                        books_ids.append(book_id)

                    else:
                        self.logger.error(
                            f"Couldn't add book (ID: '{book_id}') to shelf (ID: '{shelf_data.get('internal_id')}') : Book doesn't exists !"
                        )

                self.new_shelf(**shelf_data)

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
        self.books_ids = kwargs.get("books_ids", [])
        self.cover_path = kwargs.get("cover_path")
        self.id = kwargs.get("id", str(dt.datetime.timestamp(dt.datetime.now())))

    def add_book(self, book: Book):

        if book.internal_id not in self.books_ids:
            self.books_ids.append(book.internal_id)

        else:
            self.logger.error(
                f"Book with ID {book.internal_id} arleady exists in the shelfID : {self.id})"
            )

    def remove_book(self, book_id: str) -> bool:
        """Remove book specified by <book_id> from this shelf"""
        self.logger.info(
            f"Removing book with ID : '{book_id}' from book shelf with ID : '{self.id}'..."
        )

        if book_id in self.books_ids:
            del self.books_ids[self.books_ids.index(book_id)]
            return True

        else:
            self.logger.warning(
                f"Couldn't remove book with ID '{book_id}' from shelf with ID '{self.id}' : Book not exists in the shelf !"
            )
            return False

    def has_book_with_id(self, id: str):
        if id in self.books_ids:
            return True

        else:
            return False
