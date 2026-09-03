import os

from app.src.book_sys import (
    Book,
    BooksDict,
    BooksHandler,
    BooksList,
    Shelf,
    ShelvesDict,
    ShelvesList,
)
from app.src.services import res_files
from app.utils import paths


class BooksService:
    def __init__(self, res_file: res_files.ResourcesFilesService):
        self.books_handler = BooksHandler()
        self.res_files_api = res_file

    def get_cover_path(self, object: Shelf | Book, return_default: bool = True) -> str:
        """
        Constructs and returns the path to the `object` (an `Shelf`/`Book` instance) cover file.

        Parameters
        ----------
        shelf (book_sys.Shelf|book_sys.Book): the shelf/book object
        return_default (bool=True): whether to return the default cover path if the constructed path does not exist
        """
        if isinstance(object, Book):
            excepted_path = (
                os.path.join(
                    self.res_files_api.get_res("data.user.books.covers"),
                    object.str_id(),
                )
                + ".png"
            )

        elif isinstance(object, Shelf):
            excepted_path = (
                os.path.join(
                    self.res_files_api.get_res("data.user.bookshelves.covers"),
                    object.str_id(),
                )
                + ".png"
            )

        else:
            raise TypeError(f"Could not get cover for object of type {type(object)}")

        if not os.path.exists(excepted_path):
            if return_default:
                return self.res_files_api.get_res("assets.defaults_covers.shelf")

            raise FileNotFoundError(
                f"No cover file found for Book/Shelf (ID={object.str_id()}) at '{excepted_path}' !"
            )

        return excepted_path

    def get_shelf_cover_path(
        self, shelf: Shelf, return_default: bool = True
    ) -> str | None:
        """
        Constructs and returns the path to the `shelf` cover file.

        Parameters
        ----------
        shelf (book_sys.Shelf): the shelf object
        return_default (bool=True): whether to return the default cover path if the constructed path does not exist
        """
        return self.get_cover_path(shelf, return_default)

    def get_book_cover_path(self, book: Book, return_default: bool = True):
        """
        Constructs and returns the path to the `book` cover file.

        Parameters
        ----------
        shelf (book_sys.Book): the book object
        return_default (bool=True): whether to return the default cover path if the constructed path does not exist
        """
        return self.get_cover_path(book, return_default)

    def delete_book(self, book: Book):
        self.books_handler.delete_book(book.id)
        book_cover_path = self.get_book_cover_path(book, return_default=True)
        self.res_files_api.delete(book_cover_path)

    def delete_book_with_id(self, book_id: str):
        """Permantely removes a book and all its informations"""
        book = self.books_handler.get_books(id=(book_id, True, True))
        return self.delete_book(book[0])
