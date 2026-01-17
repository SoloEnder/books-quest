
import json
import pathlib
import logging

logger = logging.getLogger(__name__)

def write_json(filepath:str|pathlib.Path, data):

    try:
        with open(filepath, "w") as f:
            json.dump(data, f)

    except PermissionError:
        logger.error(f"Unable to write in file {filepath} : Permission Denied !")

    except Exception as e:
        logger.error(f"Unable to write in file {filepath} : {e}")

def read_json(filepath: str|pathlib.Path):
    data = None

    try:
        with open(filepath, "r") as f:
            data = json.load(f)

    except FileNotFoundError:
        logger.error(f"Unable to load file {filepath} : File not found !")

    except json.JSONDecodeError:
        logger.error(f"Unable to load file {filepath} : File corrupted !")

    except Exception as e:
        logger.error(f"Unable to load file {filepath} :{e}")

    finally:
        return data




    