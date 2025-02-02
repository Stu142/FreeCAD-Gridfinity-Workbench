"""Feature modules contain bins an baseplate objects."""

from abc import abstractmethod

import FreeCAD
import Part
from FreeCAD import Units

from . import const
from .baseplate_feature_construction import (
    make_baseplate_connection_holes,
    make_baseplate_magnet_holes,
    make_baseplate_screw_bottom_chamfer,
)
from .feature_construction import (
    make_baseplate_center_cut,
    make_bin_base,
    make_bottom_holes,
    make_compartments,
    make_eco_bin_cut,
    make_label_shelf,
    make_scoop,
    make_stacking_lip,
)
from .feature_construction_complex_bin import (
    make_complex_bin_base,
    make_complex_bottom_holes,
    make_complex_stacking_lip,
    make_l_mid_section,
)
from .utils import Utils
from .version import __version__

unitmm = Units.Quantity("1 mm")


__all__ = [
    "Baseplate",
    "BinBlank",
    "EcoBin",
    "EcoBin",
    "LBinBlank",
    "MagnetBaseplate",
    "PartsBin",
    "ScrewTogetherBaseplate",
]


HOLE_SHAPES = ["Round", "Hex"]


def _add_bin_properties(  # noqa: PLR0913
    obj: FreeCAD.DocumentObject,
    *,
    screw_holes: bool,
    scoop: bool,
    dividers: bool,
    shelf: bool,
    l_shaped: bool,
) -> None:
    if l_shaped:
        obj.addProperty(
            "App::PropertyInteger",
            "aGridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).aGridUnits = 3
        obj.addProperty(
            "App::PropertyInteger",
            "bGridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).bGridUnits = 1
        obj.addProperty(
            "App::PropertyInteger",
            "cGridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).cGridUnits = 1
        obj.addProperty(
            "App::PropertyInteger",
            "dGridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).dGridUnits = 1
    else:
        obj.addProperty(
            "App::PropertyInteger",
            "xGridUnits",
            "Gridfinity",
            "Length of the edges of the outline",
        ).xGridUnits = 2
        obj.addProperty(
            "App::PropertyInteger",
            "yGridUnits",
            "Gridfinity",
            "Length of the edges of the outline",
        ).yGridUnits = 2

    obj.addProperty(
        "App::PropertyInteger",
        "HeightUnits",
        "Gridfinity",
        "Height of the bin in units, each is 7 mm",
    ).HeightUnits = 6

    obj.addProperty(
        "App::PropertyBool",
        "StackingLip",
        "Gridfinity",
        "Toggle the stacking lip on or off",
    ).StackingLip = True

    obj.addProperty(
        "App::PropertyBool",
        "MagnetHoles",
        "Gridfinity",
        "Toggle the magnet holes on or off",
    ).MagnetHoles = True

    if screw_holes:
        obj.addProperty(
            "App::PropertyBool",
            "ScrewHoles",
            "Gridfinity",
            "Toggle the screw holes on or off",
        ).ScrewHoles = False

    if scoop:
        obj.addProperty(
            "App::PropertyBool",
            "Scoop",
            "Gridfinity",
            "Toggle the Scoop fillet on or off",
        ).Scoop = False

    if dividers:
        obj.addProperty(
            "App::PropertyInteger",
            "xDividers",
            "Gridfinity",
            "Select the Number of Dividers in the x direction",
        ).xDividers = 0
        obj.addProperty(
            "App::PropertyInteger",
            "yDividers",
            "Gridfinity",
            "Select the number of Dividers in the y direction",
        ).yDividers = 0

    if shelf:
        obj.addProperty(
            "App::PropertyEnumeration",
            "LabelShelfPlacement",
            "Gridfinity",
            "Choose the style of the label shelf",
        ).LabelShelfPlacement = ["Center", "Full Width", "Left", "Right"]
        obj.addProperty(
            "App::PropertyEnumeration",
            "LabelShelfStyle",
            "Gridfinity",
            "Choose to turn the label shelf on or off",
        ).LabelShelfStyle = ["Off", "Standard", "Overhang"]


def _add_bin_custom_properties(  # noqa: PLR0913
    obj: FreeCAD.DocumentObject,
    *,
    screw_holes: bool,
    scoop: bool,
    dividers: bool,
    shelf: bool,
    empty: bool,
    wall_thickness: float,
    inside_fillet_radius: float,
    divider_thickness: float,
) -> None:
    obj.addProperty(
        "App::PropertyLength",
        "CustomHeight",
        "GridfinityNonStandard",
        "total height of the bin using the custom height instead of increments of 7 mm",
    ).CustomHeight = 42

    obj.addProperty(
        "App::PropertyLength",
        "SequentialBridgingLayerHeight",
        "GridfinityNonStandard",
        "Layer Height that you print in for optimal print results",
    ).SequentialBridgingLayerHeight = 0.2

    obj.addProperty(
        "App::PropertyBool",
        "NonStandardHeight",
        "GridfinityNonStandard",
        "use a custom height if selected",
    ).NonStandardHeight = False
    obj.addProperty(
        "App::PropertyEnumeration",
        "MagnetHolesShape",
        "GridfinityNonStandard",
        "Shape of magnet holes. <br> <br> Hex meant to be press fit. <br> Round meant to beglued",
    ).MagnetHolesShape = HOLE_SHAPES
    obj.addProperty(
        "App::PropertyLength",
        "MagnetHoleDiameter",
        "GridfinityNonStandard",
        "Diameter of Magnet Holes <br>For Hex holes, inscribed diameter<br> <br>default = 6.5 mm",
    ).MagnetHoleDiameter = const.MAGNET_HOLE_DIAMETER
    obj.addProperty(
        "App::PropertyLength",
        "MagnetHoleDepth",
        "GridfinityNonStandard",
        "Depth of Magnet Holes <br> <br> default = 2.4 mm",
    ).MagnetHoleDepth = const.MAGNET_HOLE_DEPTH

    if screw_holes:
        obj.addProperty(
            "App::PropertyLength",
            "ScrewHoleDiameter",
            "GridfinityNonStandard",
            "Diameter of Screw Holes <br> <br> default = 3.0 mm",
        ).ScrewHoleDiameter = const.SCREW_HOLE_DIAMETER
        obj.addProperty(
            "App::PropertyLength",
            "ScrewHoleDepth",
            "GridfinityNonStandard",
            "Depth of Screw Holes <br> <br> default = 6.0 mm",
        ).ScrewHoleDepth = const.SCREW_HOLE_DEPTH

    if scoop:
        obj.addProperty(
            "App::PropertyLength",
            "ScoopRadius",
            "GridfinityNonStandard",
            "Radius of the Scoop <br> <br> default = 21 mm",
        ).ScoopRadius = const.SCOOP_RADIUS

    if dividers:
        obj.addProperty(
            "App::PropertyLength",
            "DividerThickness",
            "GridfinityNonStandard",
            (
                "Thickness of the dividers, ideally an even multiple of layer width <br> <br> "
                f"default = {divider_thickness} mm"
            ),
        ).DividerThickness = divider_thickness
        obj.addProperty(
            "App::PropertyLength",
            "xDividerHeight",
            "GridfinityNonStandard",
            "Custom Height of x dividers <br> <br> default = 0 mm = full height",
        ).xDividerHeight = 0
        obj.addProperty(
            "App::PropertyLength",
            "yDividerHeight",
            "GridfinityNonStandard",
            "Custom Height of y dividers <br> <br> default = 0 mm = full height",
        ).yDividerHeight = 0

    if shelf:
        obj.addProperty(
            "App::PropertyLength",
            "LabelShelfWidth",
            "GridfinityNonStandard",
            "Thickness of the Label Shelf <br> <br> default = 12 mm",
        ).LabelShelfWidth = const.LABEL_SHELF_WIDTH
        obj.addProperty(
            "App::PropertyLength",
            "LabelShelfLength",
            "GridfinityNonStandard",
            "Length of the Label Shelf <br> <br> default = 42 mm",
        ).LabelShelfLength = const.LABEL_SHELF_LENGTH
        obj.addProperty(
            "App::PropertyAngle",
            "LabelShelfAngle",
            "GridfinityNonStandard",
            "Angle of the bottom part of the Label Shelf <br> <br> default = 45",
        ).LabelShelfAngle = const.LABEL_SHELF_ANGLE

    if empty:
        obj.addProperty(
            "App::PropertyLength",
            "WallThickness",
            "GridfinityNonStandard",
            f"Wall thickness of the bin <br> <br> default = {wall_thickness} mm",
        ).WallThickness = wall_thickness
        obj.addProperty(
            "App::PropertyLength",
            "InsideFilletRadius",
            "GridfinityNonStandard",
            f"Inside fillet at the bottom of the bin <br> <br> default = {inside_fillet_radius} mm",
        ).InsideFilletRadius = inside_fillet_radius


def _add_bin_reference_properties(
    obj: FreeCAD.DocumentObject,
    *,
    usable_height: bool,
    seperate_bin_units: bool,
    l_shaped: bool,
) -> None:
    obj.addProperty(
        "App::PropertyLength",
        "xTotalWidth",
        "ReferenceDimensions",
        "total width of bin in x direction",
        1,
    )
    obj.addProperty(
        "App::PropertyLength",
        "yTotalWidth",
        "ReferenceDimensions",
        "total width of bin in y direction",
        1,
    )
    obj.addProperty(
        "App::PropertyLength",
        "TotalHeight",
        "ReferenceDimensions",
        "total height of the bin",
        1,
    )

    obj.addProperty(
        "App::PropertyLength",
        "BaseProfileHeight",
        "ReferenceDimensions",
        "Height of the Gridfinity Base Profile",
        1,
    )

    if seperate_bin_units:
        obj.addProperty(
            "App::PropertyLength",
            "xBinUnit",
            "ReferenceDimensions",
            "Width of a single bin unit",
            1,
        ).xBinUnit = const.BIN_UNIT
        obj.addProperty(
            "App::PropertyLength",
            "yBinUnit",
            "ReferenceDimensions",
            "Width of a single bin unit",
            1,
        ).yBinUnit = const.BIN_UNIT
    else:
        obj.addProperty(
            "App::PropertyLength",
            "BinUnit",
            "ReferenceDimensions",
            "Width of a single bin unit",
            1,
        ).BinUnit = const.BIN_UNIT

    if usable_height:
        obj.addProperty(
            "App::PropertyLength",
            "UsableHeight",
            "ReferenceDimensions",
            (
                "Height of the bin minus the bottom unit, "
                "the amount of the bin that can be effectively used"
            ),
            1,
        )

    if l_shaped:
        obj.addProperty(
            "App::PropertyLength",
            "aTotalDimension",
            "ReferenceDimensions",
            "total width of a dimension",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "bTotalDimension",
            "ReferenceDimensions",
            "total width of b dimension",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "cTotalDimension",
            "ReferenceDimensions",
            "total width of c dimension",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "dTotalDimension",
            "ReferenceDimensions",
            "total width of d dimension",
            1,
        )


def _add_bin_expert_properties(
    obj: FreeCAD.DocumentObject,
    *,
    shelf: bool,
) -> None:
    obj.addProperty(
        "App::PropertyLength",
        "BaseProfileBottomChamfer",
        "zzExpertOnly",
        "height of chamfer in bottom of bin base profile <br> <br> default = 0.8 mm",
        1,
    ).BaseProfileBottomChamfer = const.BIN_BASE_BOTTOM_CHAMFER

    obj.addProperty(
        "App::PropertyLength",
        "BaseProfileVerticalSection",
        "zzExpertOnly",
        "Height of the vertical section in bin base profile",
        1,
    ).BaseProfileVerticalSection = const.BIN_BASE_VERTICAL_SECTION

    obj.addProperty(
        "App::PropertyLength",
        "BaseProfileTopChamfer",
        "zzExpertOnly",
        "Height of the top chamfer in the bin base profile",
        1,
    ).BaseProfileTopChamfer = const.BIN_BASE_TOP_CHAMFER

    obj.addProperty(
        "App::PropertyLength",
        "GridSize",
        "zzExpertOnly",
        "Size of the Grid",
    ).GridSize = const.GRID_SIZE

    obj.addProperty(
        "App::PropertyLength",
        "HeightUnitValue",
        "zzExpertOnly",
        "height per unit, default is 7mm",
        1,
    ).HeightUnitValue = const.HEIGHT_UNIT

    obj.addProperty(
        "App::PropertyLength",
        "BinOuterRadius",
        "zzExpertOnly",
        "Outer radius of the bin",
        1,
    ).BinOuterRadius = const.BIN_OUTER_RADIUS

    obj.addProperty(
        "App::PropertyLength",
        "BinVerticalRadius",
        "zzExpertOnly",
        "Radius of the base profile Vertical section",
        1,
    ).BinVerticalRadius = const.BIN_BASE_VERTICAL_RADIUS

    obj.addProperty(
        "App::PropertyLength",
        "BinBottomRadius",
        "zzExpertOnly",
        "bottom of bin corner radius",
        1,
    ).BinBottomRadius = const.BIN_BASE_BOTTOM_RADIUS

    obj.addProperty(
        "App::PropertyLength",
        "Clearance",
        "zzExpertOnly",
        (
            "The tolerance on each side of a bin between before the edge of the grid <br> <br>"
            "default = 0.25 mm"
        ),
    ).Clearance = const.CLEARANCE

    obj.addProperty(
        "App::PropertyLength",
        "MagnetHoleDistanceFromEdge",
        "zzExpertOnly",
        "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",
        1,
    ).MagnetHoleDistanceFromEdge = const.MAGNET_HOLE_DISTANCE_FROM_EDGE

    obj.addProperty(
        "App::PropertyLength",
        "StackingLipTopLedge",
        "zzExpertOnly",
        "Top Ledge of the stacking lip <br> <br> default = 0.4 mm",
        1,
    ).StackingLipTopLedge = const.STACKING_LIP_TOP_LEDGE

    obj.addProperty(
        "App::PropertyLength",
        "StackingLipTopChamfer",
        "zzExpertOnly",
        "Top Chamfer of the Stacking lip",
        1,
    )

    obj.addProperty(
        "App::PropertyLength",
        "StackingLipBottomChamfer",
        "zzExpertOnly",
        "Bottom Chamfer of the Stacking lip<br> <br> default = 0.7 mm",
        1,
    ).StackingLipBottomChamfer = const.STACKING_LIP_BOTTOM_CHAMFER

    obj.addProperty(
        "App::PropertyLength",
        "StackingLipVerticalSection",
        "zzExpertOnly",
        "vertical section of the Stacking lip<br> <br> default = 1.8 mm",
        1,
    ).StackingLipVerticalSection = const.STACKING_LIP_VERTICAL_SECTION

    if shelf:
        obj.addProperty(
            "App::PropertyLength",
            "LabelShelfVerticalThickness",
            "zzExpertOnly",
            "Vertical Thickness of the Label Shelf <br> <br> default = 2 mm",
        ).LabelShelfVerticalThickness = const.LABEL_SHELF_VERTICAL_THICKNESS
        obj.addProperty(
            "App::PropertyLength",
            "LabelShelfStackingOffset",
            "zzExpertOnly",
            "Vertical Thickness of the Label Shelf <br> <br> default = 0.4 mm",
        ).LabelShelfStackingOffset = const.LABEL_SHELF_STACKING_OFFSET


def _add_bin_hidden_properties(obj: FreeCAD.DocumentObject) -> None:
    obj.addProperty(
        "App::PropertyLength",
        "WallThickness",
        "GridfinityNonStandard",
        "for stacking lip",
    ).WallThickness = 1
    obj.setEditorMode("WallThickness", 2)


def _add_baseplate_properties(obj: FreeCAD.DocumentObject, *, magnet_holes: bool) -> None:
    obj.addProperty(
        "App::PropertyInteger",
        "xGridUnits",
        "Gridfinity",
        "Length of the edges of the outline",
    ).xGridUnits = 2

    obj.addProperty(
        "App::PropertyInteger",
        "yGridUnits",
        "Gridfinity",
        "Height of the extrusion",
    ).yGridUnits = 2

    if magnet_holes:
        obj.addProperty(
            "App::PropertyBool",
            "MagnetHoles",
            "Gridfinity",
            "MagnetHoles",
        ).MagnetHoles = True


def _add_baseplate_custom_properties(obj: FreeCAD.DocumentObject, *, screw_together: bool) -> None:
    obj.addProperty(
        "App::PropertyLength",
        "SmallFillet",
        "NonStandard",
        "Small fillet on iside of baseplate <br> <br> default = 1 mm",
    ).SmallFillet = const.BASEPLATE_SMALL_FILLET

    obj.addProperty(
        "App::PropertyEnumeration",
        "MagnetHolesShape",
        "NonStandard",
        (
            "Shape of magnet holes. <br> <br> Hex meant to be press fit. <br> "
            "Round meant to be glued"
        ),
    )

    obj.MagnetHolesShape = HOLE_SHAPES

    obj.addProperty(
        "App::PropertyLength",
        "MagnetHoleDiameter",
        "NonStandard",
        (
            "Diameter of Magnet Holes <br>For Hex holes, inscribed diameter<br> <br> "
            "default = 6.5 mm"
        ),
    ).MagnetHoleDiameter = const.MAGNET_HOLE_DIAMETER

    obj.addProperty(
        "App::PropertyLength",
        "MagnetHoleDepth",
        "NonStandard",
        "Depth of Magnet Holes <br> <br> default = 2.4 mm",
    ).MagnetHoleDepth = const.MAGNET_HOLE_DEPTH

    obj.addProperty(
        "App::PropertyLength",
        "MagnetEdgeThickness",
        "NonStandard",
        "Thickness of edge holding magnets in place <br> <br> default = 1.2 mm",
    ).MagnetEdgeThickness = const.MAGNET_EDGE_THICKNESS

    if screw_together:
        obj.addProperty(
            "App::PropertyLength",
            "BaseThickness",
            "NonStandard",
            "Thickness of base under the normal baseplate  profile <br> <br> default = 6.4 mm",
        ).BaseThickness = const.BASE_THICKNESS
    else:
        obj.addProperty(
            "App::PropertyLength",
            "MagnetBase",
            "NonStandard",
            "Thickness of base under the magnets <br> <br> default = 0.4 mm",
        ).MagnetBase = const.MAGNET_BASE

    obj.addProperty(
        "App::PropertyLength",
        "MagnetBaseHole",
        "NonStandard",
        "Diameter of the hole at the bottom of the magnet cutout <br> <br> default = 3 mm",
    ).MagnetBaseHole = const.MAGNET_BASE_HOLE

    obj.addProperty(
        "App::PropertyLength",
        "MagnetChamfer",
        "NonStandard",
        "Chamfer at top of magnet hole <br> <br> default = 0.4 mm",
    ).MagnetChamfer = const.MAGNET_CHAMFER

    if screw_together:
        obj.addProperty(
            "App::PropertyLength",
            "MagnetBottomChamfer",
            "NonStandard",
            "Chamfer at bottom of magnet hole <br> <br> default = 2 mm",
        ).MagnetBottomChamfer = const.MAGNET_BOTTOM_CHAMFER

        obj.addProperty(
            "App::PropertyLength",
            "ScrewHoleDiameter",
            "NonStandard",
            "Diameter of screw holes inside magnet holes <br> <br> default = 3 mm",
        ).ScrewHoleDiameter = const.SCREW_HOLE_DIAMETER

        obj.addProperty(
            "App::PropertyLength",
            "ConnectionHoleDiameter",
            "NonStandard",
            "Holes on the sides to connect multiple baseplates together <br> <br> default = 3.2 mm",
        ).ConnectionHoleDiameter = const.CONNECTION_HOLE_DIAMETER


def _add_baseplate_reference_properties(obj: FreeCAD.DocumentObject) -> None:
    obj.addProperty(
        "App::PropertyLength",
        "xTotalWidth",
        "ReferenceDimensions",
        "total width of bin in x direction",
        1,
    )

    obj.addProperty(
        "App::PropertyLength",
        "yTotalWidth",
        "ReferenceDimensions",
        "total width of bin in y direction",
        1,
    )

    obj.addProperty(
        "App::PropertyLength",
        "TotalHeight",
        "ReferenceDimensions",
        "total height of the bin",
        1,
    )

    obj.addProperty(
        "App::PropertyLength",
        "BaseProfileHeight",
        "ReferenceDimensions",
        "Height of the Gridfinity Base Profile",
        1,
    )


def _add_baseplate_expert_properties(obj: FreeCAD.DocumentObject) -> None:
    obj.addProperty(
        "App::PropertyLength",
        "BaseProfileBottomChamfer",
        "zzExpertOnly",
        "height of chamfer in bottom of bin base profile <br> <br> default = 0.8 mm",
        1,
    ).BaseProfileBottomChamfer = const.BASEPLATE_BOTTOM_CHAMFER

    obj.addProperty(
        "App::PropertyLength",
        "BaseProfileVerticalSection",
        "zzExpertOnly",
        "Height of the vertical section in bin base profile",
        1,
    ).BaseProfileVerticalSection = const.BASEPLATE_VERTICAL_SECTION

    obj.addProperty(
        "App::PropertyLength",
        "BaseProfileTopChamfer",
        "zzExpertOnly",
        "Height of the top chamfer in the bin base profile",
        1,
    ).BaseProfileTopChamfer = const.BASEPLATE_TOP_CHAMFER

    obj.addProperty(
        "App::PropertyLength",
        "BaseplateProfileTotalHeight",
        "zzExpertOnly",
        "Height of the bin base profile",
        1,
    )

    obj.addProperty(
        "App::PropertyLength",
        "GridSize",
        "zzExpertOnly",
        "Size of the Grid",
    ).GridSize = const.GRID_SIZE

    obj.addProperty(
        "App::PropertyLength",
        "HeightUnitValue",
        "zzExpertOnly",
        "height per unit, default is 7mm",
        1,
    ).HeightUnitValue = const.HEIGHT_UNIT

    obj.addProperty(
        "App::PropertyLength",
        "BinOuterRadius",
        "zzExpertOnly",
        "Outer radius of the baseplate",
        1,
    ).BinOuterRadius = const.BASEPLATE_OUTER_RADIUS

    obj.addProperty(
        "App::PropertyLength",
        "BinVerticalRadius",
        "zzExpertOnly",
        "Radius of the baseplate profile Vertical section",
        1,
    ).BinVerticalRadius = const.BASEPLATE_VERTICAL_RADIUS

    obj.addProperty(
        "App::PropertyLength",
        "BinBottomRadius",
        "zzExpertOnly",
        "bottom of baseplate corner radius",
        1,
    ).BinBottomRadius = const.BASEPLATE_BOTTOM_RADIUS

    obj.addProperty(
        "App::PropertyLength",
        "BaseplateTopLedgeWidth",
        "zzExpertOnly",
        "Top ledge of baseplate",
        1,
    ).BaseplateTopLedgeWidth = const.BASEPLATE_TOP_LEDGE_WIDTH

    obj.addProperty(
        "App::PropertyLength",
        "BinUnit",
        "zzExpertOnly",
        "Width of a single bin unit",
        2,
    ).BinUnit = const.BIN_UNIT

    obj.addProperty(
        "App::PropertyLength",
        "Clearance",
        "zzExpertOnly",
        (
            "The tolerance on each side of a bin between before the edge of the grid <br> <br> "
            "default = 0.25 mm"
        ),
        1,
    ).Clearance = const.CLEARANCE

    obj.addProperty(
        "App::PropertyLength",
        "MagnetHoleDistanceFromEdge",
        "zzExpertOnly",
        "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",
        1,
    ).MagnetHoleDistanceFromEdge = const.MAGNET_HOLE_DISTANCE_FROM_EDGE


def _add_baseplate_hidden_properties(obj: FreeCAD.DocumentObject) -> None:
    obj.addProperty(
        "App::PropertyLength",
        "BaseThickness",
        "NonStandard",
        "Thickness of base under the normal baseplate  profile <br> <br> default = 6.4 mm",
    ).BaseThickness = const.BASE_THICKNESS
    obj.setEditorMode("BaseThickness", 2)


class FoundationGridfinity:
    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        obj.addProperty(
            "App::PropertyString",
            "version",
            "version",
            "Gridfinity Workbench Version",
            1,
        )

        obj.version = __version__

    def execute(self, fp: Part.Feature) -> None:
        gridfinity_shape = self.generate_gridfinity_shape(fp)

        if hasattr(fp, "BaseFeature") and fp.BaseFeature is not None:
            # we're inside a PartDesign Body, thus need to fuse with the base feature

            gridfinity_shape.Placement = (
                fp.Placement
            )  # ensure the bin is placed correctly before fusing

            result_shape = fp.BaseFeature.Shape.fuse(gridfinity_shape)

            result_shape.transformShape(fp.Placement.inverse().toMatrix(), copy=True)

            fp.Shape = result_shape

        else:
            fp.Shape = gridfinity_shape

    @abstractmethod
    def generate_gridfinity_shape(self, fp: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate the TopoShape of the object."""


class BinBlank(FoundationGridfinity):
    """Gridfinity BinBlank object."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Create BinBlank object.

        Args:
            obj (FreeCAD.DocumentObject): Document object


        """
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        _add_bin_properties(
            obj,
            screw_holes=True,
            scoop=False,
            dividers=False,
            shelf=False,
            l_shaped=False,
        )

        _add_bin_custom_properties(
            obj,
            screw_holes=True,
            scoop=False,
            dividers=False,
            shelf=False,
            empty=False,
            wall_thickness=0,
            inside_fillet_radius=0,
            divider_thickness=0,
        )

        _add_bin_reference_properties(
            obj,
            usable_height=False,
            seperate_bin_units=False,
            l_shaped=False,
        )

        _add_bin_expert_properties(obj, shelf=False)

        _add_bin_hidden_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate BinBlanek Shape.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Bin Blank shape

        """
        obj.xTotalWidth = obj.xGridUnits * obj.GridSize - obj.Clearance * 2

        obj.yTotalWidth = obj.yGridUnits * obj.GridSize - obj.Clearance * 2

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )

        obj.StackingLipTopChamfer = (
            obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
        )

        obj.BinUnit = obj.GridSize - const.CLEARANCE * 2 * unitmm

        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight

        else:
            obj.TotalHeight = obj.HeightUnits * obj.HeightUnitValue

        fuse_total = make_bin_base(obj)

        solid_center = Utils.rounded_rectangle_extrude(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.TotalHeight + obj.BaseProfileHeight,
            obj.TotalHeight - obj.BaseProfileHeight,
            obj.BinOuterRadius,
        )

        solid_center.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 - obj.BinUnit / 2,
                obj.yTotalWidth / 2 - obj.BinUnit / 2,
                0,
            ),
        )

        fuse_total = Part.Shape.fuse(fuse_total, solid_center)

        if obj.StackingLip:
            stacking_lip = make_stacking_lip(obj)

            fuse_total = Part.Shape.fuse(stacking_lip, fuse_total)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = make_bottom_holes(obj)

            fuse_total = Part.Shape.cut(fuse_total, holes)

        return fuse_total


class BinBase(FoundationGridfinity):
    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        _add_bin_properties(
            obj,
            screw_holes=True,
            scoop=False,
            dividers=False,
            shelf=False,
            l_shaped=False,
        )

        _add_bin_custom_properties(
            obj,
            screw_holes=True,
            scoop=False,
            dividers=False,
            shelf=False,
            empty=False,
            wall_thickness=1,
            inside_fillet_radius=0,
            divider_thickness=0,
        )

        _add_bin_reference_properties(
            obj,
            usable_height=False,
            seperate_bin_units=False,
            l_shaped=False,
        )

        _add_bin_expert_properties(obj, shelf=False)

        _add_bin_hidden_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        obj.xTotalWidth = obj.xGridUnits * obj.GridSize - obj.Clearance * 2

        obj.yTotalWidth = obj.yGridUnits * obj.GridSize - obj.Clearance * 2

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )

        obj.StackingLipTopChamfer = (
            obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
        )

        obj.BinUnit = obj.GridSize - const.CLEARANCE * 2 * unitmm

        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight

        else:
            obj.TotalHeight = obj.HeightUnits * obj.HeightUnitValue

        fuse_total = make_bin_base(obj)

        solid_center = Utils.rounded_rectangle_extrude(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.TotalHeight + obj.BaseProfileHeight,
            obj.TotalHeight - obj.BaseProfileHeight,
            obj.BinOuterRadius,
        )

        solid_center.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 - obj.BinUnit / 2,
                obj.yTotalWidth / 2 - obj.BinUnit / 2,
                0,
            ),
        )

        fuse_total = Part.Shape.fuse(fuse_total, solid_center)

        if obj.StackingLip:
            stacking_lip = make_stacking_lip(obj)

            fuse_total = Part.Shape.fuse(stacking_lip, fuse_total)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = make_bottom_holes(obj)

            fuse_total = Part.Shape.cut(fuse_total, holes)

        return fuse_total


