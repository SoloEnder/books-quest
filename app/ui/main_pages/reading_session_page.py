import enum
import logging

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import api, book_sys, timer
from app.ui.main_pages import base_page

logger = logging.getLogger(__name__)


class ReadingSessionPage(base_page.BasePage):
    def __init__(self, parent: QtWidgets.QWidget | None, api: api.API, book_id: str):
        super().__init__(parent, api)
        self._book = (
            self.books.books_handler.default_book
            if book_id == self.books.books_handler.default_book.str_id()
            else self.books.books_handler.books[book_id]
        )

        # Widgets
        self.currently_reading_book_title_lb = QtWidgets.QLabel(
            f'Reading "{self._book.title}"...'
        )
        self.time_lb = QtWidgets.QLabel()
        self.timer_action_b = QtWidgets.QPushButton("Pause")
        self.main_lyt.addWidget(
            self.currently_reading_book_title_lb,
            0,
            0,
            QtCore.Qt.AlignmentFlag.AlignCenter,
        )
        self.main_lyt.addWidget(self.time_lb, 1, 0, QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_lyt.addWidget(
            self.timer_action_b, 2, 0, QtCore.Qt.AlignmentFlag.AlignCenter
        )
