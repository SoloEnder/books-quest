import json
import logging
import os
import shutil
import typing

import gui

logger = logging.getLogger("updater.utils")


class MyBaseException(Exception):
    def __init__(self):
        """Common base class to my Exceptions"""
        self.msg = "An exception has occured !"
        super().__init__()

    def __str__(self):
        return self.msg


class UncomparablesVersionsError(MyBaseException):
    """
    Usually raised when one version is not comparable to another/
    e.g. : version A is 1.2.3.4 but version B is 1.2.3 -> cannot be compared since they have not the same length
    Parameters
    ----------
    - version_a (str): the first version
    - version_b (str): the second version
    """

    def __init__(self, version_a: str, version_b: str):
        super().__init__()
        self.version_a = version_a
        self.version_b = version_b
        self.msg = f"Version {self.version_a} is not comparable with version {self.version_b} !"


class InvalidUpdateInstructionError(MyBaseException):
    """
    Exception ususally raised when an update instrcuctions is not recognized
    Parameters
    ----------
    msg: the message to display
    """

    def __init__(self, msg):
        super().__init__()
        self.msg = msg


class InvalidPathAliasError(MyBaseException):
    def __init__(self, alias: str):
        super().__init__()
        self.msg = f"String '{alias}' is not recognized as a valid path alias !"


class PathAlias:
    def __init__(self, path: str, alias: str):
        self.path = path
        self.alias = alias

    def __str__(self):
        return self.path

    def __call__(self):
        return self.alias

    def __repr__(self):
        return f"PathAlias(path={self.path}, alias={self.alias})"


class UpdateRes:
    def __init__(
        self,
        installation_folder: str,
        update_folder: str,
        backup_folder: str,
        update_state_filepath: str,
        undo_filepath: str,
        installation_infos: dict,
        installation_app_infos: dict,
        update_infos: dict,
        update_state_data: dict,
        installation_alias: str,
        update_alias: str,
        backup_alias: str,
    ):
        self._installation_folder = installation_folder
        self._update_folder = update_folder
        self._backup_folder = backup_folder
        self._update_state_filepath = update_state_filepath
        self._undo_filepath = undo_filepath
        self._installation_alias = PathAlias(
            self.installation_folder, installation_alias
        )
        self._update_alias = PathAlias(self.update_folder, update_alias)
        self._backup_alias = PathAlias(self.backup_folder, backup_alias)
        self.installation_infos = installation_infos
        self.installation_app_infos = installation_app_infos
        self.update_infos = update_infos
        self.update_state_data = update_state_data

    @property
    def installation_folder(self):
        return self._installation_folder

    @property
    def update_folder(self):
        return self._update_folder

    @property
    def backup_folder(self):
        return self._backup_folder

    @property
    def update_state_filepath(self):
        return self._update_state_filepath

    @property
    def undo_filepath(self):
        return self._undo_filepath

    @property
    def installation_alias(self):
        return self._installation_alias()

    @property
    def backup_alias(self):
        return self._backup_alias()

    @property
    def update_alias(self):
        return self._update_alias()


