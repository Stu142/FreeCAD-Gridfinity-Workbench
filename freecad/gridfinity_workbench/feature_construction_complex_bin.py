"""Featrues for constructing a complex bin."""

import math
from dataclasses import dataclass

import FreeCAD
import Part
from FreeCAD import Units

from .feature_construction import make_bottom_hole_shape
from .utils import Utils

from abc import abstractmethod
from enum import Enum

from .const import (
    RECESSED_TOP_DEPTH,
    HEIGHT_UNIT_VALUE,
    HEIGHT_UNITS,
    MAGNET_HOLES,
    MAGNET_HOLE_DIAMETER,
    MAGNET_HOLE_DEPTH,
    SCREW_HOLES,
    SCREW_HOLE_DIAMETER,
    SCREW_HOLE_DEPTH,
    MAGNET_HOLE_DISTANCE_FROM_EDGE,
    SEQUENTIAL_BRIDGING_LAYER_HEIGHT,
    STACKING_LIP,
    STACKING_LIP_TOP_LEDGE,
    STACKING_LIP_BOTTOM_CHAMFER,
    STACKING_LIP_VERTICAL_SECTION,
    WALL_THICKNESS,
    BIN_BASE_BOTTOM_CHAMFER,
    BIN_BASE_VERTICAL_SECTION,
    BIN_BASE_TOP_CHAMFER,
    BIN_OUTER_RADIUS,
    BIN_BASE_VERTICAL_RADIUS,
    BIN_BASE_BOTTOM_RADIUS,
    CLEARANCE,
)

HOLE_SHAPES = ["Round", "Hex"]

unitmm = Units.Quantity("1 mm")
zeromm = Units.Quantity("0 mm")

GridfinityLayout = list[list[bool]]



class Feature:
    @abstractmethod
    def Make(obj):
        raise NotImplementedError()

@dataclass
class LShapeData:
    """Data class containing information regarding a L shape.

    L shape side names:
      c
    ┌───┐
    │   │d
    │   └──────┐
    │          │b
    └──────────┘
         a
    """

    a: float
    b: float
    c: float
    d: float


