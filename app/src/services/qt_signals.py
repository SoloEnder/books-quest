import logging
import typing
from enum import Enum, auto

from PySide6 import QtCore, QtWidgets


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
        self.logger.info("QtSignals Service initialized")

    def emit_signal(self, signal_name: str, *args):
        """
        Emit the signal named `signal_name`.
        If the signal is not enabled (e.g. it is blacklisted in ENABLED mode or not in the whitelist in DISABLED mode), then he is not emited

        Parameters
        ----------
        - signal_name: the name of the signal
        - *args: the arguments to pass to the signal
        """
        if not self.has_signal(signal_name):
            raise UnknownSignalError(signal_name)

        signal = getattr(self, signal_name)

        if self.signal_enabled(signal_name):
            self.logger.debug(
                f"Trying to emit '{signal_name}', but signal is not enabled !"
            )
            return signal.emit(*args)

    def has_signal(self, signal_name: str) -> bool:
        """
        Checks whether `signal_name` exists

        Parameters
        ----------
        - signal_name (str): the name of the signal to check

        Returns
        -------
        - bool: whether the signal exists or not
        """
        if not getattr(self, signal_name, None):
            return False

        return True

    def signal_enabled(self, signal_name: str) -> bool:
        """
        Checks if `signal_name` is currently enabled or not

        Parameters
        ----------
        - signal_name (str): the name of the signal to check
        """
        if (
            self.state == QtSignalsServiceState.ENABLED
            and signal_name in self.blacklist
        ):
            return False

        if (
            self.state == QtSignalsServiceState.DISABLED
            and signal_name not in self.whitelist
        ):
            return False

        return True

    def connect_to_signal(self, signal_name: str, func):
        """
        Connects `signal_name` to `func`
        `func` will be called everytime the signal will be emitted

        Parameters
        ----------
        - signal_name (str): The name of the signal
        - func (a function): The function object to connect
        """
        if self.has_signal(signal_name):
            signal = getattr(self, signal_name)
            signal.connect(func)

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
