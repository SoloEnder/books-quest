import logging
import os
from pathlib import Path

from PIL import Image
from PySide6 import QtWidgets

logger = logging.getLogger(__name__)


def select_image(base_path: str | None = None):
    """Open a file selecter window for enable user to select an image"""
    if not base_path:
        base_path = str(Path.home())
    infos = QtWidgets.QFileDialog.getOpenFileName(
        None,
        "Select Image",
        base_path,
        "Supported Formats (*.png *.jpeg);;PNG Images (*.png);;JPEG Images (*.jpeg)",
    )
    return infos


def prepare_image(
    image_path: str | Path, dest_path: str, size: tuple[int, int] = (170, 250)
) -> tuple[str, Image.Image]:
    """
    Convert <image_path> to PNG format, resize it and save it in the temporary directory and return the path
    """

    image_path = Path(image_path)
    if image_path.exists():
        with Image.open(image_path) as img:
            res = resize_image(img, (size[0], size[1]))
            res = convert_img_to_png(res)
            res.save(dest_path, "PNG")

        return (dest_path, res)

    else:
        logger.error(
            f"Unable to select cover image at {image_path.resolve()} : File not Found"
        )
        raise FileNotFoundError(
            f"Book cover image at {image_path.resolve()} not found !"
        )


def resize_image(img, new_size: tuple[int, int]):
    img_width, img_height = img.size
    new_width = new_size[0]
    new_height = new_size[1]
    resized_img = img.resize(
        (
            int(img_width * (new_width / img_width)),
            int(img_height * (new_height / img_height)),
        )
    )

    return resized_img


def convert_img_to_png(img: Image.Image):
    """
    Convert <img> to PNG format and return it
    """
    img_rgb = img.convert(mode="RGB")

    return img_rgb
