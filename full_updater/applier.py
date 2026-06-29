import datetime as dt
import os
import pathlib
import shutil
import sys
import typing

import utils

FULL_UPDATE_MANAGER_VERSION = "1.0.0"


def run(installation_path: str):
    update_exe_path = sys.executable
    update_path = str(pathlib.Path(update_exe_path).parent)
    check_update(str(update_path), installation_path)
    update_infos_filepath = os.path.join(installation_path, "update_infos.json")
    upgrader_infos = getuinfos(update_path)
    installation_infos = utils.get_installation_infos(installation_path)
    installation_semantic_version = installation_infos["version"]["semantic"]
    backup_folder = os.path.join(
        installation_path, f"backup_{installation_semantic_version}"
    )
    update_infos_data = {
        "from_version": installation_infos["version"],
        "to_version": upgrader_infos["upgrade_to"],
        "state": "IN_PROGRESS",
        "started_at": str(dt.datetime.now()),
        "ended_at": None,
        "backup_folder": backup_folder,
    }
    utils.write_json(update_infos_filepath, update_infos_data)
    update_instructions = utils.read_json(
        os.path.join(update_path, "update_instructions.json")
    )
    undo_filepath = os.path.join(backup_folder, "undo.json")
    utils.check_and_make_folder(backup_folder)
    utils.write_json(undo_filepath, [])
    apply_upgrade(
        update_instructions,
        installation_path,
        backup_folder,
        update_path,
        undo_filepath,
    )
    update_infos_data["state"] = "COMPLETED"
    utils.write_json(update_infos_filepath, update_infos_data)


def apply_upgrade(
    instructions: list,
    installation_folder,
    backup_folder,
    update_folder: str,
    undo_filepath: str,
):
    """
    Apply the update instructions

    Parameters
    ----------
    - instructions (list): a list of instructions to execute
    - installation_folder (str): the folder where is located the user program installation
    - backup_folder: the folder where will be temporary stored the client files that has been modified, for allow downgrade if something went wrong during the update
    - update_folder (str): the path where is located the content of the update
    - undo_filepath (list): the filepath where to store the data used for downgrade if something went wrong during the update

    Raises
    ------
    - InvalidUpdateInstructions: if `from_` or `to` does not respect the allowed syntax
    """
    undo = []

    for step in instructions:
        if step["type"] == "move":
            move_item(
                step["from"],
                step["to"],
                os.path.join(update_folder),
                installation_folder,
                undo,
            )
            utils.write_json(undo_filepath, undo)

        elif step["type"] == "remove":
            remove_item(step["path"], installation_folder, backup_folder, undo)
            utils.write_json(undo_filepath, undo)

        else:
            raise InvalidUpdateInstructions


def move_item(
    from_: str, to: str, update_content_path: str, installation_path: str, undo: list
):
    """
    Moves a file/directory from an extracted update folder to a specific destination in the user installation folder

    Parameters
    ----------
    - from_ (str): the original location of the file/directory, relative to `update_content_path`. The path must starts by 'update::' or `installation::`,
    - to (str): the destination of the moved file, relative to `ìnstallation_path`. The path must starts with 'installation::' or `update::`
    - update_content_path (str): the path where is located the content of the update
    - installation_path (str): the path where is located the user program installation
    - undo (list): the list where are stored the opposite of the actions done by the updater

    Raises
    ------
    - InvalidUpdateInstructions: if `from_` or `to` does not respect the allowed syntax
    """
    old_from_ = from_
    from_ = from_.split("::")[1]
    if old_from_.startswith("update::"):
        from_ = os.path.abspath(os.path.join(update_content_path, from_))

    elif old_from_.startswith("installation::"):
        from_ = os.path.abspath(os.path.join(installation_path, from_))

    else:
        raise InvalidUpdateInstructions()

    old_to = to
    if to.startswith("installation::"):
        to = os.path.abspath(os.path.join(installation_path, to.split("::")[1]))

    elif to.startswith("update::"):
        to = os.path.abspath(os.path.join(update_content_path, to.split("::")[1]))

    else:
        raise InvalidUpdateInstructions

    if os.path.isdir(from_):
        shutil.copytree(from_, to)

    else:
        shutil.copy(from_, to)

    undo.insert(
        0,
        {
            "type": "remove",
            "path": old_to,
        },
    )


