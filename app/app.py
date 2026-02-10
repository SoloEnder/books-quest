
import sys
import json
import logging
import pathlib
import datetime as dt
from PySide6 import QtWidgets
from app.ui import ui
from app.src import book
from app.utils import paths
from app.utils import json_file_manager as jfm

class AppSystem:

    def __init__(self):
        self.app_ui = QtWidgets.QApplication([])
        begin = dt.datetime.now()
        self.logger = logging.getLogger(__name__)
        self.check_folder(paths.get_abspath("app/data"), paths.get_abspath("app/assets"), paths.get_abspath("app/data/books"))
        self.load_app_infos(paths.get_abspath("app/data/app_infos.json"))
        self.app_infos["boot_count"] += 1
        self.check_fisrt_boot()
        self.logger.info("Initialising application...")
        self.books_handler = book.BooksHandler()
        self.books_handler.load_books(paths.get_abspath("app/data/books/books.json"))
        self.books_handler.create_shelf("Tout les livres", self.books_handler.books, str(dt.datetime.timestamp(dt.datetime.now())).replace(".", ""))
        self.books_handler.load_shelfs(paths.get_abspath("app/data/books/shelfs.json"))
        self.app_ui.aboutToQuit.connect(self.close_app)
        self.ui = ui.UI(self.books_handler)
        end = dt.datetime.now()
        self.logger.info(f"Initialising app in {end - begin}")

        
    def running(self):
        self.logger.info("Showing main window...")
        self.ui.show()
        sys.exit(self.app_ui.exec())

    def close_app(self):
        self.logger.info("Closing window...")
        self.logger.info("Saving data...")
        self.save_app_infos(paths.get_abspath("app/data/app_infos.json"))
        self.books_handler.save_books(paths.get_abspath("app/data/books/books.json"))
        self.books_handler.save_shelfs(paths.get_abspath("app/data/books/shelfs.json"))
        self.logger.info("Deleting files in temporary folder...")
        self.empty_tmp_folder()
        self.logger.info("Exiting app...")

    def empty_tmp_folder(self):
        """
        Erase all the files in the tmp directory
        """
        tmp_path = pathlib.Path(paths.get_abspath("app/tmp"))

        for element in tmp_path.iterdir():

            if element.is_file():
                element.unlink()

    def check_fisrt_boot(self):

        if self.app_infos:

            if self.app_infos["boot_count"] == 1:
                path = pathlib.Path(paths.get_abspath("app/data/books"))

                if not path.exists():
                
                    try:
                        path.mkdir()
                        self.books_handler.save_books(paths.get_abspath("app/data/books/books.json"))

                    except Exception:
                        self.logger.error(f"Unable to make folder {path} : Unknown error")

    def check_folder(self, *folders):
        """
        Check the existence of a folder send an logging.ERROR message else
        """

        for folder in folders:
            self.logger.info(f"Checking the existence of {folder}")
            folder = pathlib.Path(folder)

            if not folder.exists():
                self.logger.error(f"Folder {folder} not found !")

    def load_app_infos(self, filepath: str|pathlib.Path):
        """
        Load app infos from filepath

        Args:
        - filepath (str, pathlib.Path): the app infos file path
        """
        self.app_infos = jfm.read_json(paths.get_abspath("app/data/app_infos.json"))

        if not self.app_infos:
            self.app_infos = {
                "version":{
                    "readable":"Unknown",
                    "true":"Unknown",
                },
                "boot_count":0,
            }

    def save_app_infos(self, filepath: str|pathlib.Path):
        jfm.write_json(filepath, data=self.app_infos)



