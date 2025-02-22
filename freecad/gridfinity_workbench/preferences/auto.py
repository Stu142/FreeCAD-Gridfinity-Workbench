"""This file was auto generated, do not edit it directly!

If you want to:
- change a default value: do it in a `.ui` file.
- change a paramter name: do it in a `.ui` file.
- customize a function behaviour: override it in `__init__.py` in this directory

If you make changes to the `.ui` files, run `codegen_preferences.py` again to update this file.
"""
# fmt: off

import FreeCAD

_PARAMS = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Gridfinity")

def baseplate_bottom_chamfer() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("BaseplateBottomChamfer", 0.700000000000000)

def baseplate_bottom_radius() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("BaseplateBottomRadius", 1.150000000000000)

def baseplate_outer_radius() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("BaseplateOuterRadius", 4.000000000000000)

def baseplate_top_chamfer() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("BaseplateTopChamfer", 1.750000000000000)

def baseplate_top_ledge_width() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("BaseplateTopLedgeWidth", 0.400000000000000)

def baseplate_vertical_radius() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("BaseplateVerticalRadius", 1.850000000000000)

def baseplate_vertical_section() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("BaseplateVerticalSection", 1.800000000000000)

def bin_base_bottom_chamfer() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("BinBaseBottomChamfer", 0.800000000000000)

def bin_base_bottom_radius() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("BinBaseBottomRadius", 0.800000000000000)

def bin_base_top_chamfer() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("BinBaseTopChamfer", 2.150000000000000)

def bin_base_vertical_radius() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("BinBaseVerticalRadius", 1.600000000000000)

def bin_base_vertical_section() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("BinBaseVerticalSection", 1.800000000000000)

def bin_height() -> int:
    # from preferences.ui
    return _PARAMS.GetInt("BinHeight", 6)

def bin_magnet_holes() -> bool:
    # from preferences.ui
    return _PARAMS.GetBool("BinMagnetHoles", True)

def bin_outer_radius() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("BinOuterRadius", 3.750000000000000)

def bin_screw_holes() -> bool:
    # from preferences.ui
    return _PARAMS.GetBool("BinScrewHoles", False)

def bin_wall_thickness() -> float:
    # from preferences.ui
    return _PARAMS.GetFloat("BinWallThickness", 1.000000000000000)

def bin_width_x() -> int:
    # from preferences.ui
    return _PARAMS.GetInt("BinWidthX", 2)

def bin_width_y() -> int:
    # from preferences.ui
    return _PARAMS.GetInt("BinWidthY", 2)

def blank_bin_recessed_top_depth() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("BlankBinRecessedTopDepth", 0.000000000000000)

def clearance() -> float:
    # from preferences.ui
    return _PARAMS.GetFloat("Clearance", 0.250000000000000)

def divider_custom_x() -> bool:
    # from preferences-features.ui
    return _PARAMS.GetBool("DividerCustomX", False)

def divider_custom_x_height() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("DividerCustomXHeight", 1.000000000000000)

def divider_custom_y() -> bool:
    # from preferences-features.ui
    return _PARAMS.GetBool("DividerCustomY", False)

def divider_custom_y_height() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("DividerCustomYHeight", 1.000000000000000)

def divider_fillet_radius() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("DividerFilletRadius", 1.850000000000000)

def divider_thickness() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("DividerThickness", 1.200000000000000)

def eco_bin_base_wall_thickness() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("EcoBinBaseWallThickness", 0.800000000000000)

def eco_bin_divider_thickness() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("EcoBinDividerThickness", 0.800000000000000)

def eco_bin_dividers_x() -> int:
    # from preferences-default.ui
    return _PARAMS.GetInt("EcoBinDividersX", 0)

def eco_bin_dividers_y() -> int:
    # from preferences-default.ui
    return _PARAMS.GetInt("EcoBinDividersY", 0)

def eco_bin_inside_fillet_radius() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("EcoBinInsideFilletRadius", 1.000000000000000)

