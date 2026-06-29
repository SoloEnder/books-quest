import datetime as dt
import os
import pathlib
import shutil
import sys
import typing

import utils

SUPPORTED_UPDATES_FORMATS = ("1",)


def run(installation_path: str):
    upgrader_filepath = sys.executable
    upgrader_folder = str(pathlib.Path(upgrader_filepath).parent)
    manifest = check_update(str(upgrader_folder), installation_path)
    update_state_filepath = os.path.abspath(
        os.path.join(installation_path, "update_state.json")
    )
    installation_infos = utils.get_installation_infos(installation_path)
    installation_semantic_version = installation_infos["version"]["semantic"]
    backup_folder = os.path.join(
        installation_path, f"backup_{installation_semantic_version}"
    )
    update_state_data = {
        "state": "IN_PROGRESS",
        "from_version": installation_infos["version"],
        "to_version": manifest["upgrade_to"],
        "started_at": str(dt.datetime.now()),
        "ended_at": None,
        "backup_folder": backup_folder,
    }
    utils.write_json(update_state_filepath, update_state_data)
    update_instructions = utils.read_json(
        os.path.join(upgrader_folder, "update_instructions.json")
    )
    undo_filepath = os.path.join(backup_folder, "undo.json")
    utils.check_and_make_folder(backup_folder)
    utils.write_json(undo_filepath, [])
    apply_patch(
        update_instructions,
        installation_path,
        backup_folder,
        upgrader_folder,
        undo_filepath,
        manifest["type"],
    )
    update_state_data["state"] = "COMPLETED"
    update_state_data["ended_at"] = str(dt.datetime.now())
    utils.write_json(update_state_filepath, update_state_data)


def apply_patch(
    instructions: list,
    installation_folder,
    backup_folder,
    update_content_folder: str,
    undo_filepath: str,
    update_type: typing.Literal["FULL", "PATCH"],
):
    """
    Apply the patch instructions

    Parameters
    ----------
    - instructions (list): a list of instructions to execute
    - installation_folder (str): the folder where is located the user program installation
    - backup_folder: the folder where will be temporary stored the client files that has been modified, for allow downgrade if something went wrong during the update
    - update_content_folder (str): the path where is located the content of the update
    - undo_filepath (list): the filepath where to store the data used for downgrade if something went wrong during the update

    Raises
    ------
    - InvalidUpdateInstructions: if `from_` or `to` does not respect the allowed syntax
    """
    undo = []

    for step in instructions:
        if step["type"] == "move":
            content_folder = (
                os.path.join(update_content_folder, "content")
                if update_type == "PATCH"
                else update_content_folder
            )
            move_item(
                step["from"],
                step["to"],
                content_folder,
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
    from_: str, to: str, udpdate_content_folder: str, installation_path: str, undo: list
):
    """
    Copy a file/directory from an update content folder to a specific destination in the user installation folder

    Parameters
    ----------
    - from_ (str): the original location of the file/directory, relative to `update_content_folder`. The path must starts by 'update::',
    - to (str): the destination of the moved file, relative to `ìnstallation_path`. The path must starts with 'installation::'
    - patch_content_path (str): the path where is located the content of the patch
    - installation_path (str): the path where is located the user program installation
    - undo (list): the list where are stored the opposite of the actions done by the updater

    Raises
    ------
    - InvalidUpdateInstructions: if `from_` or `to` does not respect the allowed syntax
    """

    if from_.startswith("update::"):
        from_ = from_.split("::")[1]
        from_ = os.path.abspath(os.path.join(udpdate_content_folder, from_))

    else:
        raise InvalidUpdateInstructions

    if to.startswith("installation::"):
        old_to = to
        to = os.path.abspath(os.path.join(installation_path, to.split("::")[1]))

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
    Moves an item deleted by the patch instructions in the backup folder, to allow recovery.

    - path (str): the path to the element to delete, relative to the `installation_folder`. It must starts with 'installation::'.
    - installation_folder (str): the path to the location of the user program installation
    - backup_folder (str): the folder where moves the pseudo deleted element
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


