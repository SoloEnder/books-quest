import logging

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import api
from app.ui import notification_service
from app.ui.main_pages import (
    base_page,
    book_creation_page,
    book_details_page,
    reading_session_page,
    settings_page,
    shelf_creation_page,
    shelf_details_page,
    shelfs_view_page,
)
from app.utils import images_tools, utils_funcs


class UI(QtWidgets.QMainWindow):
    def __init__(
        self,
        api: api.API,
    ):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.api = api
        self.books = self.api.books
        self.res_files = self.api.res_files
        self.qt_signals = self.api.qt_signals
        self.langs = self.api.langs
        self.settings = self.api.settings
        self.notification_service = notification_service.NotificationService(
            self, self.langs
        )
        self.qt_signals.connect_to_signal("notify_sg", self.notification_service.notify)
        self.draw_ui()
        self.progress_info_lb = QtWidgets.QLabel()
        self.statusBar().addPermanentWidget(self.progress_info_lb)
        self.qt_signals.connect_to_signal("edit_progress_msg", self.set_progress_msg)
        self.qt_signals.connect_to_signal("refresh_ui_sg", self.refresh_ui)
        self.setWindowTitle("Books Quest")
        self.setWindowIcon(
            QtGui.QIcon(self.res_files.get_res("assets.splashscreen.splashscreen"))
        )

    def draw_ui(self):
        """
        Draws almost the entire widgets, and remove the existant ones before.
        """
        self.logger.info("Drawing UI...")
        self.langs.set_language(
            self.settings.get_setting_value("general.appearance.language"), False
        )
        self.set_app_theme()
        self.books.books_handler.edit_default_shelf(
            title=self.langs.tr("shelf.infos.default_shelf_title")
        )
        self.logger.info("Refreshing UI...")

        # Removes actions
        if hasattr(self, "my_actions"):
            [action.deleteLater() for action in self.my_actions.values()]
        self.set_actions()

        # Removes menus
        self.menuBar().clear()
        self.config_menus()

        if hasattr(self, "my_stacked_widgets"):
            if self.centralWidget() == self.my_stacked_widgets:
                self.takeCentralWidget()
            self.my_stacked_widgets.deleteLater()

        self.my_stacked_widgets = MyStackedWidgets(
            self,
            self.api,
        )
        if hasattr(self, "toolbar"):
            self.removeToolBar(self.toolbar)
            self.toolbar.clear()
            self.toolbar.deleteLater()

        self.toolbar = ToolBar(self, self.my_actions)
        self.addToolBar(self.toolbar)
        self.gen_qss_filepath = self.res_files.get_res("assets.qss.general")
        utils_funcs.load_and_set_ss(
            self.gen_qss_filepath, widget=self.my_stacked_widgets, logger=self.logger
        )
        self.my_stacked_widgets.switch_page("SHELFS_VIEW_PAGE")
        self.setCentralWidget(self.my_stacked_widgets)

    def set_app_theme(self):
        """
        Sets the app theme according to the settings
        """
        style_hints = QtWidgets.QApplication.styleHints()
        theme = self.settings.get_setting_value("general.appearance.theme")

        if theme == "light":
            style_hints.setColorScheme(QtCore.Qt.ColorScheme.Light)

        elif theme == "dark":
            style_hints.setColorScheme(QtCore.Qt.ColorScheme.Dark)

        elif theme == "system":
            style_hints.unsetColorScheme()

    def refresh_ui(self):
        """
        Refresh the UI
        """
        self.logger.info("Refreshing UI...")
        images_tools.clear_all_caches()
        self.langs.tr.cache_clear()
        current_page_infos_before_redraw = (
            self.my_stacked_widgets.current_page_infos[0],
            self.my_stacked_widgets.current_page_infos[2],
        )
        self.draw_ui()
        QtWidgets.QApplication.processEvents()
        self.qt_signals.emit_signal(
            "switch_page_sg",
            current_page_infos_before_redraw[0],
            True,
            current_page_infos_before_redraw[1],
        )  # The first element should be the page name

    def set_progress_msg(self, msg: str):
        self.progress_info_lb.setText(msg)
        QtWidgets.QApplication.processEvents()

    def set_actions(self):
        self.my_actions = {
            "close_page": QtGui.QAction(
                self.langs.tr("shared.actions.close"),
                icon=images_tools.get_svg(
                    self.res_files.get_res("assets.icons.exit"), "red"
                ),
            ),
            "open_settings": QtGui.QAction(
                self.langs.tr("shared.actions.open_settings"),
                icon=images_tools.get_svg(
                    self.res_files.get_res("assets.icons.settings")
                ),
            ),
            "quit_app": QtGui.QAction(
                "Quit Books Quest",
                icon=images_tools.get_svg(self.res_files.get_res("assets.icons.exit")),
            ),
        }
        self.my_actions["close_page"].triggered.connect(
            lambda: self.my_stacked_widgets.close_page()
        )
        self.my_actions["open_settings"].triggered.connect(
            lambda: self.my_stacked_widgets.switch_page("SETTINGS_PAGE", True, {})
        )
        self.my_actions["quit_app"].triggered.connect(QtWidgets.QApplication.quit)

    def config_menus(self):
        """
        Adds menus to the menu bar
        """
        self.app_menu = self.menuBar().addMenu("Books Quest")
        self.app_menu.addAction(self.my_actions["open_settings"])
        self.app_menu.addAction(self.my_actions["quit_app"])


