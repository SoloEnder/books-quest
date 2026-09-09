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

    def edit_book_with_id(
        self, book_id: str, title: str, replace_old_ref: bool = True, **books_data
    ):
        """
        Replaces the data of the Book that has `book_id` for id with the new `books_data`

        Parameters
        ----------
        - book_id (Book): the ID of the book to edit
        - title (str): the new title of the book
        - replace_original_ref (bool=True): wether to replace the reference of the old book (the one before the edition) by the new
        - **books_data: the new data of the book

        Raises
        ------
        BookNotFoundError: if no Book has this ID
        """
        book = self.books_handler.get_books(id=(book_id, True, True))

        if not book:
            raise book_sys.BookNotFoundError(book_id)

        return self.edit_book(book[0], title, replace_old_ref, **books_data)

    def edit_book(
        self,
        book: book_sys.Book,
        title: str,
        replace_old_ref: bool = True,
        **books_data,
    ):
        """
        Replaces the data of `Book` with the new `books_data`

        Parameters
        ----------
        - book (Book): the book to edit
        - title (str): the new title of the book
        - replace_original_ref (bool=True): wether to replace the reference of the old book (the one before the edition) by the new
        - **books_data: the new data of the book

        Raises
        ------
        BookNotFoundError: if this Book does not exists
        """
        book.delete_from_parents()  # Removes from all the parent to allow proper reset
        new_book = self.books_handler.create_book(title=title, **books_data)
        self.books_handler.edit_book(book.id, new_book)

        if replace_old_ref:
            book = new_book

    def get_cover_path(
        self,
        object: book_sys.Shelf | book_sys.Book,
        return_default: bool = True,
        raise_file_not_found: bool = False,
    ) -> str | None:
        """
        Constructs and returns the path to the `object` (an `Shelf`/`Book` instance) cover file.

        Parameters
        ----------
        - shelf (book_sys.Shelf|book_sys.Book): the shelf/book object
        - return_default (bool=True): whether to return the default cover path if the constructed path does not exists
        - raise_file_not_found (bool): whether to raise `FileNotFoundError` instead of returning `None` if the constructed path does not exists and `return_default=False`
        NOTE : `return_default` has always priority over `raise_file_not_found`
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

            if raise_file_not_found:
                raise FileNotFoundError(
                    f"No cover file found for Book/Shelf (ID={object.str_id()}) at '{excepted_path}' !"
                )

            return None

        return excepted_path

    def get_shelf_cover_path(
        self,
        shelf: book_sys.Shelf,
        return_default: bool = True,
        check_existence: bool = True,
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

    def delete_book(self, book: book_sys.Book, del_ref: bool = True):
        """
        Remove `book` and all its data

        Parameters
        ----------
        - book (Book) the book to delete
        - del_ref (bool=True): whether to delete the reference too

        Raises
        ------
        - BookNotFoundError: if the book does not exists
        """
        self.books_handler.delete_book(book.id)
        book_cover_path = self.get_book_cover_path(book, return_default=False)
        book_id = book.id

        if del_ref:
            del book

        if book_cover_path:
            self.logger.debug(f"Deleting cover of book (ID={book_id})...")
            self.res_files_api.delete(book_cover_path)
            return

        self.logger.warning(f"Could not find cover for book (ID={book_id})")

    def delete_book_with_id(self, book_id: str, del_ref: bool = False):
        """
        Remove book that's ID is `book_id` and all its data

        Parameters
        ----------
        - book_id (str): the ID of the book to delete
        - del_ref (bool=True): whether to delete the reference too

        Raises
        -------
        - BookNotFoundError: If the book does not exists
        """
        book = self.books_handler.get_books(id=(book_id, True, True))
        return self.delete_book(book[0], del_ref)

    def delete_shelf(self, shelf: book_sys.Shelf, del_ref: bool = True):
        """
        Removes `shelf` and all its data.

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

        shelf_id = shelf.id
        if del_ref:
            del shelf

        if cover_path:
            self.logger.debug(f"Deleting cover of shelf (ID={shelf_id}")
            self.res_files_api.delete(cover_path)
            return

        self.logger.warning(f"Could not find cover file for shelf (ID={shelf_id}")

    def delete_shelf_with_id(self, shelf_id: str, del_ref: bool = True):
        """
        Removes the shelf that's ID is `shelf_id` and all its data

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

    def load_books(self, custom_path: str | None = None):
        """
        Loads books data from a file.

        Parameters
        ----------
        - custom_path (str): the path of the file. If not given/equal to `None`, then the value in the files indexes is used
        """
        filepath = custom_path or self.res_files_api.get_res("data.user.books.books")
        self.books_handler.load_books(filepath)

    def load_shelves(self, custom_path: str | None = None):
        """
        Loads shelves data from a file.

        Parameters
        ----------
        - custom_path (str): the path of the file. If not given/equal to `None`, then the value in the files indexes is used
        """
        filepath = custom_path or self.res_files_api.get_res(
            "data.user.bookshelves.bookshelves"
        )
        self.books_handler.load_shelves(filepath)

    def save_books(self, custom_path: str | None = None):
        """
        Saves books data in a file.

        Parameters
        ----------
        - custom_path (str): the path of the file. If not given/equal to `None`, then the value in the files indexes is used
        """
        filepath = custom_path or self.res_files_api.get_res("data.user.books.books")
        self.books_handler.save_books(filepath)

    def save_shelves(self, custom_path: str | None = None):
        """
        Saves shelves data in a file.

        Parameters
        ----------
        - custom_path (str): the path of the file. If not given/equal to `None`, then the value in the files indexes is used
        """
        filepath = custom_path or self.res_files_api.get_res(
            "data.user.bookshelves.bookshelves"
        )
        self.books_handler.save_shelfs(filepath)
