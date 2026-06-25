import argparse
import os
import traceback

import applier

parser = argparse.ArgumentParser()
parser.add_argument(
    "installation_path",
    help="The path to the folder where is located the installation to update",
)
args = parser.parse_args()


def check_installation(installation_path: str):
    if not os.path.isdir(installation_path):
        NotADirectoryError(f"Element at {installation_path} is not a directory !")


try:
    print("Checking user installation...")
    check_installation(args.installation_path)

except NotADirectoryError:
    print("Unable to perform update : invalid installation path !")

else:
    try:
        applier.run(args.installation_path)

    except Exception:
        print("Unable to perform update due to the following exception :")
        print(traceback.format_exc())
        input("Type something to exit : ")
