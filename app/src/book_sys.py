from __future__ import annotations

import logging
import os
import pathlib
import uuid

from app.src import resources_handler
from app.utils import json_file_manager as jfm
from app.utils import my_exceptions


class DefaultCoverPathDeletion(Exception):
    def __init__(self, path):
        self.path = path
        self.msg = "Deleting default book or shelf cover file is not allowed !"

    def __str__(self):
        return self.msg


class IsParentShelfError(Exception):
    def __init__(self, parent_id: uuid.UUID, child_id: uuid.UUID):
        """
        Excpetion usually raised when trying to add Shelf A as a child to Shelf B, while A is parent of B
        """
        super().__init__()
        self.parent_id = parent_id
        self.child_id = child_id
        self.msg = f"Couldn't define shelf A (ID={self.parent_id}) as child to shelf B (ID={self.child_id}) : Shelf A is parent of Shelf B !"

    def __str__(self):
        return self.msg


class IsChildShelfError(Exception):
    def __init__(self, shelf_id: uuid.UUID, parent_id: uuid.UUID):
        super().__init__()
        self.shelf_id = shelf_id
        self.parent_id = parent_id
        self.msg = f"Shelf (ID={self.shelf_id}) is already a child of shelf with ID={self.parent_id}"

    def __str__(self):
        return self.msg


class NotAChildShelfError(Exception):
    def __init__(self, shelf_id: uuid.UUID, parent_id: uuid.UUID):
        self.shelf_id = shelf_id
        self.parent_id = parent_id
        self.msg = (
            f"Shelf (ID={self.shelf_id} is not a child of Shelf {self.parent_id})"
        )

    def __str__(self):
        return self.msg


class InvalidUUIDError(Exception):
    """
    Exception usually raised when the format of a `Book` or `Shelf` UUID is not valid
    """

    def __init__(self, id):
        self.id = id
        self.msg = f"ID '{self.id}' is not a valid UUID !"
        super().__init__(self.msg)

    def __str__(self):
        return self.msg


class Shelf:
    def __init__(self, **kwargs):
        self.title = kwargs["title"]
        self.title_suffix = kwargs.get("title_suffix")
        self._parent_shelves: ShelvesList = kwargs.get("parents_shelves", [])
        self._children_shelves: ShelvesList = kwargs.get("children_shelves", [])
        self._books: BooksList = kwargs.get("books", [])
        self.cover_path = kwargs.get("cover_path")
        self.id = kwargs.get("id", uuid.uuid4())
        # -- Check if the ID is a valid UUID
        if not isinstance(self.id, uuid.UUID):
            raise InvalidUUIDError(self.id)
        for book in self._books:
            if not book.has_parent(self):
                book._parents_shelves.append(self)

        for shelf in self._parent_shelves:
            if not shelf.has_shelf(self):
                shelf._children_shelves.append(self)

        for shelf in self._children_shelves:
            if not shelf.has_parent_shelf(self):
                shelf._parent_shelves.append(self)

    def add_child_shelf(self, shelf: Shelf):
        """
        Define `shelf` as a child of this shelf

        Parameters
        ----------
        - shelf (Shelf): the shelf to define as child
        """
        if shelf not in self._parent_shelves:
            if self not in shelf._children_shelves:
                self._children_shelves.append(shelf)
                shelf._parent_shelves.append(self)

            else:
                raise IsChildShelfError(shelf.id, self.id)

        else:
            raise IsParentShelfError(shelf.id, self.id)

    def remove_child_shelf(self, shelf: Shelf):
        """
        Removes `shelf` from the child of this shelf

        Parameters
        ----------
        shelf: the child shelf to remove
        """
        if shelf in self._children_shelves:
            self._children_shelves.remove(shelf)
            shelf._parent_shelves.remove(self)

        else:
            raise NotAChildShelfError(shelf.id, self.id)

    def remove_from_parent(self):
        """
        Removes this shelf from all its parents
        """
        for parent_shelf in self._parent_shelves.copy():
            parent_shelf.remove_child_shelf(self)

    def has_shelf(self, shelf: Shelf) -> bool:
        "Checks if `shelf` is a child of this shelf. Returns a boolean value (yes (True)/no (False))"
        if shelf in self._children_shelves:
            return True

        else:
            return False

    def has_parent_shelf(self, parent: Shelf) -> bool:
        """
        Cheks if `parent` is a parent of this shelf
        """
        if parent in self._parent_shelves:
            return True

        else:
            return False

    def add_book(self, book: Book):
        """
        Defines 'book' as a book of this shelf
        """

        if book not in self._books:
            self._books.append(book)

        else:
            my_exceptions.BookExistsError(book.id, f"this Shelf ({self})")

    def remove_book(self, book: Book):
        """Removes 'book' from this shelf"""

        if book in self._books:
            self._books.remove(book)

        else:
            raise my_exceptions.BookNotFoundError(
                book.id,
                f"Book with (ID={book.id}) is not contained in Shelf (ID={self.id}) !",
            )

    def remove_all_books(self):
        """
        Remove that shelf from all its books
        """
        for book in self._books:
            book._parents_shelves.remove(self)

    def has_book(self, book: Book):
        """
        Return True if 'book' is in the '_books' attribute, otherwise return False
        """

        if book in self._books:
            return True

        else:
            return False

    def get_infos(self) -> dict:
        return {
            "title": self.title,
            "title_suffix": self.title_suffix,
            "id": self.id,
            "children_shelves": self._children_shelves,
            "parents_shelves": self._parent_shelves,
            "books": self._books,
            "cover_path": self.cover_path,
        }

    def str_id(self) -> str:
        return str(self.id)


