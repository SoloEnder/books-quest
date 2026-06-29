import os
import shutil

import utils


def run(installation_path: str, backup_folder: str):
    undo_filepath = os.path.join(backup_folder, "undo.json")
    undo_instructions = utils.read_json(undo_filepath)
    undo(undo_instructions, installation_path, backup_folder)


def undo(instructions: list, installation_path: str, backup_folder: str):
    """
    Undo the changes made by a patch

    Parameters
    ----------
    - instructions (list): a list of undo instructions to execute
    - installation_folder (str): the folder where is located the user program installation
    - backup_folder (str): the folder where are stored the client files that has been modified, used for downgrading.

    Raises
    ------
    - InvalidUpdateInstructions: if `from_` or `to` does not respect the allowed syntax
    """

    for step in instructions:
        if step["type"] == "move":
            move_item(step["from"], step["to"], backup_folder, installation_path)

        elif step["type"] == "remove":
            remove_item(step["path"], installation_path)

        else:
            raise InvalidUndoInstructions


def move_item(from_: str, to: str, backup_folder: str, installation_path: str):
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

    if from_.startswith("backup::"):
        from_ = from_.split("::")[1]
        from_ = os.path.join(backup_folder, from_)

    else:
        raise InvalidUndoInstructions

    if to.startswith("installation::"):
        to = to.split("::")[1]
        to = os.path.join(installation_path, to)

    else:
        raise InvalidUndoInstructions

    print(from_, to)
    shutil.move(from_, to)


def remove_item(
    path: str,
    installation_folder: str,
):
    """
    Removes an element moved by the patch updater

    - path (str): the path to element to delete, relative to the `installation_folder`. It must starts with 'installation::'.
    - installation_folder (str): the path to the location of the user program installation

    Raises
    ------
    - InvalidUpdateInstructions: if `path` does not respect the allowed syntax
    """
    if path.startswith("installation::"):
        path = os.path.join(installation_folder, path.split("::")[1])

    else:
        raise InvalidUndoInstructions

    if os.path.isdir(path):
        shutil.rmtree(path)

    else:
        os.remove(path)


class InvalidUndoInstructions(utils.MyBaseException):
    def __init__(self):
        """
        When the instructions given by `undo.json` are not valid
        """
        super().__init__()
        self.msg = "The undo file instructions are invalid"
