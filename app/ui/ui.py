import logging

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import book_sys, langs_handler, settings_handler
from app.ui import notification_service, qt_signals_handler
from app.ui.main_pages import (
    book_creation_page,
    settings_page,
    shelf_creation_page,
    shelf_details_page,
    shelfs_view_page,
)
from app.utils import utils_funcs


class UI(QtWidgets.QMainWindow):
    def __init__(
        self,
        books_handler,
        res_handler,
        settings_handler: settings_handler.SettingsHandler,
        langs_handler: langs_handler.LangsHandler,
    ):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.res_handler = res_handler
        self.settings_handler = settings_handler
        self.langs_handler = langs_handler
        self.qt_signals_handler = qt_signals_handler.QtSignalsHandler()
        self.notification_service = notification_service.NotificationService(
            self, self.langs_handler
        )
        self.qt_signals_handler.notify_sg.connect(self.notification_service.notify)
        self.books_handler.edit_default_shelf(
            title=self.langs_handler.tr("shelf.infos.default_shelf_title")
        )
        self.draw_ui()
        self.progress_info_lb = QtWidgets.QLabel()
        self.statusBar().addPermanentWidget(self.progress_info_lb)
        self.qt_signals_handler.edit_progress_msg.connect(self.set_progress_msg)
        self.qt_signals_handler.refresh_ui_sg.connect(self.draw_ui)
        self.setWindowTitle("Books Quest")
        self.setWindowIcon(
            QtGui.QIcon(self.res_handler.get_res("assets.splashscreen.splashscreen"))
        )

    def draw_ui(self):
        """
        Draws almost the entire widgets, and remove the existant ones before.
        """
        self.logger.info("Drawing UI...")
        self.langs_handler.set_current_language(
            self.settings_handler.get_setting_value("general.appearance.language")
        )
        self.logger.info("Refreshing UI...")

        if hasattr(self, "my_stacked_widgets"):
            self.my_stacked_widgets.deleteLater()

        self.my_stacked_widgets = MyStackedWidgets(
            self,
            self.books_handler,
            self.res_handler,
            self.qt_signals_handler,
            self.settings_handler,
            self.langs_handler,
        )
        if hasattr(self, "toolbar"):
            self.removeToolBar(self.toolbar)
            self.toolbar.deleteLater()

        self.toolbar = ToolBar(self, self.res_handler, self.langs_handler)
        self.addToolBar(self.toolbar)
        self.toolbar.close_page_act.triggered.connect(
            lambda: self.my_stacked_widgets.close_page()
        )
        self.toolbar.open_settings_act.triggered.connect(
            lambda: self.my_stacked_widgets.switch_page("SETTINGS_PAGE", True, {})
        )
        self.qt_signals_handler.add_action_sg.connect(self.toolbar.addActions)
        self.gen_qss_filepath = self.res_handler.get_res("assets.qss.general")
        utils_funcs.load_and_set_ss(
            self.gen_qss_filepath, widget=self.my_stacked_widgets, logger=self.logger
        )
        self.my_stacked_widgets.switch_page("shelfs_view_page")
        self.setCentralWidget(self.my_stacked_widgets)

    def set_progress_msg(self, msg: str):
        self.progress_info_lb.setText(msg)
        QtWidgets.QApplication.processEvents()