def remove_item(
    path: str,
    installation_folder: str,
    backup_folder: str,
    undo: list,
):
    """
    Moves an item deleted by the update instructions in the backup folder, for allow recovery.

    - path (str): the path to element to delete, relative to the `installation_folder`. It must starts with 'installation::'.
    - installation_folder (str): the path to the location of the user program installation
    - backup_folder (str): the folder where where to moves the pseudo deleted element
    - undo (list): the list where are stored the opposite of the actions done by the updater

    Raises
    ------
    - InvalidUpdateInstructions: if `path` does not respect the allowed syntax
    """
    if path.startswith("installation::"):
        old_path = path
        path = os.path.abspath(os.path.join(installation_folder, path.split("::")[1]))

    else:
        raise InvalidUpdateInstructions

    shutil.move(path, backup_folder)
    undo.insert(
        0,
        {
            "type": "move",
            "from": "backup::" + os.path.basename(path),
            "to": old_path,
        },
    )


def check_update(update_path: str, installation_path: str):
    update_content = os.listdir(update_path)
    excepted_content = (
        "_internal",
        "app",
        "installation_upgrader_infos.json",
        "update_instructions.json",
        "installation_upgrader.exe",
        "books_quest.exe",
    )
    missings_elements = []
    for excepted in excepted_content:
        if excepted not in update_content:
            missings_elements.append(excepted)

    if missings_elements:
        raise MissingsElementsError(missings_elements)

    upgrade_infos = getuinfos(update_path)
    excepted_keys = (
        "upgrade_to",
        "format_version",
    )
    if not tuple(upgrade_infos.keys()) == excepted_keys:
        raise InvalidUpdateInfos

    if not upgrade_infos["format_version"] == FULL_UPDATE_MANAGER_VERSION:
        raise UnsupportedUpgraderVersion(
            FULL_UPDATE_MANAGER_VERSION, upgrade_infos["format_version"]
        )

    installation_infos = utils.get_installation_infos(installation_path)

    if int(installation_infos["version"]["semantic"]) > int(
        upgrade_infos["upgrade_to"]["semantic"]
    ):
        raise DownGradeError(
            upgrade_infos["version"]["readable"],
            installation_infos["version"]["readable"],
        )


def getuinfos(update_content: str) -> dict:
    """
    Returns the content of `installation_upgrader_infos.json` file in the upgrader instance
    """
    return utils.read_json(
        os.path.join(update_content, "installation_upgrader_infos.json")
    )


class MyBaseException(Exception):
    def __init__(self):
        """Common base class to my Exceptions"""
        self.msg = "An exception has occured !"
        super().__init__()

    def __str__(self):
        return self.msg


class MissingsElementsError(MyBaseException):
    def __init__(self, missing_elements: typing.Sequence[str]):
        super().__init__()
        self.msg = (
            f"The following elements {missing_elements} are missing in the update !"
        )


class InvalidUpdateInfos(MyBaseException):
    def __init__(self):
        super().__init__()
        self.msg = "The information declared by the installation upgrader are not in a valid format !"


class UnsupportedUpgraderVersion(MyBaseException):
    def __init__(self, supported_version: str, declared_version: str):
        super().__init__()
        self.supported_version = supported_version
        self.declared_version = declared_version
        self.msg = f"Upgrader declared version is {declared_version}, but the version supported by the upgrader manager is only {supported_version}"


class UntargetedInstallationError(MyBaseException):
    def __init__(self, update_infos: str, program_version: str):
        self.update_infos = update_infos
        self.program_version = program_version
        self.msg = f"Update target version is {self.update_infos}, but program version is {self.program_version} !"


class InvalidUpdateInstructions(MyBaseException):
    def __init__(self):
        super().__init__()
        self.msg = "The update instructions are not valid !"


class DownGradeError(MyBaseException):
    def __init__(self, update_infos: str, installation_version: str):
        super().__init__()
        self.update_infos = update_infos
        self.installation_version = installation_version
        self.msg = f"Update upgrade to {self.update_infos}, but installation version is already {self.installation_version}"
