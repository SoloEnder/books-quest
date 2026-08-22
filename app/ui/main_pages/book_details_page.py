import logging
import uuid

import widgets_pagination_view
from PySide6 import QtCore, QtGui, QtWidgets

from app.src import book_sys, langs_handler, resources_handler, settings_handler
from app.ui import qt_signals_handler
from app.ui.main_pages import base_page
from app.utils import images_tools, my_exceptions, utils_funcs

logger = logging.getLogger(__name__)


class BookDetailsPage(base_page.BasePage):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        res_handler: resources_handler.RessourcesHandler,
        settings_handler: settings_handler.SettingsHandler,
        langs_handler: langs_handler.LangsHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        books_handler: book_sys.BooksHandler,
        book_id: uuid.UUID,
    ):
        super().__init__(
            parent, res_handler, settings_handler, langs_handler, qt_signals_handler
        )
        self.books_handler = books_handler
        self._book_id = book_id
        self._book = (
            self.books_handler.default_book
            if self.book_id == self.books_handler.default_book.id
            else self.books_handler.books[str(book_id)]
        )

        # Connecting signals to slot
        self.book_widget = BookWidget(
            self.book,
            self.books_handler,
            self.res_handler,
            self.langs_handler,
            self.qt_signals_handler,
        )
        self.book_widget.sub_widget.book_details_b.setVisible(False)
        # All the details about the book
        self.detailed_book_infos = DetailedBookInfos(
            self,
            self.res_handler,
            self.settings_handler,
            self.langs_handler,
            self.qt_signals_handler,
            self.book,
        )
        self.main_sep = QtWidgets.QFrame()
        self.main_sep.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.main_lyt.addWidget(self.book_widget, 0, 0)
        self.main_lyt.addWidget(self.main_sep, 0, 1)
        self.main_lyt.addWidget(self.detailed_book_infos, 0, 2)

    @property
    def book_id(self):
        return self._book_id

    @book_id.setter
    def book_id(self, new_value: uuid.UUID):
        if isinstance(new_value, uuid.UUID):
            self._book_id = new_value
            self.qt_signals_handler.refresh_current_page_sg.emit()

    @property
    def book(self):
        return self._book


