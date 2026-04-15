
from app.utils import json_file_manager as jfm

class SettingsHandler:

    def __init__(self, settings: dict|None=None):
        self.settings = settings if settings else {}

    def get_setting_value(self, setting_path: str):
        """
        Get the value of a setting by it's setting path and return it.
        setting path must have the following format:
        keyA.keyAA.keyAAA, etc. For exemple : 
        {"general":{"ui":{"theme":"dark"}}
        in this case, the setting path of "theme" will be :
        "general.ui.theme", and this method will return "dark"
        """
        path_sections = setting_path.split(".")
        current_setting = self.settings.copy()

        for key in path_sections:
            current_setting = current_setting[key]

        return current_setting

    def load_from_file(self, filepath):
        """
        Load a settings dictionnary from a JSON file, and replace the current settings by it
        """
        new_settings = jfm.read_json(filepath)
        self.settings = new_settings

    def save_in_file(self, filepath):
        """
        Save a settings dictionnary in a JSON file
        """

    def edit_setting_value(self, setting_path, setting_value):
        path_sections = setting_path.split(".")
        current_setting = self.settings.copy()

        for key in path_sections[:-1]:
            current_setting = current_setting[key]

        current_setting[path_sections[-1]] = setting_value


