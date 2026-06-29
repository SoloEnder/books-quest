import json
import os


class MyBaseException(Exception):
    def __init__(self):
        """Common base class to my Exceptions"""
        self.msg = "An exception has occured !"
        super().__init__()

    def __str__(self):
        return self.msg


def get_installation_infos(installation_path: str) -> dict:
    """
    Returns the infos about the installation

    Parameters
    ----------
    - installation_path (str): the path to the installation root directory
    """
    with open(os.path.join(installation_path, "app", "app_infos.json"), "r") as f:
        return json.load(f)


def read_json(filepath: str):

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(filepath: str, data):

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f)


def check_and_make_folder(folder: str):
    """
    Checks if a folder exists, and make it otherwise

    Parameters
    ----------
    - folder: the folder to check
    """
    if not os.path.exists(folder):
        os.mkdir(folder)
