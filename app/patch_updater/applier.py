import datetime as dt
import os
import pathlib
import shutil
import sys
import typing

import utils

PATCH_FORMAT_VERSION = "1.0.0"


def run(installation_path: str):
    patch_exe_path = sys.executable
    patch_path = str(pathlib.Path(patch_exe_path).parent)
    check_patch(str(patch_path), installation_path)
    update_infos_filepath = os.path.join(installation_path, "update_infos.json")
    patch_infos = getpinfos(patch_path)
    installation_infos = utils.get_installation_infos(installation_path)
    installation_semantic_version = installation_infos["version"]["semantic"]
    backup_folder = os.path.join(
        installation_path, f"backup_{installation_semantic_version}"
    )
    update_infos_data = {
        "from_version": installation_infos["version"]["readable"],
        "to_version": patch_infos["upgrade_to"]["readable"],
        "state": "IN_PROGRESS",
        "started_at": str(dt.datetime.now()),
        "ended_at": None,
        "backup_folder": backup_folder,
    }
    utils.write_json(update_infos_filepath, update_infos_data)
    patch_instructions = utils.read_json(os.path.join(patch_path, "instructions.json"))
    undo_filepath = os.path.join(backup_folder, "undo.json")
    utils.check_and_make_folder(backup_folder)
    apply_patch(
        patch_instructions, installation_path, backup_folder, patch_path, undo_filepath
    )
    update_infos_data["state"] = "COMPLETED"
    utils.write_json(update_infos_filepath, update_infos_data)


def apply_patch(
    instructions: list,
    installation_folder,
    backup_folder,
    extracted_patch_folder: str,
    undo_filepath: str,
):
    """
    Apply the patch instructions

    Parameters
    ----------
    - instructions (list): a list of instructions to execute
    - installation_folder (str): the folder where is located the user program installation
    - backup_folder: the folder where will be temporary stored the client files that has been modified, for allow downgrade if something went wrong during the update
    - patch_content_path (str): the path where is located the content of the patch
    - undo_filepath (list): the filepath where to store the data used for downgrade if something went wrong during the update

    Raises
    ------
    - InvalidUpdateInstructions: if `from_` or `to` does not respect the allowed syntax
    """
    undo = []
    updater_helper_infos = {}

    for step in instructions:
        if step["type"] == "move":
            move_item(
                step["from"],
                step["to"],
                os.path.join(extracted_patch_folder, "content"),
                installation_folder,
                undo,
            )
            utils.write_json(undo_filepath, undo)

        elif step["type"] == "remove":
            remove_item(step["path"], installation_folder, backup_folder, undo)
            utils.write_json(undo_filepath, undo)

        elif step["type"] == "replace_updater":
            updater_helper_infos = {**step}
            updater_helper_infos["installation_path"]
            updater_helper_infos["extracted_patch_content"] = os.path.join(
                extracted_patch_folder, "content"
            )

        else:
            raise InvalidUpdateInstructions


def move_item(
    from_: str, to: str, patch_content_path: str, installation_path: str, undo: list
):
    """
    Moves a file/directory from an extracted patch folder to a specific destination in the user installation folder

    Parameters
    ----------
    - from_ (str): the original location of the file/directory, relative to `patch_content_folder`. The path must starts by 'patch::',
    - to (str): the destination of the moved file, relative to `ìnstallation_path`. The path must starts with 'installation::'
    - patch_content_path (str): the path where is located the content of the patch
    - installation_path (str): the path where is located the user program installation
    - undo (list): the list where are stored the opposite of the actions done by the updater

    Raises
    ------
    - InvalidUpdateInstructions: if `from_` or `to` does not respect the allowed syntax
    """

    if from_.startswith("patch::"):
        from_ = from_.split("::")[1]
        from_ = os.path.join(patch_content_path, from_)

    else:
        raise InvalidUpdateInstructions

    if to.startswith("installation::"):
        to_parts = to.split("::")

        if len(to_parts) > 1:
            to = os.path.join(installation_path, to_parts[1])

        else:
            to = installation_path

    else:
        raise InvalidUpdateInstructions

    shutil.move(from_, to)

    undo.insert(
        0,
        {
            "type": "remove",
            "path": f"{to_parts[0]}::{to if to != installation_path else ''}",
        },
    )


