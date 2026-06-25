import argparse
import os
import shutil

import undo
import utils

parser = argparse.ArgumentParser()
parser.add_argument(
    "installation_path",
    help="The path to the folder where is located the installation to update",
)
parser.add_argument("-c", "--check_state", action="store_true")

args = parser.parse_args()

if args.check_state:
    update_infos = utils.read_json(
        os.path.join(args.installation_path, "update_infos.json")
    )
    backup_folder = update_infos["backup_folder"]
    update_infos_filepath = os.path.join(args.installation_path, "update_infos.json")
    if not update_infos["state"] == "COMPLETED":
        undo.run(
            args.installation_path,
            os.path.join(args.installation_path, backup_folder),
        )
    shutil.rmtree(backup_folder)
    os.remove(update_infos_filepath)
