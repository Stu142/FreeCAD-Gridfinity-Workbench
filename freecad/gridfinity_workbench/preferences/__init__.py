"""A module to get user preferences.

Prefernces are customized in FreeCAD > Edit > Preferences > Gridfinity. Python bindings are auto
generated from `.ui` files.
"""

from . import auto
from .auto import *

# ruff: noqa: D103, F403, RET505

# Overrides

def grid_size_y() -> float:
    if auto.independent_grid_size():
        return auto.grid_size_y()
    else:
        return auto.grid_size_x()

def divider_custom_x_height() -> float:
    if auto.divider_custom_x():
        return auto.divider_custom_x_height()
    else:
        return 0  # maximum height

def divider_custom_y_height() -> float:
    if auto.divider_custom_y():
        return auto.divider_custom_y_height()
    else:
        return 0  # maximum height
