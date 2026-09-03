import logging
from enum import Enum, auto

from PySide6 import QtCore, QtGui, QtWidgets

from app.src.book_sys import Book, Shelf


class UnknownSignalError(Exception):
    def __init__(self, signal_name: str):
        self.signal_name = signal_name
        self.msg = f"Unknown Signal '{signal_name}' !"


class QtSignalsServiceState(Enum):
    DISABLED = auto()
    ENABLED = auto()


class QtSignalsService(QtCore.QObject):
    apply_settings_sg = QtCore.Signal()
    refresh_ui_sg = QtCore.Signal()
    refresh_page_sg = QtCore.Signal(str, dict)
    refresh_current_page_sg = QtCore.Signal()
    switch_page_sg = QtCore.Signal(str, bool, dict)
    close_page_sg = QtCore.Signal()
    notify_sg = QtCore.Signal(str, str, str, str)
    edit_progress_msg = QtCore.Signal(str)
    show_about_sg = QtCore.Signal(bool)
    write_version_on_widget_sg = QtCore.Signal(
        QtWidgets.QWidget
    )  # Write the app current version on an widget that support `setText` method
    check_for_updates_sg = QtCore.Signal(
        bool
    )  # Checks for update. First argument indicates whether to show a pop-up when app is up to date
    # ---- Signal emited when user add/edit an object in the library. First parameter is the object ID
    book_added_sg = QtCore.Signal(str)
    book_edited_sg = QtCore.Signal(str)
    book_removed_sg = QtCore.Signal(str)
    shelf_added_sg = QtCore.Signal(str)
    shelf_edited_sg = QtCore.Signal(str)
    shelf_removed_sg = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}-QtSignalsService")
        self.state = QtSignalsServiceState.ENABLED
        self.whitelist = []  # Signals that are allowed to be emitted in DISABLED mode
        self.blacklist = []  # Signals that are not allowed to be emitted in ENABLED mode

    def emit_signal(self, signal_name: str, *args):
        """
        Emit the signal named `signal_name`

        Parameters
        ----------
        - signal_name: the name of the signal
        - *args: the arguments to pass to the signal
        """

        try:
            signal = getattr(
                self, signal_name
            )  # Getting signal from the attribute (look below the class definition)

        # The signal is not found
        except AttributeError:
            raise UnknownSignalError(signal_name)

        if (
            self.state == QtSignalsServiceState.ENABLED
            and signal_name not in self.blacklist
        ):
            return signal.emit(*args)

        if (
            self.state == QtSignalsServiceState.DISABLED
            and signal_name in self.whitelist
        ):
            return signal.emit(*args)

    def disable(self, exceptions: list[str]):
        """Disable the `QtSignalsService`, meaning that any emition request with `emit_signal` methods will be ignored

        Parameters
        ----------
        - exceptions (list[str]): a list of signal's name that can be emitted in DISABLED mode
        """
        self.state = QtSignalsServiceState.DISABLED
        self.whitelist = exceptions
        self.logger.info("Switching to DISABLED mode")
        self.logger.debug(f"Registering {len(exceptions)} signals in whitelist")

    def enable(self, exceptions: list[str]):
        """Enable the `QtSignalsService`

        Parameters
        ----------
        - exceptions (list[str]): a list of signal's names that are not allowed to be emitted in ENABLED mode
        """
        self.state = QtSignalsServiceState.ENABLED
        self.blacklist = exceptions
        self.logger.info("Switching to ENABLED mode")
        self.logger.debug(f"Registering {len(exceptions)} signals in blacklist")
