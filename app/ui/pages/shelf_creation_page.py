from PySide6 import QtCore, QtWidgets

from app.src import book_stuff
from app.ui import qt_signals_handler


class ShelfCreationPage(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        books_handler: book_stuff.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(parent)

        self.main_widget = QtWidgets.QWidget()
        self.main_lyt = QtWidgets.QGridLayout()
        self.setLayout(self.main_lyt)
        self.main_lyt.addWidget(self.main_widget)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self)
