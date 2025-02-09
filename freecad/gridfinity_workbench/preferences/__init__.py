from .auto import *
from .import auto

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
