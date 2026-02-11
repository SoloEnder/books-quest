
import logging
from PySide6 import QtWidgets, QtCore
from app.ui.pages import books_page, book_creation_page

class UI(QtWidgets.QWidget):

    def __init__(self, books_handler):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.stacked_widgets = MyStackedWidgets(self)
        self.main_layout.addWidget(self.stacked_widgets)
        self.books_page = books_page.BooksPage(parent=self.stacked_widgets, books_handler=self.books_handler)
        self.book_creation_page = book_creation_page.BookCreationPage(self.stacked_widgets, self.books_handler)
        self.stacked_widgets.add_page("books_page", self.books_page)
        self.stacked_widgets.add_page("book_creation_page", self.book_creation_page)

class MyStackedWidgets(QtWidgets.QStackedWidget):

    def __init__(self, parent: QtWidgets.QWidget|None=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.pages = {}
        self.history = []
        self.default_page = {}

    def switch_page(self, page_name: str):
        """
        Switch widget displayed by the stacked widget to <page_name>. <page_name> must be in the <pages> attribut.

        page_name (str): the page name (a key of the <pages> attribut)
        """
        self.logger.info(f"Switching to page <{page_name}>...")

        if page_name in self.pages.keys():
            self.setCurrentIndex(self.pages[page_name])
            self.history.append(page_name)

        else:
            self.logger.error(f"Page <{page_name}> dosen't exists !")

    def add_page(self, page_name, page_obj):
        """
        Add a new page. Use this instead of the method <addWidget()> only for better organisation 
        """
        self.pages[page_name] = self.addWidget(page_obj)

        if not self.default_page:
            self.default_page = {page_name:self.pages[page_name]}

    def switch_to_default_page(self):
        self.switch_page(list(self.default_page.keys())[0])

        