def create_rounded_l(
    shape_data: LShapeData,
    xoffset: float,
    yoffset: float,
    radius: float,
) -> Part.Wire:
    """Create rounded L shaped wire.

    Args:
        shape_data (LShapeData): Size data for the L shape.
        xoffset (float): Offest in the X direction
        yoffset (float): Offset in the Y direction
        radius (float): Radius of the corners.

    Returns:
        Part.Wire: L shaped wire.

    """
    # Starting with bottom rigth corner vertex going around L shape clockwise

    l1x = xoffset
    l1y1 = yoffset + radius
    l1y2 = yoffset + shape_data.b + shape_data.d - radius
    arc1x = xoffset + radius - radius * math.sin(math.pi / 4)
    arc1y = yoffset + shape_data.b + shape_data.d - radius + radius * math.sin(math.pi / 4)

    l2x1 = xoffset + radius
    l2x2 = xoffset + shape_data.c - radius
    l2y = yoffset + shape_data.b + shape_data.d
    arc2x = xoffset + shape_data.c - radius + radius * math.sin(math.pi / 4)
    arc2y = arc1y

    l3x = xoffset + shape_data.c
    l3y1 = l1y2
    l3y2 = yoffset + shape_data.b + radius
    arc3x = xoffset + shape_data.c + radius - radius * math.sin(math.pi / 4)
    arc3y = xoffset + shape_data.b + radius - radius * math.sin(math.pi / 4)

    l4x1 = xoffset + shape_data.c + radius
    l4x2 = xoffset + shape_data.a - radius
    l4y = yoffset + shape_data.b
    arc4x = xoffset + shape_data.a - radius + radius * math.sin(math.pi / 4)
    arc4y = yoffset + shape_data.b - radius + radius * math.sin(math.pi / 4)

    l5x = xoffset + shape_data.a
    lsy1 = yoffset + shape_data.b - radius
    l5y2 = l1y1
    arc5x = arc4x
    arc5y = yoffset + radius - radius * math.sin(math.pi / 4)

    l6y = yoffset
    l6x1 = l4x2
    l6x2 = l2x1
    arc6x = arc1x
    arc6y = yoffset + radius - radius * math.sin(math.pi / 4)

    l1v1 = FreeCAD.Vector(l1x, l1y1, 0)
    l1v2 = FreeCAD.Vector(l1x, l1y2, 0)
    arc1v = FreeCAD.Vector(arc1x, arc1y, 0)
    l2v1 = FreeCAD.Vector(l2x1, l2y, 0)
    l2v2 = FreeCAD.Vector(l2x2, l2y, 0)
    arc2v = FreeCAD.Vector(arc2x, arc2y, 0)
    l3v1 = FreeCAD.Vector(l3x, l3y1, 0)
    l3v2 = FreeCAD.Vector(l3x, l3y2, 0)
    arc3v = FreeCAD.Vector(arc3x, arc3y, 0)
    l4v1 = FreeCAD.Vector(l4x1, l4y, 0)
    l4v2 = FreeCAD.Vector(l4x2, l4y, 0)
    arc4v = FreeCAD.Vector(arc4x, arc4y, 0)
    l5v1 = FreeCAD.Vector(l5x, lsy1, 0)
    l5v2 = FreeCAD.Vector(l5x, l5y2, 0)
    arc5v = FreeCAD.Vector(arc5x, arc5y, 0)
    l6v1 = FreeCAD.Vector(l6x1, l6y, 0)
    l6v2 = FreeCAD.Vector(l6x2, l6y, 0)
    arc6v = FreeCAD.Vector(arc6x, arc6y, 0)

    lines = [
        Part.LineSegment(l1v1, l1v2),
        Part.Arc(l1v2, arc1v, l2v1),
        Part.LineSegment(l2v1, l2v2),
        Part.Arc(l2v2, arc2v, l3v1),
        Part.LineSegment(l3v1, l3v2),
        Part.Arc(l3v2, arc3v, l4v1),
        Part.LineSegment(l4v1, l4v2),
        Part.Arc(l4v2, arc4v, l5v1),
        Part.LineSegment(l5v1, l5v2),
        Part.Arc(l5v2, arc5v, l6v1),
        Part.LineSegment(l6v1, l6v2),
        Part.Arc(l6v2, arc6v, l1v1),
    ]

    return Utils.curve_to_wire(lines)


def rounded_l_extrude(
    shape_data: LShapeData,
    xoffset: float,
    yoffset: float,
    radius: float,
    height: float,
) -> Part.Wire:
    """Create rounded L shaped Shape.

    Args:
        shape_data (LShapeData): Size data for the L shape.
        xoffset (float): Offest in the X direction
        yoffset (float): Offset in the Y direction
        radius (float): Radius of the corners.
        height (float): Shape height.

    Returns:
        Part.Wire: L shaped Shape.

    """
    w1 = create_rounded_l(shape_data, xoffset, yoffset, radius)
    face = Part.Face(w1)
    return face.extrude(FreeCAD.Vector(0, 0, height))

