import datetime as dt
import logging
import os
import pathlib
import sys
import tempfile

from PySide6 import QtWidgets

from app.src import book_stuff
from app.ui import ui
from app.utils import json_file_manager as jfm
from app.utils import paths


class AppSystem:
    def __init__(self):
        self.app_ui = QtWidgets.QApplication([])
        begin = dt.datetime.now()
        self.logger = logging.getLogger(__name__)
        self.app_infos = self.load_app_infos(
            os.path.join(paths.DATA_PATH, "app_infos.json")
        )
        self.app_infos["boot_count"] += 1
        first_boot = self.check_first_boot()
        if first_boot:
            self.first_boot_operations()

        else:
            self.check_folder(
                paths.DATA_PATH,
                paths.ASSETS_PATH,
                paths.BOOKS_DATA_PATH,
                paths.BOOKS_COVERS_PATH,
                paths.SHELFS_COVERS_PATH,
            )
        self.logger.info("Initialising application...")
        self.books_handler = book_stuff.BooksHandler()
        self.books_handler.load_books(os.path.join(paths.BOOKS_DATA_PATH, "books.json"))
        self.books_handler.edit_default_shelf(name="Tout les livres")
        self.books_handler.load_shelfs(
            os.path.join(paths.BOOKS_DATA_PATH, "shelfs.json")
        )
        self.app_ui.aboutToQuit.connect(self.close_app)
        self.ui = ui.UI(self.books_handler)
        paths.TMP_DIR_PATH = tempfile.mkdtemp(prefix="tmp", dir=paths.BASE_PATH)
        end = dt.datetime.now()
        self.logger.info(f"Initialising app in {end - begin}")

    def running(self):
        self.logger.info("Showing main window...")
        self.ui.show()
        sys.exit(self.app_ui.exec())

    def close_app(self):
        self.logger.info("Closing window...")
        self.logger.info("Saving data...")
        self.save_app_infos(os.path.join(paths.DATA_PATH, "app_infos.json"))
        self.books_handler.save_books(os.path.join(paths.BOOKS_DATA_PATH, "books.json"))
        self.books_handler.save_shelfs(
            os.path.join(paths.BOOKS_DATA_PATH, "shelfs.json")
        )
        self.logger.info("Deleting files in temporary folder...")
        self.empty_tmp_folder(paths.TMP_DIR_PATH)
        self.logger.info("Exiting app...")

    def empty_tmp_folder(self, dir_path):
        """
        Erase all the files in the tmp directory
        """
        tmp_path = pathlib.Path(dir_path)

        for element in tmp_path.iterdir():
            try:
                if element.is_file():
                    element.unlink()
            except Exception:
                self.logger.error(
                    f"Unable to destroy file <{element}> in the temporary folder !"
                )
        tmp_path.rmdir()

    def check_first_boot(self):
        if self.app_infos:
            if self.app_infos["boot_count"] == 1:
                return True

    def first_boot_operations(self):
        folder_to_make = (
            paths.BOOKS_DATA_PATH,
            paths.BOOKS_COVERS_PATH,
            paths.SHELFS_COVERS_PATH,
        )
        file_to_make = (
            os.path.join(paths.BOOKS_DATA_PATH, "books.json"),
            os.path.join(paths.BOOKS_DATA_PATH, "shelfs.json"),
        )

        for folder in folder_to_make:
            try:
                os.mkdir(folder)

            except FileExistsError:
                self.logger.error(
                    f"Failed to make folder '{folder}' : Folder already exists !"
                )
                raise

            except FileNotFoundError:
                self.logger.error(
                    f"Failed to make folder '{folder}' : A parent directory is missing !"
                )
                raise

            except Exception as e:
                self.logger.error(
                    f"Failed to make folder '{folder}' dues to exception : {e}"
                )

        for file in file_to_make:
            jfm.write_json(file, [])

    def check_folder(self, *folders):
        """
        Check the existence of a folder send an logging.ERROR message else
        """

        for folder in folders:
            self.logger.info(f"Checking the existence of {folder}")
            folder = pathlib.Path(folder)

            if not folder.exists():
                self.logger.error(f"Folder {folder} not found !")

    def load_app_infos(self, filepath: str | pathlib.Path) -> dict:
        """
        Load app infos from filepath

        Args:
        - filepath (str, pathlib.Path): the app infos file path
        """
        app_infos = jfm.read_json(filepath)

        if not app_infos:
            app_infos = {
                "version": {
                    "readable": "Unknown",
                    "semantic": "Unknown",
                },
                "boot_count": 0,
            }
            self.logger.warning(
                "App infos file empty or corrupted, writing default app infos."
            )
        return app_infos

    def save_app_infos(self, filepath: str | pathlib.Path):
        jfm.write_json(filepath, data=self.app_infos)