def remove_item(
    path: str,
    installation_folder: str,
    backup_folder: str,
    undo: list,
):
    """
    Moves an item deleted by the patch instructions in the backup folder, for allow recovery.

    - path (str): the path to element to delete, relative to the `installation_folder`. It must starts with 'installation::'.
    - installation_folder (str): the path to the location of the user program installation
    - backup_folder (str): the folder where moves the pseudo deleted element
    - undo (list): the list where are stored the opposite of the actions done by the updater

    Raises
    ------
    - InvalidUpdateInstructions: if `path` does not respect the allowed syntax
    """
    if path.startswith("installation::"):
        old_path = path
        path = os.path.join(installation_folder, path.split("::")[1])

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


def check_patch(patch_path: str, installation_path: str):
    patch_content = os.listdir(patch_path)
    excepted_content = ("content", "infos.json", "instructions.json", "patch.exe")
    missings_elements = []
    for excepted in excepted_content:
        if excepted not in patch_content:
            missings_elements.append(excepted)

    if missings_elements:
        raise MissingsElementsError(missings_elements)

    patch_infos = getpinfos(patch_path)
    excepted_keys = (
        "target_version",
        "upgrade_to",
        "creation_date",
        "format_version",
    )
    if not tuple(patch_infos.keys()) == excepted_keys:
        raise InvalidPatchInfos

    if not patch_infos["format_version"] == PATCH_FORMAT_VERSION:
        raise UnsupportedPatchVersion(
            PATCH_FORMAT_VERSION, patch_infos["format_version"]
        )

    installation_infos = utils.get_installation_infos(installation_path)
    if (
        not installation_infos["version"]["semantic"]
        == patch_infos["target_version"]["semantic"]
    ):
        raise UntargetedInstallationError(
            patch_infos["target_version"]["readable"],
            installation_infos["version"]["readable"],
        )

    if int(installation_infos["version"]["semantic"]) > int(
        patch_infos["upgrade_to"]["semantic"]
    ):
        raise DownGradeError(
            patch_infos["version"]["readable"],
            installation_infos["version"]["readable"],
        )


def getpinfos(patch_path: str) -> dict:
    """
    Returns the content of `infos.json` file in the patch
    """
    return utils.read_json(os.path.join(patch_path, "infos.json"))


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
            f"The following elements {missing_elements} are missing in the patch file !"
        )


class InvalidPatchInfos(MyBaseException):
    def __init__(self):
        super().__init__()
        self.msg = "The information declared by the patch are not in a valid formet !"


class UnsupportedPatchVersion(MyBaseException):
    def __init__(self, supported_version: str, declared_version: str):
        super().__init__()
        self.supported_version = supported_version
        self.declared_version = declared_version
        self.msg = f"Patch declared version is {declared_version}, but the version supported by the updater is only {supported_version}"


class UntargetedInstallationError(MyBaseException):
    def __init__(self, patch_target: str, program_version: str):
        self.patch_target = patch_target
        self.program_version = program_version
        self.msg = f"Patch target version is {self.patch_target}, but program version is {self.program_version} !"


class InvalidUpdateInstructions(MyBaseException):
    def __init__(self):
        super().__init__()
        self.msg = "The update instructions of the patch file are not valid !"


class DownGradeError(MyBaseException):
    def __init__(self, patch_version: str, installation_version: str):
        super().__init__()
        self.patch_version = patch_version
        self.installation_version = installation_version
        self.msg = f"Patch upgrade to {self.patch_version}, but installation version is already {self.installation_version}"