class UpdateActionsHandler:
    def __init__(
        self, update_res: UpdateRes, window: gui.Window, undo_data: list | None = None
    ):
        self.update_res = update_res
        self.window = window
        self.undo_data = undo_data or []
        self.elements_to_preserve: set = set(
            self.update_res.installation_app_infos["elements_to_preserve"].copy()
        )

    def add_undo(self, action):
        """
        Add an undo action at the end of the undo actions list, and save the data at `undo_filepath` attr.
        """
        self.undo_data.insert(0, action)
        self.save_undo_data()

    def save_undo_data(self, filepath: str | None = None):
        """
        Save the undo data in a file.

        Parameters
        ----------
        - filepath (str|None=None): the file where to save the data. If not given/equal to `None`, then the `undo_filepath` is used.
        """
        write_json(filepath or self.update_res.undo_filepath, self.undo_data, True)

    def load_undo_data(
        self,
        filepath: str | None = None,
        to_do: typing.Literal["SET", "APPEND", "INSERT_0", "RETURN"] = "SET",
    ) -> list:
        """
        Load an list of undo action from a file, and allows you to do the following actions:
        - set these data as new data (SET)
        - append them to the existings data (APPEND)
        - insert them at the beggining of the existing data (INSERT_0)
        Anyway, the loaded data will be returned (RETURN)

        Parameters
        ----------
        - filepath (str|None=None): the file containing the data. if not given/equal to `None`, then the value of the `undo_filepath` attr is used
        - to_do (str, choice in ['SET', 'APPEND', 'INSERT_0', 'RETURN']): please look at the description of the function to know wath each choice do.

        Returns
        - list: the loaded data
        """
        data: list = read_json(filepath or self.update_res.undo_filepath)
        if to_do == "SET":
            self.undo_data = data

        elif to_do == "APPEND":
            self.undo_data.extend(data)

        elif to_do == "INSERT_0":
            data.extend(self.undo_data)
            self.undo_data = data

        return data

    def remove_element(
        self,
        path: str,
        backup: bool = True,
        add_undo: bool = True,
        **kwargs,
    ):
        """
        Removes an element from the installation folder

        Parameters
        ----------
        path (str): the path to the element, that can be relative to an path alias value.
        backup (bool=True): wether to move the element to the backup folder instead of deleting it.
        add_undo (bool_True): wether to add an undo instruction for this element. Will be ignored if `backup=False`
        """
        logger.info(f"Removing element at {path}, with {backup=} and {add_undo=}")
        old_path = path
        path_alias, path = path.split("::")
        path_alias_value = get_path_alias_value(path_alias, self.update_res)
        abs_path = os.path.abspath(os.path.join(path_alias_value, path))

        if not os.path.exists(abs_path):
            logger.warning(
                f"Element at {old_path} does not exists, skipping its deletion"
            )
            return

        if backup:
            if add_undo:
                self.add_undo(
                    {
                        "type": "COPY",
                        "from_": f"BACKUP::{path}",
                        "to": f"{path_alias}::{path}",
                        "add_undo": False,
                        "ignore_missing_src": True,
                    },
                )
            os.replace(abs_path, os.path.join(self.update_res.backup_folder, path))

        else:
            if os.path.isdir(abs_path):
                shutil.rmtree(abs_path)

            else:
                os.remove(abs_path)

    def copy(
        self,
        from_: str,
        to: str,
        add_undo: bool = True,
        ignore_updater: bool = False,
        ignore_missing_src: bool = False,
        **kwargs,
    ):
        """
        Removes an element from the installation folder

        Parameters
        ----------
        - from_ (str): the path to the element to move, relative to the path alias value or not.
        - to (str): the path where to move the element, relative to the path alias value or not.
        - add_undo (bool=True): wheter to add an undo for this action.
        - ignore_updater (bool=True): whether to write an PREPARE_UPDATER_REPLACEMENT for the `from_` value which ends with 'updater.exe'
        """
        logger.info(f"Copying element from {from_} to {to} with {add_undo=}")

        from_abs_path = get_abs_path(from_, self.update_res)

        # -- Cecks if the source is missing --
        if not os.path.exists(from_abs_path):
            if ignore_missing_src:
                logger.warning(
                    f"Source file to copy at '{from_abs_path}' does not exists, ignoring it because {ignore_missing_src=}"
                )
                return

            else:
                raise FileNotFoundError(
                    f"Source file to copy at '{from_abs_path}' does not exists !"
                )
        to_abs_path = get_abs_path(to, self.update_res)

        if add_undo:
            # This part assume that the updater is always at the root directory of the installation, under the name 'updater.exe', and that the existing updater has already been removed with backup=True
            if from_.endswith("updater.exe") and not ignore_updater:
                logger.info("Writing PREPARE_UPDATER_REPLACEMENT instruction...")
                self.add_undo(
                    {
                        "type": "PREPARE_UPDATER_REPLACEMENT",
                        "updater_to_replace": to,
                        "new_updater": f"{self.update_res.backup_alias}::updater.exe",
                    }
                )

            else:
                logger.debug("Writting default copy undo instructions")
                self.add_undo({"type": "REMOVE", "path": to, "backup": False})
        self._core_copy(from_abs_path, to_abs_path)

    def _core_copy(self, from_: str, to: str):
        # In this function, `from_` and `to` should be absolute path
        if os.path.isdir(from_):
            shutil.copytree(from_, to, dirs_exist_ok=True)

        else:
            shutil.copy(from_, to)

    def make_dir(self, path: str, add_undo: bool = True, **kwargs):
        """
        Make a dir at `dir_path`

        Parameters
        ----------
        - path (str): the path to the directory to create
        - add_undo (bool=True): wheter to add an undo for this action.
        """
        logger.info(f"Making directory at {path} with {add_undo}")
        final_path = get_abs_path(path, self.update_res)
        os.mkdir(final_path)

        if add_undo:
            self.add_undo({"type": "remove", "path": f"{path}", "add_undo": False})

    def apply_instructions(
        self,
        instructions: list[dict],
        ignore_unknown: bool = True,
    ):
        """
        Apply a list of update instructons (like REMOVE, to permanently or not remove an element, COPY to copy an element, etc)

        Parameters
        ----------
        - instructions: a list of instructions to do on files
        - ignore_unknown (bool=True): whether to ignore unknown instruction (otherwise, this will raise an `InvalidUpdateInstructionError`)
        """
        self.window.work_in_progress_sc.add_operations_group(
            "update",
            "Applying update...",
            operations_count=len(instructions),
            set_as_current=True,
        )
        self.window.switch_screen("work_in_progress_screen")
        for instruction in instructions:
            if instruction["type"] == "REMOVE":
                self.remove_element(**instruction)

            elif instruction["type"] == "COPY":
                self.copy(**instruction)

            elif instruction["type"] == "MKDIR":
                self.make_dir(**instruction)

            else:
                if not ignore_unknown:
                    raise InvalidUpdateInstructionError(
                        f"Unknwon update instruction type : '{instruction['type']}'"
                    )
                logger.warning(
                    f"Found unrecognized instruction '{instruction}', ignoring it."
                )
            self.window.work_in_progress_sc.progress_group()

    def remove_from_preserved_elements(self, element: str):
        if element in self.elements_to_preserve:
            logger.info(f"Removing {element} from elements to restore...")
            self.elements_to_preserve.remove(element)

    def restore_preserved_elements(self):
        """
        Restore the elements that the installation marked as should be restored.
        Note that this methods will ignore the elements that has been modified by an migration.
        For example, if `app/data/books_data` should be retored, but a migration modified it, then this elements will be ignored (normally)
        """
        self.window.work_in_progress_sc.add_operations_group(
            "restore_preserved_elements",
            "Restoring preserved data...",
            operations_count=len(self.elements_to_preserve),
            set_as_current=True,
        )
        self.window.switch_screen("work_in_progress_screen")
        for element in self.elements_to_preserve:
            self.copy(
                f"{self.update_res.backup_alias}::{element}",
                f"{self.update_res.installation_alias}::{element}",
                ignore_missing_src=True,
            )
            self.window.work_in_progress_sc.progress_group()


