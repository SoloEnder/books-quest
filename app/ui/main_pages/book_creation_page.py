import datetime as dt
import logging
import os
import shutil
import typing
import uuid

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import api, book_sys
from app.ui.main_pages import base_page
from app.utils import images_tools, utils_funcs


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
        api: api.API,
        **kwargs,
    ):
        super().__init__(
            parent,
            api,
        )
        self.books = self.api.books
        self._edition_mode_enabled = kwargs.get("edition_mode_enabled", False)
        self._book: book_sys.Book | None = kwargs.get("book", None)
        self.variables_kw = {**kwargs}

        self.PAGE_NAME = "BOOK_CREATION_PAGE"
        self.logger = logging.getLogger(__name__)

        if self._edition_mode_enabled and not self._book:
            self.logger.info(
                f"Page {self.PAGE_NAME} called in edition mode, but no book provided for edition !"
            )
            raise ValueError(
                f"Page {self.PAGE_NAME} called in edition mode, but no book provided for edition !"
            )

        self.icons_folder = self.res_files.get_res("assets.icons")
        self.today_date_dt = dt.date.today()

        self.basic_book_infos = {
            "title": self.langs.tr("shared.infos.title"),
            "authors": self.langs.tr("shared.infos.author"),
            "edition": self.langs.tr("shared.infos.edition"),
            "summary": self.langs.tr("shared.infos.summary"),
            "tot_pages": self.langs.tr("shared.infos.pages_count"),
        }
        self.basic_book_info_ew = {}
        self.left_alignment = QtCore.Qt.AlignmentFlag.AlignLeft
        self.top_alignment = QtCore.Qt.AlignmentFlag.AlignTop

        # Cover widgets
        self.default_cover_img = os.path.join(
            self.res_files.get_res("assets.defaults_covers.book")
        )
        self.cover_image = self.default_cover_img
        self.book_cover_lb = QtWidgets.QLabel()
        self.book_cover_lb.setPixmap(QtGui.QPixmap(self.default_cover_img))
        self.edit_cover_b = QtWidgets.QPushButton(
            self.langs.tr("shared.actions.edit_cover")
        )
        self.edit_cover_b.setIcon(
            images_tools.get_svg(self.res_files.get_res("assets.icons.edit"))
        )
        self.edit_cover_b.setSizePolicy(QtWidgets.QSizePolicy())
        self.edit_cover_b.clicked.connect(self.set_book_cover)
        self.restore_default_cover_b = QtWidgets.QPushButton(
            self.langs.tr("shared.actions.restore_default_cover")
        )
        self.restore_default_cover_b.setIcon(
            images_tools.get_svg(self.res_files.get_res("assets.icons.remove_img"))
        )
        self.restore_default_cover_b.clicked.connect(self.restore_default_cover)

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
                ew.setText("1")

            ew.setMaximumWidth(300)
            self.main_lyt.addWidget(lb, row, 0)
            self.main_lyt.addWidget(ew, row, 1)
            self.basic_book_info_ew[key] = ew
            row += 1

        # Book status widgets
        self.reading_state_lb = QtWidgets.QLabel(
            self.langs.tr("book.infos.reading_state_header")
        )
        self.book_reading_state_combob = QtWidgets.QComboBox()
        self.book_reading_state_combob.addItem(
            self.langs.tr("book.infos.reading_state.unread"),
            book_sys.Book.ReadingState.UNREAD,
        )
        self.book_reading_state_combob.addItem(
            self.langs.tr("book.infos.reading_state.currently_reading"),
            book_sys.Book.ReadingState.CURRENTLY_READING,
        )
        self.book_reading_state_combob.addItem(
            self.langs.tr("book.infos.reading_state.finished"),
            book_sys.Book.ReadingState.FINISHED,
        )
        self.book_reading_state_combob.currentIndexChanged.connect(
            lambda: self.set_book_status(self.book_reading_state_combob.currentData())
        )
        self.book_reading_state_widget = QtWidgets.QWidget(self)
        self.book_reading_state_widget_layout = QtWidgets.QGridLayout()
        self.book_reading_state_widget.setLayout(self.book_reading_state_widget_layout)
        self.read_pages_lb = QtWidgets.QLabel(self.langs.tr("book.infos.read_pages"))
        self.read_pages_le = QtWidgets.QLineEdit("0")
        self.read_pages_le.textEdited.connect(
            lambda: self.check_int(self.read_pages_le.text(), self.read_pages_le)
        )
        self.read_pages_le.setMaximumWidth(300)
        self.today_date = QtCore.QDate(
            self.today_date_dt.year, self.today_date_dt.month, self.today_date_dt.day
        )
        self.starting_read_date_lb = QtWidgets.QLabel(
            self.langs.tr("book.infos.starting_read_date")
        )
        self.starting_read_date_de = QtWidgets.QDateEdit()
        self.starting_read_date_de.setDate(self.today_date)
        self.starting_read_date_de.setMaximumDate(self.today_date)
        self.starting_read_date_de.setCalendarPopup(True)
        self.starting_read_date_de.setMaximumWidth(300)
        # -- Automatically sets the minimum date for book end read date as the starting read date --
        self.starting_read_date_de.dateChanged.connect(self.set_end_read_min_date)
        self.end_read_date_lb = QtWidgets.QLabel(
            self.langs.tr("book.infos.end_read_date")
        )
        self.end_read_date_de = QtWidgets.QDateEdit()
        self.end_read_date_de.setDate(self.today_date)
        self.end_read_date_de.setMaximumDate(self.today_date)
        self.end_read_date_de.setCalendarPopup(True)
        self.end_read_date_de.setMaximumWidth(300)
        # Prevent starting read date from being superior than end reading date
        self.end_read_date_de.dateChanged.connect(self.set_starting_read_max_date)
        self.set_book_status(book_sys.Book.ReadingState.UNREAD)
        self.book_reading_state_widget_layout.addWidget(self.read_pages_lb, 0, 0)
        self.book_reading_state_widget_layout.addWidget(self.read_pages_le, 0, 1)
        self.book_reading_state_widget_layout.addWidget(
            self.starting_read_date_lb, 1, 0
        )
        self.book_reading_state_widget_layout.addWidget(
            self.starting_read_date_de, 1, 1
        )
        self.book_reading_state_widget_layout.addWidget(self.end_read_date_lb, 2, 0)
        self.book_reading_state_widget_layout.addWidget(self.end_read_date_de, 2, 1)

        # Shelfs widgets
        self.shelfs_selection_lb = QtWidgets.QLabel(
            self.langs.tr("book.infos.shelfs_selection")
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

        for shelf in self.books.books_handler.shelves.values():
            shelf_cb = QtWidgets.QCheckBox(
                utils_funcs.add_title_suffix(shelf.title, shelf.title_suffix)
            )
            self.shelfs_selection_cbs[shelf.str_id()] = shelf_cb
            self.shelfs_selection_layout.addWidget(shelf_cb)

        self.existence_msgbox = QtWidgets.QMessageBox()
        self.cancel_b = self.existence_msgbox.addButton(
            self.langs.tr("shared.actions.cancel"),
            QtWidgets.QMessageBox.ButtonRole.RejectRole,
        )
        self.rename_b = self.existence_msgbox.addButton(
            self.langs.tr("shared.actions.rename"),
            QtWidgets.QMessageBox.ButtonRole.AcceptRole,
        )
        self.existence_msgbox.setText(self.langs.tr("shared.msg.add_confirm"))

        self.add_b = QtWidgets.QPushButton(self.langs.tr("shared.actions.done"))
        self.add_b.clicked.connect(self.save_modifications)

        # Add the widgets
        self.main_lyt.addWidget(self.book_cover_lb, 0, 0)
        self.main_lyt.addWidget(self.edit_cover_b, 1, 0)
        self.main_lyt.addWidget(
            self.restore_default_cover_b, 2, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_lyt.addWidget(self.reading_state_lb, self.main_lyt.rowCount() + 1, 0)
        self.main_lyt.addWidget(
            self.book_reading_state_combob, self.main_lyt.rowCount() + 1, 0
        )
        self.main_lyt.addWidget(
            self.book_reading_state_widget,
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
        self.qt_signals.emit_signal("switch_page_sg", "BOOK_CREATION_PAGE", True, {})

    @QtCore.Slot()
    def set_starting_read_max_date(self):
        """
        Sets the maximum starting reading date to the current end read date
        """
        self.starting_read_date_de.setMaximumDate(self.end_read_date_de.date())

    @QtCore.Slot()
    def set_end_read_min_date(self):
        """
        Sets the minimum date for end reading date to the current value of starting read date
        """
        self.end_read_date_de.setMinimumDate(self.starting_read_date_de.date())

    def apply_edition_mode(self):
        """
        Switch the page to edition mode
        """

        self.logger.info("Appling edition mode...")
        if self.book:
            self.cover_image = (
                self.books.get_book_cover_path(self.book) or self.default_cover_img
            )
            self.book_cover_lb.setPixmap(QtGui.QPixmap(self.cover_image))
            for book_attr in self.basic_book_infos:
                value = getattr(self.book, book_attr)
                self.basic_book_info_ew[book_attr].setText(
                    str(value) if isinstance(value, (int, bool)) else value
                )

            combob_choices_indexes = {
                "UNREAD": 0,
                "CURRENTLY_READING": 1,
                "FINISHED": 2,
            }
            self.book_reading_state_combob.setCurrentIndex(
                combob_choices_indexes[self.book.reading_state.value]
            )
            self.read_pages_le.setText(str(self.book.read_pages))

            if self.book.starting_read_date:
                starting_read_date_dt = QtCore.QDate()
                starting_read_date_dt = starting_read_date_dt.fromString(
                    self.book.starting_read_date, QtCore.Qt.DateFormat.ISODate
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

    def set_book_status(self, status: book_sys.Book.ReadingState):
        """
        Set the book status and draw the appriopriate widgets

        Args:
        - status (Book.ReadingState): the book reading state
        """
        if status == book_sys.Book.ReadingState.FINISHED:
            self.read_pages_le.setEnabled(False)
            self.starting_read_date_de.setEnabled(True)
            self.end_read_date_de.setEnabled(True)

        elif status == book_sys.Book.ReadingState.CURRENTLY_READING:
            self.read_pages_le.setEnabled(True)
            self.starting_read_date_de.setEnabled(True)
            self.end_read_date_de.setEnabled(False)

        elif status == book_sys.Book.ReadingState.UNREAD:
            self.read_pages_le.setEnabled(False)
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
        """
        Displays a files picker, allowing user to select an image as cover.
        The selected images is then redimensionned and set as the current cover.
        """
        final_infos = self.books.select_book_cover()

        if final_infos:
            self.cover_image = final_infos[0]
            self.book_cover_lb.setPixmap(QtGui.QPixmap(self.cover_image))

    def set_cover_lb_pixmap(self, new_path):
        self.book_cover_lb.setPixmap(QtGui.QPixmap(self.cover_image))

    def restore_default_cover(self):
        """
        Set the cover image to the default value
        """
        # -- Removes the previous cover file
        if self.edition_mode_enabled:
            book_cover = self.books.get_book_cover_path(self.book, False)  # type: ignore

            if book_cover:
                self.res_files.delete(book_cover)
        self.cover_image = self.default_cover_img
        self.set_cover_lb_pixmap(self.cover_image)

    def get_matches(self, title: str, authors: str | None):
        """
        Get the books that have the same title and author as the current book
        In edition mode, this method checks if the book title/author has been modified before get the matches
        """
        matches = []
        if self.edition_mode_enabled and self.book:
            if self.book.title != title:
                matches = self.books.books_handler.get_books(
                    title=(title, True, False), authors=(authors, True, False)
                )

            elif self.book.authors != authors:
                matches = self.books.books_handler.get_books(
                    title=(title, True, False), authors=(authors, True, False)
                )

        elif not self.edition_mode_enabled:
            self.logger.debug(
                "Searching for books the same title and authors as the currently being created book..."
            )
            matches = self.books.books_handler.get_books(
                title=(title, True, False), authors=(authors, True, False)
            )

        return matches

    def copy_book_cover(self, cover_path: str, dest_path: str, set_as_new: bool = True):
        """
        Copy the books cover from `cover_path` to `dest_path`:

        Parameters
        ----------
        - cover_path (str): the original book cover
        - dest_path (str): the path where to moves the cover
        - set_as_new (bool=True): wether to set `dest_path` as the current book cover
        """
        shutil.copy2(
            cover_path,
            dest_path,
        )
        if set_as_new:
            self.cover_image = dest_path
            self.set_cover_lb_pixmap(self.cover_image)

    def attach_cover(self, id: str):
        """
        Attach the current cover to the book that has 'id' as ID
        """
        try:
            self.books.set_cover_for_book(id)

        except FileNotFoundError:
            self.logger.error(
                f"Could not attach cover file to book (ID='{id}') : File not found"
            )
            self.qt_signals.emit_signal(
                "notify_sg", "error", "Cover not found", "Cover file not found", ""
            )
            return

        except PermissionError:
            self.logger.error(
                f"Could not attach cover to book (ID='{id}') : Permission denied"
            )
            self.qt_signals.emit_signal(
                "notify_sg",
                "error",
                "Permission denied",
                "Access to cover file denied !",
                "",
            )
            return

        except FileExistsError:
            self.qt_signals.emit_signal(
                "notify_sg",
                "error",
                "Cover Exists",
                "A cover file already exists for this book !",
            )

    def get_book_infos(self):
        books_infos = {}

        for key, w in self.basic_book_info_ew.items():
            if isinstance(w, QtWidgets.QLineEdit):
                text = w.text()

                if key == "tot_pages":
                    value = int(text) if text else 1

                    if value <= 0:
                        self.qt_signals.emit_signal(
                            "notify_sg",
                            "error",
                            "Books Quest",
                            self.langs.tr("book.msg.invalid_pages_count"),
                            "",
                        )
                        return
                    books_infos[key] = value

                else:
                    if text:
                        books_infos[key] = text.strip()

            elif isinstance(w, QtWidgets.QTextEdit):
                text = w.toPlainText()

                if text:
                    books_infos[key] = text

        if not books_infos.get("title"):
            self.qt_signals.emit_signal(
                "notify_sg", "error", "", self.langs.tr("book.msg.invalid_title"), ""
            )
            return

        matches = self.get_matches(books_infos["title"], books_infos.get("authors"))

        if matches:
            title_suffix = utils_funcs.get_title_suffix(matches)
            self.logger.debug(
                f"Found {title_suffix} {[x.id for x in matches]} books which have the same authors and the same title that the on creating book !"
            )
            self.existence_msgbox.setInformativeText(
                f"{self.langs.tr('book.msg.book_already_exists')} ({title_suffix})\n{self.langs.tr('shared.msg.renaming_future')} '{books_infos.get('title')} ({title_suffix})'"
            )
            self.existence_msgbox.exec()

            if self.existence_msgbox.clickedButton() == self.rename_b:
                books_infos["title_suffix"] = title_suffix

            else:
                return

        books_infos["id"] = uuid.uuid4()

        # If in edition mode, the ID of the currently being edited book is used
        if self.edition_mode_enabled:
            books_infos["id"] = self.book.id  # type: ignore

        books_infos["reading_state"] = self.book_reading_state_combob.currentData()

        if self.read_pages_le.isEnabled():
            text = self.read_pages_le.text()
            books_infos["read_pages"] = int(text) if text else 0

            # Checking if read pages are less than total pages
            if books_infos["read_pages"] > books_infos["tot_pages"]:
                self.qt_signals.emit_signal(
                    "notify_sgerror",
                    "Books Quest",
                    self.langs.tr("book.msg.invalid_read_pages_count.too_high"),
                    "",
                )
                return

        if self.starting_read_date_de.isEnabled():
            books_infos["starting_read_date"] = (
                self.starting_read_date_de.date().toString(QtCore.Qt.DateFormat.ISODate)
            )

        if self.end_read_date_de.isEnabled():
            books_infos["end_read_date"] = self.end_read_date_de.date().toString(
                QtCore.Qt.DateFormat.ISODate
            )

        # Parents shelves
        books_infos["parents_shelves"] = self.get_selected_shelves()
        return books_infos

    def is_original_cover(self):
        """
        Check if the current book cover is it's original cover (the one he had before any changes were made)
        """
        original_cover = self.default_cover_img

        if self.edition_mode_enabled:
            original_cover = self.books.get_book_cover_path(self.book)  # type: ignore

        return original_cover == self.cover_image

    def get_selected_shelves(self, return_ids_only: bool = False):
        """
        Get and return the shelves that has been selected by the user.

        Parameters
        ----------
        return_ids_only (bool=False): wether to return only the shelves ids instead of their objects.
        """
        shelves = []
        for shelf_id, shelf_selection_cbs in self.shelfs_selection_cbs.items():
            if shelf_selection_cbs.isChecked():
                if return_ids_only:
                    shelves.append(shelf_id)
                    continue
                shelves.append(self.books.books_handler.shelves[shelf_id])
        return shelves

    def save_modifications(self):
        books_infos = self.get_book_infos()

        if books_infos:
            try:
                if self.edition_mode_enabled and self.book:
                    self.books.edit_book(self.book, **books_infos)

                else:
                    self.books.books_handler.new_book(**books_infos)

                if (
                    not self.is_original_cover()
                    and self.cover_image != self.default_cover_img
                ):  # Cheking if the cover has changed, and if it's not the default cover
                    self.logger.debug(
                        f"Book cover has changed, attaching new cover to book (ID={books_infos['id']})"
                    )
                    self.attach_cover(books_infos["id"])

            except Exception:
                self.logger.exception("Failed to create valid book : ")
                self.qt_signals.emit_signal("notify_sg", "error", "", "", "")

            else:
                if self.edition_mode_enabled:
                    QtWidgets.QMessageBox.information(
                        self,
                        "Success",
                        self.langs.tr("book.msg.book_edition_success"),
                    )
                    self.qt_signals.emit_signal("book_edited_sg", self.book.id)  # type: ignore
                    self.qt_signals.emit_signal("close_page_sg")

                else:
                    QtWidgets.QMessageBox.information(
                        self,
                        "Success",
                        self.langs.tr("book.msg.book_addition_success"),
                    )
                    self.qt_signals.emit_signal("book_added_sg", books_infos["id"])
                    self.qt_signals.emit_signal("refresh_current_page_sg")
