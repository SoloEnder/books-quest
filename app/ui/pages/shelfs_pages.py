import datetime as dt
import logging
import os
from app.utils import utils_funcs

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import book_sys
from app.ui import qt_signals_handler
from app.utils import paths


class ShelfsPage(QtWidgets.QWidget):
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
        self.main_layout = QtWidgets.QGridLayout(self)
        self.go_back_b = QtWidgets.QPushButton("Fermer")
        self.go_back_b.setIcon(
            QtGui.QIcon(os.path.join(paths.ICONS_PATH, "cross_ico.png"))
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
        self.add_shelf_b.clicked.connect(
            lambda: self.qt_signals_handler.switch_page_sg.emit(
                "shelf_creation_page", True, {"mode": "creation"}
            )
        )
        self.shelfs_container = QtWidgets.QWidget(self)
        self.shelfs_container_layout = QtWidgets.QVBoxLayout(self.shelfs_container)
        self.shelfs_container.setLayout(self.shelfs_container_layout)
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.shelfs_container)

        # Shelf books view
        # self.main_layout.addWidget(
        # self.go_back_b, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        # )
        self.main_layout.addWidget(
            self.add_book_b, 1, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_layout.addWidget(
            self.add_shelf_b, 2, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )

        self.main_layout.addWidget(self.scroll_area, 3, 0)
        self.default_shelf_widget = DefaultShelfWidget(
            self.books_handler.default_shelf,
            self.books_handler,
            self.qt_signals_handler,
        )
        self.shelfs_container_layout.addWidget(
            self.default_shelf_widget, QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.shelfs_widgets = []
        self.generate_shelfs_widgets(self.books_handler.books_shelfs)

    def load_shelfs_widgets_ss(self):
        filepath = os.path.join(paths.QSS_FILES_PATH, "shelf_widget.qss")

        try:
            with open(filepath, "r") as f:
                return f.read()

        except:
            self.logger.exception(f"Couldn't load shelfs widgets stylesheet from file {filepath}")

    def generate_shelfs_widgets(self, shelfs: dict|None=None):
        stylesheet = self.load_shelfs_widgets_ss()

        if not shelfs:
            shelfs = self.books_handler.books_shelfs

        self.shelfs_widgets.clear()
        names = set()

        for index, shelf in enumerate(shelfs.values()):
            shelf_widget = ShelfWidget(
                shelf, self.books_handler, self.qt_signals_handler
            )
            if stylesheet:
                shelf_widget.setStyleSheet(stylesheet)

            displayed_name = shelf_widget.name_lb.text()
            matches_count = 0
            for name in names:
                if name == displayed_name and not shelf.name:
                    matches_count += 1

            if matches_count:
                shelf_widget.name_lb.setText(f"{displayed_name} ({str(matches_count)})")

            names.add(displayed_name)
            self.shelfs_widgets.append(shelf_widget)
            self.shelfs_container_layout.addWidget(
                shelf_widget, index + 1, QtCore.Qt.AlignmentFlag.AlignTop
            )

class ShelfWidget(QtWidgets.QWidget):
    def __init__(
        self,
        shelf: book_sys.Shelf,
        books_handler: book_sys.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__()
        self.icons_folder = paths.ICONS_PATH
        self.shelf = shelf
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        self.logger = logging.getLogger(__name__)

        self.main_layout = QtWidgets.QGridLayout(self)
        self.default_cover = os.path.join(
            paths.DEFAULT_COVERS_PATH, "default_shelf_cover.png"
        )

        if self.shelf.cover_path:
            if os.path.exists(self.shelf.cover_path):
                self.displayed_cover = self.shelf.cover_path

            else:
                self.displayed_cover = self.default_cover
                self.logger.warning(f"Couldn't found shelf cover file at {self.shelf.cover_path}, switching to default cover")

        else:
            self.displayed_cover = self.default_cover

        self.cover_pm = QtGui.QPixmap(self.displayed_cover)
        self.cover_lb = QtWidgets.QLabel()
        self.cover_lb.setPixmap(self.cover_pm)
        self.name_lb = QtWidgets.QLabel(
            self.shelf.name
            if self.shelf.name
            else utils_funcs.unknown_shelf_name_fmt(self.shelf)
        )
        self.name_lb.setObjectName("name_lb")
        self.total_books = QtWidgets.QLabel(f"{len(self.shelf.books_ids)} livres")
        self.total_books.setObjectName("total_books_lb")
        self.unread_books_count = 0
        self.on_reading_books_count = 0
        self.finished_books_count = 0

        for book_id in self.shelf.books_ids:
            book = self.books_handler.books[book_id]
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
        self.unread_books_lb.setIndent(10)
        self.on_reading_books_lb.setIndent(10)
        self.finished_books_lb.setIndent(10)

        self.button_size = QtWidgets.QSizePolicy()
        self.view_b = QtWidgets.QPushButton("Voir les livres")
        self.view_b.setIcon(
            QtGui.QIcon(os.path.join(self.icons_folder, "view_books_ico.png"))
        )
        self.view_b.setSizePolicy(self.button_size)
        self.view_b.clicked.connect(lambda: self.qt_signals_handler.switch_page_sg.emit("shelf_details_page", True, {"shelf":self.shelf}))

        self.edit_b = QtWidgets.QPushButton("Modifier")
        self.edit_b.setIcon(
            QtGui.QIcon(os.path.join(self.icons_folder, "edit_ico.png"))
        )
        self.edit_b.clicked.connect(
            lambda: self.qt_signals_handler.switch_page_sg.emit(
                "shelf_creation_page", True, {"mode": "edition", "shelf": self.shelf}
            )
        )
        self.edit_b.setSizePolicy(self.button_size)

        self.delete_b = QtWidgets.QPushButton("Supprimer")
        self.delete_b.setProperty("role", "delete_b")
        self.delete_b.setIcon(
            QtGui.QIcon(os.path.join(self.icons_folder, "cross_ico.png"))
        )
        self.delete_b.setSizePolicy(self.button_size)
        self.delete_b.clicked.connect(self.delete_shelf)

        self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.name_lb, 0, 0, 1, 2)
        self.main_layout.addWidget(self.cover_lb, 1, 0, 8, 1)
        self.main_layout.addWidget(self.total_books, 1, 1)
        self.main_layout.addWidget(self.unread_books_lb, 2, 1)
        self.main_layout.addWidget(self.on_reading_books_lb, 3, 1)
        self.main_layout.addWidget(self.finished_books_lb, 4, 1)
        self.main_layout.addWidget(self.view_b, 5, 1)
        self.main_layout.addWidget(self.edit_b, 6, 1)
        self.main_layout.addWidget(self.delete_b, 7, 1)

        # The book creation information

    def delete_shelf(self):
        self.books_handler.remove_shelf(self.shelf.id)
        self.qt_signals_handler.switch_page_sg.emit("shelfs_page", True, {})


class DefaultShelfWidget(ShelfWidget):
    def __init__(
        self,
        shelf: book_sys.Shelf,
        books_handler: book_sys.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(shelf, books_handler, qt_signals_handler)
        self.edit_b.hide()
        self.delete_b.hide()
        self.main_layout.removeWidget(self.cover_lb)
        self.main_layout.addWidget(self.cover_lb, 1, 0, 6, 1)



