import datetime as dt
import logging
import os
import pathlib
import sys
import tempfile
from tkinter.messagebox import showerror

from PySide6 import QtWidgets, QtCore

from app.src import book_sys
from app.ui import ui
from app.utils import json_file_manager
from app.utils import paths
from app.src import my_logging_stuff
from app.src import settings_handler

class AppSystem:
    def __init__(self, qt_app):
        begin = dt.datetime.now()
        self.qt_app = qt_app
        self.instance_locker = None
        self.logger = logging.getLogger(__name__)
        self.jfm = json_file_manager.JsonFileManager()
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
                paths.BOOKSHELVES_DATA_PATH,
            )
        self.logger.info("Initialising application...")
        self.books_handler = book_sys.BooksHandler(self.jfm)
        self.books_handler.load_books(os.path.join(paths.BOOKS_DATA_PATH, "books.json"))
        self.books_handler.edit_default_shelf(name="Tout les livres")
        self.books_handler.load_shelfs(
            os.path.join(paths.BOOKSHELVES_DATA_PATH, "shelves.json")
        )
        self.qt_app.aboutToQuit.connect(self.close_app)
        self.settings_handler = settings_handler.SettingsHandler(self.jfm)
        self.settings_handler.load_from_file(paths.SETTINGS_FILEPATH)
        self.empty_tmp_folder(paths.TMP_DIR_PATH)
        end = dt.datetime.now()
        self.logger.info(f"Loaded app in {end - begin}")

    def start(self):
        self.logger.info("Showing main window...")
        self.start_ui()
        
    def start_ui(self):
        self.logger.info("Initialising GUI...")
        self.ui = ui.UI(self.books_handler, self.settings_handler,)
        self.jfm.set_signals_handler(self.ui.qt_signals_handler)
        
        if self.app_infos["version"]["semantic"] == "indev" and self.settings_handler.get_setting_value("developer_settings.show_indev_warning") == True:
            self.ui.show_indev_warn()
            
        self.ui.show()

    def close_app(self):
        self.logger.info("Closing window...")
        self.logger.info("Saving data...")
        self.save_app_infos(os.path.join(paths.DATA_PATH, "app_infos.json"))
        self.books_handler.save_books(os.path.join(paths.BOOKS_DATA_PATH, "books.json"))
        self.books_handler.save_shelfs(
            os.path.join(paths.BOOKSHELVES_DATA_PATH, "shelves.json")
        )
        self.logger.info("Deleting files in temporary folder...")
        self.empty_tmp_folder(paths.TMP_DIR_PATH)
        self.settings_handler.save_in_file(paths.SETTINGS_FILEPATH)
        self.logger.info("Exiting app...")
        
        
    def set_instance_locker(self, instance_locker: QtCore.QLockFile):
        self.instance_locker = instance_locker

            
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
                    f"Unable to destroy file '{element}' in the temporary folder !"
                )

    def check_first_boot(self):
        if self.app_infos:
            if self.app_infos["boot_count"] == 1:
                return True

    def first_boot_operations(self):
        folder_to_make = (
            paths.BOOKS_DATA_PATH,
            paths.BOOKS_COVERS_PATH,
            paths.BOOKSHELVES_DATA_PATH,
            paths.BOOKSHELVES_COVERS_PATH,
            paths.TMP_DIR_PATH,
        )
        file_to_make = (
            os.path.join(paths.TMP_DIR_PATH, "bq"),
            os.path.join(paths.BOOKS_DATA_PATH, "books.json"),
            os.path.join(paths.BOOKSHELVES_DATA_PATH, "shelves.json"),
        )

        for folder in folder_to_make:
            
            if os.path.exists(folder):
                self.logger.warning(f"Folder {folder} already exists, skipping its creation")
                continue
                
            try:
                os.mkdir(folder)

            except FileNotFoundError:
                self.logger.error(
                    f"Failed to make folder '{folder}' : A parent directory is missing !"
                )
                raise

            except Exception:
                self.logger.exception(
                    f"Failed to make folder '{folder}' dues to unhandled exception :"
                )

        for file in file_to_make:
            
            if os.path.exists(file):
                self.logger.warning(f"File {file} already exists, skipping its creation")
                continue
            
            if file.endswith(".json"):
                self.jfm.write_json(file, [], catch_error=False)
                
            else:
                with open(file, "w") as f:
                    f.write("")

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
        app_infos = self.jfm.read_json(filepath, catch_error=False)

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
        self.jfm.write_json(filepath, data=self.app_infos, catch_error=False)
