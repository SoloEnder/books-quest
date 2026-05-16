# app/base_path.py
import os
import typing
from pathlib import Path


def get_base_path(mode: typing.Literal["frozen", "unfrozen"] = "unfrozen") -> str:
    """
    Return the direcory which is the base of all the programs path

    Args:
        mode: "frozen" if the app is a binary file made with pyinstaller in --onedir mode, "unfrozen" if else (default)
    """

    if mode == "frozen":
        path = Path(__file__).parents[1]

    elif mode == "unfrozen":
        path = Path(__file__).parents[1]

    else:
        raise ValueError(f"Invalid value given for argument <mode> : '{mode}'")

    return str(path)


BASE_PATH = get_base_path()

RESS_INDEXES_FILEPATH = os.path.join(BASE_PATH, "indexes.json")
