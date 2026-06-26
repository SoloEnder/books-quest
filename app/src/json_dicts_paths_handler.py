from dicts_paths_handler import DictsPathsHandler

from app.utils import json_file_manager as jfm


class JSONDictPathHandler(DictsPathsHandler):
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
