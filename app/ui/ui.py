import logging
from re import PatternError

from PySide6 import QtCore, QtWidgets

from app.src import book
from app.ui.pages import book_creation_page, shelf_view_page, shelfs_pages


class UI(QtWidgets.QWidget):
    def __init__(self, books_handler):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.my_stacked_widgets = MyStackedWidgets(self, self.books_handler)
        self.main_layout.addWidget(self.my_stacked_widgets)
        self.my_stacked_widgets.switch_page("shelfs_page")


class MyStackedWidgets(QtWidgets.QStackedWidget):
    def __init__(
        self, parent: QtWidgets.QWidget | None, books_handler: book.BooksHandler
    ):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.shelfs_page = shelfs_pages.ShelfsPage(self, self.books_handler)
        self.book_creation_page = book_creation_page.BookCreationPage(
            self, self.books_handler
        )
        self.shelfs_view_page = shelfs_pages.ShelfsPage(self, self.books_handler)
        self.pages = {
            "shelfs_page": self.shelfs_page,
            "book_creation_page": self.book_creation_page,
            "shelfs_view_page": self.shelfs_view_page,
        }
        self.addWidget(self.shelfs_page)
        self.addWidget(self.book_creation_page)
        self.addWidget(self.shelfs_view_page)
        self.history = []
        self.history.append(self.shelfs_page)

    def switch_page(self, page_name: str, refresh: bool = False, **kwargs):
        """
        Change the current widget displayed by the value of <name> in the attribute <pages>

        Args:
            - page_name (str): the name of the page, a key of the attribute <pages>.
            - refresh (bool): if true, the page will be refreshed. default to False
        """

        if page_name in self.pages.keys():
            page_obj = self.pages[page_name]
            self.setCurrentWidget(page_obj)

            if refresh:
                self.refresh(page_name, **kwargs)
                self.history.append(page_obj)

        else:
            self.logger.error(f"Page <{page_name} not found !>")

    def go_back(self):
        self.switch_page(list(self.pages.keys())[self.indexOf(self.history[0])])

    def refresh(self, *pages_names, **kwargs):
        to_update = pages_names

        for to_update_page in to_update:
            if to_update_page == "shelfs_page":
                self.removeWidget(self.shelfs_page)
                self.shelfs_page.setParent(None)
                self.shelfs_page.deleteLater()
                self.shelfs_page = shelfs_pages.ShelfsPage(self, self.books_handler)
                self.pages["shelfs_page"] = self.shelfs_page
                self.addWidget(self.shelfs_page)

            elif to_update_page == "book_creation_page":
                self.removeWidget(self.book_creation_page)
                self.book_creation_page.setParent(None)
                self.book_creation_page.deleteLater()
                self.book_creation_page = book_creation_page.BookCreationPage(
                    self, self.books_handler
                )
                self.pages["book_creation_page"] = self.book_creation_page
                self.addWidget(self.book_creation_page)
