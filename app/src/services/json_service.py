import json
import logging
import typing


class JSONService:
    """
    Supports operations on JSON files
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}-JSON Service")
        self.logger.info("JSONAPI initialized")

    def write(self, filepath: str, data: typing.Any, encoding: str = "utf-8"):
        """
        Write `data` to `filepath`

        Parameters
        ----------
        filepath (str): the file where to write the data
        data: the data to write
        encoding: the encoding in which to write the data
        """
        with open(filepath, "w", encoding=encoding) as f:
            json.dump(data, f)

    def read(self, filepath: str, encoding: str = "utf-8"):
        """
        Return the content of `filepath`, which must be a JSON file

        Parameters
        ----------
        - filepath (str): the file to open
        - encoding (str): the encoding of the file
        """

        with open(filepath, "r", encoding=encoding) as f:
            return json.load(f)
