import os

import dicts_paths_handler

from app.src import json_dicts_paths_handler


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


class RessourcesHandler(json_dicts_paths_handler.JSONDictPathHandler):
    def __init__(self, jfm, base_dict: dict, base_path: str):
        super().__init__(jfm, base_dict)
        self.base_path = base_path

    def get_res(self, ress_dict_path: str):
        sections = ress_dict_path.split(".")
        ress_path = self.base_path
        current_value = self.base_dict.copy()

        try:
            for key in sections:
                current_value = current_value[key]

                if isinstance(current_value, dict):
                    dir_name = current_value["_base_"]

                    if dir_name:
                        ress_path = os.path.join(ress_path, dir_name)

                    else:
                        raise RessBasePathNotFound(ress_dict_path)

                else:
                    ress_path = os.path.join(ress_path, current_value)

        except KeyError:
            raise dicts_paths_handler.InvalidDictPathError(ress_dict_path)

        else:
            return ress_path