class DetailedBookInfos(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        res_handler: resources_handler.RessourcesHandler,
        settings_handler: settings_handler.SettingsHandler,
        langs_handler: langs_handler.LangsHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        book: book_sys.Book,
    ):
        super().__init__(parent)
        self.res_handler = res_handler
        self.settings_handler = settings_handler
        self.langs_handler = langs_handler
        self.qt_signals_handler = qt_signals_handler
        self._book = book

        self.logger = logging.getLogger(__name__)
        self.fixed_sp = QtWidgets.QSizePolicy()
        self.main_lyt = QtWidgets.QVBoxLayout()
        self.main_lyt.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.main_lyt)
        self.book_basic_infos = {
            "title": (
                self.langs_handler.tr("shared.infos.title"),
                utils_funcs.add_title_suffix(self.book.title, self.book.title_suffix),
            ),  # Basic info:(title, value)
            "authors": (
                self.langs_handler.tr("shared.infos.author"),
                self.book.authors or "Unknown",
            ),
            "edition": (
                self.langs_handler.tr("shared.infos.edition"),
                self.book.edition or "Unknown",
            ),
            "summary": (
                self.langs_handler.tr("shared.infos.summary"),
                self.book.summary or "Unknown",
            ),
            "total_pages_count": (
                self.langs_handler.tr("shared.infos.pages_count"),
                self.book.tot_pages,
            ),
            "reading_state": (
                self.langs_handler.tr("book.infos.reading_state_header"),
                utils_funcs.get_reading_state_tr(
                    self.book.reading_state, self.langs_handler
                ),
            ),
            "read_pages": (
                self.langs_handler.tr("book.infos.read_pages"),
                self.book.read_pages,
            ),
            "starting_reading_date": (
                self.langs_handler.tr("book.infos.starting_read_date"),
                self.book.starting_read_date,
            ),
            "end_reading_date": (
                self.langs_handler.tr("book.infos.end_read_date"),
                self.book.end_read_date,
            ),
        }
        self.config_basic_infos_widgets()
        utils_funcs.load_and_set_ss(
            self.res_handler.get_res("assets.qss.general"),
            self.res_handler.get_res("assets.qss.book_details_page"),
            widget=self,
            logger=self.logger,
        )

    def config_basic_infos_widgets(self):
        for key, value in self.book_basic_infos.items():
            if (
                key == "starting_reading_date"
                and self.book.reading_state == book_sys.Book.ReadingState.UNREAD
            ):
                continue

            if (
                key == "read_pages"
                and self.book.reading_state
                != book_sys.Book.ReadingState.CURRENTLY_READING
            ):
                continue

            if (
                key == "end_reading_date"
                and self.book.reading_state != book_sys.Book.ReadingState.FINISHED
            ):
                continue

            if type(value[1]) is int:
                value = (value[0], str(value[1]))

            title_lb = QtWidgets.QLabel(value[0])
            title_lb.setProperty("role", "h5")
            title_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

            if key == "summary":
                value_widget = QtWidgets.QTextEdit(value[1])
                value_widget.setMinimumSize(350, 120)
                value_widget.setMaximumSize(400, 120)

            else:
                value_widget = QtWidgets.QLabel(value[1])

            value_widget.setProperty("role", "BookDetailValue")
            value_widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

            sep = QtWidgets.QFrame()
            sep.setFrameShape(QtWidgets.QFrame.Shape.HLine)
            sep.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
            self.main_lyt.addWidget(
                title_lb,
            )
            self.main_lyt.addWidget(
                value_widget,
            )
            self.main_lyt.addWidget(
                sep,
            )

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
        utils_funcs.load_and_set_ss(
            self.res_handler.get_res("assets.qss.general"),
            self.res_handler.get_res("assets.qss.book_widget"),
            widget=self,
            logger=self.logger,
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
        self.book_details_b = QtWidgets.QPushButton(
            self.langs_handler.tr("shared.actions.see_details")
        )
        self.book_details_b.setIcon(
            images_tools.get_svg(self.res_handler.get_res("assets.icons.infos"))
        )
        self.book_details_b.setObjectName("SeeDetailsButton")
        self.book_details_b.clicked.connect(
            lambda: self.qt_signals_handler.switch_page_sg.emit(
                "BOOK_DETAILS_PAGE", True, {"book_id": self.book.id}
            )
        )
        self.book_details_b.setSizePolicy(self.fixed_sp)
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
            self.book_details_b,
            3,
            1,
        )
        self.main_layout.addWidget(
            self.edit_b,
            4,
            1,
        )
        self.main_layout.addWidget(
            self.delete_b,
            5,
            1,
        )
        self.main_layout.addWidget(
            self.book_cover_lb,
            0,
            0,
            6,
            1,
        )

    def display_reading_state(self):
        """
        Set the text displayed by the book reading state label
        """
        if self.book.reading_state == book_sys.Book.ReadingState.UNREAD:
            self.book_reading_state_lb.setText(
                f"{self.langs_handler.tr('book.infos.reading_state.unread')} - {self.langs_handler.tr('shared.infos.pages_count_args', count=self.book.tot_pages)}"
            )

        elif self.book.reading_state == book_sys.Book.ReadingState.CURRENTLY_READING:
            self.book_reading_state_lb.setText(
                f"{self.langs_handler.tr('book.infos.reading_state.currently_reading')} - {self.book.read_pages}/{self.langs_handler.tr('shared.infos.pages_count_args', count=self.book.tot_pages)}"
            )

        elif self.book.reading_state == book_sys.Book.ReadingState.FINISHED:
            self.book_reading_state_lb.setText(
                f"{self.langs_handler.tr('book.infos.reading_state.finished')} - {self.langs_handler.tr('shared.infos.pages_count_args', count=self.book.tot_pages)}"
            )

        else:
            self.logger.warning(
                f"Book ID={self.book.id} has an unknown reading state '{self.book.reading_state}'"
            )
