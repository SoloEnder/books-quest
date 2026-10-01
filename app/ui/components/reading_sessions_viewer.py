from PySide6 import QtWidgets

from app.src import api, book_sys


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
        self.duration_lb = QtWidgets.QLabel(
            self, text=self.format_duration(self._session.duration)
        )
        self.duration_lb.setProperty("role", "BookDetailValue")
        self.pages_read_lb = QtWidgets.QLabel(
            self, text=f" +{self._session.pages_read} pages"
        )
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
            formatted += f"{hours:02}h, "

        if minutes:
            formatted += f"{minutes:02}min, "

        formatted += f"{seconds:02}s"

        return formatted

    def format_date(
        self,
        year: int | str,
        month: int | str,
        day: int | str,
        format: str = "yyyy-mm-dd",
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
