
from app.src import book_sys
from app.utils import paths
from app.ui import qt_signals_handler
from app.utils import utils_funcs
from PySide6 import QtWidgets, QtCore, QtGui
import os
import logging

class ShelfDetailsPage(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget|None, shelf: book_sys.Shelf, books_handler: book_sys.BooksHandler, qt_signals_handler: qt_signals_handler.QtSignalsHandler):
        super().__init__(parent)
        self.shelf = shelf
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        
        #Widgets
        self.main_lyt = QtWidgets.QGridLayout()
        self.setLayout(self.main_lyt)
        self.main_widget = QtWidgets.QWidget()
        self.books_widgets = []

        #close button
        self.close_b = QtWidgets.QPushButton("Fermer")
        self.close_b.setIcon(QtGui.QIcon(os.path.join(paths.ICONS_PATH, "cross_ico.png")))
        self.close_b.clicked.connect(
            lambda: self.qt_signals_handler.go_previous_page_sg.emit(True)
        )

        #books widgets containers
        self.books_container_widget = QtWidgets.QWidget()
        self.books_container_lyt = QtWidgets.QGridLayout()
        self.books_container_widget.setLayout(self.books_container_lyt)
        self.books_container_sa = QtWidgets.QScrollArea()
        self.books_container_sa.setWidgetResizable(True)
        self.books_container_sa.setWidget(self.books_container_widget)

        #books widgets
        self.generate_books_widgets(self.books_handler.books)

        #Adding widgets to layout
        self.main_lyt.addWidget(self.close_b, 0, 0)
        self.main_lyt.addWidget(self.books_container_sa, 1, 0)

    def generate_books_widgets(self, books: dict|None=None):
        self.books_widgets.clear()

        if not books:
            books = self.books_handler.books

        for index, book in enumerate(books.values()):
            book_widget = BookWidget(book)
            self.books_widgets.append(book_widget)
            self.books_container_lyt.addWidget(book_widget, index, 0)

class BookWidget(QtWidgets.QWidget):
    def __init__(self, book: book_sys.Book):
        super().__init__()
        #self.setStyleSheet("""
        #    border-style: solid;
        #    border-width: 56px;
        #""")
        self.logger = logging.getLogger(__name__)
        self.default_cover_path = os.path.join(paths.DEFAULT_COVERS_PATH, "default_book_cover.png")
        self.qss_filepath = os.path.join(paths.QSS_FILES_PATH, "book_widget.qss")
        utils_funcs.load_and_set_ss(self.qss_filepath, self, self.logger)
        self.book = book
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.book_cover_lb = QtWidgets.QLabel(self)

        if self.book.cover_img_path:
            self.book_cover_lb.setPixmap(QtGui.QPixmap(self.book.cover_img_path))

        else:
            self.book_cover_lb.setPixmap(QtGui.QPixmap(self.default_cover_path))
            
        self.book_title_lb = QtWidgets.QLabel(self.book.title if self.book.title else utils_funcs.unknown_book_title_fmt(self.book))
        self.book_title_lb.setObjectName("book_title_lb")
        self.main_layout.addWidget(self.book_title_lb, 1)
        self.main_layout.addWidget(self.book_cover_lb, 0)

