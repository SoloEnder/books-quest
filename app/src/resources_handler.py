import os

from app.src import json_dicts_paths_handler
from app.utils import my_exceptions


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
                        raise my_exceptions.RessBasePathNotFound(ress_dict_path)

                else:
                    ress_path = os.path.join(ress_path, current_value)

        except KeyError:
            raise my_exceptions.InvalidDictPathError(ress_dict_path)

        else:
            return ress_path
