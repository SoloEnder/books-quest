
import json
import zipfile
import datetime
import os
import bbs
import bks
import utils

BSAV_VERSION = "1.0.0"

def create_bsav(
    dest_path: str, 
    books_data: list[dict], 
    books_cover_dir: str, 
    shelves_data: list[dict], 
    shelves_cover_dir: str, 
    program_version: str,
    tmp_dir: str|None=None, 
    ):
    """
    Create a new BooksQuest Save File 
    
    Parameters
    ----------
    dest_path(str): the name to give to the save file
    books_data: a list of `Books` data
    books_covers_dir(str): the directory where are stored the books covers files (and ONLY them)
    shelves_data: a list of `Shelves` data
    shelves_covers_dir(str): the directory where are stored the shelves covers files (and ONLY them)
    program_version: the version of BooksQuest under which this function is called
    tmp_dir(str|None=None): a directory where this function can store temporary file. If equal to None, then the current working directory is used
    """
    
    bks_data = bks.create_bks_data(books_data, "1.0.0")
    bks.create_bks_file(bks_data, books_cover_dir)
    bbs_data = bbs.create_bbs_data(shelves_data, "1.0.0")
    bks.create_bks_file(bbs_data, shelves_cover_dir)
    bsav_infos = create_bsav_infos()
    utils.write_json("infos.json", bsav_infos)
    
    with zipfile.ZipFile(dest_path, "w") as zpf:
        zpf.write("books.bks")
        zpf.write("shelves.bbs")
        zpf.write("infos.json")
    

def create_bsav_infos():
    """
    Generate and return the data to put in `infos.json` file in the save file
    """
    
    return {
        "type":"BSAV",
        "created_at":str(datetime.datetime.now()),
        "content":("bks", "bbs"),
        "format_version":BSAV_VERSION,
        "program_version":"1.0.0"
    }
    
def open_bsav_file(arcpath, dest_dir: str, extrac_sub: bool=True):
    """
    Exctract the content of a BooksQuest save file and return it's informations
    
    Parameters
    ----------
    filepath(str): the path to the save file
    dest_dir(str): the path to the directory where the file content will be extracted
    extract_sub (bool): specifies if the BooksQuest Books save file and BooksQuest Shelves save file inside the archive should be extracted too.
    
    Returns
    -------
    dict: the informations stored into the `infos.json` file inside the save
    """
    
    with zipfile.ZipFile(arcpath, "r") as zpf:
        zpf.extractall(dest_dir)
        infos = utils.read_json(os.path.join(dest_dir, "infos.json"))
        
        if extrac_sub:
            shelves_arc = os.path.join(dest_dir, "shelves.bbs")
            shelves_dest = os.path.join(dest_dir, "shelves")
            books_arc = os.path.join(dest_dir, "books.bks")
            books_dest = os.path.join(dest_dir, "books")
            
            for filepath in os.listdir():
                if os.path.splitext(filepath)[1] == ".bbs":
                    if not os.path.exists(shelves_dest):
                        os.mkdir(shelves_dest)
                    bbs_infos = bbs.open_bbs_file(shelves_arc, shelves_dest)
                    
                if os.path.splitext(filepath)[1] == ".bks":
                    if not os.path.exists(books_dest):
                        os.mkdir(books_dest)
                    bks_infos = bks.open_bks_file(books_arc, books_dest)
            return {
                "bsav_infos":infos,
                "bbs_infos":bbs_infos,
                "bks_infos":bks_infos,
            }
    
        