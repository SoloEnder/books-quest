
from app.utils import json_file_manager as jfm
from app.utils import my_exceptions

class DictPathHandler:

    def __init__(self, base_dict: dict|None=None):
        self.base_dict = base_dict if base_dict else {}

    def get_value(self, dict_path: str):
        """
        Get the value of a setting by it's setting path and return it.
        setting path must have the following format:
        keyA.keyAA.keyAAA, etc. For exemple : 
        {"general":{"ui":{"theme":"dark"}}
        in this case, the setting path of "theme" will be :
        "general.ui.theme", and this method will return "dark"
        """
        path_sections = dict_path.split(".")
        current_value = self.base_dict.copy()

        try:
            for key in path_sections:
                current_value = current_value[key]

        except KeyError:
            raise my_exceptions.InvalidSettingPathError(dict_path)
        
        else:
            return current_value
    
    def edit_value(self, dict_path, new_value):
        """
        Replace the value of a setting by <setting_value>
        setting path must have the following format:
        keyA.keyAA.keyAAA, etc. For exemple : 
        {"general":{"ui":{"theme":"dark"}}
        in this case, the setting path of "theme" will be :
        "general.ui.theme", and this method will return "dark"
        """
        path_sections = dict_path.split(".")
        current_value = self.base_dict.copy()

        try:
            for key in path_sections[:-1]:
                current_value = current_value[key]

            current_value[path_sections[-1]] = dict_path

        except KeyError:
            raise my_exceptions.InvalidSettingPathError(dict_path)

    def load_from_file(self, filepath):
        """
        Load a settings dictionnary from a JSON file, and replace the current settings by it
        """
        new_base_dict = jfm.read_json(filepath)
        self.base_dict = new_base_dict

    def save_in_file(self, filepath):
        """
        Save a settings dictionnary in a JSON file
        """
        jfm.write_json(filepath, self.base_dict)
