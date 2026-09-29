import datetime as dt
import logging

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import api, book_sys, timer
from app.ui.main_pages import base_page
from app.utils import images_tools, utils_funcs


class SessionsDetailsWindow(QtWidgets.QWidget):
    reading_session_saved = QtCore.Signal()
    about_to_close = QtCore.Signal()

    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        api: api.API,
        start_date: QtCore.QDate,
        session_duration: int,
        read_book: book_sys.Book,
    ):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__ + " - SessionsDetailsWindow")
        self.api = api
        self.start_date = start_date
        self.session_duration = session_duration
        self.read_book = read_book

        self.seconds = self.session_duration % 60
        self.minutes = self.session_duration // 60 if self.session_duration else 0
        self.minutes %= 60  # Prevent from having value >= 60
        self.hours = self.session_duration // 3600

        # Widgets
        self.main_lyt = QtWidgets.QGridLayout(self)
        self.start_date_lb = QtWidgets.QLabel("Started at :")
        self.start_date_selector = QtWidgets.QDateEdit(self.start_date)
        self.start_date_selector.setCalendarPopup(True)

        # -- Duration
        self.hours_selector_lb = QtWidgets.QLabel("Session duration (hours) : ")
        self.hours_selector_lb.setObjectName("HoursSelectorLabel")
        self.hours_selector = QtWidgets.QSpinBox(minimum=0, value=self.hours)
        self.hours_selector.setObjectName("HoursSelector")
        self.minutes_selector_lb = QtWidgets.QLabel("Session duration (minutes) : ")
        self.minutes_selector_lb.setObjectName("MinutesSelectorLabel")
        self.minutes_selector = QtWidgets.QSpinBox(
            minimum=0, maximum=60, value=self.minutes
        )
        self.minutes_selector.setObjectName("MinutesSelector")
        self.seconds_selector_lb = QtWidgets.QLabel("Session duration (seconds) : ")
        self.seconds_selector_lb.setObjectName("SecondsSelectorLabel")
        self.seconds_selector = QtWidgets.QSpinBox(
            minimum=0, maximum=60, value=self.seconds
        )
        self.seconds_selector_lb.setObjectName("SecondsSelector")
        self.calc_duration()
        self.current_page_selector_lb = QtWidgets.QLabel(self, text="Current page : ")
        self.current_page_selector_lb.setObjectName("CurrentPageSelectorLabel")
        self.current_page_selector = QtWidgets.QSpinBox(
            self, minimum=self.read_book.read_pages, maximum=self.read_book.tot_pages
        )
        self.current_page_selector.setObjectName("CurrentPageSelector")
        self.book_finished_b = QtWidgets.QPushButton("Book finished")
        self.book_finished_b.setObjectName("BookFinishedButton")
        self.book_finished_b.clicked.connect(
            lambda: self.current_page_selector.setValue(self.read_book.tot_pages)
        )
        self.save_b = QtWidgets.QPushButton("Save")
        self.save_b.clicked.connect(lambda: self.save_session(True))

        self.main_lyt.setSpacing(15)
        self.main_lyt.addWidget(self.start_date_lb, 0, 0)
        self.main_lyt.addWidget(self.start_date_selector, 0, 1, 1, 2)
        self.main_lyt.addWidget(self.hours_selector_lb, 1, 0)
        self.main_lyt.addWidget(self.hours_selector, 1, 1, 1, 2)
        self.main_lyt.addWidget(self.minutes_selector_lb, 2, 0)
        self.main_lyt.addWidget(self.minutes_selector, 2, 1, 1, 2)
        self.main_lyt.addWidget(self.seconds_selector_lb, 3, 0)
        self.main_lyt.addWidget(self.seconds_selector, 3, 1, 1, 2)
        self.main_lyt.addWidget(self.current_page_selector_lb, 4, 0)
        self.main_lyt.addWidget(self.current_page_selector, 4, 1)
        self.main_lyt.addWidget(self.book_finished_b, 4, 2)
        self.main_lyt.addWidget(self.save_b, 5, 0, 1, 3)

    def closeEvent(self, event: QtGui.QCloseEvent, /) -> None:
        self.about_to_close.emit()
        return super().closeEvent(event)

    def calc_duration(self, duration: int | None = None) -> int:
        """
        Calculate the reading session duration based on the value of the `seconds`, `minutes` and `hours` widgets
        Returns the new duration
        """
        self.seconds = self.seconds_selector.value()
        self.minutes = self.minutes_selector.value()
        self.hours = self.hours_selector.value()
        self.duration = self.seconds + self.minutes * 60 + self.hours * 3600
        return self.duration

    def set_duration(self, duration: int):
        """
        Sets the session duration to `duration`
        """
        self.session_duration = duration
        self.seconds = duration % 60
        self.minutes = duration // 60 if duration else 0
        self.minutes %= 60  # Prevent from having value >= 60
        self.hours = duration // 3600
        self.update_duration_widgets()

    def update_duration_widgets(self):
        """
        Updates the value displayed by the `seconds`, `minutes` and `hours` widgets based on the value of
        `hours`, `minutes`, `seconds` attributs
        """
        self.hours_selector.setValue(self.hours)
        self.minutes_selector.setValue(self.minutes)
        self.seconds_selector.setValue(self.seconds)

    def get_session(self) -> book_sys.ReadingSession:
        """
        Returns the reading session data in a `ReadingSession` object
        """
        self.calc_duration()
        session_data = self.get_session_data()
        start_date = book_sys.ReadingSessionTime(
            *session_data["start_date"], hour=0, minute=0
        )
        end_date = book_sys.ReadingSessionTime(
            *session_data["start_date"], hour=0, minute=0
        )

        reading_session = book_sys.ReadingSession(
            start_date,
            end_date,
            self.session_duration,
            session_data["start_page"],
            session_data["end_page"],
        )
        return reading_session

    def get_session_data(self) -> dict:
        """
        Returns the session starts date, duration, start/end page and the book that was read
        """
        self.calc_duration()
        return {
            "start_date": [*self.start_date.getDate()],
            "duration": self.session_duration,
            "start_page": self.read_book.read_pages,
            "end_page": self.current_page_selector.value(),
            "book": self.read_book,
        }

    def save_session(self, auto_close: bool = True):
        """
        Add a new reading session for the current book, based on the infos provided by the widgets

        Parameters
        ----------
        - auto_close (bool=True): wehter to close the widgets when the session is successfully added
        """
        try:
            self.api.books.add_reading_session(self.read_book, self.get_session())

        except Exception:
            self.logger.exception("Unable to save session for book : ")
            self.close()
            self.api.qt_signals.emit_signal(
                "notify_sg",
                "error",
                "Reading Session",
                "Unable to save reading session, please try again",
                "",
            )
        else:
            self.reading_session_saved.emit()
            if auto_close:
                self.close()


