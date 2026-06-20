
import zipfile
import os
import datetime

import utils

BKS_VERSION = "1.0.0"

def create_bks_data(books_data: list[dict], program_version: str):
    """
    Returns a tuple containing the data to put in `infos.json` and `data.json` files (in this order)
    
    books_data: Books data
    """
    
    infos = {
        "type":"BKS",
        "created_at":str(datetime.datetime.now()),
        "format_version":BKS_VERSION,
        "program_version":program_version
    }
    data = books_data
    return (infos, data)

def create_bks_file(bks_data: tuple[dict, list], covers_dir: str):
    """
    Creates a BooksQuest Books save file
    
    Parameters
    ----------
    bks_data: The value returned by the `create_bks_data` function
    covers_dir: The directory where the books covers are stored (and ONLY them)
    """
    utils.write_json("infos.json", bks_data[0])
    utils.write_json("data.json", bks_data[1])
    with zipfile.ZipFile("books.bks", "w") as zpf:
        zpf.write("infos.json")
        zpf.write("data.json")
        zpf.mkdir("covers")
        
        for filename in os.listdir(covers_dir):
            zpf.write(os.path.join(covers_dir, filename), os.path.join("covers", filename))
            
def open_bks_file(filepath: str, dest_dir: str) -> dict:
    """
    Exctract the content of a BooksQuest Books save file and return it's informations
    
    Parameters
    ----------
    filepath(str): the path to the save file
    dest_dir(str): the path to the directory where the file content will be extracted
    
    Returns
    -------
    dict: the informations stored into the `infos.json` file inside the save
    """
    return utils.extract_save_file(filepath, dest_dir)
            