class MyStackedWidgets(QtWidgets.QStackedWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        books_handler: book_sys.BooksHandler,
        res_handler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        settings_handler,
        langs_handler,
    ):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.res_handler = res_handler
        self.qt_signals_handler = qt_signals_handler
        self.settings_handler = settings_handler
        self.langs_handler = langs_handler
        self.redundant_lang_path = ""
        self.current_page_infos = ()  # This tuple should contain 2 values : the current page name and the current page object (in this order)
        self.settings_page = settings_page.SettingsPage(
            self,
            self.res_handler,
            self.settings_handler,
            self.langs_handler,
            self.qt_signals_handler,
        )
        self.shelfs_view_page = shelfs_view_page.ShelfsViewPage(
            self,
            self.books_handler,
            res_handler,
            self.qt_signals_handler,
            self.settings_handler,
            self.langs_handler,
        )
        self.shelf_details_page = shelf_details_page.ShelfDetailsPage(
            self,
            self.books_handler.default_shelf,
            self.books_handler,
            self.res_handler,
            self.qt_signals_handler,
            self.settings_handler,
            self.langs_handler,
        )
        self.book_creation_page = book_creation_page.BookCreationPage(
            self,
            self.books_handler,
            self.res_handler,
            self.qt_signals_handler,
            self.settings_handler,
            self.langs_handler,
        )
        self.shelf_creation_page = shelf_creation_page.ShelfCreationPage(
            self,
            self.books_handler,
            self.res_handler,
            self.qt_signals_handler,
            self.settings_handler,
            self.langs_handler,
            mode="creation",
        )
        self.pages = {
            "SETTINGS_PAGE": self.settings_page,
            "SHELFS_VIEW_PAGE": self.shelfs_view_page,
            "SHELF_DETAILS_PAGE": self.shelf_details_page,
            "BOOK_CREATION_PAGE": self.book_creation_page,
            "SHELF_CREATION_PAGE": self.shelf_creation_page,
        }
        self.addWidget(self.shelfs_view_page)
        self.addWidget(self.book_creation_page)
        self.addWidget(self.shelfs_view_page)
        self.addWidget(self.shelf_creation_page)
        self.history = []
        self.switch_page("SHELFS_VIEW_PAGE")
        self.qt_signals_handler.switch_page_sg.connect(self.switch_page)
        self.qt_signals_handler.close_page_sg.connect(self.close_page)
        utils_funcs.load_and_set_ss(
            self.res_handler.get_res("assets.qss.general"), widget=self
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
            self.qt_signals_handler.edit_progress_msg.emit(
                self.langs_handler.tr("shared.msg.loading_page")
            )
            if refresh:
                self.refresh(page_name, page_args)

            page_obj = self.pages[page_name]
            self.setCurrentWidget(page_obj)

            self.history.insert(0, page_name)
            self.current_page_infos = (page_name, page_obj)
            self.qt_signals_handler.edit_progress_msg.emit(" ")

        else:
            self.logger.error(f"Page <{page_name}> not found !")

    @QtCore.Slot(bool)
    def close_page(self):

        if len(self.history) > 1:
            self.switch_page(
                self.history[1], True, self.pages[self.history[1]].variables_kw
            )
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

    def refresh(self, page_name, page_args):
        self.logger.debug(f"Pages switch history={self.history}")
        self.logger.debug(f"Refreshing {page_name} with kwargs {page_args}")

        if page_name == "SETTINGS_PAGE":
            self.removeWidget(self.settings_page)
            self.settings_page = settings_page.SettingsPage(
                self,
                self.res_handler,
                self.settings_handler,
                self.langs_handler,
                self.qt_signals_handler,
            )
            self.pages["SETTINGS_PAGE"] = self.settings_page
            self.addWidget(self.settings_page)

        elif page_name == "SHELFS_VIEW_PAGE":
            self.removeWidget(self.shelfs_view_page)
            self.shelfs_view_page.setParent(None)
            self.shelfs_view_page.deleteLater()
            self.shelfs_view_page = shelfs_view_page.ShelfsViewPage(
                self,
                self.books_handler,
                self.res_handler,
                self.qt_signals_handler,
                self.settings_handler,
                self.langs_handler,
            )
            self.pages["SHELFS_VIEW_PAGE"] = self.shelfs_view_page
            self.addWidget(self.shelfs_view_page)

        elif page_name == "BOOK_CREATION_PAGE":
            self.removeWidget(self.book_creation_page)
            self.book_creation_page.setParent(None)
            self.book_creation_page.deleteLater()
            self.book_creation_page = book_creation_page.BookCreationPage(
                self,
                self.books_handler,
                self.res_handler,
                self.qt_signals_handler,
                self.settings_handler,
                self.langs_handler,
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
                self.books_handler,
                self.res_handler,
                self.qt_signals_handler,
                self.settings_handler,
                self.langs_handler,
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
                page_args["shelf"],
                self.books_handler,
                self.res_handler,
                self.qt_signals_handler,
                self.settings_handler,
                self.langs_handler,
            )
            self.pages["SHELF_DETAILS_PAGE"] = self.shelf_details_page
            self.addWidget(self.shelf_details_page)

        else:
            raise ValueError(f"Unknown page : '{page_name}'")


class IndevWarnWidget(QtWidgets.QMessageBox):
    def __init__(self, parent: QtWidgets.QWidget | None):
        super().__init__(parent)

        # Setting window title
        self.setWindowTitle("Indev Warning")

        # Setting text
        self.setText(
            "This program is in developement ! If you see any bug which is not already reported, please report it <a href='https://github.com/SoloEnder/books-quest/issues'>here</a>"
        )


class ToolBar(QtWidgets.QToolBar):
    def __init__(self, parent: QtWidgets.QWidget | None, res_handler, langs_handler):
        super().__init__(parent)
        self.res_handler = res_handler
        self.langs_handler = langs_handler
        self.redundant_lang_path = "toolbar"

        self.close_page_act = QtGui.QAction(
            self.langs_handler.tr("shared.actions.close")
        )
        self.close_page_act.setIcon(
            QtGui.QIcon(self.res_handler.get_res("assets.icons.exit"))
        )
        self.open_settings_act = QtGui.QAction(
            self.langs_handler.tr("shared.actions.open_settings")
        )
        # self.close_page_act.setIcon(
        #     QtGui.QIcon(self.res_handler.get_res("assets.icons.exit"))
        # )
        self.addAction(self.close_page_act)
        self.addAction(self.open_settings_act)
