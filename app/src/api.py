import logging

from app.src.services import books, langs, qt_signals, res_files, settings
from app.utils import paths


class API:
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}-GeneralAPI")
        self.qt_signals = qt_signals.QtSignalsService()
        self.res_files = res_files.ResourcesFilesService(
            paths.APP_PATH, paths.RESS_INDEXES_FILEPATH
        )
        self.settings = settings.SettingsService(self.res_files)
        self.books = books.BooksService(self.res_files, self.qt_signals)
        self.langs = langs.LangsService(self.res_files, self.settings, self.qt_signals)
        self.logger.info("GeneralAPI initialized")
