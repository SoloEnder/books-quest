import logging

from PySide6 import QtCore, QtWidgets

from app.src import book_sys
from app.ui import qt_signals_handler
from app.ui.pages import book_creation_page, shelf_creation_page, shelf_details_page, shelfs_pages


class UI(QtWidgets.QWidget):
    def __init__(self, books_handler):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.qt_signals_handler = qt_signals_handler.QtSignalsHandler()
        self.my_stacked_widgets = MyStackedWidgets(
            self, self.books_handler, self.qt_signals_handler
        )
        self.main_layout.addWidget(self.my_stacked_widgets)
        self.my_stacked_widgets.switch_page("shelfs_page")


class MyStackedWidgets(QtWidgets.QStackedWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        books_handler: book_sys.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        self.shelfs_page = shelfs_pages.ShelfsPage(
            self, self.books_handler, self.qt_signals_handler
        )
        self.book_creation_page = book_creation_page.BookCreationPage(
            self,
            self.books_handler,
            self.qt_signals_handler,
        )
        self.shelfs_view_page = shelfs_pages.ShelfsPage(
            self, self.books_handler, self.qt_signals_handler
        )
        self.shelf_creation_page = shelf_creation_page.ShelfCreationPage(
            self, self.books_handler, self.qt_signals_handler, mode="creation",
        )
        self.shelf_details_page = shelf_details_page.ShelfDetailsPage(self, self.books_handler.default_shelf, self.books_handler, self.qt_signals_handler)
        self.pages = {
            "shelfs_page": self.shelfs_page,
            "shelfs_view_page": self.shelfs_view_page,
            "book_creation_page": self.book_creation_page,
            "shelf_creation_page": self.shelf_creation_page,
            "shelf_details_page": self.shelf_details_page,

        }
        self.addWidget(self.shelfs_page)
        self.addWidget(self.book_creation_page)
        self.addWidget(self.shelfs_view_page)
        self.addWidget(self.shelf_creation_page)
        self.addWidget(self.shelf_details_page)
        self.history = []
        self.history.append(self.shelfs_page)
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
        to_update = page_name
        self.logger.debug(f"Refreshing {page_name} with kwargs {[page_args]}")

        for to_update_page in to_update:
            if to_update_page == "shelfs_page":
                self.removeWidget(self.shelfs_page)
                self.shelfs_page.setParent(None)
                self.shelfs_page.deleteLater()
                self.shelfs_page = shelfs_pages.ShelfsPage(
                    self,
                    self.books_handler,
                    self.qt_signals_handler,
                )
                self.pages["shelfs_page"] = self.shelfs_page
                self.addWidget(self.shelfs_page)

            elif to_update_page == "book_creation_page":
                self.removeWidget(self.book_creation_page)
                self.book_creation_page.setParent(None)
                self.book_creation_page.deleteLater()
                self.book_creation_page = book_creation_page.BookCreationPage(
                    self, self.books_handler, self.qt_signals_handler
                )
                self.pages["book_creation_page"] = self.book_creation_page
                self.addWidget(self.book_creation_page)

            elif to_update_page == "shelf_creation_page":
                self.removeWidget(self.shelf_creation_page)
                self.shelf_creation_page.setParent(None)
                self.shelf_creation_page.deleteLater()
                self.shelf_creation_page = shelf_creation_page.ShelfCreationPage(
                    self, self.books_handler, self.qt_signals_handler, **page_args
                )
                self.pages["shelf_creation_page"] = self.shelf_creation_page
                self.addWidget(self.shelf_creation_page)

            elif to_update_page == "shelf_details_page":
                self.removeWidget(self.shelf_details_page)
                self.shelf_details_page.setParent(None)
                self.shelf_details_page.deleteLater()
                self.shelf_details_page = shelf_details_page.ShelfDetailsPage(
                    self, 
                    page_args["shelf"], 
                    self.books_handler, 
                    self.qt_signals_handler,
                    )
                self.pages["shelf_details_page"] = self.shelf_details_page
                self.addWidget(self.shelf_details_page)

