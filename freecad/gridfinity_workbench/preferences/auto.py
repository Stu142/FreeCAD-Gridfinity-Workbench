"""This file was auto generated, do not edit it!

If you want to change any function, override it in `__init__.py` in this directory.
If you make changes to the `.ui` files, run `codegen_preferences.py` again to update this file.
"""
# fmt: off

import FreeCAD

# Helpers

_PARAMS = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Gridfinity")
_MAGIC = -987

def _get_float(param: str) -> float:
    res = _PARAMS.GetFloat(param, _MAGIC)
    assert res != _MAGIC
    return res

def _get_int(param: str) -> int:
    res = _PARAMS.GetInt(param, _MAGIC)
    assert res != _MAGIC
    return res

def _get_bool(param: str) -> bool:
    return _PARAMS.GetBool(param, False)

# Preference getters

def baseplate_bottom_chamfer() -> float:
    return _get_float("BaseplateBottomChamfer")

def baseplate_bottom_radius() -> float:
    return _get_float("BaseplateBottomRadius")

def baseplate_outer_radius() -> float:
    return _get_float("BaseplateOuterRadius")

def baseplate_top_chamfer() -> float:
    return _get_float("BaseplateTopChamfer")

def baseplate_top_ledge_width() -> float:
    return _get_float("BaseplateTopLedgeWidth")

def baseplate_vertical_radius() -> float:
    return _get_float("BaseplateVerticalRadius")

def baseplate_vertical_section() -> float:
    return _get_float("BaseplateVerticalSection")

def bin_base_bottom_chamfer() -> float:
    return _get_float("BinBaseBottomChamfer")

def bin_base_bottom_radius() -> float:
    return _get_float("BinBaseBottomRadius")

def bin_base_top_chamfer() -> float:
    return _get_float("BinBaseTopChamfer")

def bin_base_vertical_radius() -> float:
    return _get_float("BinBaseVerticalRadius")

def bin_base_vertical_section() -> float:
    return _get_float("BinBaseVerticalSection")

def bin_height() -> int:
    return _get_int("BinHeight")

def bin_magnet_holes() -> bool:
    return _get_bool("BinMagnetHoles")

def bin_outer_radius() -> float:
    return _get_float("BinOuterRadius")

def bin_screw_holes() -> bool:
    return _get_bool("BinScrewHoles")

def bin_wall_thickness() -> float:
    return _get_float("BinWallThickness")

def bin_width_x() -> int:
    return _get_int("BinWidthX")

def bin_width_y() -> int:
    return _get_int("BinWidthY")

def blank_bin_recessed_top_depth() -> float:
    return _get_float("BlankBinRecessedTopDepth")

def clearance() -> float:
    return _get_float("Clearance")

def divider_custom_x() -> bool:
    return _get_bool("DividerCustomX")

def divider_custom_x_height() -> float:
    return _get_float("DividerCustomXHeight")

def divider_custom_y() -> bool:
    return _get_bool("DividerCustomY")

def divider_custom_y_height() -> float:
    return _get_float("DividerCustomYHeight")

def divider_fillet_radius() -> float:
    return _get_float("DividerFilletRadius")

def divider_thickness() -> float:
    return _get_float("DividerThickness")

def eco_bin_base_wall_thickness() -> float:
    return _get_float("EcoBinBaseWallThickness")

def eco_bin_divider_thickness() -> float:
    return _get_float("EcoBinDividerThickness")

def eco_bin_dividers_x() -> int:
    return _get_int("EcoBinDividersX")

def eco_bin_dividers_y() -> int:
    return _get_int("EcoBinDividersY")

def eco_bin_inside_fillet_radius() -> float:
    return _get_float("EcoBinInsideFilletRadius")

def eco_bin_wall_thickness() -> float:
    return _get_float("EcoBinWallThickness")

def grid_height() -> float:
    return _get_float("GridHeight")

def grid_size_x() -> float:
    return _get_float("GridSizeX")

def grid_size_y() -> float:
    return _get_float("GridSizeY")

def independent_grid_size() -> bool:
    return _get_bool("IndependentGridSize")

def label_shelf_angle() -> float:
    return _get_float("LabelShelfAngle")

def label_shelf_length() -> float:
    return _get_float("LabelShelfLength")

def label_shelf_stacking_offset() -> float:
    return _get_float("LabelShelfStackingOffset")

def label_shelf_vertical_thickness() -> float:
    return _get_float("LabelShelfVerticalThickness")

def label_shelf_width() -> float:
    return _get_float("LabelShelfWidth")

def magnet_baseplate_edge_thickness() -> float:
    return _get_float("MagnetBaseplateEdgeThickness")

def magnet_baseplate_magnet_base() -> float:
    return _get_float("MagnetBaseplateMagnetBase")

def magnet_baseplate_magnet_base_hole() -> float:
    return _get_float("MagnetBaseplateMagnetBaseHole")

def magnet_baseplate_magnet_chamfer() -> float:
    return _get_float("MagnetBaseplateMagnetChamfer")

def magnet_baseplate_small_fillet() -> float:
    return _get_float("MagnetBaseplateSmallFillet")

def magnet_hole_depth() -> float:
    return _get_float("MagnetHoleDepth")

def magnet_hole_diameter() -> float:
    return _get_float("MagnetHoleDiameter")

def magnet_hole_distance_from_edge() -> float:
    return _get_float("MagnetHoleDistanceFromEdge")

def parts_bin_dividers_x() -> int:
    return _get_int("PartsBinDividersX")

def parts_bin_dividers_y() -> int:
    return _get_int("PartsBinDividersY")

def parts_bin_scoop() -> bool:
    return _get_bool("PartsBinScoop")

def scoop_radius() -> float:
    return _get_float("ScoopRadius")

def screw_baseplate_base_thickness() -> float:
    return _get_float("ScrewBaseplateBaseThickness")

def screw_baseplate_connection_hole_diameter() -> float:
    return _get_float("ScrewBaseplateConnectionHoleDiameter")

def screw_baseplate_magnet_bottom_chamfer() -> float:
    return _get_float("ScrewBaseplateMagnetBottomChamfer")

def screw_hole_depth() -> float:
    return _get_float("ScrewHoleDepth")

def screw_hole_diameter() -> float:
    return _get_float("ScrewHoleDiameter")

def sequential_bridging_layer_height() -> float:
    return _get_float("SequentialBridgingLayerHeight")

def stacking_lip() -> bool:
    return _get_bool("StackingLip")

def stacking_lip_bottom_chamfer() -> float:
    return _get_float("StackingLipBottomChamfer")

def stacking_lip_top_ledge() -> float:
    return _get_float("StackingLipTopLedge")

def stacking_lip_vertical_section() -> float:
    return _get_float("StackingLipVerticalSection")

# fmt: on
