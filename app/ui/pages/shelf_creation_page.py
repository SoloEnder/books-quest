import datetime as dt
import os

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import book_stuff
from app.ui import qt_signals_handler
from app.utils import paths


class ShelfCreationPage(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        books_handler: book_stuff.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(parent)
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler

        self.main_lyt = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_lyt)
        self.main_widget = QtWidgets.QWidget()
        self.main_widget_lyt = QtWidgets.QGridLayout()
        self.main_widget.setLayout(self.main_widget_lyt)

        # Back button
        self.back_b = QtWidgets.QPushButton("Fermer")
        self.back_b.setIcon(QtGui.QIcon(os.path.join(paths.ICONS_PATH, "back_ico.png")))
        self.back_b.clicked.connect(
            lambda: self.qt_signals_handler.go_previous_page_sg.emit(True)
        )
        self.main_lyt.addWidget(self.back_b, 0, QtCore.Qt.AlignmentFlag.AlignLeft)

        # Scroll area
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.main_widget)
        self.main_lyt.addWidget(self.scroll_area, 1)

        # Shelf name input widget
        self.name_lb = QtWidgets.QLabel("Nom : ")
        self.name_e = QtWidgets.QLineEdit()
        self.name_e.setMinimumWidth(300)

        # Books selection widgets
        self.books_selection_lb = QtWidgets.QLabel("Livres : ")
        self.books_tree = QtWidgets.QTreeView()
        self.books_tree_model = QtGui.QStandardItemModel()
        self.books_tree_model.setHorizontalHeaderLabels(("Titre", "Auteur", "Edition"))
        self.books_tree.setModel(self.books_tree_model)
        self.books_title_items = []

        # Books items

        for book in self.books_handler.books.values():
            book_title_item = QtGui.QStandardItem(book.title)
            book_title_item.setData(book)
            book_title_item.setCheckable(True)
            book_author_item = QtGui.QStandardItem(book.authors)
            book_edition_item = QtGui.QStandardItem(book.edition)
            self.books_tree_model.appendRow(
                (book_title_item, book_author_item, book_edition_item)
            )
            self.books_title_items.append(book_title_item)

        self.books_tree.setColumnWidth(0, 150)
        self.books_tree.setColumnWidth(1, 150)
        self.books_tree.setColumnWidth(2, 150)
        self.books_tree.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )

        # Confirm widgets
        self.confirm_b = QtWidgets.QPushButton("Terminé")
        self.confirm_b.clicked.connect(self.create_shelf)

        # Add the widgets tot the layout
        self.main_widget_lyt.addWidget(
            self.name_lb, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_widget_lyt.addWidget(
            self.name_e, 1, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_widget_lyt.addWidget(
            self.books_selection_lb, 2, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_widget_lyt.addWidget(self.books_tree, 3, 0)
        self.main_widget_lyt.addWidget(
            self.confirm_b, 4, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )

    def get_shelf_infos(self) -> dict | None:
        shelf_name = self.name_e.text()
        shelfs_books = {}

        for book_title_item in self.books_title_items:
            book_obj = book_title_item.data()
            shelfs_books[book_obj.internal_id] = book_obj

        if shelf_name.lower() != "tout les livres":
            return {
                "name": shelf_name,
                "books": shelfs_books,
                "id": str(dt.datetime.timestamp(dt.datetime.now())).replace(".", ""),
            }

        else:
            return

    def create_shelf(self):
        shelf_infos = self.get_shelf_infos()

        if shelf_infos:
            self.books_handler.create_shelf(**shelf_infos)