class SimpleStorageBin(FoundationGridfinity):
    """Simple Storage Bin."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize Simple storage bin properties.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        _add_bin_properties(
            obj,
            screw_holes=True,
            scoop=True,
            dividers=True,
            shelf=True,
            l_shaped=False,
        )

        _add_bin_custom_properties(
            obj,
            screw_holes=True,
            scoop=True,
            dividers=True,
            shelf=True,
            empty=True,
            wall_thickness=1,
            inside_fillet_radius=1.85,
            divider_thickness=1.2,
        )

        _add_bin_reference_properties(
            obj,
            usable_height=True,
            seperate_bin_units=False,
            l_shaped=False,
        )

        _add_bin_expert_properties(obj, shelf=True)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate simple storage bin.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Storage bin shape.

        """
        ## Parameter Calculations

        obj.xTotalWidth = obj.xGridUnits * obj.GridSize - obj.Clearance * 2

        obj.yTotalWidth = obj.yGridUnits * obj.GridSize - obj.Clearance * 2

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )

        obj.StackingLipTopChamfer = (
            obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
        )

        obj.BinUnit = obj.GridSize - const.CLEARANCE * 2 * unitmm

        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight

        else:
            obj.TotalHeight = obj.HeightUnits * obj.HeightUnitValue

        obj.UsableHeight = obj.TotalHeight - obj.HeightUnitValue

        ## Error Checking

        divmin = obj.HeightUnitValue + obj.InsideFilletRadius + 0.05 * unitmm

        if obj.xDividerHeight < divmin and obj.xDividerHeight != 0:
            obj.xDividerHeight = divmin

            FreeCAD.Console.PrintWarning(
                "Divider Height must be equal to or greater than:  ",
            )

            FreeCAD.Console.PrintWarning(divmin)

            FreeCAD.Console.PrintWarning("\n")

        if obj.yDividerHeight < divmin and obj.yDividerHeight != 0:
            obj.yDividerHeight = divmin

            FreeCAD.Console.PrintWarning(
                "Divider Height must be equal to or greater than:  ",
            )

            FreeCAD.Console.PrintWarning(divmin)

            FreeCAD.Console.PrintWarning("\n")

        if (
            obj.xDividerHeight < obj.TotalHeight
            and obj.LabelShelfStyle != "Off"
            and obj.xDividerHeight != 0
            and obj.xDividers != 0
        ):
            obj.LabelShelfStyle = "Off"

            FreeCAD.Console.PrintWarning(
                "Label Shelf turned off for less than full height x dividers",
            )

        ## Bin Construction

        fuse_total = make_bin_base(obj)

        solid_center = Utils.rounded_rectangle_extrude(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.TotalHeight + obj.BaseProfileHeight,
            obj.TotalHeight - obj.BaseProfileHeight,
            obj.BinOuterRadius,
        )

        solid_center.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 - obj.BinUnit / 2,
                obj.yTotalWidth / 2 - obj.BinUnit / 2,
                0,
            ),
        )

        fuse_total = fuse_total.fuse(solid_center)

        compartements = make_compartments(obj)

        fuse_total = fuse_total.cut(compartements)

        if obj.StackingLip:
            stacking_lip = make_stacking_lip(obj)

            fuse_total = Part.Shape.fuse(stacking_lip, fuse_total)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = make_bottom_holes(obj)

            fuse_total = Part.Shape.cut(fuse_total, holes)

        if obj.LabelShelfStyle != "Off":
            label_shelf = make_label_shelf(obj)

            fuse_total = fuse_total.fuse(label_shelf)

        if obj.Scoop:
            scoop = make_scoop(obj)

            fuse_total = fuse_total.fuse(scoop)

        return Part.Solid.removeSplitter(fuse_total)


