import datetime
import os
import zipfile

import utils

BBS_VERSION = "1.0.0"
SUPPORTED_VERSIONS = ("1.0.0",)


def create_bbs_data(shelves_data: list[dict], program_version: str):
    """
    Returns a tuple containing the data to put in `infos.json` and `data.json` files (in this order)

    shelves_data: Shelves data
    """
    infos = {
        "type": "BBS",
        "created_at": str(datetime.datetime.now()),
        "format_version": BBS_VERSION,
        "program_version": program_version,
    }
    data = shelves_data
    return (infos, data)


def create_bbs_file(bbs_data: tuple[dict, list], covers_dir: str, dest_dir: str):
    """
    Creates a BooksQuest Shelves save file

    Parameters
    ----------
    bks_data: The value returned by the `create_bbs_data` function
    covers_dir: The directory where the shelves covers are stored (and ONLY them)
    dest (str): the path to the directory where to put the save result
    """
    utils.write_json(os.path.join(dest_dir, "infos.json"), bbs_data[0])
    utils.write_json(os.path.join(dest_dir, "shelves.json"), bbs_data[1])
    with zipfile.ZipFile(os.path.join(dest_dir, "shelves.bbs"), "w") as zpf:
        zpf.write("infos.json")
        zpf.write("shelves.json")
        zpf.mkdir("covers")

        for filename in os.listdir(covers_dir):
            zpf.write(
                os.path.join(covers_dir, filename), os.path.join("covers", filename)
            )


def open_bbs_file(save_path, dest_dir: str):
    """
    Exctract the content of a BooksQuest Shelves save file and return it's informations

    Parameters
    ----------
    save_path(str): the path to the save file
    dest_dir(str): the path to the directory where the file content will be extracted

    Returns
    -------
    dict: the informations stored into the `infos.json` file inside the save
    """
    utils.check_save(
        save_path,
        SUPPORTED_VERSIONS,
        [
            "BBS",
        ],
        ("infos.json", "shelves.json", "covers/"),
    )
    return utils.extract_save_file(save_path, dest_dir)
