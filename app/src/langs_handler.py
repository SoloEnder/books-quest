
from app.src import dict_paths_handler

class LangsHandler(dict_paths_handler.JSONDictPathHandler):
    
    def __init__(self, jfm, base_dict):
        super().__init__(jfm, base_dict)
        
    def tr(self, lang_dict_path: str, **kwargs):
        text = self.get_value(lang_dict_path)
        
        if isinstance(text, str):
            
            for kwarg, value in kwargs.items():
                text = text.replace(f"/f:<{kwarg}>/f", str(value))
                
            return text
        