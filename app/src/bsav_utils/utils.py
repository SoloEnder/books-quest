import json
import json.decoder
import os
import zipfile

str_sequence = list[str] | set[str] | tuple[str, ...]


def write_json(filepath: str, data):

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f)


def read_json(filepath):

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_infos(arcpath: str) -> dict:
    "Return the content of the infos file in BooksQuest Save/Books/Shelves file"
    with zipfile.ZipFile(arcpath, "r") as zpf:
        infos_data = zpf.read("infos.json")
        return json.loads(infos_data)


def extract_save_file(filepath: str, dest_dir: str):
    """
    Exctract the content of an BooksQuest save file return it's informations

    Parameters
    ----------
    filepath(str): the path to the save file
    dest_dir(str): the path to the directory where the file content will be extracted

    Returns
    -------
    dict: the informations stored into the `infos.json` file inside the save
    """
    with zipfile.ZipFile(filepath, "r") as zpf:
        zpf.extractall(dest_dir)

    return read_json(os.path.join(dest_dir, "infos.json"))


def check_save(
    save_path: str,
    supported_versions: str_sequence,
    supported_types: str_sequence,
    excepted_content: str_sequence,
):
    """
    Checks the following things in a save file:
        - If the save version is supported
        - If some excepted files are missings

    Parameters
    ----------
    - save_file (str): the path to the save file
    - supported_versions (sequence of str items): the save versions which are supported
    - supported_types: the type of saves files supported (usually BBS, BSAV or BKS)
    - excepted_content (): the path of the files/directories (relatives to the save file path) excepted in the save file

    Raises
    ------
    - InfosFileNotFoundError: if the `infos.json` excepted file is not found in the save
    - InvalidSaveInfosError: if the `infos.json` excepted file is found, but could not be read
    - UnsupportedSaveVersionError: if the version declared by the save in `infos.json` is not supported
    - MissingsElementsError: if excepted elements are missings in the save file
    """
    try:
        infos = get_infos(save_path)

    except json.decoder.JSONDecodeError:
        raise InvalidSaveInfosError(save_path)

    except KeyError:
        raise InfosFileNotFoundError(save_path)

    else:
        type_supported, save_type = is_type_supported(save_path, infos, supported_types)
        print(type_supported, save_type, supported_types)

        if not type_supported:
            raise UnsupportedSaveTypeError(save_path, save_type, supported_types)

        version_supported, save_version = is_version_supported(
            save_path, infos, supported_versions
        )

        if not version_supported:
            raise UnsupportedSaveVersionError(
                save_path, save_version, supported_versions
            )
        missings_elements = check_content(save_path, excepted_content)
        if missings_elements:
            raise MissingsElementError(save_path, missings_elements)


def is_version_supported(
    save_path: str,
    save_infos: dict,
    supported_versions: str_sequence,
) -> tuple[bool, str]:
    """
    Cheks if the version declared by a save file is supported

    Parameters
    ----------
    - save_path (str): the save file path
    - save_infos (dict): the dictionnary containing the save infos, usually in `save_path/infos.json`
    - supported_versions (sequence of strings): a sequence containing the supported versions

    Returns
    -------
    - tuple(bool, str): the first element declare if the save is supported or not, and the second is the save version

    Raises
    ------
    - InvalidSaveInfos: if the save infos does not contain some expected keys used for the verification
    """
    save_version = get_infos_value(save_path, save_infos, "format_version")
    if save_version in supported_versions:
        return (True, save_version)

    else:
        return (False, save_version)


def get_infos_value(save_path: str, save_infos: dict, key_to_get: str):
    """
    Attempts to get a key from a save infos dict

    Parameters
    ----------
    - save_path: the path to the save file
    - save_infos (dict): the save infos
    - key_to_get (str): the key to get

    Returns
    -------
    - the value obtained

    Raises
    ------
    - InvalidSaveInfosError: if the value of the key could not be obtained
    """
    try:
        value = save_infos[key_to_get]

    except KeyError:
        raise InvalidSaveInfosError(save_path)

    else:
        return value


def is_type_supported(
    save_path: str, save_infos: dict, supported_types: str_sequence
) -> tuple[bool, str]:
    """
    Checks if the type of a save file is supported

    Parameters
    ----------
    save_path (str): the path to the save file
    save_infos (dict): the save info
    supported_types (sequence of strings): the save type supported
    """

    save_type = get_infos_value(save_path, save_infos, "type")
    if save_type in supported_types:
        return (True, save_type)

    else:
        return (False, save_type)


def check_content(
    save_path: str,
    excepted_content: str_sequence,
) -> list[str]:
    """
    Checks if all elements listed in `execpted_content` are in a save file

    NOTE
    ----
    This function does not check the files/dir that are inside another archive in the save file

    Parameters
    ----------
    - save_path (str): the path to the save file to check
    - excepted_content (sequence of str items): the name of the elements (their path must be relative to the save file) that you want to check
    (e.g. ["infos.json", "covers"] are the relative path of save_path/infos.json and save_path/covers)

    Returns
    -------
    - list: a list of the element that have not been found in the save file
    """
    missings_elements = []

    with zipfile.ZipFile(save_path, "r") as zpf:
        save_content = zpf.namelist()

    for element in excepted_content:
        if element not in save_content:
            missings_elements.append(element)

    return missings_elements


class InvalidSaveInfosError(Exception):
    def __init__(self, save_path: str):
        self.save_path = save_path
        self.msg = "Unable to get save infos : Invalid save infos !"
        super().__init__()

    def __str__(self):
        return self.msg


class UnsupportedSaveVersionError(Exception):
    def __init__(
        self, save_filepath: str, save_version: str, supported_versions: str_sequence
    ):
        """
        Exception usually raised when trying to do stuff with save file that have another version than the program version.

        Parameters
        ----------
        - save_filepath (str): the path to the save file
        - save_version (str): the version of the save file
        - supported_version (list[str]|tuple[str]|set[str]): the versions supported by the module
        """
        self.save_filepath = save_filepath
        self.supported_versions = supported_versions
        self.save_version = save_version
        self.msg = f"Save file at '{self.save_filepath}' declared version is {self.save_version} but supported version are only {', '.join(self.supported_versions)} !"
        super().__init__()

    def __str__(self):
        return self.msg


class UnsupportedSaveTypeError(Exception):
    def __init__(
        self, save_filepath: str, save_type: str, supported_types: str_sequence
    ):
        """
        Exception usually raised when trying to do stuff with save file that have another version than the program version.

        Parameters
        ----------
        - save_filepath (str): the path to the save file
        - save_type (str): the type of the save file
        - supported_types (a sequence of strings): the versions supported by the module
        """
        self.save_filepath = save_filepath
        self.supported_types = supported_types
        self.save_type = save_type
        self.msg = f"Save file at '{self.save_filepath}' declared type is {self.save_type} but supported types are only {', '.join(self.supported_types)} !"
        super().__init__()

    def __str__(self):
        return self.msg


class InfosFileNotFoundError(InvalidSaveInfosError):
    def __init__(self, save_path: str):
        super().__init__(save_path)
        self.msg = "Unabled to get save infos : infos.json file not found !"


class MissingsElementError(Exception):
    def __init__(self, save_path, missing_elements: str_sequence):
        super().__init__()
        self.msg = f"The following elements : {missing_elements} are missing in the save file !"

    def __str__(self):
        return self.msg
