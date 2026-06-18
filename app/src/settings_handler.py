import collections
import pathlib

from app.src import json_dicts_paths_handler
from app.utils import json_file_manager


class SettingsHandler(json_dicts_paths_handler.JSONDictPathHandler):
    def __init__(
        self,
        jfm: json_file_manager.JsonFileManager,
        base_settings: dict | None = None,
        user_settings: dict | None = None,
    ):
        """
        This class handle the settings of the applications\n
        It can load/save/edit/get settings\n
        There is two type of settings files:
        - base_settings file: contain the default value of the settings and the possible choices for each settings
        - user_settings file: contain the value of each settings modified by the user\n
        Unlike the base_settings file, the user_settings does only contain the settings that has been edited.
        When the 'apply_user_settings()' method is called, the base_settings file and the user_settings file are merged into one dict, where the user_settings override the defaults values.
        """
        super().__init__(jfm, None)
        self.settings = self.base_dict
        self.base_settings = base_settings or {}
        self.user_settings = user_settings or {}

    def set_setting_value(self, setting_path: str, new_value):
        """
        Set a setting current value to `new_value`

        Parameters
        ----------
        setting_path (str): a setting path to a setting
        new_value: the new current value to the setting

        Raises
        ------
        InvalidSettingFormat: if the setting at `setting_path` is not in a recognized format
        ValueNotAllowedError: if `new_value` isn't in the list of availables values for the setting

        """
        if self.is_valid_setting(setting_path):
            setting_infos = self.get_value(setting_path)
            if new_value in setting_infos["choices"]:
                self.edit_value(f"{setting_path}.current", new_value)

            else:
                raise ValueNotAllowedError(
                    setting_path, new_value, setting_infos["choices"]
                )
        else:
            raise InvalidSettingFormat(setting_path)

    def get_setting_value(self, setting_path: str):
        """
        Get the value of the `current` key from a setting.
        If `setting_path` already end with '.current', then this method do the same as `get_value` method

        Raises
        ------
        InvalidSettingFormat: if the setting at `setting_path` is not valid
        See `get_value` method raises if `setting_path` end with '.current'
        """

        if setting_path.endswith(".current"):
            return self.get_value(setting_path)

        if self.is_valid_setting(setting_path):
            return self.get_value(f"{setting_path}.current")

        else:
            raise InvalidSettingFormat(setting_path)

    def is_valid_setting(self, setting_path: str):
        """
        Checks if the setting at `setting_path` respect the valid setting format

        Returns
        -------
        bool: if the setting is valid or not

        Details
        -------
        Valid setting format : {setting_name: {'current':current_value, 'choices':availables_choices}}
        """
        setting_infos = self.get_value(setting_path)

        if isinstance(setting_infos, dict):
            if setting_infos.get("choices") and setting_infos.get("current"):
                setting_choices = setting_infos["choices"]
                if isinstance(setting_choices, list):
                    return True

            else:
                return False

        else:
            return False

    def load_user_settings(self, filepath: str | pathlib.Path):
        """
        Load user settings from a JSON file

        Parameters
        ----------
        - filepath (str|pathlib.Path): the path of the file
        """

        self.user_settings = self.jfm.read_json(filepath, catch_error=False)

    def load_base_settings(self, filepath: str | pathlib.Path):
        """
        Load base settings from a JSON file

        Parameters
        ----------
        - filepath (str|pathlib.Path): the path of the file
        """
        self.base_settings = self.jfm.read_json(filepath, catch_error=False)

    def load_settings(
        self,
        base_settings_filepath: str | pathlib.Path,
        user_settings_filepath: str | pathlib.Path,
    ):
        """
        Load user settings and base settings from JSONs files\n
        Equivalent to call the 'load_base_settings' and the 'load_user_settings' methods

        Parameters
        ----------
        - base_settings_filepath (str|pathlib.Path): the path to the base settings file
        - user_settings_filepath (str|pathlib.Path): the path to the user settings file
        """
        self.load_base_settings(base_settings_filepath)
        self.load_user_settings(user_settings_filepath)

    def apply_user_settings(self):
        """
        Merge the base_settings dictionary and the user_settings dictionary into one, thus forming a complete settings dictionary.
        """

        self.settings = dict(
            collections.ChainMap(self.base_settings, self.user_settings)
        )
        self.base_dict = self.settings

    def save_user_settings(self, filepath: str | pathlib.Path):
        """
        Save user settings in a JSON file

        Parameters
        ----------
        - filepath (str|pathlib.Path): the path to the save file
        """
        self.jfm.write_json(filepath, self.user_settings)

    def save_base_settings(self, filepath: str | pathlib.Path):
        """
        Save base settings in a JSON file

        Parameters
        ----------
        - filepath (str|pathlib.Path): the path to the save file
        """
        self.jfm.write_json(filepath, self.base_settings)

    def save_settings(
        self,
        base_settings_filepath: str | pathlib.Path,
        user_settings_filepath: str | pathlib.Path,
    ):
        """
        Save user settings and base settings in JSONs files\n
        Equivalent to call the 'save_base_settings' and the 'save_user_settings' methods

        Parameters
        ----------
        - base_settings_filepath (str|pathlib.Path): the path to the base settings save file
        - user_settings_filepath (str|pathlib.Path): the path to the user settings save file
        """
        self.save_base_settings(base_settings_filepath)
        self.save_user_settings(user_settings_filepath)


class InvalidSettingFormat(Exception):
    """
    Exception usually raised when trying to assign an forbidden value to a setting.
    """

    def __init__(self, setting_path: str):
        self.setting = setting_path
        self.msg = f"""
        Setting at '{setting_path}' is not recognized as a valid setting.
        Valid setting format : {"{setting_name: {'current':current_value, 'choices':availables_choices}}"}"""
        super().__init__(self.msg)

    def __str__(self):
        return self.msg


class ValueNotAllowedError(Exception):
    """
    Exception usually raised when trying to assign an forbidden value to a setting.
    """

    def __init__(self, setting_path: str, value, availables_choices: list):
        self.setting = setting_path
        self.value = value
        self.availables_choices = availables_choices
        self.msg = f"Value {self.value} isn't allowed for setting '{setting_path}'\nAllowed values: {availables_choices}"
        super().__init__(self.msg)

    def __str__(self):
        return self.msg
