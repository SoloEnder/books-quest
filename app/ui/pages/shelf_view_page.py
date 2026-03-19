from PySide6 import QtWidgets

from app.src import book_sys


class ShelfViewPage(QtWidgets.QWidget):
    def __init__(self, parent: None | QtWidgets.QWidget, shelf) -> None:
        super().__init__(parent)
        self.shelf = shelf

        # Main layout
        self.main_layout = QtWidgets.QGridLayout(self)
        self.setLayout(self.main_layout)

        self.actions_widget = QtWidgets.QWidget()
        self.edit_b = QtWidgets.QPushButton("Modifier")
        self.main_layout.addWidget(self.edit_b)


class ShelfActionsWidget(QtWidgets.QWidget):
    def __init__(
        self, parent: QtWidgets.QWidget | None, books_handler: book_sys.BooksHandler
    ) -> None:
        super().__init__(parent)
        self.books_handler = books_handler

        # Main Layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # Widgets
        self.edit_b = QtWidgets.QPushButton("Editer")