class BinBaseValues(Feature):
    """Add bin base properties and calculate values"""

    def __init__(self, obj:FreeCAD.DocumentObject):
        """Create BinBaseValues.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        """
        ## Reference Parameters
        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileHeight",
            "ReferenceParameters",
            "Height of the Gridfinity Base Profile",
            1,
        )

        ## Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileBottomChamfer",
            "zzExpertOnly",
            "height of chamfer in bottom of bin base profile <br> <br> default = 0.8 mm",
            1,
        ).BaseProfileBottomChamfer = BIN_BASE_BOTTOM_CHAMFER

        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileVerticalSection",
            "zzExpertOnly",
            "Height of the vertical section in bin base profile",
            1,
        ).BaseProfileVerticalSection = BIN_BASE_VERTICAL_SECTION

        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileTopChamfer",
            "zzExpertOnly",
            "Height of the top chamfer in the bin base profile",
            1,
        ).BaseProfileTopChamfer = BIN_BASE_TOP_CHAMFER

        obj.addProperty(
            "App::PropertyLength",
            "BinOuterRadius",
            "zzExpertOnly",
            "Outer radius of the bin",
            1,
        ).BinOuterRadius = BIN_OUTER_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "BinVerticalRadius",
            "zzExpertOnly",
            "Radius of the base profile Vertical section",
            1,
        ).BinVerticalRadius = BIN_BASE_VERTICAL_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "BinBottomRadius",
            "zzExpertOnly",
            "bottom of bin corner radius",
            1,
        ).BinBottomRadius = BIN_BASE_BOTTOM_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "Clearance",
            "zzExpertOnly",
            (
                "The tolerance on each side of a bin between before the edge of the grid <br> <br>"
                "default = 0.25 mm"
            ),
        ).Clearance = CLEARANCE

    def Make(self, obj:FreeCAD.DocumentObject) -> None:
        """Generate Rectanble layout and calculate relevant parameters.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )

        return


def make_complex_bin_base(
    obj: FreeCAD.DocumentObject,
    layout: GridfinityLayout,
) -> Part.Shape:
    """Creaet complex shaped bin base.

    Args:
        obj (FreeCAD.DocumentObject): Document object.mro
        layout (GridfinityLayout): 2 dimentional list of feature locations.

    Returns:
        Part.Shape: Complex bin base shape.

    """
    if obj.Baseplate:
        baseplate_size_adjustment = obj.BaseplateTopLedgeWidth - obj.Clearance
    else:
        baseplate_size_adjustment = 0 * unitmm

    x_bt_cmf_width = (obj.xGridSize - obj.Clearance * 2) - 2 * obj.BaseProfileBottomChamfer - 2 * obj.BaseProfileTopChamfer - 2 * baseplate_size_adjustment
    y_bt_cmf_width = (obj.yGridSize - obj.Clearance * 2) - 2 * obj.BaseProfileBottomChamfer - 2 * obj.BaseProfileTopChamfer - 2 * baseplate_size_adjustment
    x_vert_width = (obj.xGridSize - obj.Clearance * 2) - 2 * obj.BaseProfileTopChamfer - 2 * baseplate_size_adjustment
    y_vert_width = (obj.yGridSize - obj.Clearance * 2) - 2 * obj.BaseProfileTopChamfer - 2 * baseplate_size_adjustment
    xtranslate = zeromm
    ytranslate = zeromm

    bottom_chamfer = Utils.rounded_rectangle_chamfer(
        x_bt_cmf_width,
        y_bt_cmf_width,
        -obj.TotalHeight,
        obj.BaseProfileBottomChamfer,
        obj.BinBottomRadius,
    )

    vertical_section = Utils.rounded_rectangle_extrude(
        x_vert_width,
        y_vert_width,
        -obj.TotalHeight + obj.BaseProfileBottomChamfer,
        obj.BaseProfileVerticalSection,
        obj.BinVerticalRadius,
    )
    assembly = Part.Shape.fuse(bottom_chamfer, vertical_section)

    top_chamfer = Utils.rounded_rectangle_chamfer(
        x_vert_width,
        y_vert_width,
        -obj.TotalHeight + obj.BaseProfileBottomChamfer + obj.BaseProfileVerticalSection,
        obj.BaseProfileTopChamfer,
        obj.BinVerticalRadius,
    )

    assembly = Part.Solid.multiFuse(bottom_chamfer, [vertical_section, top_chamfer])

    parts = []

    for x in range(obj.xMaxGrids):
        ytranslate = zeromm
        for y in range(obj.yMaxGrids):
            if layout[x][y]:
                b = assembly.copy()
                b.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

            if x == 0 and y == 0:
                b1 = b
            else:
                parts.append(b)

            ytranslate += obj.yGridSize

        xtranslate += obj.xGridSize

    func_fuse = b1 if obj.xMaxGrids < 2 and obj.yMaxGrids < 2 else Part.Solid.multiFuse(b1, parts)

    func_fuse.translate(
        FreeCAD.Vector(obj.xGridSize / 2, obj.yGridSize / 2, 0),
    )

    return func_fuse

class BinSolidMidSection(Feature):
    """Generate bin mid section and add relevant properties"""

    def __init__(self, obj:FreeCAD.DocumentObject, default_height_units = HEIGHT_UNITS, default_wall_thickness = WALL_THICKNESS):
        """Create bin solid mid section.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        """

        ## Gridfinity Standard Parameters
        obj.addProperty(
            "App::PropertyInteger",
            "HeightUnits",
            "Gridfinity",
            "Height of the bin in units, each is 7 mm",
        ).HeightUnits = default_height_units

        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "CustomHeight",
            "GridfinityNonStandard",
            "total height of the bin using the custom height instead of increments of 7 mm",
        ).CustomHeight = 42

        obj.addProperty(
            "App::PropertyBool",
            "NonStandardHeight",
            "GridfinityNonStandard",
            "use a custom height if selected",
        ).NonStandardHeight = False

        obj.addProperty(
            "App::PropertyLength",
            "WallThickness",
            "GridfinityNonStandard",
            "for stacking lip",
        ).WallThickness = default_wall_thickness

        ## Reference Parameters
        obj.addProperty(
            "App::PropertyLength",
            "TotalHeight",
            "ReferenceParameters",
            "total height of the bin",
            1,
        )
        ## Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "HeightUnitValue",
            "zzExpertOnly",
            "height per unit, default is 7mm",
            1,
        ).HeightUnitValue = HEIGHT_UNIT_VALUE

    def Make(self, obj:FreeCAD.DocumentObject, bin_outside_shape) -> Part.Shape:
        """Generate bin solid mid section.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            Part.Wire (bin_shape): shape of the bin

        Returns:
            Part.Shape: Extruded bin mid section of the input shape

        """
        ## Calculated Values
        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight

        else:
            obj.TotalHeight = obj.HeightUnits * obj.HeightUnitValue

        ## Bin Solid Mid Section Generation
        face = Part.Face(bin_outside_shape)

        return face.extrude(FreeCAD.Vector(0, 0, -obj.TotalHeight + obj.BaseProfileHeight))

class BlankBinRecessedTop(Feature):
    """Cut into blank bin to create recessed bin top"""

    def __init__(self, obj:FreeCAD.DocumentObject):
        """Create blank bin recessed top section.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        """
        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "RecessedTopDepth",
            "GridfinityNonStandard",
            "height per unit <br> <br> default = 0 mm",
        ).RecessedTopDepth = RECESSED_TOP_DEPTH

    def Make(self, obj:FreeCAD.DocumentObject, bin_inside_shape) -> Part.Shape:
        """Generate Rectanble layout and calculate relevant parameters.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            Part.Wire (bin_inside_shape: shape of the bin inside the walls

        Returns:
            Part.Shape: Extruded part to cut out inside of bin.

        """
        face = Part.Face(bin_inside_shape)

        return face.extrude(FreeCAD.Vector(0, 0, -obj.RecessedTopDepth))


def make_l_mid_section(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create mid section of L shaped bin.

    Args:
        obj (FreeCAD.DocumentObject): DocumentObject.

    Returns:
        Part.Shape: L shaped mid section.

    """
    return rounded_l_extrude(
        LShapeData(
            obj.aTotalDimension,
            obj.bTotalDimension,
            obj.cTotalDimension,
            obj.dTotalDimension,
        ),
        obj.Clearance,
        obj.Clearance,
        obj.BinOuterRadius,
        -obj.TotalHeight + obj.BaseProfileHeight,
    )

class BinBottomHoles(Feature):
    """Cut into blank bin to create recessed bin top"""

    def __init__(self, obj:FreeCAD.DocumentObject):
        """Create bin solid mid section.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        """
        ## Gridfinity Parameters
        obj.addProperty(
            "App::PropertyBool",
            "MagnetHoles",
            "Gridfinity",
            "Toggle the magnet holes on or off",
        ).MagnetHoles = MAGNET_HOLES

        obj.addProperty(
            "App::PropertyBool",
            "ScrewHoles",
            "Gridfinity",
            "Toggle the screw holes on or off",
        ).ScrewHoles = SCREW_HOLES

        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "SequentialBridgingLayerHeight",
            "GridfinityNonStandard",
            "Layer Height that you print in for optimal print results",
        ).SequentialBridgingLayerHeight = SEQUENTIAL_BRIDGING_LAYER_HEIGHT

        obj.addProperty(
            "App::PropertyEnumeration",
            "MagnetHolesShape",
            "GridfinityNonStandard",
            (
                "Shape of magnet holes. <br> <br> Hex meant to be press fit. <br> Round meant to be"
                "glued"
            ),
        )
        obj.MagnetHolesShape = HOLE_SHAPES

        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDiameter",
            "GridfinityNonStandard",
            (
                "Diameter of Magnet Holes <br>For Hex holes, inscribed diameter<br> <br>"
                "default = 6.5 mm"
            ),
        ).MagnetHoleDiameter = MAGNET_HOLE_DIAMETER

        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDepth",
            "GridfinityNonStandard",
            "Depth of Magnet Holes <br> <br> default = 2.4 mm",
        ).MagnetHoleDepth = MAGNET_HOLE_DEPTH

        obj.addProperty(
            "App::PropertyLength",
            "ScrewHoleDiameter",
            "GridfinityNonStandard",
            "Diameter of Screw Holes <br> <br> default = 3.0 mm",
        ).ScrewHoleDiameter = SCREW_HOLE_DIAMETER

        obj.addProperty(
            "App::PropertyLength",
            "ScrewHoleDepth",
            "GridfinityNonStandard",
            "Depth of Screw Holes <br> <br> default = 6.0 mm",
        ).ScrewHoleDepth = SCREW_HOLE_DEPTH

        ## Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDistanceFromEdge",
            "zzExpertOnly",
            "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",
            1,
        ).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE

    def Make(
        obj: FreeCAD.DocumentObject,
        layout: GridfinityLayout,
    ) -> Part.Shape:
        """Make bin bottom holes.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject
            layout (GridfinityLayout): Layout of the gridfinity grid.

        Returns:
            Part.Shape: Shape containing negatives of all holes.

        """

        bottom_hole_shape = make_bottom_hole_shape(obj)

        x_hole_pos = obj.xGridSize / 2 - obj.MagnetHoleDistanceFromEdge
        y_hole_pos = obj.yGridSize / 2 - obj.MagnetHoleDistanceFromEdge

        hole_shape_sub_array = Utils.copy_and_translate(
            bottom_hole_shape,
            [
                FreeCAD.Vector(-x_hole_pos, -y_hole_pos, -obj.TotalHeight),
                FreeCAD.Vector(x_hole_pos, -y_hole_pos, -obj.TotalHeight),
                FreeCAD.Vector(-x_hole_pos, y_hole_pos, -obj.TotalHeight),
                FreeCAD.Vector(x_hole_pos, y_hole_pos, -obj.TotalHeight),
            ],
        )
        vec_list = []
        xtranslate = 0
        for x in range(obj.xMaxGrids):
            ytranslate = 0
            for y in range(obj.yMaxGrids):
                if layout[x][y]:
                    vec_list.append(FreeCAD.Vector(xtranslate, ytranslate, 0))
                ytranslate += obj.yGridSize.Value
            xtranslate += obj.xGridSize.Value

        return Utils.copy_and_translate(hole_shape_sub_array, vec_list).translate(
            FreeCAD.Vector(obj.xGridSize / 2, obj.yGridSize / 2, 0),
        )

