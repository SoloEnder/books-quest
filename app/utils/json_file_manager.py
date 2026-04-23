import json
import logging
import pathlib

def catch_writing_error(func):
    
    def wrapper(self: JsonFileManager, filepath: str | pathlib.Path, data, catch_error: bool=False, **msg_infos):
        
        if catch_error:
            try:
                func(self, filepath, data)
                
            except PermissionError:
                self.logger.error(f"Unable to write JSON in file {filepath} : permission denied !")
                self._raise_msg(**msg_infos)
                
            except:
                self.logger.exception(f"Unable to write JSON in file {filepath} ! ")
                self._raise_msg(**msg_infos)
            
        else:
            func(self, filepath, data)
                
    return wrapper
                
def catch_reading_error(func):
    
    def wrapper(self: JsonFileManager, filepath: str | pathlib.Path, catch_error: bool=False, **msg_infos):
        
        if catch_error:
            try:
                data = func(self, filepath)
                    
            except PermissionError:
                self.logger.error(f"Unable to read JSON in file {filepath} : permission denied !")
                self._raise_msg(**msg_infos)
                
            except FileNotFoundError:
                self.logger.error(f"Unable to read JSON in file {filepath} : file not found !")
                self._raise_msg(**msg_infos)
                
            except:
                self.logger.exception(f"Unable to write JSON in file {filepath} ! ")
                self._raise_msg(**msg_infos)
            
            else:
                return data    
            
        else:
            return func(self, filepath)
        
    return wrapper
       
                
class JsonFileManager:
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._qt_signals_handler = None

    @catch_writing_error
    def write_json(self, filepath: str | pathlib.Path, data, catch_error: bool=True, **msg_infos):
        
        with open(filepath, "w") as f:
            json.dump(data, f)

    @catch_reading_error
    def read_json(self, filepath: str | pathlib.Path, catch_error: bool=True, **msg_infos):
        
        with open(filepath, "r") as f:
            data = json.load(f)

        return data
    
    def _raise_msg(self, **msg_infos):
        
        if msg_infos and self.qt_signals_handler:
            self.qt_signals_handler.notify_sg.emit("error", msg_infos.get("title", ""), msg_infos.get("msg", ""), msg_infos.get("details", ""))
            
    def set_signals_handler(self, qt_signals_handler):
        self.qt_signals_handler = qt_signals_handler
