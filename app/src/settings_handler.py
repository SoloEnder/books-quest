
from app.utils import json_file_manager as jfm
from app.src import dict_paths_handler

class SettingsHandler(dict_paths_handler.DictPathHandler):

    def __init__(self, settings: dict|None=None):
        super().__init__(settings)
        self.settings = self.base_dict

    def get_setting_value(self, setting_path: str):
        """
        Get the value of a setting by it's setting path and return it.
        setting path must have the following format:
        SettingA.SettingAA.SettingAAA,, etc. For exemple : 
        {"general":{"ui":{"theme":"dark"}}
        in this case, the setting path of "theme" will be :
        "general.ui.theme", and this method will return "dark"
        """
        return super().get_value(setting_path)
    
    def edit_setting_value(self, setting_path, new_value):
        """
        Replace the value of a setting by <setting_value>
        setting path must have the following format:
        SettingA.SettingAA.SettingAAA, etc. For exemple : 
        {"general":{"ui":{"theme":"dark"}}
        in this case, the setting path of "theme" will be :
        "general.ui.theme", and this method will return "dark"
        """
        
        return super().edit_value(setting_path, new_value)