class EcoBin(FoundationGridfinity):
    """Eco Bin."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize Eco bin properties."""
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        _add_bin_properties(
            obj,
            screw_holes=True,
            scoop=False,
            dividers=True,
            shelf=False,
            l_shaped=False,
        )

        obj.addProperty(
            "App::PropertyLength",
            "BaseWallThickness",
            "Gridfinity",
            "The thickness of the bin at the base",
        ).BaseWallThickness = 0.8

        _add_bin_custom_properties(
            obj,
            screw_holes=True,
            scoop=False,
            dividers=True,
            shelf=False,
            empty=True,
            wall_thickness=0.8,
            inside_fillet_radius=1.5,
            divider_thickness=0.8,
        )

        _add_bin_reference_properties(
            obj,
            usable_height=False,
            seperate_bin_units=False,
            l_shaped=False,
        )

        _add_bin_expert_properties(obj, shelf=False)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Create gridfinity EcoBin shape.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject.

        Returns:
            Part.Shape: EcoBin shape.

        """
        ## Parameter Calculation

        obj.xTotalWidth = obj.xGridUnits * obj.GridSize - obj.Clearance * 2

        obj.yTotalWidth = obj.yGridUnits * obj.GridSize - obj.Clearance * 2

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )

        obj.StackingLipTopChamfer = (
            obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
        )

        obj.BinUnit = obj.GridSize - const.CLEARANCE * 2 * unitmm

        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight

        else:
            obj.TotalHeight = obj.HeightUnits * obj.HeightUnitValue

        ## Error Checking

        # Divider Minimum Height

        divmin = obj.HeightUnitValue + obj.InsideFilletRadius + 0.05 * unitmm

        if obj.xDividerHeight < divmin and obj.xDividerHeight != 0:
            obj.xDividerHeight = divmin

            FreeCAD.Console.PrintWarning(
                "Divider Height must be equal to or greater than:  ",
            )

            FreeCAD.Console.PrintWarning(divmin)

            FreeCAD.Console.PrintWarning("\n")

        if obj.yDividerHeight < divmin and obj.yDividerHeight != 0:
            obj.yDividerHeight = divmin

            FreeCAD.Console.PrintWarning(
                "Divider Height must be equal to or greater than:  ",
            )

            FreeCAD.Console.PrintWarning(divmin)

            FreeCAD.Console.PrintWarning("\n")

        if obj.InsideFilletRadius > (1.6 * unitmm):
            obj.InsideFilletRadius = 1.6 * unitmm

            FreeCAD.Console.PrintWarning(
                "Inside Fillet Radius must be equal to or less than:  1.6 mm\n",
            )

        ## Bin Construction

        fuse_total = make_bin_base(obj)

        solid_center = Utils.rounded_rectangle_extrude(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.TotalHeight + obj.BaseProfileHeight,
            obj.TotalHeight - obj.BaseProfileHeight,
            obj.BinOuterRadius,
        )

        solid_center.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 - obj.BinUnit / 2,
                obj.yTotalWidth / 2 - obj.BinUnit / 2,
                0,
            ),
        )

        fuse_total = fuse_total.fuse(solid_center)

        compartements = make_eco_bin_cut(obj)

        fuse_total = fuse_total.cut(compartements)

        if obj.StackingLip:
            stacking_lip = make_stacking_lip(obj)

            fuse_total = Part.Shape.fuse(stacking_lip, fuse_total)

        if obj.MagnetHoles:
            holes = make_bottom_holes(obj)

            fuse_total = Part.Shape.cut(fuse_total, holes)

        return Part.Solid.removeSplitter(fuse_total)


class PartsBin(FoundationGridfinity):
    """PartsBin object."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize Partsbin properties.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        _add_bin_properties(
            obj,
            screw_holes=True,
            scoop=True,
            dividers=True,
            shelf=True,
            l_shaped=False,
        )

        _add_bin_custom_properties(
            obj,
            screw_holes=True,
            scoop=True,
            dividers=True,
            shelf=True,
            empty=True,
            wall_thickness=1,
            inside_fillet_radius=1.85,
            divider_thickness=0,
        )

        _add_bin_reference_properties(
            obj,
            usable_height=True,
            seperate_bin_units=False,
            l_shaped=False,
        )

        _add_bin_expert_properties(obj, shelf=True)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate Eco bin shape.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject

        Returns:
            Part.Shape: PartsBin Shape.

        """
        ## Calculated Properties

        obj.xTotalWidth = obj.xGridUnits * obj.GridSize - obj.Clearance * 2

        obj.yTotalWidth = obj.yGridUnits * obj.GridSize - obj.Clearance * 2

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )

        obj.StackingLipTopChamfer = (
            obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
        )

        obj.BinUnit = obj.GridSize - const.CLEARANCE * 2 * unitmm

        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight

        else:
            obj.TotalHeight = obj.HeightUnits * obj.HeightUnitValue

        obj.UsableHeight = obj.TotalHeight - obj.HeightUnitValue

        ## Error Checking

        # Divider Minimum Height

        divmin = obj.HeightUnitValue + obj.InsideFilletRadius + 0.05 * unitmm

        if obj.xDividerHeight < divmin and obj.xDividerHeight != 0:
            obj.xDividerHeight = divmin

            FreeCAD.Console.PrintWarning(
                "Divider Height must be equal to or greater than:  ",
            )

            FreeCAD.Console.PrintWarning(divmin)

            FreeCAD.Console.PrintWarning("\n")

        if obj.yDividerHeight < divmin and obj.yDividerHeight != 0:
            obj.yDividerHeight = divmin

            FreeCAD.Console.PrintWarning(
                "Divider Height must be equal to or greater than:  ",
            )

            FreeCAD.Console.PrintWarning(divmin)

            FreeCAD.Console.PrintWarning("\n")

        if (
            obj.xDividerHeight < obj.TotalHeight
            and obj.LabelShelfStyle != "Off"
            and obj.xDividerHeight != 0
            and obj.xDividers != 0
        ):
            obj.LabelShelfStyle = "Off"

            FreeCAD.Console.PrintWarning(
                "Label Shelf turned off for less than full height x dividers",
            )

        ## Bin Construction

        fuse_total = make_bin_base(obj)

        solid_center = Utils.rounded_rectangle_extrude(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.TotalHeight + obj.BaseProfileHeight,
            obj.TotalHeight - obj.BaseProfileHeight,
            obj.BinOuterRadius,
        )

        solid_center.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 - obj.BinUnit / 2,
                obj.yTotalWidth / 2 - obj.BinUnit / 2,
                0,
            ),
        )

        fuse_total = fuse_total.fuse(solid_center)

        compartements = make_compartments(obj)

        fuse_total = fuse_total.cut(compartements)

        if obj.StackingLip:
            stacking_lip = make_stacking_lip(obj)

            fuse_total = Part.Shape.fuse(stacking_lip, fuse_total)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = make_bottom_holes(obj)

            fuse_total = Part.Shape.cut(fuse_total, holes)

        if obj.LabelShelfStyle != "Off":
            label_shelf = make_label_shelf(obj)

            fuse_total = fuse_total.fuse(label_shelf)

        if obj.Scoop:
            scoop = make_scoop(obj)

            fuse_total = fuse_total.fuse(scoop)

        return Part.Solid.removeSplitter(fuse_total)


class Baseplate(FoundationGridfinity):
    """BasePlate object."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize Baseplate properties.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        """
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        _add_baseplate_properties(obj, magnet_holes=False)
        _add_baseplate_reference_properties(obj)
        _add_baseplate_expert_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate partsbin shape.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        Returns:
            Part.Shape: PartsBin Shape.

        """
        obj.xTotalWidth = obj.xGridUnits * obj.GridSize

        obj.yTotalWidth = obj.yGridUnits * obj.GridSize

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )

        obj.TotalHeight = obj.BaseProfileHeight

        obj.BinUnit = obj.GridSize - obj.BaseplateTopLedgeWidth * 2

        fuse_total = make_bin_base(obj)

        solid_center = Utils.rounded_rectangle_extrude(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.TotalHeight,
            obj.TotalHeight,
            obj.BinOuterRadius,
        )

        solid_center.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 - obj.GridSize / 2,
                obj.yTotalWidth / 2 - obj.GridSize / 2,
                0,
            ),
        )

        return Part.Shape.cut(solid_center, fuse_total)


class MagnetBaseplate(FoundationGridfinity):
    """Magnet baseplate object."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize magent baseplate properties.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject.

        """
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        _add_baseplate_properties(obj, magnet_holes=True)
        _add_baseplate_custom_properties(obj, screw_together=False)
        _add_baseplate_reference_properties(obj)
        _add_baseplate_expert_properties(obj)
        _add_baseplate_hidden_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate partsbin shape.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        Returns:
            Part.Shape: PartsBin Shape.

        """
        obj.xTotalWidth = obj.xGridUnits * obj.GridSize

        obj.yTotalWidth = obj.yGridUnits * obj.GridSize

        # Bottom of Bin placement, used for ability to reuse previous features.

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )

        # actaully the total height of the baseplate

        obj.TotalHeight = obj.BaseProfileHeight + obj.MagnetHoleDepth + obj.MagnetBase

        obj.BinUnit = obj.GridSize - obj.BaseplateTopLedgeWidth * 2

        fuse_total = make_bin_base(obj)

        fuse_total.translate(FreeCAD.Vector(0, 0, obj.TotalHeight - obj.BaseProfileHeight))

        solid_center = Utils.rounded_rectangle_extrude(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.TotalHeight,
            obj.TotalHeight,
            obj.BinOuterRadius,
        )

        solid_center.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 - obj.GridSize / 2,
                obj.yTotalWidth / 2 - obj.GridSize / 2,
                0,
            ),
        )

        fuse_total = Part.Shape.cut(solid_center, fuse_total)

        cutout = make_baseplate_center_cut(obj)

        fuse_total = Part.Shape.cut(fuse_total, cutout)

        magholes = make_baseplate_magnet_holes(obj)

        return Part.Shape.cut(fuse_total, magholes)


