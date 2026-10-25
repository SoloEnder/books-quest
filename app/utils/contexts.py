"""
Various enums and variables that are used for contexts by others modules
"""

import enum


class EditorMode(enum.Enum):
    """
    Describe the state of an editor
    """

    CREATION = enum.auto()
    EDITION = enum.auto()
