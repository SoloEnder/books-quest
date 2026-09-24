import enum
import logging

from PySide6.QtCore import QObject, QTimer
from shiboken6.Shiboken import Object


class TimerState(enum.Enum):
    INACTIVE = enum.auto()
    ACTIVE = enum.auto()
    PAUSED = enum.auto()


class Timer(QTimer):
    """
    This class act as a subclass of `QTimer`, that add methods to pause/resume timer
    """

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__ + " - Timer")
        self.loops_count: int = 0
        self.interval_: int = 1000
        self.timer_state = TimerState.INACTIVE
        self.timeout.connect(self.count_time)

    def count_time(self):
        self.loops_count += 1

    def start_timer(self, interval: int = 1000):
        """
        Start or restart the timer

        Parameters
        ----------
        """
        self.timer_state = TimerState.ACTIVE
        self.loops_count = 0
        self.interval_ = interval
        self.start(interval)
        self.logger.debug("Timer restarted !")

    def stop_timer(self):
        """
        Stops the timer
        """
        self.stop()
        self.timer_state = TimerState.INACTIVE
        self.logger.info(
            f"Timer stopped, counted {self.loops_count} loops with interval={self.interval()} "
        )

    def pause(self):
        """
        Pause the timer if it was active. Otherwise, this will do nothing
        """
        if self.timer_state == TimerState.ACTIVE:
            self.timer_state = TimerState.PAUSED
            self.stop()
            self.logger.debug(
                f"Timer paused, counted {self.loops_count} with interval={self.interval} ms !"
            )

        else:
            self.logger.warning("Timer is not active, could not pause it")

    def resume(self):
        """
        Resume the timer if it was paused. Otherwise, this will do nothing
        """
        if self.timer_state == TimerState.PAUSED:
            self.start(self.interval_)
            self.logger.info("Timer resumed !")

        else:
            self.logger.warning("Timer is not paused, could not resume it")
