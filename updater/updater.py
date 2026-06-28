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
    update_infos_filepath = os.path.join(args.installation_path, "update_infos.json")
    update_infos = utils.read_json(update_infos_filepath)
    backup_folder = update_infos["backup_folder"]
    if not update_infos["state"] == "COMPLETED":
        undo.run(
            args.installation_path,
            os.path.join(args.installation_path, backup_folder),
        )

    else:
        installation_infos = utils.get_installation_infos(args.installation_path)
        installation_infos["version"] = update_infos["to_version"]
        utils.write_json(
            os.path.join(args.installation_path, "app", "app_infos.json"),
            installation_infos,
        )
    shutil.rmtree(backup_folder)
    os.remove(update_infos_filepath)
