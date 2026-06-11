
import pathlib

from app.src import json_dicts_paths_handler
from app.utils import json_file_manager

class SettingsHandler(json_dicts_paths_handler.JSONDictPathHandler):
    
    def __init__(self, jfm: json_file_manager.JsonFileManager, base_settings: dict|None=None, user_settings: dict|None=None):
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
        
    def load_user_settings(self, filepath: str|pathlib.Path):
        """
        Load user settings from a JSON file
        
        Parameters
        ----------
        - filepath (str|pathlib.Path): the path of the file
        """
        
        self.user_settings = self.jfm.read_json(filepath, catch_error=False)
        
    def load_base_settings(self, filepath: str|pathlib.Path):
        """
        Load base settings from a JSON file
        
        Parameters
        ----------
        - filepath (str|pathlib.Path): the path of the file
        """
        self.base_settings = self.jfm.read_json(filepath, catch_error=False)
        
    def load_settings(self, base_settings_filepath: str|pathlib.Path, user_settings_filepath: str|pathlib.Path):
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
        
        self.settings = {**self.base_settings, **self.user_settings}
        self.base_dict = self.settings
        
    def save_user_settings(self, filepath: str|pathlib.Path):
        """
        Save user settings in a JSON file
        
        Parameters
        ----------
        - filepath (str|pathlib.Path): the path to the save file
        """
        self.jfm.write_json(filepath, self.user_settings)
        
    def save_base_settings(self, filepath: str|pathlib.Path):
        """
        Save base settings in a JSON file
        
        Parameters
        ----------
        - filepath (str|pathlib.Path): the path to the save file
        """
        self.jfm.write_json(filepath, self.base_settings)
        
    def save_settings(self, base_settings_filepath: str|pathlib.Path, user_settings_filepath: str|pathlib.Path,):
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