class MyStackedWidgets(QtWidgets.QStackedWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        api: api.API,
    ):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.api = api
        self.books = self.api.books
        self.res_files = self.api.res_files
        self.qt_signals = self.api.qt_signals
        self.langs = self.api.langs
        self.settings = self.api.settings
        self.redundant_lang_path = ""
        self.current_page_infos: (
            tuple[str, base_page.BasePage, dict] | tuple
        ) = ()  # This tuple should contain 3 values : the current page name the current page object (in this order), and the specials arguments of the current page
        self.reading_session_page = reading_session_page.ReadingSessionPage(
            self, self.api, self.books.books_handler.default_book.str_id()
        )
        self.settings_page = settings_page.SettingsPage(
            self,
            self.api,
        )
        self.shelfs_view_page = shelfs_view_page.ShelfsViewPage(
            self,
            self.api,
        )
        self.shelf_details_page = shelf_details_page.ShelfDetailsPage(
            self, self.books.books_handler.default_shelf.id, self.api
        )
        self.book_creation_page = book_creation_page.BookCreationPage(
            self,
            self.api,
        )
        self.shelf_creation_page = shelf_creation_page.ShelfCreationPage(
            self,
            self.api,
            mode="creation",
        )
        self.book_details_page = book_details_page.BookDetailsPage(
            self,
            self.api,
            self.books.books_handler.default_book.id,
        )
        self.pages = {
            "READING_SESSION_PAGE": self.reading_session_page,
            "SETTINGS_PAGE": self.settings_page,
            "SHELFS_VIEW_PAGE": self.shelfs_view_page,
            "SHELF_DETAILS_PAGE": self.shelf_details_page,
            "BOOK_CREATION_PAGE": self.book_creation_page,
            "SHELF_CREATION_PAGE": self.shelf_creation_page,
            "BOOK_DETAILS_PAGE": self.book_details_page,
        }
        self.addWidget(self.shelfs_view_page)
        self.addWidget(self.book_creation_page)
        self.addWidget(self.shelfs_view_page)
        self.addWidget(self.shelf_creation_page)
        self.addWidget(self.book_details_page)
        self.history = []
        self.qt_signals.connect_to_signal("switch_page_sg", self.switch_page)
        self.qt_signals.connect_to_signal("close_page_sg", self.close_page)
        self.qt_signals.connect_to_signal("refresh_page_sg", self.refresh)
        self.qt_signals.connect_to_signal(
            "refresh_current_page_sg", self.refresh_current_page
        )
        utils_funcs.load_and_set_ss(
            self.res_files.get_res("assets.qss.general"), widget=self
        )

    @QtCore.Slot(str, bool, dict)
    def switch_page(self, page_name: str, refresh: bool = False, page_args={}):
        """
        Change the current widget displayed by the value of <name> in the attribute <pages>

        Args:
            - page_name (str): the name of the page, a key of the attribute <pages>.
            - refresh (bool): if true, the page will be refreshed. default to False
        """

        self.logger.info(f"Switching to page {page_name}...")
        if page_name in self.pages.keys():
            self.qt_signals.emit_signal(
                "edit_progress_msg", self.langs.tr("shared.msg.loading_page")
            )
            if refresh:
                self.refresh(page_name, page_args)

            page_obj = self.pages[page_name]
            self.setCurrentWidget(page_obj)

            self.current_page_infos = (page_name, page_obj, page_args)

            if (
                len(self.history) >= 1
                and self.history[0][0] == self.current_page_infos[0]
            ):
                self.history[0] = self.current_page_infos

            else:
                self.history.insert(0, self.current_page_infos)
            self.qt_signals.emit_signal("edit_progress_msg", " ")

        else:
            self.logger.error(f"Page <{page_name}> not found !")

    @QtCore.Slot(bool)
    def close_page(self):

        if len(self.history) > 1:
            self.switch_page(self.history[1][0], True, self.history[1][2])
            del self.history[1]
            del self.history[0]

        # history_copy = self.history.copy()
        # if len(history_copy) >= 1:

        #     if history_copy[0] != history_copy[1]:
        #         del self.history[1]
        #         self.switch_page(
        #             history_copy[1],
        #             True if refresh else False,
        #             self.pages[history_copy[1]].variables_kw
        #         )

    @QtCore.Slot(str, dict)
    def refresh(self, page_name: str, page_args: dict):
        self.logger.debug(f"Refreshing {page_name} with kwargs {page_args}")

        if page_name == "SETTINGS_PAGE":
            self.removeWidget(self.settings_page)
            self.settings_page = settings_page.SettingsPage(
                self,
                self.api,
            )
            self.pages["SETTINGS_PAGE"] = self.settings_page
            self.addWidget(self.settings_page)

        elif page_name == "SHELFS_VIEW_PAGE":
            self.removeWidget(self.shelfs_view_page)
            self.shelfs_view_page.setParent(None)
            self.shelfs_view_page.deleteLater()
            self.shelfs_view_page = shelfs_view_page.ShelfsViewPage(
                self,
                self.api,
            )
            self.pages["SHELFS_VIEW_PAGE"] = self.shelfs_view_page
            self.addWidget(self.shelfs_view_page)

        elif page_name == "BOOK_CREATION_PAGE":
            self.removeWidget(self.book_creation_page)
            self.book_creation_page.setParent(None)
            self.book_creation_page.deleteLater()
            self.book_creation_page = book_creation_page.BookCreationPage(
                self,
                self.api,
                **page_args,
            )
            self.pages["BOOK_CREATION_PAGE"] = self.book_creation_page
            self.addWidget(self.book_creation_page)

        elif page_name == "SHELF_CREATION_PAGE":
            self.removeWidget(self.shelf_creation_page)
            self.shelf_creation_page.setParent(None)
            self.shelf_creation_page.deleteLater()
            self.shelf_creation_page = shelf_creation_page.ShelfCreationPage(
                self,
                self.api,
                **page_args,
            )
            self.pages["SHELF_CREATION_PAGE"] = self.shelf_creation_page
            self.addWidget(self.shelf_creation_page)

        elif page_name == "SHELF_DETAILS_PAGE":
            self.removeWidget(self.shelf_details_page)
            self.shelf_details_page.setParent(None)
            self.shelf_details_page.deleteLater()
            self.shelf_details_page = shelf_details_page.ShelfDetailsPage(
                self,
                page_args["shelf_id"],
                self.api,
            )
            self.pages["SHELF_DETAILS_PAGE"] = self.shelf_details_page
            self.addWidget(self.shelf_details_page)

        elif page_name == "BOOK_DETAILS_PAGE":
            self.removeWidget(self.book_details_page)
            self.book_details_page.deleteLater()
            self.book_details_page = book_details_page.BookDetailsPage(
                self,
                self.api,
                page_args["book_id"],
            )
            self.pages["BOOK_DETAILS_PAGE"] = self.book_details_page
            self.addWidget(self.book_details_page)

        elif page_name == "READING_SESSION_PAGE":
            self.removeWidget(self.reading_session_page)
            self.reading_session_page.deleteLater()
            self.reading_session_page = reading_session_page.ReadingSessionPage(
                self,
                self.api,
                page_args["book_id"],
            )
            self.pages["READING_SESSION_PAGE"] = self.reading_session_page
            self.addWidget(self.reading_session_page)

        else:
            raise ValueError(f"Unknown page : '{page_name}'")

    @QtCore.Slot()
    def refresh_current_page(self):
        """
        Refresh the current page.
        """
        self.logger.info("Refreshing current page...")
        self.refresh(self.current_page_infos[0], self.current_page_infos[2])
        new_page_infos = (
            self.current_page_infos[0],
            self.pages[self.current_page_infos[0]],
            self.current_page_infos[2],
        )
        self.setCurrentWidget(new_page_infos[1])
        self.current_page_infos = new_page_infos


class ToolBar(QtWidgets.QToolBar):
    def __init__(
        self, parent: QtWidgets.QWidget | None, actions: dict[str, QtGui.QAction]
    ):
        super().__init__(parent)
        self.my_actions = actions
        self.addAction(self.my_actions["close_page"])