class ScrewTogetherBaseplate(FoundationGridfinity):
    """Screw together baseplate object."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize screw together baseplate properties.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        _add_baseplate_properties(obj, magnet_holes=False)
        _add_baseplate_custom_properties(obj, screw_together=True)
        _add_baseplate_reference_properties(obj)
        _add_baseplate_expert_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate Parts Bin shape.

        Args:
            obj (FreeCAD.DocumentObject): Document Object.

        Returns:
            Part.Shape: ParstBin Shape.

        """
        obj.xTotalWidth = obj.xGridUnits * obj.GridSize

        obj.yTotalWidth = obj.yGridUnits * obj.GridSize

        # Bottom of Bin placement, used for ability to reuse previous features.

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )

        # actaully the total height of the baseplate

        obj.TotalHeight = obj.BaseProfileHeight + obj.BaseThickness

        obj.BinUnit = obj.GridSize - obj.BaseplateTopLedgeWidth * 2

        fuse_total = make_bin_base(obj)

        fuse_total.translate(FreeCAD.Vector(0, 0, obj.TotalHeight - obj.BaseProfileHeight))

        solid_center = Utils.rounded_rectangle_extrude(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.TotalHeight,
            obj.TotalHeight,
            obj.BinOuterRadius,
        )

        solid_center.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 - obj.GridSize / 2,
                obj.yTotalWidth / 2 - obj.GridSize / 2,
                0,
            ),
        )

        fuse_total = Part.Shape.cut(solid_center, fuse_total)

        cutout = make_baseplate_center_cut(obj)

        fuse_total = Part.Shape.cut(fuse_total, cutout)

        magholes = make_baseplate_magnet_holes(obj)

        fuse_total = Part.Shape.cut(fuse_total, magholes)

        magchamfer = make_baseplate_screw_bottom_chamfer(obj)

        fuse_total = Part.Shape.cut(fuse_total, magchamfer)

        conholes = make_baseplate_connection_holes(obj)

        return Part.Shape.cut(fuse_total, conholes)


