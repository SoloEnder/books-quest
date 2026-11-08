"""
Various enums and variables that are used for contexts by others modules
"""

import enum


class SortsOptions(enum.Enum):
    """
    Sorts options
    """

    MOST_RECENT = "MOST_RECENT"
    LEAST_RECENT = "LEAST_RECENT"
    NAME_AZ = "NAME_AZ"
    NAME_ZA = "NAME_ZA"


class EditorMode(enum.Enum):
    """
    Describe the state of an editor
    """

    CREATION = enum.auto()
    EDITION = enum.auto()
