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
        self.check_folder(
            paths.DATA_PATH,
            paths.ASSETS_PATH,
            paths.BOOKS_DATA_PATH,
            paths.BOOKS_COVERS_PATH,
            paths.SHELFS_COVERS_PATH,
            make=True,
        )
        paths.TMP_DIR_PATH = tempfile.mkdtemp(prefix="tmp", dir=paths.BASE_PATH)
        self.app_infos = self.load_app_infos(
            os.path.join(paths.DATA_PATH, "app_infos.json")
        )
        self.app_infos["boot_count"] += 1
        self.check_fisrt_boot()
        self.logger.info("Initialising application...")
        self.books_handler = book_stuff.BooksHandler()
        self.books_handler.load_books(os.path.join(paths.BOOKS_DATA_PATH, "books.json"))
        self.books_handler.edit_default_shelf(name="Tout les livres")
        self.books_handler.load_shelfs(
            os.path.join(paths.BOOKS_DATA_PATH, "shelfs.json")
        )
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

    def check_fisrt_boot(self):

        if self.app_infos:
            if self.app_infos["boot_count"] == 1:
                path = pathlib.Path(paths.BOOKS_DATA_PATH)

                if not path.exists():
                    try:
                        path.mkdir()
                        self.books_handler.save_books(
                            os.path.join(paths.BOOKS_DATA_PATH, "books.json")
                        )

                    except Exception:
                        self.logger.error(
                            f"Unable to make folder {path} : Unknown error"
                        )

    def check_folder(self, *folders, make: bool = False):
        """
        Check the existence of a folder send an logging.ERROR message else
        """

        for folder in folders:
            self.logger.info(f"Checking the existence of {folder}")
            folder = pathlib.Path(folder)

            if not folder.exists():
                self.logger.error(f"Folder {folder} not found !")

                if make:
                    self.logger.info(f"Attempting to create {folder}...")

                    try:
                        os.mkdir(folder)

                    except FileExistsError:
                        self.logger.error(
                            f"Failed to make directory <{folder}> : This directory already exists !"
                        )

                    except FileNotFoundError:
                        self.logger.error(
                            f"Failed to make directory <{folder}> : A parent directory is missing !"
                        )

                    except PermissionError:
                        self.logger.error(
                            f"Failed to make directory <{folder}> : Permission denied !"
                        )

                    except Exception:
                        self.logger.error(
                            f"Failed to make directory <{folder}> : Unknown Exception !"
                        )

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
