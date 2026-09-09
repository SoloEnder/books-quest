import logging
import os
import pathlib
import time
import webbrowser

from PySide6 import QtCore, QtWidgets

from app.src import (
    api,
    book_sys,
)
from app.ui import ui
from app.utils import paths, update_tools


class AppSystem:
    def __init__(self, qt_app: QtWidgets.QApplication):
        self.boot_start_time = time.time()
        self.qt_app = qt_app
        self.instance_locker = None
        self.logger = logging.getLogger(__name__)
        self.api = api.API()
        self.books = self.api.books
        self.res_files = self.api.res_files
        self.qt_signals = self.api.qt_signals
        self.langs = self.api.langs
        self.settings = self.api.settings

        # Loading data
        self.res_files.load_indexes()
        self.books.load_books()
        self.books.load_shelves()
        self.settings.load_settings()
        self.settings.apply_user_settings()

        self.app_infos = self.load_app_infos(self.res_files.get_res("app_infos"))
        self.installation_infos = self.get_installation_infos()
        self.clean_updater_files()
        self.check_and_make_missing()
        self.check_folder(
            self.res_files.get_res("data"),
            self.res_files.get_res("assets"),
            self.res_files.get_res("data.user"),
            self.res_files.get_res("data.user.books"),
            self.res_files.get_res("data.user.books.covers"),
            self.res_files.get_res("data.user.bookshelves"),
            self.res_files.get_res("data.user.bookshelves.covers"),
        )
        self.logger.info("Initialising application...")
        self.qt_app.aboutToQuit.connect(self.close_app)
        self.load_and_apply_settings()
        self.langs.set_prefered_language()
        self.logger.info("Connecting signals to loaded slots...")
        self.connect_signals()
        self.logger.info("Erasing files in temporary folder...")
        self.res_files.empty_tmp_folder()

    def connect_signals(self):
        """
        Connect signals to the already loaded slots
        """
        self.qt_signals.connect_to_signal("show_about_sg", self.about)
        self.qt_signals.connect_to_signal("check_for_updates_sg", self.check_for_update)
        self.qt_signals.connect_to_signal(
            "write_version_on_widget_sg", self.write_version_on_widget
        )

    def get_installation_infos(self):
        installation_infos = self.res_files.read_indexed_file(
            "data.app.installation_infos"
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

        if installation_infos["app_version"] != self.app_infos["app_version"]:
            installation_infos["previous_versions"].append(
                installation_infos["app_version"]
            )
            installation_infos["app_version"] = self.app_infos[
                "app_version"
            ]  # Force synchronisation with app infos
        return installation_infos

    def save_installation_infos(self):
        self.res_files.write_indexed_file(
            "data.app.installation_infos",
            self.installation_infos,
        )

    def load_and_apply_settings(self):
        self.settings.load_base_settings(
            self.res_files.get_res("data.app.static.base_settings")
        )

        try:
            self.settings.load_user_settings(
                self.res_files.get_res("data.user.settings")
            )

        except FileNotFoundError:
            QtWidgets.QMessageBox.warning(
                None,
                "Settings Error",
                "Failed to load user settings : File not found !",
            )

        self.settings.apply_user_settings()

    def start(self):
        self.start_ui()
        self.installation_infos["boots_count"] += 1

        if self.settings.get_setting_value("general.update.auto_update_check_enabled"):
            self.check_for_update()

    def start_ui(self):
        self.logger.info("Initialising GUI...")
        self.ui = ui.UI(
            self.api,
        )
        self.ui.show()
        self.boot_end_time = time.time()
        self.logger.info(
            f"Initialised app in {self.boot_end_time - self.boot_start_time:.3f}s"
        )

        if self.settings.get_setting_value("developer_settings.show_indev_warning"):
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
        self.books.save_books()
        self.books.save_shelves()
        self.settings.save_settings(
            self.res_files.get_res("data.app.static.base_settings"),
            self.res_files.get_res("data.user.settings"),
        )
        self.save_installation_infos()
        self.res_files.empty_tmp_folder()
        self.logger.info("Exiting app...")

    def set_instance_locker(self, instance_locker: QtCore.QLockFile):
        self.instance_locker = instance_locker

    def check_first_boot(self):
        if self.installation_infos["boots_count"] == 0:
            return True

        else:
            return False

    def check_and_make_missing(self):
        folder_to_make = (
            self.res_files.get_res("data.user"),
            self.res_files.get_res("data.user.books"),
            self.res_files.get_res("data.user.books.covers"),
            self.res_files.get_res("data.user.bookshelves"),
            self.res_files.get_res("data.user.bookshelves.covers"),
            self.res_files.get_res("tmp"),
        )
        file_to_make = (
            (self.res_files.get_res("data.user.books.books"), []),
            (self.res_files.get_res("data.user.bookshelves.bookshelves"), []),
            (self.res_files.get_res("data.user.settings"), {}),
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
                self.res_files.write_file(filepath, data, catch_error=False)

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
            app_infos = self.res_files.read_file(str(filepath))

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
            self.res_files.write_file(
                str(filepath),
                app_infos,
            )
        return app_infos

    def show_indev_warn(self):
        """
        Show the in develepoment warning window
        """

        # self.indev_warning_w.show()
        QtWidgets.QMessageBox.information(
            None, "Books Quest", self.langs.tr("shared.msg.indev_warn")
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
            print(f"===== {self.langs.tr('about.title')} =====")
            print(
                self.langs.tr(
                    "about.msg",
                    version=self.app_infos["app_version"],
                    developer="SoloEnder",
                    license="MIT",
                )
            )
            print("=============================")
        QtWidgets.QMessageBox.about(
            None,
            self.langs.tr("about.title"),
            self.langs.tr(
                "about.msg",
                version=self.app_infos["app_version"],
                developer="SoloEnder",
                license="MIT",
            ),
        )

    @QtCore.Slot(QtWidgets.QWidget)
    def write_version_on_widget(self, widget):
        """
        Set the text of `widget` to the current app version
        Only works with widgets that has the `setText` method
        """
        widget.setText(self.app_infos["app_version"])

    @QtCore.Slot(bool)
    def check_for_update(self, show_up_to_date_msg: bool = False):
        self.logger.info("Checking for updates...")
        self.qt_signals.emit_signal(
            "edit_progress_msg", self.langs.tr("updates.infos.checking_for_updates")
        )
        release_infos = update_tools.get_latest_release_infos(
            "https://api.github.com/repos/soloender/books-quest/releases/latest",
            self.langs,
        )
        if not release_infos:
            self.qt_signals.emit_signal("edit_progress_msg", " ")
            return
        pop_up_title = self.langs.tr("updates.download_pop_up_title")
        release_version = release_infos[
            "tag_name"
        ]  # Should be formatted like this : 'vminor.major.patch'. The 'v' is not a mistake

        # Checking if the latest release is an update
        try:
            is_update = update_tools.is_higher_version(
                release_version.split("v")[1], self.app_infos["app_version"]
            )

        except update_tools.UncomparablesVersionsError:
            self.logger.error(
                f"Could not compare latest release version to app version tag name='{release_version}', app_version='{self.app_infos['app_version']}'"
            )
            self.qt_signals.emit_signal(
                "notify_sg",
                "error",
                pop_up_title,
                self.langs.tr("updates.errors.uncomparables_versions"),
                "",
            )
            self.qt_signals.emit_signal("edit_progress_msg", " ")
            return

        if not is_update:
            self.logger.info("App is up-to-date")
            if show_up_to_date_msg:
                self.qt_signals.emit_signal(
                    "notify_sg",
                    "info",
                    pop_up_title,
                    self.langs.tr("updates.infos.up_to_date"),
                    "",
                )
            self.qt_signals.emit_signal("edit_progress_msg", " ")
            return

        self.logger.info(f"Books Quest {release_version} is available")
        # Show pop up to download the update
        download = update_tools.download_pop_up(
            release_infos,
            pop_up_title,
            self.langs.tr(
                "updates.infos.update_available", update_version=release_version
            ),
            self.langs.tr("shared.actions.download"),
        )
        if download:
            self.logger.info(
                f"Opening update page url ({release_infos['html_url']}) in web browser"
            )
            webbrowser.open_new_tab(release_infos["html_url"])
        self.qt_signals.emit_signal("edit_progress_msg", " ")
