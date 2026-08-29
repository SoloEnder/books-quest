import logging
import os
import typing

import dicts_paths_handler
from dicts_paths_handler.dicts_paths_handler import DictsPathsHandler

from app.src.apis import json_api


class ResourcesFilesAPI:
    def __init__(self, base_path: str, indexes_filepath: str):
        self.indexes_filepath = indexes_filepath
        self.base_path = base_path

        self.logger = logging.getLogger(f"{__name__}-ResourcesFilesAPI")
        self.dicts_paths_handler = DictsPathsHandler()
        self.json_api = json_api.JSONAPI()
        self.load_indexes(indexes_filepath)
        self.logger.info("ResourcesFileAPI initialized")

    def load_indexes(self, filepath: str | None = None):
        """
        Load BooksQuests indexes from a JSON file

        Parameters
        ----------
        filepath (str|None=None): the file from which load the indexes. If not given or None, then `indexes_filepath` attr is used
        """
        self.dicts_paths_handler.base_dict = self.json_api.read(
            filepath or self.indexes_filepath
        )

    def write_indexed_file(
        self,
        dict_path: str,
        data: typing.Any,
        mode: str = "w",
        encoding: str = "utf-8",
        **kwargs,
    ):
        """
        Write in an indexed file

        Parameters
        ----------
        - dict_path (str): the dict path to the file in the index
        - mode (str="w"): the mode in which open the file, must start by "w" or "a" since this function *writes* in a file
        - encoding (str="utf-8"): the encoding of the file
        - **kwargs: additionnal arguments to pass to the `open` function

        """
        filepath = self.get_res(dict_path)
        return self.write_file(filepath, data, mode, encoding, **kwargs)

    def write_file(
        self,
        filepath: str,
        data: typing.Any,
        mode: str = "w",
        encoding: str = "utf-8",
        **kwargs,
    ):
        """
        Write `data` in `filepath`

        Parameters
        ----------
        - filepath (str): the path to the file to write
        - data: the data to write
        - mode (str="r"): the mode in which open the file, must start by "w" or "a" since this function *write* a in file
        - encoding (str="utf-8"): the encoding of the file
        - **kwargs: additionnal arguments to pass to the `open` function

        """
        self.logger.debug(f"Writing in {filepath}...")
        if not mode.startswith(("a", "w")):
            raise ValueError(
                "Opening modes that does not start by 'a' or 'w' are not allowed !"
            )

        if os.path.splitext(filepath)[1] == ".json":
            self.logger.info("File is a JSON file, writing it with JSONAPI")
            return self.json_api.write(filepath, data)

        with open(filepath, mode=mode, encoding=encoding, **kwargs) as f:
            return f.write(data)

    def read_indexed_file(
        self,
        dict_path: str,
        mode: str = "r",
        encoding: str = "utf-8",
        reading_length: int = -1,
        **kwargs,
    ) -> typing.Any:
        """
        Read an indexed file and return its content

        Parameters
        ----------
        - dict_path (str): the dict path to the file in the index
        - mode (str="r"): the mode in which open the file, must start by "r" since this function *read* a file
        - encoding (str="utf-8"): the encoding of the file
        - reading_length (int=-1): the numbers of characters to read, default to all.
        - **kwargs: additionnal arguments to pass to the `open` function

        """
        filepath = self.get_res(dict_path)
        return self.read_file(filepath, mode, encoding, reading_length, **kwargs)

    def read_file(
        self,
        filepath: str,
        mode: str = "r",
        encoding: str = "utf-8",
        reading_length: int = -1,
        **kwargs,
    ) -> typing.Any:
        """
        Read `filepath` and return its content

        Parameters
        ----------
        - filepath (str): the path to the file to read
        - mode (str="r"): the mode in which open the file, must start by "r" since this function *read* a file
        - encoding (str="utf-8"): the encoding of the file
        - reading_length (int=-1): the numbers of characters to read, default to all.
        - **kwargs: additionnal arguments to pass to the `open` function

        """
        self.logger.debug(f"Reading data in {filepath}...")
        if not mode.startswith("r"):
            raise ValueError(
                "Opening mode that does not start with 'r' are not allowed !"
            )

        if os.path.splitext(filepath)[1] == ".json":
            self.logger.info("File is a JSON file, reading it with JSONAPI")
            return self.json_api.read(filepath)

        with open(filepath, mode=mode, encoding=encoding, **kwargs) as f:
            return f.read(reading_length)

    def delete(self, path: str):
        """
        Delete the element at `path`.

        Parameters
        ----------
        - path (str): The path to the element to delete

        """

        if os.path.isfile(path):
            os.remove(path)

        elif os.path.isdir(path):
            os.rmdir(path)

        else:
            raise FileNotFoundError(path)

    def get_res(self, res_dict_path: str):
        """
        Return the absolute path of `res_dict_path`, which must be a dict path *present* in the indexes file
        """

        sections = res_dict_path.split(".")
        res_path = self.base_path
        current_value = self.dicts_paths_handler.base_dict.copy()

        try:
            for key in sections:
                print(key)
                current_value = current_value[key]

                if isinstance(current_value, dict):
                    dir_name = current_value["_base_"]

                    if dir_name:
                        res_path = os.path.join(res_path, dir_name)

                    else:
                        raise RessBasePathNotFound(res_dict_path)

                else:
                    res_path = os.path.join(res_path, current_value)

        except KeyError:
            raise dicts_paths_handler.InvalidDictPathError(res_dict_path)

        else:
            return res_path


class RessBasePathNotFound(Exception):
    def __init__(self, dict_path, msg: str | None = None):
        self.dict_path = dict_path
        self.msg = (
            msg
            or f"Unable to make path with dict path '{self.dict_path}' : no valid _base_ key found !"
        )
        super().__init__(self.msg)

    def __str__(self) -> str:
        return self.msg