class StackingLip(Feature):
    """Cut into blank bin to create recessed bin top"""

    def __init__(self, obj:FreeCAD.DocumentObject, stacking_lip_default = STACKING_LIP):
        """Create bin solid mid section.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        """
        ## Gridfinity Parameters
        obj.addProperty(
            "App::PropertyBool",
            "StackingLip",
            "Gridfinity",
            "Toggle the stacking lip on or off",
        ).StackingLip = stacking_lip_default

        ## Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "StackingLipTopLedge",
            "zzExpertOnly",
            "Top Ledge of the stacking lip <br> <br> default = 0.4 mm",
            1,
        ).StackingLipTopLedge = STACKING_LIP_TOP_LEDGE

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
        ).StackingLipBottomChamfer = STACKING_LIP_BOTTOM_CHAMFER

        obj.addProperty(
            "App::PropertyLength",
            "StackingLipVerticalSection",
            "zzExpertOnly",
            "vertical section of the Stacking lip<br> <br> default = 1.8 mm",
            1,
        ).StackingLipVerticalSection = STACKING_LIP_VERTICAL_SECTION


    def Make(obj: FreeCAD.DocumentObject, bin_outside_shape) -> Part.Shape:
        """Create stacking lip based on input bin shape.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject
            bin_outside_shape (Part.Wire): exterior wall of the bin

        Returns:
            Part.Shape: Stacking lip shape.

        """
        ## Calculated Values
        obj.StackingLipTopChamfer = (
            obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
        )

        ## Stacking Lip Generation
        st1 = FreeCAD.Vector(obj.Clearance, obj.yGridSize / 2, 0)
        st2 = FreeCAD.Vector(
            obj.Clearance,
            obj.yGridSize / 2,
            obj.StackingLipBottomChamfer + obj.StackingLipVerticalSection + obj.StackingLipTopChamfer,
        )
        st3 = FreeCAD.Vector(
            obj.Clearance + obj.StackingLipTopLedge,
            obj.yGridSize / 2,
            obj.StackingLipBottomChamfer + obj.StackingLipVerticalSection + obj.StackingLipTopChamfer,
        )
        st4 = FreeCAD.Vector(
            obj.Clearance + obj.StackingLipTopLedge + obj.StackingLipTopChamfer,
            obj.yGridSize / 2,
            obj.StackingLipBottomChamfer + obj.StackingLipVerticalSection,
        )
        st5 = FreeCAD.Vector(
            obj.Clearance + obj.StackingLipTopLedge + obj.StackingLipTopChamfer,
            obj.yGridSize / 2,
            obj.StackingLipBottomChamfer,
        )
        st6 = FreeCAD.Vector(
            obj.Clearance
            + obj.StackingLipTopLedge
            + obj.StackingLipTopChamfer
            + obj.StackingLipBottomChamfer,
            obj.yGridSize / 2,
            0,
        )
        st7 = FreeCAD.Vector(
            obj.Clearance
            + obj.StackingLipTopLedge
            + obj.StackingLipTopChamfer
            + obj.StackingLipBottomChamfer,
            obj.yGridSize / 2,
            -obj.StackingLipVerticalSection,
        )
        st8 = FreeCAD.Vector(
            obj.Clearance + obj.WallThickness,
            obj.yGridSize / 2,
            -obj.StackingLipVerticalSection
            - (
                obj.StackingLipTopLedge
                + obj.StackingLipTopChamfer
                + obj.StackingLipBottomChamfer
                - obj.WallThickness
            ),
        )
        st9 = FreeCAD.Vector(obj.Clearance + obj.WallThickness, obj.yGridSize / 2, 0)

        stl1 = Part.LineSegment(st1, st2)
        stl2 = Part.LineSegment(st2, st3)
        stl3 = Part.LineSegment(st3, st4)
        stl4 = Part.LineSegment(st4, st5)
        stl5 = Part.LineSegment(st5, st6)
        stl6 = Part.LineSegment(st6, st7)
        stl7 = Part.LineSegment(st7, st8)
        stl8 = Part.LineSegment(st8, st9)
        stl9 = Part.LineSegment(st9, st1)

        sts1 = Part.Shape([stl1, stl2, stl3, stl4, stl5, stl6, stl7, stl8, stl9])

        wire = Part.Wire(sts1.Edges)

        stacking_lip = Part.Wire(bin_outside_shape).makePipe(wire)

        return Part.makeSolid(stacking_lip)
