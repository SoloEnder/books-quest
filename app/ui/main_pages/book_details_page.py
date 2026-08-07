import logging

import widgets_pagination_view
from PySide6 import QtCore, QtGui, QtWidgets

from app.src import book_sys, langs_handler, resources_handler, settings_handler
from app.ui import qt_signals_handler
from app.ui.main_pages import base_page
from app.utils import images_tools, my_exceptions, utils_funcs


class BookDetailsPage(base_page.BasePage):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        res_handler: resources_handler.RessourcesHandler,
        settings_handler: settings_handler.SettingsHandler,
        langs_handler: langs_handler.LangsHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        books_handler: book_sys.BooksHandler,
        book: book_sys.Book,
    ):
        super().__init__(
            parent, res_handler, settings_handler, langs_handler, qt_signals_handler
        )
        self.books_handler = books_handler
        self._book = book
        self.book_widget = BookWidget(
            self.book,
            self.books_handler,
            self.res_handler,
            self.langs_handler,
            self.qt_signals_handler,
        )
        self.main_lyt.addWidget(self.book_widget)

    @property
    def book(self):
        return self._book


class BookWidget(widgets_pagination_view.InPageWidget):
    def __init__(
        self,
        book: book_sys.Book,
        books_handler: book_sys.BooksHandler,
        res_handler: resources_handler.RessourcesHandler,
        langs_handler: langs_handler.LangsHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(None, None)
        self.logger = logging.getLogger(__name__)
        self.book = book
        self.books_handler = books_handler
        self.res_handler = res_handler
        self.langs_handler = langs_handler
        self.redundant_lang_path = "main_pages.shelf_details_page"
        self.qt_signals_handler = qt_signals_handler

        self.main_layout = QtWidgets.QGridLayout(self)
        self.book_title_lb = QtWidgets.QLabel(
            utils_funcs.add_title_suffix(book.title, title_suffix=book.title_suffix)
        )
        self.sub_widget = SubBookWidget(
            self.book,
            self.books_handler,
            self.res_handler,
            self.langs_handler,
            self.qt_signals_handler,
        )
        self.book_title_lb.setObjectName("BookTitleLabel")
        self.sub_widget.delete_b.clicked.connect(self.delete_book)
        self.max_sp = QtWidgets.QSizePolicy()
        self.max_sp.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Maximum)
        self.max_sp.setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Maximum)
        self.setSizePolicy(QtWidgets.QSizePolicy())
        self.main_layout.addWidget(
            self.book_title_lb,
            0,
            0,
            QtCore.Qt.AlignmentFlag.AlignLeft,
            QtCore.Qt.AlignmentFlag.AlignTop,
        )
        self.main_layout.addWidget(
            self.sub_widget,
            1,
            0,
            QtCore.Qt.AlignmentFlag.AlignLeft,
            QtCore.Qt.AlignmentFlag.AlignTop,
        )

    def delete_book(self):

        if self.pages_widgets_handler:
            self.logger.info(f"Deleting book with ID={self.book.id}")
            self.qt_signals_handler.edit_progress_msg.emit(
                self.langs_handler.tr("book.msg.book_deletion", count=1)
            )

            try:
                self.books_handler.delete_book(self.book.str_id())

            except my_exceptions.BookNotFoundError:
                self.logger.error(
                    f"Failed to delete book with ID={self.book.id} : Book not found in BooksHandler ({self.books_handler}) !"
                )
                self.qt_signals_handler.notify_sg.emit(
                    "error",
                    "",
                    self.langs_handler.tr("book.msg.book_not_found"),
                    "",
                )

            self.pages_widgets_handler.delete_widget(self)
            self.qt_signals_handler.edit_progress_msg.emit(" ")