def get_abs_path(path: str, update_res: UpdateRes) -> str:
    """
    Get a relative BooksQuest path, and return the absolute version.

    Parameters
    ----------
    - path (str): the Books Quest relative path
    - update_res (UpdateRes): the class where are stored update ressources such as installation path, update infos, etc.

    Returns
    -------
    - str: the absolute path
    """
    path_alias, relative_path = path.split("::")
    path_alias_value = get_path_alias_value(path_alias, update_res)
    return os.path.abspath(os.path.join(path_alias_value, relative_path))


def get_path_alias_value(alias: str, update_res: UpdateRes) -> str:
    aliases = {
        update_res.installation_alias: update_res.installation_folder,
        update_res.backup_alias: update_res.backup_folder,
        update_res.update_alias: update_res.update_folder,
    }

    if alias in aliases:
        return aliases[alias]

    else:
        raise InvalidPathAliasError(alias)


def ishigher(version_a: str, version_b: str) -> bool:
    """
    Checks whether `version_a` is higher than `version_b`

    Parameters
    ----------
    - version_a (str): the first version, in semver (major.minor.patch)
    - version_b (str): the version compared to, in semver (major.minor.patch)

    Returns
    -------
    - bool: wheter `version_a` version is higher than `version_b`
    """
    version_a_parts = version_a.split(".")
    version_b_parts = version_b.split(".")

    if len(version_a_parts) != len(version_b_parts):
        raise UncomparablesVersionsError(version_a, version_b)

    for index, version_a_part in enumerate(version_a_parts):
        if int(version_a_part) > int(version_b_parts[index]):
            return True

    else:
        return False


def get_installation_app_infos(installation_path: str) -> dict:
    """
    Returns the infos about the installation

    Parameters
    ----------
    - installation_path (str): the path to the installation root directory
    """
    with open(os.path.join(installation_path, "app", "app_infos.json"), "r") as f:
        return json.load(f)


def get_manifest(update_path: str) -> dict:
    """
    Returns the content of `infos.json` file in the update
    """
    return read_json(os.path.join(update_path, "update_manifest.json"))


def read_json(filepath: str):

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(filepath: str, data, atomic_replace: bool = False):
    """
    Write JSON data in a file.

    Parameters
    ----------
    - filepath (str): the file where will be writed the data
    - data: the data to write (in valid JSON format)
    - atomic_replace (bool=True): wheter to use atomic replace to write the file (wil generate an other file called `<filepath>.atmp`).
    """

    if atomic_replace:
        atomic_tmp_filepath = filepath + ".atmp"
        with open(atomic_tmp_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)

        os.replace(atomic_tmp_filepath, filepath)

    else:
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
