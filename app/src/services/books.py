import logging
import os
import shutil
import typing

from PIL.Image import Image

from app.src import book_sys
from app.src.services import res_files
from app.utils import images_tools


class BooksService:
    def __init__(self, res_file: res_files.ResourcesFilesService):
        self.books_handler = book_sys.BooksHandler()
        self.res_files_api = res_file
        self.logger = logging.getLogger(f"{__name__}-BooksService")

    def set_cover_for(
        self,
        object_id: str,
        cover_path: str,
        parent_folder: str,
        cover_exists_ok: bool = False,
    ):
        """
        Copy the object cover, rename it withe it's ID and save it.

        Parameters
        ----------
        - object_id (str): the object ID (probably a Book or a Shelf)
        - cover_path (str): the source cover path.
        - parent_folder (str): the folder where to copy the cover file.
        - cover_exists_ok (bool=False): wether to check if a cover is already assigned to this ID in `parent_folder`

        Raises
        - FileExistsError: if `cover_exists_ok` is `True` and a cover is already assigned to this ID

        """

        # Constructs final cover path
        cover_dest_path = os.path.join(
            parent_folder,
            f"{object_id}.png",
        )

        if cover_exists_ok and os.path.exists(cover_dest_path):
            raise FileExistsError(
                f"A cover file for object (ID={object_id}) already exists !"
            )

        # Copying to destination
        shutil.copy(cover_path, cover_dest_path)

    def set_cover_for_book(
        self,
        book_id: str,
        cover_path: str | None = None,
        check_book_exists: bool = False,
        cover_exists_ok: bool = False,
    ):
        """
        Copy the book cover to the app internal covers folder

        Parameters
        ----------
        - book_id (str): the book ID
        - cover_path (str|None): the original cover path. If not given or equal to `None`, then the app tries to find an image named 'book_cover.png' in the temporary folder
        - check_book_existence (bool=False): wether to check if a Book with this ID exists in the BooksHandler
        - cover_exists_ok (bool=False): wether to check if a cover is already assigned to this ID

        Raises
        - BookNotFoundError: if `check_book_existence` is `True` and the book is not found in the BooksHandler
        - FileNotFoundError: if `cover_path` is not found or no cover is found in the temporary folder
        - FileExistsError: if `cover_exists_ok` is `True` and a cover is already assigned to this ID

        """

        # If books exitences checking is enabled
        if check_book_exists and not self.books_handler.books.get(book_id):
            raise book_sys.BookNotFoundError(book_id)

        default_cover_path = os.path.join(
            self.res_files_api.get_res("tmp"), "book_cover.png"
        )

        # Copying to destination
        self.set_cover_for(
            book_id,
            cover_path or default_cover_path,
            self.res_files_api.get_res("data.user.books.covers"),
            cover_exists_ok,
        )

    def set_cover_for_shelf(
        self,
        shelf_id: str,
        cover_path: str | None = None,
        check_shelf_exists: bool = False,
        cover_exists_ok: bool = False,
    ):
        """
        Copy the book cover to the app internal covers folder

        Parameters
        ----------
        - shelf_id (str): the Shelf ID
        - cover_path (str|None): the original cover path. If not given or equal to `None`, then the app tries to find an image named 'shelf_cover.png' in the temporary folder
        - check_shelf_existence (bool=False): wether to check if a Shelf with this ID exists in the BooksHandler
        - cover_exists_ok (bool=False): wether to check if a cover is already assigned to this ID

        Raises
        - BookShelfNotFoundError: if `check_shelf_existence` is `True` and the book is not found in the BooksHandler
        - FileNotFoundError: if `cover_path` is not found or no cover is found in the temporary folder
        - FileExistsError: if `cover_exists_ok` is `True` and a cover is already assigned to this ID

        """
        # If books exitences checking is enabled
        if check_shelf_exists and not self.books_handler.shelves.get(shelf_id):
            raise book_sys.BooksShelfNotFoundError(shelf_id)

        default_cover_path = os.path.join(
            self.res_files_api.get_res("tmp"), "shelf_cover.png"
        )

        # Copying to destination
        self.set_cover_for(
            shelf_id,
            cover_path or default_cover_path,
            self.res_files_api.get_res("data.user.bookshelves.covers"),
            cover_exists_ok,
        )

    def select_cover(self, save_path: str):
        """
        Display an file picker and prepare (copying to the app location, and redimensioning it) the selected image that be used as cover

        Parameters
        ----------
        - save_path (str): the path where to save the prepared cover

        Returns
        -------
        - tuple[str, PIL.Image.Image]: the filepath to the prepared image, and the prepared Image object
        - None: if no image is selected by the user
        """
        infos = images_tools.select_image()
        self.logger.debug(f"User selected image with {infos=}")

        if infos and infos[0]:
            final_infos = images_tools.prepare_image(
                infos[0],
                save_path,
            )
            return final_infos

    def select_book_cover(self) -> tuple[str, Image] | None:
        """
        Display an file picker and prepare (copying to the app location, and redimensioning it) the selected image that be used as cover

        Returns
        -------
        - tuple[str, PIL.Image.Image]: the filepath to the prepared image, and the prepared Image object
        - None: if no image  is selected by the user
        """
        return self.select_cover(
            os.path.join(self.res_files_api.get_res("tmp"), "book_cover.png")
        )

    def select_shelf_cover(self) -> tuple[str, Image] | None:
        """
        Display an file picker and prepare (copying to the app location, and redimensioning it) the selected image that be used as cover

        Returns
        -------
        - tuple[str, PIL.Image.Image]: the filepath to the prepared image, and the prepared Image object
        - None: if no image  is selected by the user
        """
        return self.select_cover(
            os.path.join(self.res_files_api.get_res("tmp"), "shelf_cover.png")
        )

    def edit_shelf_with_id(self, shelf_id: str, **shelf_data):
        """
        Edit the informations of the Shelfw that has `shelf_id`

        Parameters
        ----------
        - shelf_id (Shelf): the ID of the shelf to edit
        - **shelf_data: The new data of the shelf
        """
        shelf = self.books_handler.shelves.get(shelf_id)

        # Shelf don't exists
        if not shelf:
            raise book_sys.BooksShelfNotFoundError(shelf_id)

        self.edit_shelf(shelf, False, **shelf_data)

    def edit_shelf(
        self,
        shelf: book_sys.Shelf,
        replace_old_ref: bool = True,
        **shelf_data,
    ):
        """
        Edit the informations of `shelf`

        Parameters
        ----------
        - shelf (Shelf): the shelf to edit
        - replace_old_ref (bool=True): Wehter to replace `shelf` variable by the edited Shelf
        - **shelf_data: The new data of the shelf
        """

        self.logger.debug(
            f"Editing Shelf (ID={shelf.id}), shelves={self.books_handler.shelves}"
        )
        # Remove from parents/child
        shelf.remove_from_books()
        shelf.remove_from_child_shelves()
        shelf_data["parents_shelves"] = shelf._parent_shelves.copy()
        shelf.remove_from_parents()

        # Creating the edited shelf
        new_shelf = self.books_handler.create_shelf(
            **shelf_data
        )  # Adding to the default shelf
        self.books_handler.edit_shelf(shelf.str_id(), new_shelf)  # Applying the edition

        if replace_old_ref:
            shelf = new_shelf

    def edit_book_with_id(self, book_id: str, **books_data):
        """
        Replaces the data of the Book that has `book_id` for id with the new `books_data`

        Parameters
        ----------
        - book_id (Book): the ID of the book to edit
        - **books_data: the new data of the book

        Raises
        ------
        BookNotFoundError: if no Book has this ID
        """
        book = self.books_handler.books.get(str(book_id))

        if not book:
            raise book_sys.BookNotFoundError(book_id)

        return self.edit_book(book, False, **books_data)

    def edit_book(
        self,
        book: book_sys.Book,
        replace_old_ref: bool = True,
        **books_data,
    ):
        """
        Replaces the data of `Book` with the new `books_data`

        Parameters
        ----------
        - book (Book): the book to edit
        - replace_original_ref (bool=True): wether to replace the reference of the old book (the one before the edition) by the new
        - **books_data: the new data of the book

        Raises
        ------
        BookNotFoundError: if this Book does not exists
        """
        book.delete_from_parents()  # Removes from all the parent to allow proper reset
        new_book = self.books_handler.create_book(**books_data)
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
            default_cover = self.res_files_api.get_res("assets.defaults_covers.book")

        elif isinstance(object, book_sys.Shelf):
            excepted_path = (
                os.path.join(
                    self.res_files_api.get_res("data.user.bookshelves.covers"),
                    object.str_id(),
                )
                + ".png"
            )
            default_cover = self.res_files_api.get_res("assets.defaults_covers.shelf")

        else:
            raise TypeError(f"Could not get cover for object of type {type(object)}")

        if not os.path.exists(excepted_path):
            if return_default:
                return default_cover

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
        raise_file_not_found: bool = False,
    ) -> str | None:
        """
        Constructs and returns the path to the `shelf` cover file.

        Parameters
        ----------
        -shelf (book_sys.Shelf): the shelf object
        -return_default (bool=True): whether to return the default cover path if the constructed path does not exist
        - raise_file_not_found (bool): whether to raise `FileNotFoundError` instead of returning `None` if the constructed path does not exists and `return_default=False`
        NOTE : `return_default` has always priority over `raise_file_not_found`
        """
        return self.get_cover_path(shelf, return_default, raise_file_not_found)

    def get_book_cover_path(
        self,
        book: book_sys.Book,
        return_default: bool = True,
        raise_file_not_found: bool = False,
    ):
        """
        Constructs and returns the path to the `book` cover file.

        Parameters
        ----------
        - book (book_sys.Book): the book object
        - return_default (bool=True): whether to return the default cover path if the constructed path does not exist
        - raise_file_not_found (bool): whether to raise `FileNotFoundError` instead of returning `None` if the constructed path does not exists and `return_default=False`
        NOTE : `return_default` has always priority over `raise_file_not_found`
        """
        return self.get_cover_path(book, return_default, raise_file_not_found)

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
        result = self.books_handler.get_shelfs(id=(shelf_id, True, True))

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