def check_update(upgrader_folder: str, installation_path: str) -> dict:
    """
    Checks partially the validity of an update.

    Parameters
    ----------
    - upgrader_folder (str): the folder where is located the `upgrader.exe` file, and where should be the update infos and instructions
    - installation_path (str): the path to the installation to update

    Returns
    -------
    dict: the update infos (usually found in the `manifest.json` file)
    """
    upgrader_folder_content = os.listdir(upgrader_folder)
    manifest_data = get_manifest(upgrader_folder)

    update_type = manifest_data["type"]
    if update_type == "PATCH":
        excepted_content = ["content", "update_instructions.json", "upgrader.exe"]

    elif update_type == "FULL":
        excepted_content = [
            "update_manifest.json",
            "update_instructions.json",
            "upgrader.exe",
            "books-quest.exe",
            "app",
            "_internal",
        ]

    else:
        raise InvalidManifestData(f"Unknown update type : '{update_type}'")

    missings_elements = []
    for excepted in excepted_content:
        if excepted not in upgrader_folder_content:
            missings_elements.append(excepted)

    if missings_elements:
        raise MissingsElementsError(missings_elements)

    if manifest_data["format_version"] not in SUPPORTED_UPDATES_FORMATS:
        raise UnsupportedUpdateFormat(
            SUPPORTED_UPDATES_FORMATS, manifest_data["format_version"]
        )

    installation_infos = utils.get_installation_infos(installation_path)

    if update_type == "PATCH":
        if (
            not installation_infos["version"]["semantic"]
            == manifest_data["target_version"]["semantic"]
        ):
            raise UntargetedInstallationError(
                manifest_data["target_version"]["readable"],
                installation_infos["version"]["readable"],
            )

    if int(installation_infos["version"]["semantic"]) > int(
        manifest_data["upgrade_to"]["semantic"]
    ):
        raise DownGradeError(
            manifest_data["upgrade_to"]["readable"],
            installation_infos["version"]["readable"],
        )
    return manifest_data


def get_manifest(patch_path: str) -> dict:
    """
    Returns the content of `infos.json` file in the patch
    """
    return utils.read_json(os.path.join(patch_path, "update_manifest.json"))


class MyBaseException(Exception):
    def __init__(self):
        """Common base class to my Exceptions"""
        self.msg = "An exception has occured !"
        super().__init__()

    def __str__(self):
        return self.msg


class InvalidManifestData(MyBaseException):
    """
    Usually raised when the update manifest gives an unexpected/invalid information
    """

    def __init__(self, msg):
        super().__init__()
        self.msg = msg


class MissingsElementsError(MyBaseException):
    def __init__(self, missing_elements: typing.Sequence[str]):
        super().__init__()
        self.msg = f"The following elements {missing_elements} are missing in the update content !"


class InvalidPatchInfos(MyBaseException):
    def __init__(self):
        super().__init__()
        self.msg = "The information declared by the update are not in a valid formet !"


class UnsupportedUpdateFormat(MyBaseException):
    def __init__(self, supported_formats: tuple[str, ...], given_version: str):
        super().__init__()
        self.supported_formats = supported_formats
        self.given_version = given_version
        self.msg = f"Update format is {self.given_version}, but upgrader supported formats are {self.supported_formats} !"


class UntargetedInstallationError(MyBaseException):
    def __init__(self, patch_target: str, program_version: str):
        self.patch_target = patch_target
        self.program_version = program_version
        self.msg = f"Update target version is {self.patch_target}, but program version is {self.program_version} !"


class InvalidUpdateInstructions(MyBaseException):
    def __init__(self):
        super().__init__()
        self.msg = "The update instructions are not valid !"


class DownGradeError(MyBaseException):
    def __init__(self, patch_version: str, installation_version: str):
        super().__init__()
        self.patch_version = patch_version
        self.installation_version = installation_version
        self.msg = f"Update upgrade to {self.patch_version}, but installation version is already {self.installation_version}"
