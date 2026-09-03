import logging

from app.src.services import books, res_files
from app.utils import paths


class API:
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}-GeneralAPI")
        self.books = books.BooksService(self.res_files)
        self.res_files = res_files.ResourcesFilesService(
            paths.APP_PATH, paths.RESS_INDEXES_FILEPATH
        )
        self.logger.info("GeneralAPI initialized")
