import copy
import logging
import typing

import dicts_paths_handler

from app.src.services import res_files


class SettingsService:
    def __init__(
        self,
        res_files: res_files.ResourcesFilesService,
        base_settings: dict | None = None,
        user_settings: dict | None = None,
    ):
        self.res_files = res_files
        self.base_settings = base_settings or {}
        self.user_settings = user_settings or {}

        self.logger = logging.getLogger(f"{__name__}-Settings Service")
        self.settings = {}
        self.dicts_paths_handler = dicts_paths_handler.DictsPathsHandler(self.settings)

        self.logger.info("Settings Service initialized")

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
            setting_infos = self.dicts_paths_handler.get_value(setting_path)
            if new_value in setting_infos["choices"]:
                self.edit_user_setting(f"{setting_path}.current", new_value)
                self.dicts_paths_handler.edit_value(
                    f"{setting_path}.current", new_value
                )

            else:
                raise ValueNotAllowedError(
                    setting_path, new_value, setting_infos["choices"]
                )
        else:
            raise InvalidSettingFormat(setting_path)

    def edit_user_setting(self, setting_path: str, value):
        parts = setting_path.split(".")
        current_value = self.user_settings

        for part in parts[
            :-1
        ]:  # Last element is ignored, because this is the new value of the settings path
            if part not in current_value:
                current_value[
                    part
                ] = {}  # Creating the missing key and assigning an empty dict as value
            current_value = current_value[part]

        current_value[parts[-1]] = value

    def get_setting_value(self, setting_path: str) -> typing.Any:
        """
        Get the value of the `current` key from a setting.
        If `setting_path` already end with '.current', then this method do the same as `get_value` method

        Raises
        ------
        InvalidSettingFormat: if the setting at `setting_path` is not valid
        See `get_value` method raises if `setting_path` end with '.current'
        """
        if setting_path.endswith(".current"):
            return self.dicts_paths_handler.get_value(setting_path)

        if self.is_valid_setting(setting_path):
            return self.dicts_paths_handler.get_value(f"{setting_path}.current")

        else:
            raise InvalidSettingFormat(setting_path)

    def get_setting_choices(self, setting_path: str):
        """
        Returns the availables choices for a setting
        """
        if setting_path.endswith(".choices"):
            return self.dicts_paths_handler.get_value(setting_path)

        if self.is_valid_setting(setting_path):
            return self.dicts_paths_handler.get_value(f"{setting_path}.choices")

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
        setting_infos = self.dicts_paths_handler.get_value(setting_path)

        if isinstance(setting_infos, dict):
            if "choices" in setting_infos and "current" in setting_infos:
                setting_choices = setting_infos["choices"]
                if isinstance(setting_choices, list):
                    return True

            else:
                return False

        else:
            return False

    def load_user_settings(self, filepath: str | None = None):
        """
        Load user settings from a JSON file

        Parameters
        ----------
        - filepath (str | None): the path of the file. If not given or equal to None, then the path of the indexed user settings file is used
        """

        if filepath:
            self.user_settings = self.res_files.json_service.read(
                str(filepath),
            )

        else:
            self.user_settings = self.res_files.read_indexed_file("data.user.settings")

    def load_base_settings(self, filepath: str | None = None):
        """
        Load base settings from a JSON file

        Parameters
        ----------
        - filepath (str | None): the path of the file. If not given or equal to None, then the path of the indexed base settings file is used
        """
        if filepath:
            self.base_settings = self.res_files.json_service.read(
                str(filepath),
            )

        else:
            self.base_settings = self.res_files.read_indexed_file(
                "data.app.static.base_settings"
            )

    def load_settings(
        self,
        base_settings_filepath: str | None = None,
        user_settings_filepath: str | None = None,
    ):
        """
        Load user settings and base settings from JSONs files\n
        Equivalent to call the 'load_base_settings' and the 'load_user_settings' methods

        Parameters
        ----------
        - base_settings_filepath (str|None): the path to the base settings. If not given or equal to None, then the path of the indexed settings file is used
        - user_settings_filepath (str|None): the path to the user settings file. If not given or equal to None, then the path of the indexed settings file is used
        """
        self.load_base_settings(base_settings_filepath)
        self.load_user_settings(user_settings_filepath)

    def apply_user_settings(self):
        """
        Merge the base_settings dictionary and the user_settings dictionary into one, thus forming a complete settings dictionary.
        """
        self.settings = copy.deepcopy(self.base_settings)
        self.dicts_paths_handler.base_dict = copy.deepcopy(self.user_settings)
        user_settings_path_list = self.dicts_paths_handler.get_all_dicts_paths("")
        user_settings_path_dict = {}

        for setting_path in user_settings_path_list:
            if setting_path.endswith(".current"):  # Ignore invalid settings path
                user_settings_path_dict[setting_path] = self.get_setting_value(
                    setting_path
                )

        # Overide base settings by user settings
        self.dicts_paths_handler.base_dict = self.settings
        invalid_settings_count = 0
        valid_settings_count = 0
        for setting_path, setting_value in user_settings_path_dict.items():
            try:
                self.dicts_paths_handler.edit_value(setting_path, setting_value)

            except dicts_paths_handler.InvalidDictPathError:
                invalid_settings_count += 1

            else:
                valid_settings_count += 1

        self.logger.info(
            f"Applied {valid_settings_count} user settings, ignored {invalid_settings_count} invalid settings"
        )

    def save_user_settings(self, filepath: str | None = None):
        """
        Save user settings in a JSON file

        Parameters
        ----------
        - filepath (str | None): the path of the file. If not given or equal to None, then the path of the indexed user settings file is used
        """

        if filepath:
            self.res_files.json_service.write(filepath, self.user_settings)

        else:
            self.res_files.write_indexed_file("data.user.settings", self.user_settings)

    def save_base_settings(self, filepath: str | None):
        """
        Save base settings in a JSON file

        Parameters
        ----------
        - filepath (str | None): the path of the file. If not given or equal to None, then the path of the indexed base settings file is used
        """
        if filepath:
            self.res_files.json_service.write(filepath, self.base_settings)

        else:
            self.res_files.write_indexed_file(
                "data.app.static.settings", self.base_settings
            )

    def save_settings(
        self,
        base_settings_filepath: str | None = None,
        user_settings_filepath: str | None = None,
    ):
        """
        Save user settings and base settings in JSONs files\n
        Equivalent to call the 'save_base_settings' and the 'save_user_settings' methods

        Parameters
        ----------
        - base_settings_filepath (str): the path to the base settings save file. If not given or equal to None, then the path of the indexed settings file is used
        - user_settings_filepath (str): the path to the user settings save file. If not given or equal to None, then the path of the indexed settings file is used
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
