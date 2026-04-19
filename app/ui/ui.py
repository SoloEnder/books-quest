import logging

from PySide6 import QtCore, QtWidgets, QtGui
import os

from app.src import book_sys
from app.ui import qt_signals_handler
from app.ui.pages import book_creation_page, shelf_creation_page, shelf_details_page, shelfs_view_page
from app.utils import utils_funcs
from app.utils import paths
from app.src import settings_handler

class UI(QtWidgets.QWidget):
    def __init__(self, books_handler, settings_handler: settings_handler.SettingsHandler):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.settings_handler = settings_handler
        self.main_layout = QtWidgets.QVBoxLayout(self)

        #Indev warning window
        #self.indev_warning_w = QtWidgets.QMessageBox()

        self.qt_signals_handler = qt_signals_handler.QtSignalsHandler()
        self.qt_signals_handler.raise_error_msg_sg.connect(self.show_error)
        self.my_stacked_widgets = MyStackedWidgets(
            self, self.books_handler, self.qt_signals_handler, self.settings_handler,
        )
        self.main_layout.addWidget(self.my_stacked_widgets)
        self.gen_qss_filepath = os.path.join(paths.QSS_FILES_PATH, "general.qss")
        utils_funcs.load_and_set_ss(self.gen_qss_filepath, widget=self.my_stacked_widgets, logger=self.logger)
        self.my_stacked_widgets.switch_page("shelfs_view_page")

    def show_indev_warn(self):
        """
        Show the in devellepoment warning window
        """
        
        #self.indev_warning_w.show()
        QtWidgets.QMessageBox.information(self, "Indev Warning", "This program is in developement ! If you see any bug which is not already reported, please report it <a href='https://github.com/SoloEnder/books-quest/issues'>here</a>")
        
    @QtCore.Slot(str)
    def show_error(self, error_msg: str|None):
        
        if not error_msg:
            error_msg = "Une erreur est survenue, veuillez réessayer"
        
        QtWidgets.QMessageBox.warning(self, "Error", error_msg)
            
        

class MyStackedWidgets(QtWidgets.QStackedWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        books_handler: book_sys.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        settings_handler,
    ):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        self.settings_handler = settings_handler

        self.shelfs_view_page = shelfs_view_page.ShelfsViewPage(
            self, self.books_handler, self.qt_signals_handler, self.settings_handler, 
        )
        self.shelf_details_page = shelf_details_page.ShelfDetailsPage(self, self.books_handler.default_shelf, self.books_handler, self.qt_signals_handler, self.settings_handler,)
        self.book_creation_page = book_creation_page.BookCreationPage(
            self,
            self.books_handler,
            self.qt_signals_handler,
            self.settings_handler,
        )
        self.shelf_creation_page = shelf_creation_page.ShelfCreationPage(
            self, self.books_handler, self.qt_signals_handler, self.settings_handler, mode="creation",
        )
        self.pages = {
            "shelfs_view_page": self.shelfs_view_page,
            "shelf_details_page": self.shelf_details_page,
            "book_creation_page": self.book_creation_page,
            "shelf_creation_page": self.shelf_creation_page,
        }
        self.addWidget(self.shelfs_view_page)
        self.addWidget(self.book_creation_page)
        self.addWidget(self.shelfs_view_page)
        self.addWidget(self.shelf_creation_page)
        self.history = []
        self.history.append(self.shelfs_view_page)
        self.qt_signals_handler.switch_page_sg.connect(self.switch_page)
        self.qt_signals_handler.go_previous_page_sg.connect(self.go_back)

    @QtCore.Slot(str, bool, dict)
    def switch_page(self, page_name: str, refresh: bool = False, page_args={}):
        """
        Change the current widget displayed by the value of <name> in the attribute <pages>

        Args:
            - page_name (str): the name of the page, a key of the attribute <pages>.
            - refresh (bool): if true, the page will be refreshed. default to False
        """

        self.logger.info(f"Switching to page <{page_name}>...")
        if page_name in self.pages.keys():
            if refresh:
                self.refresh(page_name, page_args)

            page_obj = self.pages[page_name]
            self.setCurrentWidget(page_obj)

            self.history.insert(0, page_name)

        else:
            self.logger.error(f"Page <{page_name}> not found !")

    @QtCore.Slot(bool)
    def go_back(self, refresh: bool):
        self.switch_page(
            self.history[1] if len(self.history) >= 1 else self.history[0],
            True if refresh else False,
        )

    def refresh(self, page_name, page_args: dict = {}):
        self.logger.debug(f"Refreshing {page_name} with kwargs {page_args}")
        if page_name == "shelfs_view_page":
            self.removeWidget(self.shelfs_view_page)
            self.shelfs_view_page.setParent(None)
            self.shelfs_view_page.deleteLater()
            self.shelfs_view_page = shelfs_view_page.ShelfsViewPage(
                self,
                self.books_handler,
                self.qt_signals_handler,
                self.settings_handler,
            )
            self.pages["shelfs_view_page"] = self.shelfs_view_page
            self.addWidget(self.shelfs_view_page)

        elif page_name == "book_creation_page":
            self.removeWidget(self.book_creation_page)
            self.book_creation_page.setParent(None)
            self.book_creation_page.deleteLater()
            self.book_creation_page = book_creation_page.BookCreationPage(
                self, 
                self.books_handler, 
                self.qt_signals_handler, 
                self.settings_handler,
            )
            self.pages["book_creation_page"] = self.book_creation_page
            self.addWidget(self.book_creation_page)

        elif page_name == "shelf_creation_page":
            self.removeWidget(self.shelf_creation_page)
            self.shelf_creation_page.setParent(None)
            self.shelf_creation_page.deleteLater()
            self.shelf_creation_page = shelf_creation_page.ShelfCreationPage(
                self, 
                self.books_handler, 
                self.qt_signals_handler, 
                self.settings_handler,
                **page_args,
            )
            self.pages["shelf_creation_page"] = self.shelf_creation_page
            self.addWidget(self.shelf_creation_page)

        elif page_name == "shelf_details_page":
            self.removeWidget(self.shelf_details_page)
            self.shelf_details_page.setParent(None)
            self.shelf_details_page.deleteLater()
            self.shelf_details_page = shelf_details_page.ShelfDetailsPage(
                self, 
                page_args["shelf"], 
                self.books_handler, 
                self.qt_signals_handler,
                self.settings_handler,
                )
            self.pages["shelf_details_page"] = self.shelf_details_page
            self.addWidget(self.shelf_details_page)

class IndevWarnWidget(QtWidgets.QMessageBox):

    def __init__(self, parent: QtWidgets.QWidget|None):
        super().__init__(parent)

        #Setting window title
        self.setWindowTitle("Indev Warning")

        #Setting text
        self.setText("This program is in developement ! If you see any bug which is not already reported, please report it <a href='https://github.com/SoloEnder/books-quest/issues'>here</a>")
    


