
from app.utils import json_file_manager as jfm
from app.utils import my_exceptions

class DictPathHandler():

    def __init__(self, base_dict: dict|None=None):
        self.base_dict = base_dict if base_dict else {}

    def get_value(self, dict_path: str):
        """
        Get the value of a dict value tting by it's dict path and return it.
        setting path must have the following format:
        keyA.keyAA.keyAAA, etc. For exemple : 
        {"general":{"ui":{"theme":"dark"}}
        in this case, the dict path path of "theme" will be :
        "general.ui.theme", and this method will return "dark"
        """
        path_sections = dict_path.split(".")
        current_value = self.base_dict.copy()

        try:
            for key in path_sections:
                current_value = current_value[key]

        except KeyError:
            raise my_exceptions.InvalidDictPathError(dict_path)
        
        else:
            return current_value
    
    def edit_value(self, dict_path, new_value):
        """
        Replace the value of a key in the dict by <new_value>
        dict_path must have the following format:
        keyA.keyAA.keyAAA, etc. For exemple : 
        {"general":{"ui":{"theme":"dark"}}
        in this case, the dict path of "theme" will be :
        "general.ui.theme"
        """
        path_sections = dict_path.split(".")
        current_value = self.base_dict.copy()

        try:
            for key in path_sections[:-1]:
                current_value = current_value[key]

            current_value[path_sections[-1]] = new_value

        except KeyError:
            raise my_exceptions.InvalidDictPathError(dict_path)
        
class JSONDictPathHandler(DictPathHandler):
    
    def __init__(self, jfm: jfm.JsonFileManager, base_dict: dict | None = None):
        super().__init__(base_dict)
        self.jfm = jfm
                
    def load_from_file(self, filepath):
        """
        Load a dictionnary from a JSON file, and replace the current settings by it
        """
        new_base_dict = self.jfm.read_json(filepath)
        self.base_dict = new_base_dict

    def save_in_file(self, filepath):
        """
        Save a dictionnary in a JSON file
        """
        self.jfm.write_json(filepath, self.base_dict)
