import logging

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import api, timer
from app.ui.main_pages import base_page
from app.utils import images_tools, utils_funcs


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

        self.switch_timer_action()
        self.refresh_time_label()

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
