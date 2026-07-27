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
from app.ui import qt_signals_handler, ui
from app.utils import json_file_manager, paths


class AppSystem:
    def __init__(self, qt_app: QtWidgets.QApplication):
        self.boot_start_time = time.time()
        self.qt_app = qt_app
        self.instance_locker = None
        self.logger = logging.getLogger(__name__)
        self.jfm = json_file_manager.JsonFileManager()
        self.res_handler = resources_handler.RessourcesHandler(
            self.jfm, {}, paths.APP_PATH
        )
        self.res_handler.load_from_file(paths.RESS_INDEXES_FILEPATH)
        self.qt_signals_handler = qt_signals_handler.QtSignalsHandler()
        self.app_infos = self.load_app_infos(self.res_handler.get_res("app_infos"))
        self.installation_infos = self.get_installation_infos()
        self.clean_updater_files()
        if self.check_first_boot():
            self.logger.info("Processing first boot operations...")
            self.first_boot_operations()

        else:
            self.check_folder(
                self.res_handler.get_res("data"),
                self.res_handler.get_res("assets"),
                self.res_handler.get_res("data.user"),
                self.res_handler.get_res("data.user.books"),
                self.res_handler.get_res("data.user.books.covers"),
                self.res_handler.get_res("data.user.bookshelves"),
                self.res_handler.get_res("data.user.bookshelves.covers"),
            )
        self.logger.info("Initialising application...")
        self.books_handler = book_sys.BooksHandler(
            jfm=self.jfm,
            res_handler=self.res_handler,
        )
        self.books_handler.load_books(self.res_handler.get_res("data.user.books.books"))
        self.books_handler.load_shelves(
            self.res_handler.get_res("data.user.bookshelves.bookshelves")
        )
        self.qt_app.aboutToQuit.connect(self.close_app)
        self.settings_handler = settings_handler.SettingsHandler(self.jfm)
        self.load_and_apply_settings()
        self.langs_handler = langs_handler.LangsHandler(self.jfm, {}, self.res_handler)
        self.langs_handler.load_from_file(
            self.res_handler.get_res(
                f"assets.langs.{self.settings_handler.get_setting_value('general.appearance.language')}"
            )
        )
        self.logger.info("Connecting signals to loaded slots...")
        self.connect_signals()
        self.logger.info("Erasing files in temporary folder...")
        self.empty_tmp_folder(self.res_handler.get_res("tmp"))

    def connect_signals(self):
        """
        Connect signals to the already loaded slots
        """
        self.qt_signals_handler.show_about_sg.connect(self.about)
        self.qt_signals_handler.get_app_infos_sg.connect(self.get_app_infos)

    def get_installation_infos(self):
        installation_infos = self.jfm.read_json(
            self.res_handler.get_res("data.app.installation_infos"), catch_error=True
        )

        if not installation_infos:
            self.logger.warning(
                "Could not get valid installation infos from file, writting default installation infos"
            )
            installation_infos = {
                "boots_count": 0,
                "app_version": self.app_infos["app_version"],
                "previous_versions": [],
                "last_update_date": None,
            }
        return installation_infos

    def save_installation_infos(self):
        self.jfm.write_json(
            self.res_handler.get_res("data.app.installation_infos"),
            self.installation_infos,
        )

    def load_and_apply_settings(self):
        self.settings_handler.load_base_settings(
            self.res_handler.get_res("data.app.static.base_settings")
        )

        try:
            self.settings_handler.load_user_settings(
                self.res_handler.get_res("data.user.settings")
            )

        except FileNotFoundError:
            QtWidgets.QMessageBox.warning(
                None,
                "Settings Error",
                "Failed to load user settings : File not found !",
            )

        self.settings_handler.apply_user_settings()

    def start(self):
        self.start_ui()
        self.installation_infos["boots_count"] += 1

    def start_ui(self):
        self.logger.info("Initialising GUI...")

        if hasattr(self, "ui"):
            self.ui.deleteLater()
        self.ui = ui.UI(
            self.books_handler,
            self.res_handler,
            self.qt_signals_handler,
            self.settings_handler,
            self.langs_handler,
        )
        self.jfm.set_signals_handler(self.ui.qt_signals_handler)
        self.ui.show()
        self.boot_end_time = time.time()
        self.logger.info(
            f"Initialised app in {self.boot_end_time - self.boot_start_time:.3f}s"
        )

        if self.settings_handler.get_setting_value(
            "developer_settings.show_indev_warning"
        ):
            self.show_indev_warn()

    def clean_updater_files(self):
        if paths.MODE == "frozen" and self.installation_infos["boots_count"] > 5:
            to_remove_files = (
                os.path.join(paths.BASE_PATH, "update_instructions.json"),
                os.path.join(paths.BASE_PATH, "update_manifest.json"),
                os.path.join(paths.BASE_PATH, "upgrader.exe"),
            )
            for file in to_remove_files:
                try:
                    os.remove(file)

                except FileNotFoundError:
                    self.logger.error(
                        f"Coundn't remove upgrade file '{file}' : file not found !"
                    )

                except PermissionError:
                    self.logger.error(
                        f"Coundn't remove upgrade file '{file}' : permission denied !"
                    )

                except Exception:
                    self.logger.exception(
                        f"Coundn't remove upgrade file '{file}' due to the following error :\n"
                    )

    def close_app(self):
        self.logger.info("Closing window...")
        self.logger.info("Saving data...")
        self.books_handler.save_books(self.res_handler.get_res("data.user.books.books"))
        self.books_handler.save_shelfs(
            self.res_handler.get_res("data.user.bookshelves.bookshelves")
        )
        self.settings_handler.save_settings(
            self.res_handler.get_res("data.app.static.base_settings"),
            self.res_handler.get_res("data.user.settings"),
        )
        self.save_installation_infos()
        self.empty_tmp_folder(self.res_handler.get_res("tmp"))
        self.logger.info("Exiting app...")

    def set_instance_locker(self, instance_locker: QtCore.QLockFile):
        self.instance_locker = instance_locker

    def empty_tmp_folder(self, dir_path):
        """
        Create the tmp directory if it does not exists, then erase its content
        """
        tmp_path = pathlib.Path(dir_path)

        if not tmp_path.exists():
            self.logger.warning(
                "Temporary directory not found, attempting to make it..."
            )
            tmp_path.mkdir()

        for element in tmp_path.iterdir():
            try:
                if element.is_file():
                    element.unlink()
            except Exception:
                self.logger.error(
                    f"Unable to destroy file '{element}' in the temporary folder !"
                )

    def check_first_boot(self):
        if self.installation_infos["boots_count"] == 0:
            return True

        else:
            return False

    def first_boot_operations(self):
        folder_to_make = (
            self.res_handler.get_res("data.user"),
            self.res_handler.get_res("data.user.books"),
            self.res_handler.get_res("data.user.books.covers"),
            self.res_handler.get_res("data.user.bookshelves"),
            self.res_handler.get_res("data.user.bookshelves.covers"),
            self.res_handler.get_res("tmp"),
        )
        file_to_make = (
            (self.res_handler.get_res("data.user.books.books"), []),
            (self.res_handler.get_res("data.user.bookshelves.bookshelves"), []),
            (self.res_handler.get_res("data.user.settings"), {}),
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
        try:
            app_infos = self.jfm.read_json(filepath, catch_error=False)

        except (FileNotFoundError, PermissionError):
            self.logger.error("Could not find app infos file !")
            app_infos = None

        if not app_infos:
            self.logger.warning(
                "App infos file not found or corrupted, using default app infos"
            )
            app_infos = {
                "app_version": "0.3.0",
                "root_directory_content": [
                    "app",
                    "licenses",
                    "LICENSE",
                    "THIRD_PARTY_NOTICE.txt",
                    "main.py",
                ],
                "elements_to_preserve": [
                    "app/data/user_data/books_data",
                    "app/data/user_data/bookshelves_data",
                ],
            }
            self.jfm.write_json(
                filepath,
                app_infos,
            )
        return app_infos

    def show_indev_warn(self):
        """
        Show the in develepoment warning window
        """

        # self.indev_warning_w.show()
        QtWidgets.QMessageBox.information(
            None, "Books Quest", self.langs_handler.tr("shared.msg.indev_warn")
        )

    @QtCore.Slot(bool)
    def about(self, print_console: bool = True):
        """
        Shows some infos about BooksQuest

        Parameters
        ----------
        print_console (bool=True): whether to show the infos in the console too
        """
        if print_console:
            print(f"===== {self.langs_handler.tr('about.title')} =====")
            print(
                self.langs_handler.tr(
                    "about.msg",
                    version=self.app_infos["app_version"],
                    developer="SoloEnder",
                    license="MIT",
                )
            )
            print("=============================")
        QtWidgets.QMessageBox.about(
            None,
            self.langs_handler.tr("about.title"),
            self.langs_handler.tr(
                "about.msg",
                version=self.app_infos["app_version"],
                developer="SoloEnder",
                license="MIT",
            ),
        )

    @QtCore.Slot(dict)
    def get_app_infos(self, dictionary: dict):
        """
        Add the app infos to `dictionnary`
        Usefull if you want to get the app infos without directly accessing them
        """
        dictionary.update(self.app_infos)
