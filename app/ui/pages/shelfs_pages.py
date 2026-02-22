import logging
import os

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import book_stuff
from app.ui import qt_signals_handler
from app.utils import paths


class ShelfsPage(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        books_handler: book_stuff.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        self.main_layout = QtWidgets.QGridLayout(self)
        self.go_back_b = QtWidgets.QPushButton("Fermer")
        self.go_back_b.setIcon(
            QtGui.QIcon(os.path.join(paths.ICONS_PATH, "back_ico.png"))
        )
        self.go_back_b.clicked.connect(
            lambda: self.qt_signals_handler.go_previous_page_sg.emit(True)
        )
        self.add_book_b = QtWidgets.QPushButton("Nouveau livre")
        self.add_book_b.setIcon(
            QtGui.QIcon(os.path.join(paths.ICONS_PATH, "new_book_ico.png"))
        )
        self.add_book_b.clicked.connect(
            lambda: self.qt_signals_handler.switch_page_sg.emit(
                "book_creation_page", True, {}
            )
        )
        self.add_shelf_b = QtWidgets.QPushButton("Nouvelle étagère")
        self.shelfs_container = QtWidgets.QWidget(self)
        self.shelfs_container_layout = QtWidgets.QVBoxLayout(self.shelfs_container)
        self.shelfs_container.setLayout(self.shelfs_container_layout)
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.shelfs_container)

        # Shelf books view
        self.main_layout.addWidget(
            self.go_back_b, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_layout.addWidget(
            self.add_book_b, 1, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_layout.addWidget(
            self.add_shelf_b, 2, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )

        self.main_layout.addWidget(self.scroll_area, 3, 0)
        self.shelfs_widgets = []

        for index, shelf in enumerate(self.books_handler.books_shelfs.values()):
            shelf_widget = ShelfWidget(shelf)
            self.shelfs_widgets.append(shelf_widget)
            self.shelfs_container_layout.addWidget(
                shelf_widget, index, QtCore.Qt.AlignmentFlag.AlignTop
            )


class ShelfWidget(QtWidgets.QWidget):
    def __init__(self, shelf):
        super().__init__()
        self.icons_folder = paths.ICONS_PATH
        self.shelf = shelf
        # self.
        self.main_layout = QtWidgets.QGridLayout(self)
        self.cover_pm = QtGui.QPixmap(
            os.path.join(paths.DEFAULT_COVERS_PATH, "default_shelf_cover.png")
        )
        self.cover_lb = QtWidgets.QLabel()
        self.cover_lb.setPixmap(self.cover_pm)
        self.name_lb = QtWidgets.QLabel(self.shelf.name)
        self.name_lb.setStyleSheet("""
            font-weight: bold;
            font-size: 20px;
        """)
        self.total_books = QtWidgets.QLabel(f"{len(self.shelf.books)} livres")
        self.total_books.setStyleSheet("""
            font-size: 17px;
        """)
        self.unread_books_count = 0
        self.on_reading_books_count = 0
        self.finished_books_count = 0

        for book in self.shelf.books.values():
            if book.status == "unread":
                self.unread_books_count += 1

            elif book.status == "on_reading":
                self.on_reading_books_count += 1

            elif book.status == "finished":
                self.finished_books_count += 1

        self.unread_books_lb = QtWidgets.QLabel(f"{self.unread_books_count} non lus")
        self.on_reading_books_lb = QtWidgets.QLabel(
            f"{self.on_reading_books_count} en cours de lecture"
        )
        self.finished_books_lb = QtWidgets.QLabel(
            f"{self.finished_books_count} terminés"
        )
        self.total_pages = QtWidgets.QLabel("600 pages")
        self.total_pages.setStyleSheet("""
            font-style: italic;
            font-size: 16px;
        """)
        self.unread_books_lb.setIndent(10)
        self.on_reading_books_lb.setIndent(10)
        self.finished_books_lb.setIndent(10)

        self.button_size = QtWidgets.QSizePolicy()
        self.view_b = QtWidgets.QPushButton("Voir les livres")
        self.view_b.setIcon(
            QtGui.QIcon(os.path.join(self.icons_folder, "view_books_ico.png"))
        )
        self.view_b.setSizePolicy(self.button_size)

        self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.name_lb, 0, 0, 1, 2)
        self.main_layout.addWidget(self.cover_lb, 1, 0, 6, 1)
        self.main_layout.addWidget(self.total_books, 1, 1)
        self.main_layout.addWidget(self.unread_books_lb, 2, 1)
        self.main_layout.addWidget(self.on_reading_books_lb, 3, 1)
        self.main_layout.addWidget(self.finished_books_lb, 4, 1)
        self.main_layout.addWidget(self.view_b, 5, 1)


class BookWidget(QtWidgets.QWidget):
    def __init__(self, book):
        super().__init__()
        self.setStyleSheet("""
            border-style: solid;
            border-width: 56px;
        """)
        self.book = book
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.book_cover_lb = QtWidgets.QLabel(self)
        self.book_cover_lb.setPixmap(QtGui.QPixmap(self.book.cover_img_path))
        self.book_title_lb = QtWidgets.QLabel(self.book.title)
        self.book_title_lb.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)
        self.main_layout.addWidget(self.book_cover_lb, 0)
        self.main_layout.addWidget(self.book_title_lb, 1)
