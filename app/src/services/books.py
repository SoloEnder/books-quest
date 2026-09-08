import logging
import os

from app.src import book_sys
from app.src.services import res_files
from app.utils import paths


class BooksService:
    def __init__(self, res_file: res_files.ResourcesFilesService):
        self.books_handler = book_sys.BooksHandler()
        self.res_files_api = res_file
        self.logger = logging.getLogger(f"{__name__}-BooksService")

    def get_cover_path(
        self, object: book_sys.Shelf | book_sys.Book, return_default: bool = True
    ) -> str:
        """
        Constructs and returns the path to the `object` (an `Shelf`/`Book` instance) cover file.

        Parameters
        ----------
        shelf (book_sys.Shelf|book_sys.Book): the shelf/book object
        return_default (bool=True): whether to return the default cover path if the constructed path does not exist
        """
        if isinstance(object, book_sys.Book):
            excepted_path = (
                os.path.join(
                    self.res_files_api.get_res("data.user.books.covers"),
                    object.str_id(),
                )
                + ".png"
            )

        elif isinstance(object, book_sys.Shelf):
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
        self, shelf: book_sys.Shelf, return_default: bool = True
    ) -> str | None:
        """
        Constructs and returns the path to the `shelf` cover file.

        Parameters
        ----------
        shelf (book_sys.Shelf): the shelf object
        return_default (bool=True): whether to return the default cover path if the constructed path does not exist
        """
        return self.get_cover_path(shelf, return_default)

    def get_book_cover_path(self, book: book_sys.Book, return_default: bool = True):
        """
        Constructs and returns the path to the `book` cover file.

        Parameters
        ----------
        shelf (book_sys.Book): the book object
        return_default (bool=True): whether to return the default cover path if the constructed path does not exist
        """
        return self.get_cover_path(book, return_default)

    def delete_book(self, book: book_sys.Book):
        self.books_handler.delete_book(book.id)
        book_cover_path = self.get_book_cover_path(book, return_default=True)
        self.res_files_api.delete(book_cover_path)

    def delete_book_with_id(self, book_id: str):
        """Permantely removes a book and all its informations"""
        book = self.books_handler.get_books(id=(book_id, True, True))
        return self.delete_book(book[0])

    def delete_shelf(self, shelf: book_sys.Shelf, del_ref: bool = True):
        """
        Removes `shelf` from the shelves.

        Parameters
        ----------
        - shelf (Shelf): the shelf to remove
        - del_ref (bool): whether to delete the reference too.

        Raises
        ------
        - BooksShelfNotFoundError: if the shelf does not exists
        """
        self.books_handler.delete_shelf(shelf.id)
        # Delete cover path
        cover_path = self.get_shelf_cover_path(shelf, return_default=False)

        if cover_path:
            self.logger.debug(f"Deleting cover of shelf (ID={shelf.id}")
            self.res_files_api.delete(cover_path)

        if del_ref:
            del shelf

    def delete_shelf_with_id(self, shelf_id: str, del_ref: bool = True):
        """
        Removes the shelf that's ID is `shelf_id`

        Parameters
        ----------
        - shelf_id (str): the ID of the shelf
        - del_ref (bool): whether to delete the reference of the shelf

        Raises
        ------
        - BooksShelfNotFoundError: if no shelf with this ID exists
        """
        result = self.books_handler.get_shelfs(id=(True, True))

        if not result:
            raise book_sys.BooksShelfNotFoundError(shelf_id)

        return self.delete_shelf(result[0], del_ref)
