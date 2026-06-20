
import json
import zipfile
import os

def write_json(filepath: str, data):
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f)
        
def read_json(filepath):
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
    
def get_infos(arcpath: str):
    "Return the content of the infos file in BooksQuest Save/Books/Shelves file"
    with zipfile.ZipFile(arcpath, "r") as zpf:
        infos_data = zpf.read(f"infos.json")
        return infos_data.decode()
    
def extract_save_file(filepath: str, dest_dir: str):
    """
    Exctract the content of an BooksQuest save file return it's informations
    
    Parameters
    ----------
    filepath(str): the path to the save file
    dest_dir(str): the path to the directory where the file content will be extracted
    
    Returns
    -------
    dict: the informations stored into the `infos.json` file inside the save
    """
    with zipfile.ZipFile(filepath, "r") as zpf:
        zpf.extractall(dest_dir)
        
    return read_json(os.path.join(dest_dir, 'infos.json'))