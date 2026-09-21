import logging

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import api, book_sys
from app.ui.main_pages import base_page


class ReadingSessionPage(base_page.BasePage):
    def __init__(self, parent: QtWidgets.QWidget | None, api: api.API, book_id: str):
        super().__init__(parent, api)
        self._book = (
            self.books.books_handler.default_book
            if book_id == self.books.books_handler.default_book.str_id()
            else self.books.books_handler.books[book_id]
        )
