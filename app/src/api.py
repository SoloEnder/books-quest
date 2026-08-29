import logging

from app.src.apis import res_files
from app.utils import paths


class API:
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}-GeneralAPI")
        self.res_files = res_files.ResourcesFilesAPI(
            paths.APP_PATH, paths.RESS_INDEXES_FILEPATH
        )
        self.logger.info("GeneralAPI initialized")
