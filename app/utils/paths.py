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

# Assets
ASSETS_PATH = os.path.join(BASE_PATH, "assets")
ICONS_PATH = os.path.join(ASSETS_PATH, "icons")
DEFAULT_COVERS_PATH = os.path.join(ASSETS_PATH, "default")
QSS_FILES_PATH = os.path.join(ASSETS_PATH, "qss")

# Data
DATA_PATH = os.path.join(BASE_PATH, "data")

BOOKS_DATA_PATH = os.path.join(DATA_PATH, "books")
BOOKS_COVERS_PATH = os.path.join(BOOKS_DATA_PATH, "books_cover")
SHELFS_COVERS_PATH = os.path.join(BOOKS_DATA_PATH, "shelfs_covers")

# Logs
LOGS_PATH = os.path.join(BASE_PATH, "logs")

# tmp
TMP_DIR_PATH = ""

all_paths = {
    "base_path": BASE_PATH,
    "assets_path": ASSETS_PATH,
    "icons_path": ICONS_PATH,
    "default_cover_path": DEFAULT_COVERS_PATH,
    "data_path": DATA_PATH,
    "books_data_path": BOOKS_DATA_PATH,
    "books_covers_path": BOOKS_COVERS_PATH,
    "shelfs_cover_path": SHELFS_COVERS_PATH,
    "logs_path": LOGS_PATH,
    "tmp_dir_path": TMP_DIR_PATH,
    "qss_files_dir":QSS_FILES_PATH,
}
