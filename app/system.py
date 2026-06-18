import logging
import os
import pathlib
import time

from PySide6 import QtCore, QtWidgets

from app.src import (
    book_sys,
    langs_handler,
    resources_handler,
    settings_handler,
)
from app.ui import ui
from app.utils import json_file_manager, paths


class AppSystem:
    def __init__(self, qt_app: QtWidgets.QApplication):
        self.boot_start_time = time.time()
        self.qt_app = qt_app
        self.instance_locker = None
        self.logger = logging.getLogger(__name__)
        self.jfm = json_file_manager.JsonFileManager()
        self.res_handler = resources_handler.RessourcesHandler(
            self.jfm, {}, paths.BASE_PATH
        )
        self.res_handler.load_from_file(paths.RESS_INDEXES_FILEPATH)
        self.app_infos = self.load_app_infos(self.res_handler.get_res("app_infos"))
        self.app_infos["boot_count"] += 1
        first_boot = self.check_first_boot()
        if first_boot:
            self.logger.info("Processing first boot operations...")
            self.first_boot_operations()

        else:
            self.check_folder(
                self.res_handler.get_res("data"),
                self.res_handler.get_res("assets"),
                self.res_handler.get_res("data.books"),
                self.res_handler.get_res("data.books.covers"),
                self.res_handler.get_res("data.bookshelves"),
                self.res_handler.get_res("data.bookshelves.covers"),
            )
        self.logger.info("Initialising application...")
        self.books_handler = book_sys.BooksHandler(
            jfm=self.jfm,
            res_handler=self.res_handler,
        )
        self.books_handler.load_books(self.res_handler.get_res("data.books.books"))
        self.books_handler.load_shelves(
            self.res_handler.get_res("data.bookshelves.bookshelves")
        )
        self.qt_app.aboutToQuit.connect(self.close_app)
        self.settings_handler = settings_handler.SettingsHandler(self.jfm)
        self.load_and_apply_settings()
        self.langs_handler = langs_handler.LangsHandler(self.jfm, {})
        self.langs_handler.load_from_file(
            self.res_handler.get_res(
                f"assets.langs.{self.settings_handler.get_value('general.appearance.language.current')}"
            )
        )
        self.empty_tmp_folder(self.res_handler.get_res("tmp"))

    def load_and_apply_settings(self):
        self.settings_handler.load_base_settings(
            self.res_handler.get_res("data.settings.base")
        )

        try:
            self.settings_handler.load_user_settings(
                self.res_handler.get_res("data.settings.user")
            )

        except FileNotFoundError:
            QtWidgets.QMessageBox.warning(
                None,
                "Settings Error",
                "Failed to load user settings : File not found !",
            )

        self.settings_handler.apply_user_settings()

    def refresh_ui(self):
        """
        Delete the MainWindow object and recreate it
        """
        self.start_ui()

    def start(self):
        self.start_ui()

    def start_ui(self):
        self.logger.info("Initialising GUI...")
        self.ui = ui.UI(
            self.books_handler,
            self.res_handler,
            self.settings_handler,
            self.langs_handler,
        )
        self.jfm.set_signals_handler(self.ui.qt_signals_handler)
        self.ui.show()
        self.boot_end_time = time.time()
        self.logger.info(
            f"Initialised app in {self.boot_end_time - self.boot_start_time:.3f}s"
        )

        if (
            self.app_infos["version"]["semantic"] == "indev"
            and self.settings_handler.get_value(
                "developer_settings.show_indev_warning.current"
            )
            == True
        ):
            self.ui.show_indev_warn()

    def close_app(self):
        self.logger.info("Closing window...")
        self.logger.info("Saving data...")
        self.save_app_infos(self.res_handler.get_res("app_infos"))
        self.books_handler.save_books(self.res_handler.get_res("data.books.books"))
        self.books_handler.save_shelfs(
            self.res_handler.get_res("data.bookshelves.bookshelves")
        )
        self.logger.info("Deleting files in temporary folder...")
        self.empty_tmp_folder(self.res_handler.get_res("tmp"))
        self.settings_handler.save_settings(
            self.res_handler.get_res("data.settings.base"),
            self.res_handler.get_res("data.settings.user"),
        )
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
            self.res_handler.get_res("data.books"),
            self.res_handler.get_res("data.books.covers"),
            self.res_handler.get_res("data.bookshelves"),
            self.res_handler.get_res("data.bookshelves.covers"),
            self.res_handler.get_res("tmp"),
        )
        file_to_make = (
            (self.res_handler.get_res("data.books.books"), []),
            (self.res_handler.get_res("data.bookshelves.bookshelves"), []),
            (self.res_handler.get_res("data.settings.user"), {}),
        )

        for folder in folder_to_make:
            if os.path.exists(folder):
                self.logger.warning(
                    f"Folder {folder} already exists, skipping its creation"
                )
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

        for filepath, data in file_to_make:
            if os.path.exists(filepath):
                self.logger.warning(
                    f"File {filepath} already exists, skipping its creation"
                )
                continue

            if filepath.endswith(".json"):
                self.jfm.write_json(filepath, data, catch_error=False)

            else:
                with open(filepath, "w") as f:
                    f.write(str(data))

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
