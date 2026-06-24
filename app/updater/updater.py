import argparse

import patch_updater

parser = argparse.ArgumentParser()
parser.add_argument("update_filepath", help="The path to the update file")
parser.add_argument(
    "installation_path",
    help="The path to the folder where is located the installation to update",
)
args = parser.parse_args()

patch_updater.run(args.update_filepath, args.installation_path)
