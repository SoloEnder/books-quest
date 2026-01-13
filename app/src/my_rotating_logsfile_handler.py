
import os
import pathlib
import logging.handlers

class MyRotatingFileHandler(logging.handlers.RotatingFileHandler):

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0,
                 encoding=None, delay=False, errors=None):
        file_parent = pathlib.Path(filename).parent

        if not file_parent.exists():
            file_parent.mkdir(parents=True)

        super().__init__(filename, mode, maxBytes, backupCount, encoding=None, delay=False, errors=None)
