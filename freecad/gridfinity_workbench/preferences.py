"""Module for getting user preferences.

The preferences are set in "Edit > Preferences > Gridfinity".
"""
# ruff: noqa: D103, FBT003

import FreeCAD as fc  # noqa: N813

# fmt: off

# Helpers

_PARAMS = fc.ParamGet("User parameter:BaseApp/Preferences/Mod/Gridfinity")

def _get_float(param: str) -> float:
    return _PARAMS.GetFloat(param, 0)

def _get_int(param: str) -> int:
    return _PARAMS.GetInt(param, 0)

def _get_bool(param: str) -> bool:
    return _PARAMS.GetBool(param, False)

# Preference getters

def grid_size_x() -> float:
    return _get_float("GridSizeX")

def grid_size_y() -> float:
    independent = _get_bool("IndependentGridSize")
    return _get_float("GridSizeY" if independent else "GridSizeX")

def grid_height() -> float:
    return _get_float("GridHeight")

def clearance() -> float:
    return _get_float("Clearance")

def magnet_hole_diameter() -> float:
    return _get_float("MagnetHoleDiameter")

def manget_hole_depth() -> float:
    return _get_float("MagnetHoleDepth")

def screw_hole_diameter() -> float:
    return _get_float("ScrewHoleDiameter")

def screw_hole_depth() -> float:
    return _get_float("ScrewHoleDepth")

def bin_width_x() -> int:
    return _get_int("BinWidthX")

def bin_width_y() -> int:
    return _get_int("BinWidthY")

def bin_height() -> int:
    return _get_int("BinHeight")

def bin_wall_thickness() -> float:
    return _get_float("BinWallThickness")

def stacking_lip() -> bool:
    return _get_bool("StackingLip")

def bin_magnet_holes() -> bool:
    return _get_bool("BinMagnetHoles")

def bin_screw_holes() -> bool:
    return _get_bool("BinScrewHoles")

# fmt: on
