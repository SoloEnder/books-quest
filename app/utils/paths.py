# app/base_path.py
import os
import sys
import typing
from pathlib import Path

print(f"{sys.executable=}")


def get_base_path(mode: typing.Literal["frozen", "unfrozen"] = "unfrozen") -> str:
    """
    Return the direcory which is the base of all the programs path

    Args:
        mode: "frozen" if the app is a binary file made with pyinstaller in --onedir mode, "unfrozen" if else (default)
    """

    if mode == "frozen":
        path = Path(sys.executable).parents[0]

    elif mode == "unfrozen":
        path = Path(__file__).parents[2]

    else:
        raise ValueError(f"Invalid value given for argument <mode> : '{mode}'")

    return str(path)


BASE_PATH = get_base_path()
APP_PATH = os.path.join(BASE_PATH, "app")
RESS_INDEXES_FILEPATH = os.path.join(APP_PATH, "indexes.json")