class LBinBlank(FoundationGridfinity):
    """L shaped blank bin object."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize L shaped blank bin properties.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject

        """
        super().__init__(obj)

        obj.addProperty("App::PropertyPythonObject", "Bin", "base", "python gridfinity object")

        _add_bin_properties(
            obj,
            screw_holes=True,
            scoop=False,
            dividers=False,
            shelf=False,
            l_shaped=True,
        )
        _add_bin_custom_properties(
            obj,
            screw_holes=True,
            scoop=False,
            dividers=False,
            shelf=False,
            empty=False,
            wall_thickness=0,
            inside_fillet_radius=0,
            divider_thickness=0,
        )
        _add_bin_reference_properties(
            obj,
            usable_height=False,
            seperate_bin_units=True,
            l_shaped=True,
        )
        _add_bin_expert_properties(obj, shelf=False)
        _add_bin_hidden_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate gridfinity L shaped bin.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject

        Returns:
            Part.Shape: L shaped bin shape.

        """
        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight
        else:
            obj.TotalHeight = obj.HeightUnits * obj.HeightUnitValue

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )
        obj.StackingLipTopChamfer = (
            obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
        )
        obj.xBinUnit = obj.GridSize - const.CLEARANCE * 2 * unitmm
        obj.yBinUnit = obj.GridSize - const.CLEARANCE * 2 * unitmm

        obj.aTotalDimension = obj.aGridUnits * obj.GridSize - obj.Clearance * 2
        obj.bTotalDimension = obj.bGridUnits * obj.GridSize - obj.Clearance * 2
        obj.cTotalDimension = obj.cGridUnits * obj.GridSize - obj.Clearance * 2
        obj.dTotalDimension = obj.dGridUnits * obj.GridSize

        binlayout = [
            [False for x in range(obj.bGridUnits + obj.dGridUnits)] for y in range(obj.aGridUnits)
        ]

        for x in range(obj.aGridUnits):
            for y in range(obj.bGridUnits + obj.dGridUnits):
                if x < obj.cGridUnits:
                    binlayout[x][y] = True
                if y < obj.bGridUnits:
                    binlayout[x][y] = True

        fusetotal = make_complex_bin_base(obj, binlayout)

        midsection = make_l_mid_section(obj)

        fusetotal = fusetotal.fuse(midsection)

        if obj.StackingLip:
            stacking_lip = make_complex_stacking_lip(obj)
            fusetotal = Part.Shape.fuse(stacking_lip, fusetotal)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = make_complex_bottom_holes(obj, binlayout)
            fusetotal = Part.Shape.cut(fusetotal, holes)

        return fusetotal
