import logging

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import api, book_sys


class ReadingSessionSummaryViewer(QtWidgets.QDialog):
    """
    Displays various information about a reading session :
        - The pages read
        - The time of reading
        - The estimated reading speed (in pages/hours)
        - The time remaining to complete reading of the book
    """

    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        api: api.API,
        reading_session: book_sys.ReadingSession,
        book_id: str,
    ):
        """
        This widget displays a summary of a reading session, including :
            - The pages read
            - The reading speed (in pages/hours)
            - The estimated reading time remaining

        Parameters
        ----------
        - api (API): the app internal api
        - reading_session (ReadingSession): the reading session to summarize
        - book_id: the id of the book that has been read
        """
        super().__init__(parent)

        # Parameters attribution
        self.api = api
        self.reading_session = reading_session
        self.book_id = book_id

        # -- Logger --
        self.logger = logging.getLogger(__name__ + " - Reading Session Summary Viewer")

        # -- Gets book with the provided id --
        self.book = self.api.books.books_handler.books[book_id]

        self.setWindowTitle("Reading Session Summary Viewer - " + self.book.title)

        self.main_lyt = QtWidgets.QGridLayout(self)

        # -- Convert seconds duration into seconds, minutes and hours --
        self.converted_duration = self.convert_duration(self.reading_session.duration)
        # -- Get reading speed, in pages/seconds --
        self.read_pages_per_sec = (
            self.reading_session.pages_read / self.reading_session.duration
            if self.reading_session.duration
            else 0
        )

        # -- Estimated Remaining reading time for the book in seconds
        self.remaining_reading_time = int(
            (self.book.tot_pages - self.book.read_pages) / self.read_pages_per_sec
            if self.read_pages_per_sec > 0
            else 0
        )
        self.converted_remaining_reading_time = self.convert_duration(
            self.remaining_reading_time
        )
        self.logger.info(
            f"Reading session summary : {self.reading_session.pages_read=}, {self.reading_session.duration=}, {self.read_pages_per_sec=}, {self.remaining_reading_time=}"
        )

        # -- Read book cover --
        self.book_cover_viewer = QtWidgets.QLabel(
            self, pixmap=QtGui.QPixmap(self.api.books.get_book_cover_path(self.book))
        )

        self.read_pages_times_lb = QtWidgets.QLabel(
            self,
            text=f"You read <b>{self.reading_session.pages_read}</b> pages in <b>{self.converted_duration[2]:02}:{self.converted_duration[1]:02}:{self.converted_duration[0]:02}</b>",
        )

        # -- Session summary widgets --
        self.read_pages_times_lb.setObjectName("ReadPagesInTimeLabel")
        self.reading_speed_lb = QtWidgets.QLabel(
            self,
            text=f"That's <b>{int(self.read_pages_per_sec * 3600)}</b> pages per hours",
        )
        self.reading_speed_lb.setObjectName("ReadingSpeedLabel")
        self.estimated_remaining_time_lb = QtWidgets.QLabel(
            text=f"The estimated reading time remaining is <b>{self.converted_remaining_reading_time[2]:02}:{self.converted_remaining_reading_time[1]:02}:{self.converted_remaining_reading_time[0]:02}</b>",
        )
        self.estimated_remaining_time_lb.setObjectName("EstimatedRemainingTimeLabel")

        # -- Congratulation message if the whole book has been read --
        self.finished_reading_lb = QtWidgets.QLabel(
            f'Congratulation, You are done reading <b>"{self.book.title}"</b> !'
        )
        self.finished_reading_lb.setObjectName("FinishedReadingLabel")

        # -- Close button --
        self.close_button = QtWidgets.QPushButton("Ok")
        self.close_button.clicked.connect(self.close)
        self.close_button.setObjectName("CloseButton")

        # -- Add widgets to layout --
        self.main_lyt.addWidget(self.book_cover_viewer, 0, 0, 7, 1)
        self.main_lyt.addWidget(
            self.read_pages_times_lb, 0, 1, QtCore.Qt.AlignmentFlag.AlignBottom
        )
        self.main_lyt.addWidget(
            QtWidgets.QFrame(frameShape=QtWidgets.QFrame.Shape.HLine),
            1,
            1,
            QtCore.Qt.AlignmentFlag.AlignTop,
        )
        self.main_lyt.addWidget(
            self.reading_speed_lb, 2, 1, QtCore.Qt.AlignmentFlag.AlignBottom
        )
        self.main_lyt.addWidget(
            QtWidgets.QFrame(frameShape=QtWidgets.QFrame.Shape.HLine),
            3,
            1,
            QtCore.Qt.AlignmentFlag.AlignTop,
        )

        # -- Wether to show congratulations message --
        if self.book.reading_state == book_sys.Book.ReadingState.FINISHED:
            self.main_lyt.addWidget(
                self.finished_reading_lb,
                4,
                1,
                QtCore.Qt.AlignmentFlag.AlignBottom,
            )

        else:
            self.main_lyt.addWidget(
                self.estimated_remaining_time_lb,
                4,
                1,
                QtCore.Qt.AlignmentFlag.AlignBottom,
            )

        self.main_lyt.addWidget(
            QtWidgets.QFrame(frameShape=QtWidgets.QFrame.Shape.HLine),
            5,
            1,
            QtCore.Qt.AlignmentFlag.AlignTop,
        )
        self.main_lyt.addWidget(
            self.close_button,
            6,
            1,
            QtCore.Qt.AlignmentFlag.AlignLeft,
        )

    def convert_duration(self, duration) -> tuple[int, int, int]:
        """
        Convert a `duration` (in seconds) into seconds, minutes and hours and return the result in a tuple
        """
        seconds = duration % 60
        minutes = duration // 60 if duration else 0
        minutes %= 60  # Prevent from having value >= 60
        hours = duration // 3600

        return (seconds, minutes, hours)


