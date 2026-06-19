import datetime as dt
import logging
import os
import shutil
import uuid
from typing import Literal

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import book_sys, langs_handler, resources_handler, settings_handler
from app.ui import qt_signals_handler
from app.ui.main_pages import base_page
from app.utils import images_tools


class EditionModeNotEnabled(Exception):
    def __init__(self, msg: str | None = None):
        """
        Exception usually raised when trying to do something that is only possible if BookCreationPage is in edition mode
        """
        self.msg = msg or "Edition mode not enabled !"
        super().__init__(self.msg)

    def __str__(self):
        return self.msg


class BookCreationPage(base_page.BasePage):
    def __init__(
        self,
        parent: QtWidgets.QWidget,
        books_handler: book_sys.BooksHandler,
        res_handler: resources_handler.RessourcesHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        settings_handler: settings_handler.SettingsHandler,
        langs_handler: langs_handler.LangsHandler,
        **kwargs,
    ):
        super().__init__(
            parent,
            res_handler,
            settings_handler,
            langs_handler,
            qt_signals_handler,
        )
        self.books_handler = books_handler
        self._edition_mode_enabled = kwargs.get("edition_mode_enabled", False)
        self._book: book_sys.Book | None = kwargs.get("book", None)
        self.variables_kw = {**kwargs}

        self.PAGE_NAME = "BOOK_CREATION_PAGE"
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"{self._edition_mode_enabled=}")
        self.logger.debug(f"{self._book=}")

        if self._edition_mode_enabled and not self._book:
            self.logger.info(
                f"Page {self.PAGE_NAME} called in edition mode, but no book provided for edition !"
            )
            raise ValueError(
                f"Page {self.PAGE_NAME} called in edition mode, but no book provided for edition !"
            )

        self.icons_folder = self.res_handler.get_res("assets.icons")
        self.today_date_dt = dt.date.today()

        self.basic_book_infos = {
            "title": self.langs_handler.tr("shared.infos.title"),
            "authors": self.langs_handler.tr("shared.infos.author"),
            "edition": self.langs_handler.tr("shared.infos.edition"),
            "summary": self.langs_handler.tr("shared.infos.summary"),
            "tot_pages": self.langs_handler.tr("shared.infos.pages_count"),
        }
        self.basic_book_info_ew = {}
        self.left_alignment = QtCore.Qt.AlignmentFlag.AlignLeft
        self.top_alignment = QtCore.Qt.AlignmentFlag.AlignTop

        # Cover widgets
        self.default_cover_img = os.path.join(
            self.res_handler.get_res("assets.defaults_covers.book")
        )
        self.cover_image = self.default_cover_img
        self.book_cover_lb = QtWidgets.QLabel()
        self.book_cover_lb.setPixmap(QtGui.QPixmap(self.default_cover_img))
        self.edit_cover_b = QtWidgets.QPushButton(
            self.langs_handler.tr("shared.actions.edit_cover")
        )
        self.edit_cover_b.setIcon(
            QtGui.QIcon(self.res_handler.get_res("assets.icons.edit"))
        )
        self.edit_cover_b.setSizePolicy(QtWidgets.QSizePolicy())
        self.edit_cover_b.clicked.connect(self.set_book_cover)

        # Book infos widgets
        row = 3
        for (
            key,
            value,
        ) in self.basic_book_infos.items():
            lb = QtWidgets.QLabel(value)
            ew = QtWidgets.QLineEdit() if key != "summary" else QtWidgets.QTextEdit()

            if key == "summary":
                lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

            elif key == "tot_pages":
                ew.textEdited.connect(lambda: self.check_int(ew.text(), ew))  # type: ignore

            ew.setMaximumWidth(300)
            self.main_lyt.addWidget(lb, row, 0)
            self.main_lyt.addWidget(ew, row, 1)
            self.basic_book_info_ew[key] = ew
            row += 1

        # Book status widgets
        self.book_status_lb = QtWidgets.QLabel(
            self.langs_handler.tr("shared.infos.status")
        )
        self.book_status_combob = QtWidgets.QComboBox()
        self.book_status_combob.addItem("Non lut", "unread")
        self.book_status_combob.addItem("En cours", "on_reading")
        self.book_status_combob.addItem("Terminé", "finished")
        self.book_status_combob.currentIndexChanged.connect(
            lambda: self.set_book_status(self.book_status_combob.currentData())
        )
        self.book_status_widget = QtWidgets.QWidget(self)
        self.book_status_widget_layout = QtWidgets.QGridLayout()
        self.book_status_widget.setLayout(self.book_status_widget_layout)
        self.alr_read_pages_lb = QtWidgets.QLabel(
            self.langs_handler.tr("book.infos.alr_read_pages")
        )
        self.alr_read_pages_le = QtWidgets.QLineEdit()
        self.alr_read_pages_le.textEdited.connect(
            lambda: self.check_int(
                self.alr_read_pages_le.text(), self.alr_read_pages_le
            )
        )
        self.alr_read_pages_le.setMaximumWidth(300)
        self.today_date = QtCore.QDate(
            self.today_date_dt.year, self.today_date_dt.month, self.today_date_dt.day
        )
        self.starting_read_date_lb = QtWidgets.QLabel(
            self.langs_handler.tr("book.infos.starting_read_date")
        )
        self.starting_read_date_de = QtWidgets.QDateEdit()
        self.starting_read_date_de.setDate(self.today_date)
        self.starting_read_date_de.setMaximumDate(self.today_date)
        self.starting_read_date_de.setCalendarPopup(True)
        self.starting_read_date_de.setMaximumWidth(300)
        self.end_read_date_lb = QtWidgets.QLabel(
            self.langs_handler.tr("book.infos.end_read_date")
        )
        self.end_read_date_de = QtWidgets.QDateEdit()
        self.end_read_date_de.setDate(self.today_date)
        self.end_read_date_de.setMinimumDate(self.today_date)
        self.end_read_date_de.setCalendarPopup(True)
        self.end_read_date_de.setMaximumWidth(300)
        self.set_book_status("unread")
        self.book_status_widget_layout.addWidget(self.alr_read_pages_lb, 0, 0)
        self.book_status_widget_layout.addWidget(self.alr_read_pages_le, 0, 1)
        self.book_status_widget_layout.addWidget(self.starting_read_date_lb, 1, 0)
        self.book_status_widget_layout.addWidget(self.starting_read_date_de, 1, 1)
        self.book_status_widget_layout.addWidget(self.end_read_date_lb, 2, 0)
        self.book_status_widget_layout.addWidget(self.end_read_date_de, 2, 1)

        # Shelfs widgets
        self.shelfs_selection_lb = QtWidgets.QLabel(
            self.langs_handler.tr("book.infos.shelfs_selection")
        )
        self.shelfs_selection_cbs = {}
        self.shelfs_selection_widget = QtWidgets.QWidget(self)
        self.shelfs_selection_layout = QtWidgets.QVBoxLayout(
            self.shelfs_selection_widget
        )
        self.shelfs_selection_widget.setLayout(self.shelfs_selection_layout)
        self.shelfs_selection_scroll_area = QtWidgets.QScrollArea(self)
        self.shelfs_selection_scroll_area.setMaximumWidth(300)
        self.shelfs_selection_scroll_area.setMinimumHeight(400)
        self.shelfs_selection_scroll_area.setWidgetResizable(True)
        self.shelfs_selection_scroll_area.setWidget(self.shelfs_selection_widget)

        for shelf in self.books_handler.shelves.values():
            shelf_cb = QtWidgets.QCheckBox(shelf.title)
            self.shelfs_selection_cbs[shelf.str_id()] = shelf_cb
            self.shelfs_selection_layout.addWidget(shelf_cb)

        self.existence_msgbox = QtWidgets.QMessageBox()
        self.cancel_b = self.existence_msgbox.addButton(
            self.langs_handler.tr("shared.actions.cancel"),
            QtWidgets.QMessageBox.ButtonRole.RejectRole,
        )
        self.rename_b = self.existence_msgbox.addButton(
            self.langs_handler.tr("shared.actions.rename"),
            QtWidgets.QMessageBox.ButtonRole.AcceptRole,
        )
        self.existence_msgbox.setText(self.langs_handler.tr("shared.msg.add_confirm"))

        self.add_b = QtWidgets.QPushButton(self.langs_handler.tr("shared.actions.done"))
        self.add_b.clicked.connect(self.create_book)

        # Add the widgets
        self.main_lyt.addWidget(self.book_cover_lb, 0, 0)
        self.main_lyt.addWidget(self.edit_cover_b, 1, 0)
        self.main_lyt.addWidget(self.book_status_lb, self.main_lyt.rowCount() + 1, 0)
        self.main_lyt.addWidget(
            self.book_status_combob, self.main_lyt.rowCount() + 1, 0
        )
        self.main_lyt.addWidget(
            self.book_status_widget,
            self.main_lyt.rowCount() + 1,
            0,
            2,
            0,
        )
        self.main_lyt.addWidget(
            self.shelfs_selection_lb, self.main_lyt.rowCount() + 1, 0
        )
        self.main_lyt.addWidget(
            self.shelfs_selection_scroll_area,
            self.main_lyt.rowCount() + 1,
            0,
        )
        self.main_lyt.addWidget(self.add_b, self.main_lyt.rowCount() + 1, 0)
        if self._edition_mode_enabled:
            self.apply_edition_mode()

    @property
    def edition_mode_enabled(self):
        """Getter of property 'edition_mode_enabled'"""
        return self._edition_mode_enabled

    @edition_mode_enabled.setter
    def edition_mode_enabled(self, new_value: bool):
        """
        Setter of property 'edition_mode_enabled'
        """

        if isinstance(new_value, bool):
            self._edition_mode_enabled = new_value

            if self._edition_mode_enabled:
                self.apply_edition_mode()

            else:
                self.apply_creation_mode()

        else:
            raise ValueError(
                f"Wrong value given to 'edition_mode_enabled': {new_value}"
            )

    @property
    def book(self):
        """
        Getter of property 'book'
        """
        return self._book

    @book.setter
    def book(self, new_value: book_sys.Book):
        """
        Setter of property 'book'
        """
        if isinstance(new_value, book_sys.Book):
            if self.edition_mode_enabled:
                self._book = new_value
                self.apply_edition_mode()

            else:
                raise EditionModeNotEnabled(
                    "Couldn't set value of 'BookCreationPage.book' while edition mode isn't enabled"
                )

        else:
            raise ValueError(
                f"Wrong value given for 'BookCreationPage.book' : {new_value}"
            )

    def apply_creation_mode(self):
        """
        Switch the page to normal mode
        """

        self.logger.info("Appling normal mode...")
        self.qt_signals_handler.switch_page_sg.emit("BOOK_CREATION_PAGE", True, {})

    def apply_edition_mode(self):
        """
        Switch the page to edition mode
        """

        self.logger.info("Appling edition mode...")
        if self.book:
            self.cover_image = self.book.cover_path or self.default_cover_img
            self.book_cover_lb.setPixmap(QtGui.QPixmap(self.cover_image))
            for book_attr in self.basic_book_infos:
                value = getattr(self.book, book_attr)
                self.basic_book_info_ew[book_attr].setText(
                    str(value) if isinstance(value, (int, bool)) else value
                )

            combob_choices_indexes = {
                "unread": 0,
                "on_reading": 1,
                "finished": 2,
            }
            self.book_status_combob.setCurrentIndex(
                combob_choices_indexes[getattr(self.book, "status", "unread")]
            )
            self.alr_read_pages_le.setText(self.book.alr_read_pages or "0")

            if self.book.starting_read_date:
                starting_read_date_dt = QtCore.QDate()
                starting_read_date_dt = starting_read_date_dt.fromString(
                    self.book.starting_read_date, QtCore.Qt.DateFormat.ISODate
                )
                self.logger.debug(
                    f"Book started read at {starting_read_date_dt.currentDate()}"
                )

            else:
                starting_read_date_dt = self.today_date

            if self.book.end_read_date:
                end_read_date_dt = QtCore.QDate()
                end_read_date_dt = end_read_date_dt.fromString(
                    self.book.end_read_date, QtCore.Qt.DateFormat.ISODate
                )

            else:
                end_read_date_dt = self.today_date

            self.starting_read_date_de.setDate(starting_read_date_dt)
            self.end_read_date_de.setDate(end_read_date_dt)

            for shelf in self.book._parents_shelves:
                self.shelfs_selection_cbs[shelf.str_id()].setChecked(True)

    def set_book_status(self, status: Literal["finished", "on_reading", "unread"]):
        """
        Set the book status and draw the appriopriate widgets

        Args:
        - status (str): the book status ("finished", "on_read" or "unread")
        """
        if status == "finished":
            self.alr_read_pages_le.setEnabled(False)
            self.starting_read_date_de.setEnabled(True)
            self.end_read_date_de.setEnabled(True)

        elif status == "on_reading":
            self.alr_read_pages_le.setEnabled(True)
            self.starting_read_date_de.setEnabled(True)
            self.end_read_date_de.setEnabled(False)

        elif status == "unread":
            self.alr_read_pages_le.setEnabled(False)
            self.starting_read_date_de.setEnabled(False)
            self.end_read_date_de.setEnabled(False)

    def check_int(self, text: str, le: QtWidgets.QLineEdit | None = None):
        """
        Check if all characters in <text> are numbers return it, and eventually edit the PySide6.QtWidgets.QLineEdit if it is given

        Args:
        - text (str): the text to check
        - le (PySide6.QtWidgets.QLineEdit): the QLineEdit widget to change
        """

        for c in text:
            if not c.isdigit():
                text = text.replace(c, "")

        if le:
            le.setText(text)

        return text

    def set_default_cover(self):
        self.cover_image = self.default_cover_img
        self.book_cover_lb.setPixmap(QtGui.QPixmap(self.default_cover_img))

    def set_book_cover(self):
        infos = images_tools.select_image()

        if infos:
            if infos[0]:
                final_infos = images_tools.prepare_image(
                    infos[0],
                    os.path.join(self.res_handler.get_res("tmp"), "book_cover.png"),
                )
                self.cover_image = final_infos[0]
                self.book_cover_lb.setPixmap(QtGui.QPixmap(self.cover_image))

    def set_cover_lb_pixmap(self, new_path):
        self.book_cover_lb.setPixmap(QtGui.QPixmap(self.cover_image))

    def check_existence(self, **kwargs):
        """
        Check if a book who match with the requirements specified iin kwargs exists in the current books handler, and return the standard output of the method <get_book> of the books handler
        """
        return self.books_handler.get_books(**kwargs)

    def get_book_infos(self):
        books_infos = {}

        for key, w in self.basic_book_info_ew.items():
            if isinstance(w, QtWidgets.QLineEdit):
                text = w.text()

                if key == "tot_pages":
                    books_infos[key] = text if text else 0

                else:
                    if text:
                        books_infos[key] = text

            elif isinstance(w, QtWidgets.QTextEdit):
                text = w.toPlainText()

                if text:
                    books_infos[key] = text

        if not books_infos.get("title"):
            self.qt_signals_handler.notify_sg.emit(
                "error", "", "Nom de livre invalide", ""
            )
            return

        try:
            matches = self.check_existence(
                title=(books_infos.get("title"), True, False),
                authors=(books_infos.get("authors"), True, False),
            )

        except AttributeError:
            matches = []
            self.logger.exception(
                f"an error occured while checking the existence of book name {books_infos.get('title')}"
            )
            return

        else:
            if self.edition_mode_enabled and self.book:
                if self.book in matches:
                    matches = []

        if matches:
            self.logger.debug(
                f"Found {len(matches)} {[x.id for x in matches]} books which have the same authors and the same title that the on creating book !"
            )
            self.existence_msgbox.setInformativeText(
                f"{self.langs_handler.tr('book.msg.book_already_exists')} ({len(matches)})\n{self.langs_handler.tr('shared.msg.renaming_future')} '{books_infos.get('title')} ({len(matches)})'"
            )
            self.existence_msgbox.exec()

            if self.existence_msgbox.clickedButton() == self.rename_b:
                books_infos["title_suffix"] = len(matches)

            else:
                return

        books_infos["id"] = uuid.uuid4()

        if str(self.cover_image) != self.default_cover_img:
            final_cover_image = os.path.join(
                self.res_handler.get_res("data.books.covers"),
                f"{str(books_infos['id'])}.png",
            )
            self.logger.debug(f"Final book cover path : {final_cover_image}")

            if os.path.exists(self.cover_image):
                shutil.copy2(
                    self.cover_image,
                    os.path.join(
                        self.res_handler.get_res("data.books.covers"),
                        final_cover_image,
                    ),
                )
                self.cover_image = final_cover_image
                self.set_cover_lb_pixmap(self.cover_image)

            books_infos["cover_path"] = str(self.cover_image)

        books_infos["status"] = self.book_status_combob.currentData()

        if self.alr_read_pages_le.isEnabled():
            text = self.alr_read_pages_le.text()
            books_infos["alr_read_pages"] = int(text) if text else 0

        if self.starting_read_date_de.isEnabled():
            books_infos["starting_read_date"] = (
                self.starting_read_date_de.date().toString(QtCore.Qt.DateFormat.ISODate)
            )

        if self.end_read_date_de.isEnabled():
            books_infos["end_read_date"] = self.end_read_date_de.date().toString(
                QtCore.Qt.DateFormat.ISODate
            )
        self.logger.debug(
            f"{books_infos.get("starting_read_date")=}, {books_infos.get("end_read_date")=}"
        )

        return books_infos

    def create_book(self):
        books_infos = self.get_book_infos()

        if books_infos:
            try:
                shelves = []
                for shelf_id, shelf_selection_cbs in self.shelfs_selection_cbs.items():
                    if shelf_selection_cbs.isChecked():
                        shelves.append(self.books_handler.shelves[shelf_id])

                books_infos["parents_shelves"] = shelves

                if self.edition_mode_enabled and self.book:
                    books_infos["id"] = self.book.id
                    self.book.delete_from_parents()
                    new_book = self.books_handler.create_book(**books_infos)
                    self.books_handler.edit_book(self.book.id, new_book)

                else:
                    self.books_handler.new_book(**books_infos)

            except Exception:
                self.logger.exception("Failed to create valid book : ")
                self.qt_signals_handler.notify_sg.emit("error", "", "", "")

            else:
                if self.edition_mode_enabled:
                    QtWidgets.QMessageBox.information(
                        self,
                        "Success",
                        self.langs_handler.tr("book.msg.book_edition_success"),
                    )
                    self.qt_signals_handler.close_page_sg.emit()

                else:
                    QtWidgets.QMessageBox.information(
                        self,
                        "Success",
                        self.langs_handler.tr("book.msg.book_addition_success"),
                    )
