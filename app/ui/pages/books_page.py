
import os
import logging
from PIL import Image
from app.utils import paths
from PySide6 import QtWidgets, QtCore, QtGui

class BooksPage(QtWidgets.QWidget):

    def __init__(self, books_handler, parent: QtWidgets.QWidget|None=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.main_layout = QtWidgets.QGridLayout(self)
        self.add_book_b = QtWidgets.QPushButton("Nouveau livre")
        self.add_book_b.clicked.connect(lambda: self.parent().switch_page("book_creation_page"))
        self.add_shelf_b = QtWidgets.QPushButton("Nouvelle étagère")
        self.shelfs_container = QtWidgets.QWidget(self)
        self.shelfs_container_layout = QtWidgets.QVBoxLayout(self.shelfs_container)
        self.shelfs_container.setLayout(self.shelfs_container_layout)
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.shelfs_container)
        self.main_layout.addWidget(self.add_book_b, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.add_shelf_b, 1, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.scroll_area, 2, 0)
        self.shelfs_widgets = []
        self.watchdog_timer = QtCore.QTimer(self)
        self.watchdog_timer.timeout.connect(self.watchdog)
        self.watchdog_timer.start(1000)

    def watchdog(self):

        if self.books_handler.shelfs_updated == True:
            self.refresh()
        self.books_handler.shelfs_updated = False

    def refresh(self):

        for shelf_widget in self.shelfs_widgets:
            shelf_widget.setParent(None)
            shelf_widget.deleteLater()

        self.shelfs_widgets.clear()

        for index, shelf in enumerate(self.books_handler.books_shelfs.values()):
            shelf_widget = ShelfWidget(shelf)
            self.shelfs_widgets.append(shelf_widget)
            self.shelfs_container_layout.addWidget(shelf_widget, index)

    def create_shelf_widget(self, shelf):
        self.shelf_widget = ShelfWidget(self)
        self.shelfs_widgets.insert(4, self.shelf_widget)
        return self.shelf_widget

class ShelfWidget(QtWidgets.QWidget):

    def __init__(self, shelf):
        super().__init__()
        self.icons_folder = paths.get_abspath("app/assets/icons")
        self.shelf = shelf
        self.main_layout = QtWidgets.QGridLayout(self)
        self.cover_pm = QtGui.QPixmap("app/assets/default_shelf_cover.png")
        self.cover_lb = QtWidgets.QLabel()
        self.cover_lb.setPixmap(self.cover_pm)
        self.name_lb = QtWidgets.QLabel(self.shelf.name)
        self.name_lb.setStyleSheet("""
            font-weight: bold;
            font-size: 20px;
        """)
        self.total_books = QtWidgets.QLabel(f"{len(self.shelf.books)} books")
        self.total_books.setStyleSheet("""
            font-size: 17px;
        """)
        self.total_pages = QtWidgets.QLabel("600 pages")
        self.total_pages.setStyleSheet("""
            font-style: italic;
            font-size: 16px;
        """)
        self.button_size = QtWidgets.QSizePolicy()
        self.add_book_b = QtWidgets.QPushButton("Ajouter un livre")
        self.add_book_b.setSizePolicy(self.button_size)
        self.add_book_b.setIcon(QtGui.QIcon(str(os.path.join(self.icons_folder, "add_ico"))))
        self.edit_b = QtWidgets.QPushButton("Editer")
        self.edit_b.setIcon(QtGui.QIcon(os.path.join(self.icons_folder, "edit_ico.png")))
        self.edit_b.setSizePolicy(self.button_size)
        self.view_b = QtWidgets.QPushButton("Voir les livres")
        self.view_b.setIcon(QtGui.QIcon(os.path.join(self.icons_folder, "view_books_ico.png")))
        self.view_b.setSizePolicy(self.button_size)
        self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.cover_lb, 0, 0, 6, 1)
        self.main_layout.addWidget(self.name_lb, 0, 1)
        self.main_layout.addWidget(self.total_books, 1, 1)
        self.main_layout.addWidget(self.total_pages, 2, 1)
        self.main_layout.addWidget(self.add_book_b, 3, 1, 1, 1)
        self.main_layout.addWidget(self.edit_b, 4, 1, 1, 1)
        self.main_layout.addWidget(self.view_b, 5, 1, 1, 1)

class BookWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.book_title_lb = QtWidgets.QLabel("Le Manoir de CastleCatz")
        self.book_description_tb = QtWidgets.QTextEdit("Ceci est un résumé !")
        self.book_description_tb.setReadOnly(True)
        self.grid_layout.addWidget(self.book_title_lb)
        self.grid_layout.addWidget(self.book_description_tb)