class ReadingSessionWidget(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        api: api.API,
        session: book_sys.ReadingSession,
    ):
        """
        Small horizontal widget that displays some reading session details : start date, duration, pages read
        """
        super().__init__(parent)
        self.api = api
        self._session = session
        self.main_lyt = QtWidgets.QHBoxLayout(self)

        self.start_date_lb = QtWidgets.QLabel(
            self.format_date(
                self._session.start_date.year,
                self._session.start_date.month,
                self._session.start_date.day,
            )
        )
        self.start_date_lb.setProperty("role", "BookDetailValue")
        self.start_date_lb.setObjectName("SessionStartDateLabel")
        self.duration_lb = QtWidgets.QLabel(
            self, text=self.format_duration(self._session.duration)
        )
        self.start_date_lb.setObjectName("SessionDurationLabel")
        self.duration_lb.setProperty("role", "BookDetailValue")
        self.pages_read_lb = QtWidgets.QLabel(
            self,
            text=f"(+{self.api.langs.tr('shared.infos.pages_count_args', count=self._session.pages_read)} )",
        )
        self.pages_read_lb.setObjectName("SessionPagesReadLabel")
        self.pages_read_lb.setProperty("role", "BookDetailValue")

        self.main_lyt.addWidget(
            self.start_date_lb,
        )
        self.main_lyt.addWidget(
            self.duration_lb,
        )
        self.main_lyt.addWidget(
            self.pages_read_lb,
        )

    def format_duration(self, duration: int):
        seconds = self._session.duration % 60
        minutes = self._session.duration // 60 if self._session.duration else 0
        minutes %= 60  # Prevent from having value >= 60
        hours = self._session.duration // 3600
        formatted = ""

        if hours:
            formatted += (
                f"{hours}{self.api.langs.tr('shared.time_units.hours_abbreviated')}, "
            )

        if minutes:
            formatted += f"{minutes}{self.api.langs.tr('shared.time_units.minutes_abbreviated')}, "

        formatted += (
            f"{seconds}{self.api.langs.tr('shared.time_units.seconds_abbreviated')}"
        )

        return formatted

    def format_date(
        self,
        year: int | str,
        month: int | str,
        day: int | str,
        format: str = "yyyy-mm-dd : ",
    ):
        """
        Format an date (year, month, date) in an string based on `format`.

        Parameters
        ----------
        - year(str|int): the year
        - month(str|int): the month
        - day(str|int): the day
        - format(str): the format to apply. See below for more details.

        The format is specified by the `format` parameters.
        To specify where year/month/day should be, you must use their placeholder :
            - yyyy : the placeholder for the year
            - mm : the placeholder for the month
            - dd : the placeholder for the day

        Exemple
        -------
        - Assume that `year=2020`, `month=10`, `day=23` with `format='yyyy/mm/dd'`
        Then the returned string will be : "2020/10/23"
        """
        result = format
        result = result.replace("yyyy", str(year))
        result = result.replace("mm", str(month))
        result = result.replace("dd", str(day))

        return result


class ReadingSessionsViewer(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        api: api.API,
        reading_sessions: list[book_sys.ReadingSession],
    ):
        """
        Displays an vertical list of `ReadingSessionWidget` based on the reading sessions given in `reading_session`
        """
        super().__init__(parent)
        self.api = api
        self._reading_sessions = reading_sessions

        # Widgets
        self.main_lyt = QtWidgets.QVBoxLayout(self)

        # Generating widgets for each sessions
        for session in self._reading_sessions:
            self.main_lyt.addWidget(ReadingSessionWidget(self, self.api, session))
            self.main_lyt.addWidget(
                QtWidgets.QFrame(
                    self,
                    frameShape=QtWidgets.QFrame.Shape.HLine,
                    frameShadow=QtWidgets.QFrame.Shadow.Raised,
                )
            )
