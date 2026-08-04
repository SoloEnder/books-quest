import logging.handlers
import os
import pathlib
import traceback

from PySide6 import QtWidgets


class MyRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(
        self,
        filename,
        mode="a",
        maxBytes=0,
        backupCount=0,
        encoding=None,
        delay=False,
        errors=None,
    ):
        file_parent = pathlib.Path(filename).parent

        if not file_parent.exists():
            file_parent.mkdir(parents=True)

        super().__init__(
            filename,
            mode,
            maxBytes,
            backupCount,
            encoding=None,
            delay=False,
            errors=None,
        )


class SensitiveInfoFilter(logging.Filter):
    def filter(self, record):
        userpath = os.path.expanduser("~")

        if userpath.lower() in record.getMessage().lower():
            record.msg = record.getMessage().replace(userpath, "~")
            record.args = ()

        return True


class ErrorsFilter(logging.Filter):
    def filter(self, record):

        if record.levelname == "ERROR" or record.levelname == "CRITICAL":
            error_window = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Critical,
                "Error",
                record.getMessage(),
                detailedText=traceback.format_exc(),
            )
            error_window.exec()

        return True
