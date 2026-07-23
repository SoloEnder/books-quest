import logging
import os
import shutil

import utils

logger = logging.getLogger(__name__)


def run(update_state_filepath: str, update_res: utils.UpdateRes):
    logging.info("Removing update files in installation folder...")
    shutil.rmtree(update_res.backup_folder)
    os.remove(update_state_filepath)