class SubBookWidget(QtWidgets.QWidget):
    def __init__(
        self,
        book: book_sys.Book,
        books_handler: book_sys.BooksHandler,
        res_handler: resources_handler.RessourcesHandler,
        langs_handler: langs_handler.LangsHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(None)
        self.logger = logging.getLogger(__name__)
        self.book = book
        self.books_handler = books_handler
        self.res_handler = res_handler
        self.langs_handler = langs_handler
        self.qt_signals_handler = qt_signals_handler
        self.default_cover_path = self.res_handler.get_res(
            "assets.defaults_covers.book"
        )
        self.main_layout = QtWidgets.QGridLayout(self)
        self.book_cover_lb = QtWidgets.QLabel(self)
        self.cover_path = (
            self.books_handler.get_book_cover_path(self.book, False)
            or self.default_cover_path
        )
        self.book_cover_lb.setPixmap(QtGui.QPixmap(self.cover_path))
        self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.fixed_sp = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )
        self.book_authors_lb = QtWidgets.QLabel(
            self.book.authors if self.book.authors else "Unknown"
        )
        self.book_authors_lb.setObjectName("BookAuthorLabel")
        self.book_reading_state_lb = QtWidgets.QLabel()
        self.book_reading_state_lb.setObjectName("BookReadingStateLabel")
        self.display_reading_state()
        self.book_summary_te = QtWidgets.QTextEdit()
        self.book_summary_te.setText(self.book.summary if self.book.summary else "")
        self.book_summary_te.setMinimumSize(350, 120)
        self.book_summary_te.setMaximumSize(400, 120)
        self.book_summary_te.setReadOnly(True)
        self.book_summary_te.setObjectName("BookSummary")
        self.edit_b = QtWidgets.QPushButton(
            self.langs_handler.tr("shared.actions.edit")
        )  # type: ignore
        self.edit_b.setObjectName("EditButton")
        self.edit_b.setIcon(
            images_tools.get_svg(self.res_handler.get_res("assets.icons.edit"))
        )
        self.edit_b.setSizePolicy(self.fixed_sp)
        self.edit_b.clicked.connect(
            lambda: self.qt_signals_handler.switch_page_sg.emit(
                "BOOK_CREATION_PAGE",
                True,
                {"edition_mode_enabled": True, "book": self.book},
            )
        )
        self.delete_b = QtWidgets.QPushButton(
            self.langs_handler.tr("shared.actions.delete")
        )  # type: ignore
        self.delete_b.setIcon(
            images_tools.get_svg(self.res_handler.get_res("assets.icons.exit"), "red")
        )
        self.delete_b.setSizePolicy(self.fixed_sp)
        self.delete_b.setProperty("role", "DeleteButton")
        self.main_layout.addWidget(self.book_authors_lb, 0, 1)
        self.main_layout.addWidget(self.book_reading_state_lb, 1, 1)
        self.main_layout.addWidget(
            self.book_summary_te,
            2,
            1,
            QtCore.Qt.AlignmentFlag.AlignLeft,
            QtCore.Qt.AlignmentFlag.AlignTop,
        )
        self.main_layout.addWidget(
            self.edit_b,
            3,
            1,
        )
        self.main_layout.addWidget(
            self.delete_b,
            4,
            1,
        )
        self.main_layout.addWidget(
            self.book_cover_lb,
            0,
            0,
            5,
            1,
        )

    def display_reading_state(self):
        """
        Set the text displayed by the book reading state label
        """
        if self.book.status == "unread":
            self.book_reading_state_lb.setText(
                f"{self.langs_handler.tr('book.infos.reading_state.unread')} - {self.langs_handler.tr('shared.infos.pages_count_args', count=self.book.tot_pages)}"
            )

        elif self.book.status == "on_reading":
            self.book_reading_state_lb.setText(
                f"{self.langs_handler.tr('book.infos.reading_state.currently_reading')} - {self.book.alr_read_pages}/{self.langs_handler.tr('shared.infos.pages_count_args', count=self.book.tot_pages)}"
            )

        elif self.book.status == "finished":
            self.book_reading_state_lb.setText(
                f"{self.langs_handler.tr('book.infos.reading_state.finished')} - {self.langs_handler.tr('shared.infos.pages_count_args', count=self.book.tot_pages)}"
            )

        else:
            self.logger.warning(
                f"Book ID={self.book.id} has an unknown reading state '{self.book.status}'"
            )