def eco_bin_wall_thickness() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("EcoBinWallThickness", 0.800000000000000)

def grid_height() -> float:
    # from preferences.ui
    return _PARAMS.GetFloat("GridHeight", 7.000000000000000)

def grid_size_x() -> float:
    # from preferences.ui
    return _PARAMS.GetFloat("GridSizeX", 42.000000000000000)

def grid_size_y() -> float:
    # from preferences.ui
    return _PARAMS.GetFloat("GridSizeY", 42.000000000000000)

def independent_grid_size() -> bool:
    # from preferences.ui
    return _PARAMS.GetBool("IndependentGridSize", False)

def label_shelf_angle() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("LabelShelfAngle", 45.000000000000000)

def label_shelf_length() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("LabelShelfLength", 42.000000000000000)

def label_shelf_stacking_offset() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("LabelShelfStackingOffset", 0.400000000000000)

def label_shelf_vertical_thickness() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("LabelShelfVerticalThickness", 1.200000000000000)

def label_shelf_width() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("LabelShelfWidth", 12.000000000000000)

def magnet_baseplate_edge_thickness() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("MagnetBaseplateEdgeThickness", 1.200000000000000)

def magnet_baseplate_magnet_base() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("MagnetBaseplateMagnetBase", 0.400000000000000)

def magnet_baseplate_magnet_base_hole() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("MagnetBaseplateMagnetBaseHole", 3.000000000000000)

def magnet_baseplate_magnet_chamfer() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("MagnetBaseplateMagnetChamfer", 0.400000000000000)

def magnet_baseplate_small_fillet() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("MagnetBaseplateSmallFillet", 1.000000000000000)

def magnet_hole_depth() -> float:
    # from preferences.ui
    return _PARAMS.GetFloat("MagnetHoleDepth", 2.400000000000000)

def magnet_hole_diameter() -> float:
    # from preferences.ui
    return _PARAMS.GetFloat("MagnetHoleDiameter", 6.200000000000000)

def magnet_hole_distance_from_edge() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("MagnetHoleDistanceFromEdge", 8.000000000000000)

def parts_bin_dividers_x() -> int:
    # from preferences-default.ui
    return _PARAMS.GetInt("PartsBinDividersX", 0)

def parts_bin_dividers_y() -> int:
    # from preferences-default.ui
    return _PARAMS.GetInt("PartsBinDividersY", 1)

def parts_bin_scoop() -> bool:
    # from preferences-default.ui
    return _PARAMS.GetBool("PartsBinScoop", True)

def scoop_radius() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("ScoopRadius", 21.000000000000000)

def screw_baseplate_base_thickness() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("ScrewBaseplateBaseThickness", 6.400000000000000)

def screw_baseplate_connection_hole_diameter() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("ScrewBaseplateConnectionHoleDiameter", 3.200000000000000)

def screw_baseplate_magnet_bottom_chamfer() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("ScrewBaseplateMagnetBottomChamfer", 3.000000000000000)

def screw_hole_depth() -> float:
    # from preferences.ui
    return _PARAMS.GetFloat("ScrewHoleDepth", 6.000000000000000)

def screw_hole_diameter() -> float:
    # from preferences.ui
    return _PARAMS.GetFloat("ScrewHoleDiameter", 3.000000000000000)

def sequential_bridging_layer_height() -> float:
    # from preferences-default.ui
    return _PARAMS.GetFloat("SequentialBridgingLayerHeight", 0.200000000000000)

def stacking_lip() -> bool:
    # from preferences.ui
    return _PARAMS.GetBool("StackingLip", True)

def stacking_lip_bottom_chamfer() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("StackingLipBottomChamfer", 0.700000000000000)

def stacking_lip_top_ledge() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("StackingLipTopLedge", 0.400000000000000)

def stacking_lip_vertical_section() -> float:
    # from preferences-features.ui
    return _PARAMS.GetFloat("StackingLipVerticalSection", 1.800000000000000)

# fmt: on