class Book:
    def __init__(self, **kwargs):
        """
        The base class for the books
        """
        self.title = kwargs["title"]
        self.title_suffix = kwargs.get("title_suffix")
        self.authors = kwargs.get("authors")
        self.edition = kwargs.get("edition")
        self.summary = kwargs.get("summary")
        self.isbn = kwargs.get("isbn")
        self.cover_path = kwargs.get("cover_path")
        self.starting_read_date = kwargs.get("starting_read_date")
        self.end_read_date = kwargs.get("end_read_date")
        self.status = kwargs.get("status")
        self.tot_pages = kwargs.get("tot_pages", 1)
        self.alr_read_pages = kwargs.get("read_pages", 0)
        self.id = kwargs.get("id", uuid.uuid4())  # The id must be an UUID 4 !
        # -- Check if the ID is a valid UUID
        if not isinstance(self.id, uuid.UUID):
            raise InvalidUUIDError(self.id)

        self._parents_shelves: ShelvesList = kwargs.get("parents_shelves", [])

        for parent_shelf in self._parents_shelves:
            self.check_parent_shelf(parent_shelf)

    def get_infos(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "title_suffix": self.title_suffix,
            "authors": self.authors,
            "cover_path": self.cover_path,
            "edition": self.edition,
            "summary": self.summary,
            "isbn": self.isbn,
            "status": self.status,
            "starting_read_date": self.starting_read_date,
            "end_read_date": self.end_read_date,
            "tot_pages": self.tot_pages,
            "alr_read_pages": self.alr_read_pages,
            "parents_shelves": self._parents_shelves,
        }

    def check_parent_shelf(self, parent_shelf: Shelf):
        """
        Checks if this book is in 'parent_shelf'\n
        If this is not the case, add this book as a book of 'parent_shelf' and return False, otherwise, return False

        Args:
        - parent_shelf: a valid instance of Shelf
        """

        if parent_shelf.has_book(self):
            return True

        else:
            parent_shelf.add_book(self)
            return False

    def str_id(self):
        "Return a string representation of the `id` attribute"
        return str(self.id)

    def has_parent(self, parent_shelf: Shelf) -> bool:
        """
        Return True if 'parent_shelf' is in the '_parents_shelves' attribute, otherwise return False
        """

        if parent_shelf in self._parents_shelves:
            return True

        else:
            return False

    def delete_from_parents(self):
        """
        Remove this book from all his parents shelves
        """

        for parent_shelf in self._parents_shelves:
            parent_shelf.remove_book(self)


BooksList = list[Book]
BooksDict = dict[str, Book]

ShelvesList = list[Shelf]
ShelvesDict = dict[str, Shelf]
IDsList = list[str] | tuple[str, ...] | set[str]


