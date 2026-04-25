
from app.src import book_sys
from app.utils import paths
from app.ui import qt_signals_handler
from app.utils import utils_funcs
from PySide6 import QtWidgets, QtCore, QtGui
import os
import logging

class ShelfDetailsPage(QtWidgets.QWidget):

    def __init__(
        self, 
        parent: QtWidgets.QWidget|None, 
        shelf: book_sys.Shelf, books_handler: book_sys.BooksHandler, 
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        settings_handler,
        ):
        
        super().__init__(parent)
        self.shelf = shelf
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        self.settings_handler = settings_handler

        #logger
        self.logger = logging.getLogger(__name__)
        
        #Widgets
        self.gen_qss_filepath = os.path.join(paths.QSS_FILES_PATH, "general.qss")
        self.page_qss_filepath = os.path.join(paths.QSS_FILES_PATH, "shelf_details_page.qss")
        utils_funcs.load_and_set_ss(self.gen_qss_filepath, self.page_qss_filepath, widget=self, logger=self.logger)
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

        self.nothing_to_show_lb = QtWidgets.QLabel("Aucun livre ici, pourquoi ne pas en ajouter un ?")
        self.nothing_to_show_lb.setProperty("role", "nothing_to_show_lb")
        self.nothing_to_show_lb.hide()

        #books widgets containers
        self.books_container_widget = QtWidgets.QWidget()
        self.books_container_lyt = QtWidgets.QGridLayout()
        self.books_container_widget.setLayout(self.books_container_lyt)
        self.books_container_sa = QtWidgets.QScrollArea()
        self.books_container_sa.setWidgetResizable(True)
        self.books_container_sa.setWidget(self.books_container_widget)
        self.books_container_lyt.addWidget(self.nothing_to_show_lb, 0, 0, QtCore.Qt.AlignmentFlag.AlignCenter)

        #books widgets
        self.books = self.books_handler.convert_book_id(self.shelf.books_ids)
        self.generate_books_widgets(self.books)

        #Adding widgets to layout
        self.main_lyt.addWidget(self.close_b, 0, 0)
        self.main_lyt.addWidget(self.books_container_sa, 1, 0)

    def generate_books_widgets(self, books: dict|None=None):
        self.books_widgets.clear()

        if books is None:
            books = self.books_handler.books

        base_displayed_titles = []

        for index, book in enumerate(books.values()):
            book_widget = BookWidget(book)
            base_displayed_titles.append(book_widget.book_title_lb.text())
            book_widget.book_title_lb.setText(utils_funcs.set_displayed_names(base_displayed_titles)[index])
            self.books_widgets.append(book_widget)
            self.books_container_lyt.addWidget(book_widget, index, 0)

        if len(self.books_widgets) == 0:
            self.nothing_to_show_lb.show()

class BookWidget(QtWidgets.QWidget):
    def __init__(self, book: book_sys.Book):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.default_cover_path = os.path.join(paths.DEFAULT_COVERS_PATH, "default_book_cover.png")
        self.book = book
        self.main_layout = QtWidgets.QGridLayout(self)
        self.book_cover_lb = QtWidgets.QLabel(self)

        if self.book.cover_path:

            if os.path.exists(self.book.cover_path):
                self.book_cover_lb.setPixmap(QtGui.QPixmap(self.book.cover_path))

            else:
                self.logger.warning(f"Couldn't found cover file for book with ID={self.book.internal_id}, switching to default cover")
                self.book_cover_lb.setPixmap(QtGui.QPixmap(self.default_cover_path))

        else:
            self.book_cover_lb.setPixmap(QtGui.QPixmap(self.default_cover_path))

        self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.fixed_sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.book_title_lb = QtWidgets.QLabel(self.book.title if self.book.title else utils_funcs.unknown_book_title_fmt(self.book))
        self.book_title_lb.setObjectName("book_title_lb")
        self.book_authors_lb = QtWidgets.QLabel(self.book.authors if self.book.authors else "Unknown")
        self.book_authors_lb.setObjectName("book_authors_lb")
        self.book_summary_te = QtWidgets.QTextEdit()
        self.book_summary_te.setText(self.book.summary if self.book.summary else "")
        self.book_summary_te.setReadOnly(True)
        self.book_summary_te.setObjectName("book_summary_te")
        self.edit_b = QtWidgets.QPushButton("Modifier")
        self.edit_b.setObjectName("edit_b")
        self.edit_b.setSizePolicy(self.fixed_sp)
        self.delete_b = QtWidgets.QPushButton("Supprimer")
        self.delete_b.setSizePolicy(self.fixed_sp)
        self.delete_b.setObjectName("delete_b")
        self.main_layout.addWidget(self.book_title_lb, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.book_authors_lb, 1, 1)
        self.main_layout.addWidget(self.book_summary_te, 2, 1)
        self.main_layout.addWidget(self.edit_b, 3, 1)
        self.main_layout.addWidget(self.delete_b, 4, 1)
        self.main_layout.addWidget(self.book_cover_lb, 1, 0, self.main_layout.rowCount(), 1)