class ReadingSessionPage(base_page.BasePage):
    def __init__(self, parent: QtWidgets.QWidget | None, api: api.API, book_id: str):
        super().__init__(parent, api)
        self.logger = logging.getLogger(__name__)
        self._book = (
            self.books.books_handler.default_book
            if book_id == self.books.books_handler.default_book.str_id()
            else self.books.books_handler.books[book_id]
        )

        # Widgets
        self.currently_reading_book_title_lb = QtWidgets.QLabel(
            f'Reading "{self._book.title}"...'
        )
        self.currently_reading_book_title_lb.setProperty("role", "TitleLabel")
        self.currently_reading_book_title_lb.setObjectName("CurrentlyReadingBookLabel")
        self.time_lb = QtWidgets.QLabel()
        self.time_lb.setProperty("role", "h1")
        self.time_lb.setObjectName("TimerLabel")
        self.timer_action_b = QtWidgets.QPushButton("Pause")
        self.timer_action_b.setObjectName("TimerActionButton")
        self.save_session_b = QtWidgets.QPushButton("Save session")
        self.main_lyt.addWidget(
            self.currently_reading_book_title_lb,
            0,
            0,
            QtCore.Qt.AlignmentFlag.AlignCenter,
        )
        self.main_lyt.addWidget(self.time_lb, 1, 0, QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_lyt.addWidget(
            self.timer_action_b, 2, 0, QtCore.Qt.AlignmentFlag.AlignCenter
        )
        self.main_lyt.addWidget(
            self.save_session_b, 3, 0, QtCore.Qt.AlignmentFlag.AlignCenter
        )
        self.save_session_b.clicked.connect(self.show_session_details_editor)
        utils_funcs.load_and_set_ss(
            self.res_files.get_res("assets.qss.general"),
            self.res_files.get_res("assets.qss.reading_session_page"),
            widget=self,
        )

        # Timer
        self.seconds = 0
        self.minutes = 0
        self.hours = 0
        self.timer = timer.Timer()
        self.timer.timeout.connect(self.count_time)
        self.timer.start_timer(1000)
        self.timer.timer_paused.connect(self.switch_timer_action)
        self.timer.timer_resumed.connect(self.switch_timer_action)

        self._pause_connected = False
        self._resume_connected = False
        self._session_details_editor_active = False

        self.set_start_date()
        self.timer.timer_started.connect(self.set_start_date)
        self.switch_timer_action()
        self.refresh_time_label()

    def set_start_date(self):
        self.start_date = QtCore.QDate.currentDate()

    def count_time(self):
        """
        Update the values of the seconds, minutes and hours attribut and refresh the time widgets
        """
        if self.timer.timer_state == timer.TimerState.ACTIVE:
            # -- Calculate time to show --
            self.seconds = self.timer.loops_count % 60
            self.minutes = self.timer.loops_count // 60 if self.timer.loops_count else 0
            self.minutes %= 60  # Prevent from having value >= 60
            self.hours = self.timer.loops_count // 3600
            self.refresh_time_label()

    def refresh_time_label(self):
        """
        Refresh the widgets that are displaying the timer
        """
        self.time_lb.setText(f"{self.hours:02} : {self.minutes:02} : {self.seconds:02}")

    def switch_timer_action(self):
        """
        Switch the action to do when the play/pause button is clicked
        If the timer is paused, the action will be to resume it
        If the timer is active, the action will be to pause it
        """
        match self.timer.timer_state:
            case timer.TimerState.PAUSED:
                self.timer_action_b.setText("Resume")
                self.timer_action_b.setIcon(
                    images_tools.get_svg(self.res_files.get_res("assets.icons.play"))
                )
                if self._pause_connected:
                    self.timer_action_b.clicked.disconnect(self.timer.pause)
                    self._pause_connected = False

                if not self._resume_connected:
                    self.timer_action_b.clicked.connect(self.timer.resume)
                    self._resume_connected = True

            case timer.TimerState.ACTIVE:
                self.timer_action_b.setText("Pause")
                self.timer_action_b.setIcon(
                    images_tools.get_svg(self.res_files.get_res("assets.icons.pause"))
                )
                if self._resume_connected:
                    self.timer_action_b.clicked.disconnect(self.timer.resume)
                    self._resume_connected = False

                if not self._pause_connected:
                    self.timer_action_b.clicked.connect(self.timer.pause)
                    self._pause_connected = True

    def show_session_details_editor(self):
        """
        Pause the timer and show the session details editor if it is not already shown
        """
        if not self._session_details_editor_active:
            self.timer.pause()
            self.session_details_editor = SessionsDetailsWindow(
                None,
                self.api,
                QtCore.QDate.currentDate(),
                self.timer.loops_count,
                self._book,
            )
            self.session_details_editor.setWindowFlag(
                QtCore.Qt.WindowType.WindowStaysOnTopHint, True
            )
            self.session_details_editor.setAttribute(
                QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True
            )
            self._session_details_editor_active = True
            self.session_details_editor.destroyed.connect(self.session_editor_closed)
            self.session_details_editor.reading_session_saved.connect(
                lambda: self.qt_signals.emit_signal("close_page_sg")
            )
            self.session_details_editor.show()
            return

    def session_editor_closed(self):
        """
        Note that the session editor has been closed
        """
        self._session_details_editor_active = False