class BooksHandler:
    def __init__(
        self,
        jfm: jfm.JsonFileManager,
        res_handler: resources_handler.RessourcesHandler,
        books: BooksDict | None = None,
        shelves: ShelvesDict | None = None,
    ):
        """
        Handle and manage books data
        """
        self.logger = logging.getLogger(__name__)
        self.books = books or {}
        self.res_handler = res_handler
        self.jfm = jfm
        self.shelves = shelves or {}
        self.default_shelf = Shelf(title="All", books=self.books.values())

    def delete_book(self, book_id: str):
        book_id = book_id

        if book_id in self.books.keys():
            self.logger.debug(f"Deleting book with ID '{book_id}'...")
            book_obj: Book = self.books[book_id]

            if book_obj.cover_path:
                self._delete_cover(book_obj.cover_path, True)
            book_obj.delete_from_parents()
            del self.books[str(book_obj.id)]

        else:
            raise my_exceptions.BookNotFoundError(book_id, f"BooksHandler ({self})")

    def _delete_cover(self, cover_path, check_default: bool = True):

        if check_default:
            if cover_path in (
                self.res_handler.get_res("assets.defaults_covers.book"),
                self.res_handler.get_res("assets.defaults_covers.shelf"),
            ):
                raise DefaultCoverPathDeletion(cover_path)

        if os.path.exists(cover_path):
            pathlib.Path(cover_path).unlink()

        else:
            raise FileNotFoundError(
                f"Counldn't delete cover at {cover_path} : File not found !"
            )

    def create_book(self, **kwargs) -> Book:
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
        """
        Add 'book_obj' to this BooksHandler and to the default shelf
        """

        if book_obj.str_id() not in self.books:
            self.books[book_obj.str_id()] = book_obj
            self.default_shelf.add_book(book_obj)

        else:
            raise my_exceptions.BookExistsError(
                book_obj.id, f"this BooksHandler ({self})"
            )

    def create_shelf(self, **kwargs) -> Shelf:
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

    def add_shelf(self, shelf: Shelf):
        """
        Add a book shelf

        book_shelf: an instance of a BookShelf object
        """

        if shelf.str_id() not in self.shelves.keys():
            self.shelves[shelf.str_id()] = shelf

        else:
            raise my_exceptions.BooksShelfExistsError(
                shelf.id, f"Shelf (ID={shelf.id}) arleady in BooksHandler ({self}) !"
            )

    def delete_shelf(self, id: str):
        self.logger.debug(f"Deleting shelf with ID : '{id}'...")

        if id in self.shelves.keys():
            shelf = self.shelves[id]

            if shelf.cover_path:
                self._delete_cover(shelf.cover_path)

            shelf.remove_all_books()
            del self.shelves[id]

        else:
            raise my_exceptions.BooksShelfNotFoundError(id)

    def edit_book(self, book_id: str, new_book: Book):
        self.logger.debug(f"Editing book with id {book_id}...")

        if book_id != new_book.id:
            raise ValueError(
                f"Couldn't assign new book to ID {book_id} : old book and new book haven't the same ID !"
            )

        else:
            new_book.title_suffix = self.books[new_book.str_id()].title_suffix
            self.books[new_book.str_id()] = new_book

    def edit_shelf(self, shelf_id: str, new_shelf: Shelf):

        if shelf_id in self.shelves.keys():
            new_shelf.id = uuid.UUID(shelf_id)
            new_shelf.title_suffix = self.shelves[shelf_id].title_suffix
            self.shelves[shelf_id] = new_shelf

        else:
            raise my_exceptions.BooksShelfNotFoundError(shelf_id)

    def get_books(self, **kwargs):
        """
        Get all the books which matches with filters
        Each argument must following this syntax : filter_name = (filter_value, full_match, case_sensitive)
        - filter_name: an attribute of the Book class
        - filter_value: the value to check
        - full_match (bool, optionnal): if True, then match is allowed only if filter_value full match, else match is allowed if filter_value partially match. default to True.
        - case_sensitive (bool, optionnal): if filter_value is a string and this parameter is set to True, then the match is case sensitive. default to False.
        """

        return self.get_obj(self.books.values(), **kwargs)

    def get_shelfs(self, **kwargs):
        """
        Get all the shelfs which matches with filters
        Each argument must following this syntax : filter_name = (filter_value, full_match, case_sensitive)
        - filter_name: an attribute of the Shelf class
        - filter_value: the value to check
        - full_match (bool, optionnal): if True, then match is allowed only if filter_value full match, else match is allowed if filter_value partially match. default to True.
        - case_sensitive (bool, optionnal): if filter_value is a string and this parameter is set to True, then the match is case sensitive. default to False.
        """
        return self.get_obj(self.shelves.values(), **kwargs)

    def get_obj(self, sequence, **kwargs):
        """
        Get all the objects in sequence which matches with filters
        Each argument must following this syntax : filter_name = (filter_value, full_match, case_sensitive)
        - filter_name: an attribute of the object class
        - filter_value: the value to check
        - full_match (bool, optionnal): if True, then match is allowed only if filter_value full match, else match is allowed if filter_value partially match. default to True.
        - case_sensitive (bool, optionnal): if filter_value is a string and this parameter is set to True, then the match is case sensitive. default to False.
        """

        def compare(value_a, value_b, full_match: bool):
            """
            Arguments:

            - value_a: the value to compare to value_b

            - value_b: the value against which value_b is compared

            - full_match: (Boolean): indicates whether a partial match is allowed
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

        for obj in sequence:
            filter_matchs = []

            for filter_name, filter_infos in filters.items():
                if hasattr(obj, filter_name):
                    filter_value = filter_infos[0]
                    full_match = filter_infos[1] if len(filter_infos) > 1 else True
                    case_sensitive = filter_infos[2] if len(filter_infos) > 2 else False

                    if type(getattr(obj, filter_name)) is type(filter_value):
                        if type(filter_value) is str and not case_sensitive:
                            filter_value = filter_value.lower()

                        if compare(
                            filter_value,
                            getattr(obj, filter_name)
                            if case_sensitive
                            else (
                                getattr(obj, filter_name).lower()
                                if type(filter_value) is str
                                else getattr(obj, filter_name)
                            ),
                            full_match,
                        ):
                            filter_matchs.append(True)

                        else:
                            filter_matchs.append(False)

                else:
                    raise AttributeError(
                        f"Couldn't perform comparison: Book/Shelf (id='{obj.id}') has no attribute '{filter_name}'."
                    )

            if len(filter_matchs) == len(filters):
                if all(filter_matchs):
                    books_matchs.append(obj)

        return books_matchs

    def save_books(self, filepath: str):
        self.logger.debug(f"Saving books data in {filepath}...")
        data = []

        for book in self.books.values():
            book_data = book.get_infos()
            # -- Converting book `id` into a string
            book_data["id"] = book.str_id()
            book_data["parents_shelves_ids"] = []

            for shelf in book_data["parents_shelves"]:
                if shelf != self.default_shelf:
                    book_data["parents_shelves_ids"].append(shelf.str_id())

            del book_data["parents_shelves"]
            data.append(book_data)

        self.jfm.write_json(filepath, data, catch_error=False)

    def load_books(self, filepath: str):
        self.logger.info(f"Loading books data from {filepath}...")

        data = self.jfm.read_json(filepath, catch_error=False)

        if data:
            for book_data in data:
                book_data["id"] = uuid.UUID(book_data["id"])
                self.new_book(**book_data)

    def save_shelfs(self, filepath: str):
        """
        Save the shelfs data in a file

        event: used if the function is called by the  handler. set it to None if you call this func manually
        filepath (str): the path of the file where the data will be saved
        """
        self.logger.debug(f"Saving shelves data in {filepath}")
        data = []

        for shelf in self.shelves.values():
            shelf_data = shelf.get_infos()
            shelf_data["id"] = str(shelf_data["id"])
            shelf_data["books_ids"] = []
            shelf_data["parents_shelves_ids"] = [
                shelf.str_id for shelf in shelf_data["parents_shelves"]
            ]
            del shelf_data["children_shelves"]
            del shelf_data["parents_shelves"]
            for book in shelf_data["books"]:
                shelf_data["books_ids"].append(book.str_id())

            del shelf_data["books"]

            data.append(shelf_data)

        self.jfm.write_json(filepath=filepath, data=data, catch_error=False)

    def load_shelves(self, filepath):
        """
        Create shelves from shelves data in 'filepath' and add them to this BooksHandler
        """
        self.logger.debug(f"Loading shelves data from  {filepath}...")

        data: list = self.jfm.read_json(filepath)

        if data:
            for shelf_data in data:
                books = list(
                    self.convert_books_ids(shelf_data.get("books_ids", [])).values()
                )
                parent_shelves = list(
                    self.get_shelves_with_id(
                        shelf_data.get("parents_shelves", []),
                    ).values()
                )
                shelf_data["books"] = books
                shelf_data["parents_shelves"] = parent_shelves
                shelf_data["id"] = uuid.UUID(shelf_data["id"])
                self.new_shelf(**shelf_data)

    def convert_books_ids(self, books_ids: list | tuple):
        """
        Convert a list of books ids to a dict of books object

        books_id (list/tuple): the list/tuple of the ids
        """

        books_objs = {}

        for book_id in books_ids:
            try:
                book_obj = self.books[book_id]

            except KeyError:
                raise my_exceptions.BookNotFoundError(book_id, f"BooksHandler ({self})")
            books_objs[book_id] = book_obj

        return books_objs

    def get_shelves_with_id(self, ids: IDsList) -> ShelvesDict:
        shelves = {}

        for id in ids:
            try:
                shelf = self.shelves[id]

            except KeyError:
                raise my_exceptions.BooksShelfNotFoundError(id)

            else:
                shelves[id] = shelf

        return shelves


class Session:
    def __init__(self, **kwargs):
        self.start_date = kwargs.get("start_date", None)
        self.end_date = kwargs.get("end_date", None)
        self.start_page = kwargs.get("start_date", 0)
        self.end_page = kwargs.get("end_page", 0)
        self.pages_read = self.end_page - self.start_page
