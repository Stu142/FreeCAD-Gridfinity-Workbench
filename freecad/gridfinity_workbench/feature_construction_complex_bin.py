"""Featrues for constructing a complex bin."""

import math
from dataclasses import dataclass

import FreeCAD
import Part
from FreeCAD import Units

from . import utils
from .feature_construction import make_bottom_hole_shape

unitmm = Units.Quantity("1 mm")
zeromm = Units.Quantity("0 mm")

GridfinityLayout = list[list[bool]]


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

    return utils.curve_to_wire(lines)


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


def make_complex_bin_base(
    obj: FreeCAD.DocumentObject,
    binlayout: GridfinityLayout,
) -> Part.Shape:
    """Creaet complex shaped bin base.

    Args:
        obj (FreeCAD.DocumentObject): Document object.mro
        binlayout (GridfinityLayout): 2 dimentional list of bin locations.

    Returns:
        Part.Shape: Complex bin base shape.

    """
    xmaxgrids = obj.aGridUnits
    ymaxgrids = obj.bGridUnits + obj.dGridUnits

    x_bt_cmf_width = obj.xBinUnit - 2 * obj.BaseProfileBottomChamfer - 2 * obj.BaseProfileTopChamfer
    y_bt_cmf_width = obj.yBinUnit - 2 * obj.BaseProfileBottomChamfer - 2 * obj.BaseProfileTopChamfer
    x_vert_width = obj.xBinUnit - 2 * obj.BaseProfileTopChamfer
    y_vert_width = obj.yBinUnit - 2 * obj.BaseProfileTopChamfer
    xtranslate = zeromm
    ytranslate = zeromm

    bottom_chamfer = utils.rounded_rectangle_chamfer(
        x_bt_cmf_width,
        y_bt_cmf_width,
        -obj.TotalHeight,
        obj.BaseProfileBottomChamfer,
        obj.BinBottomRadius,
    )

    vertical_section = utils.rounded_rectangle_extrude(
        x_vert_width,
        y_vert_width,
        -obj.TotalHeight + obj.BaseProfileBottomChamfer,
        obj.BaseProfileVerticalSection,
        obj.BinVerticalRadius,
    )
    assembly = Part.Shape.fuse(bottom_chamfer, vertical_section)

    top_chamfer = utils.rounded_rectangle_chamfer(
        x_vert_width,
        y_vert_width,
        -obj.TotalHeight + obj.BaseProfileBottomChamfer + obj.BaseProfileVerticalSection,
        obj.BaseProfileTopChamfer,
        obj.BinVerticalRadius,
    )

    assembly = Part.Solid.multiFuse(bottom_chamfer, [vertical_section, top_chamfer])

    parts = []

    for x in range(xmaxgrids):
        ytranslate = zeromm
        for y in range(ymaxgrids):
            if binlayout[x][y]:
                b = assembly.copy()
                b.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

            if x == 0 and y == 0:
                b1 = b
            else:
                parts.append(b)

            ytranslate += obj.GridSize

        xtranslate += obj.GridSize

    func_fuse = b1 if not xmaxgrids and not ymaxgrids else Part.Solid.multiFuse(b1, parts)

    func_fuse.translate(
        FreeCAD.Vector(obj.xBinUnit / 2 + obj.Clearance, obj.yBinUnit / 2 + obj.Clearance, 0),
    )

    return func_fuse


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


def make_complex_bottom_holes(
    obj: FreeCAD.DocumentObject,
    binlayout: GridfinityLayout,
) -> Part.Shape:
    """Make comlex bottom holes.

    Args:
        obj (FreeCAD.DocumentObject): DocumentObject
        binlayout (GridfinityLayout): Layout of the gridfinity grid.

    Returns:
        Part.Shape: Shape containing negatives of all holes.

    """
    xmaxgrids = obj.aGridUnits
    ymaxgrids = obj.bGridUnits + obj.dGridUnits

    bottom_hole_shape = make_bottom_hole_shape(obj)

    hole_pos = obj.GridSize / 2 - obj.MagnetHoleDistanceFromEdge

    hole_shape_sub_array = utils.copy_and_translate(
        bottom_hole_shape,
        [
            FreeCAD.Vector(-hole_pos, -hole_pos, -obj.TotalHeight),
            FreeCAD.Vector(hole_pos, -hole_pos, -obj.TotalHeight),
            FreeCAD.Vector(-hole_pos, hole_pos, -obj.TotalHeight),
            FreeCAD.Vector(hole_pos, hole_pos, -obj.TotalHeight),
        ],
    )
    vec_list = []
    xtranslate = 0
    for x in range(xmaxgrids):
        ytranslate = 0
        for y in range(ymaxgrids):
            if binlayout[x][y]:
                vec_list.append(FreeCAD.Vector(xtranslate, ytranslate, 0))
            ytranslate += obj.GridSize.Value
        xtranslate += obj.GridSize.Value

    return utils.copy_and_translate(hole_shape_sub_array, vec_list).translate(
        FreeCAD.Vector(obj.xBinUnit / 2 + obj.Clearance, obj.yBinUnit / 2 + obj.Clearance, 0),
    )


def make_complex_stacking_lip(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create complex shaped stacking lip.

    Args:
        obj (FreeCAD.DocumentObject): DocumentObject

    Returns:
        Part.Shape: Stacking lip shape.

    """
    stacking_lip_path = create_rounded_l(
        LShapeData(
            obj.aTotalDimension,
            obj.bTotalDimension,
            obj.cTotalDimension,
            obj.dTotalDimension,
        ),
        obj.Clearance,
        obj.Clearance,
        obj.BinOuterRadius,
    )

    stacking_lip_path.translate(FreeCAD.Vector(0, 0, 20))

    st1 = FreeCAD.Vector(obj.Clearance, obj.GridSize / 2, 0)
    st2 = FreeCAD.Vector(
        obj.Clearance,
        obj.GridSize / 2,
        obj.StackingLipBottomChamfer + obj.StackingLipVerticalSection + obj.StackingLipTopChamfer,
    )
    st3 = FreeCAD.Vector(
        obj.Clearance + obj.StackingLipTopLedge,
        obj.GridSize / 2,
        obj.StackingLipBottomChamfer + obj.StackingLipVerticalSection + obj.StackingLipTopChamfer,
    )
    st4 = FreeCAD.Vector(
        obj.Clearance + obj.StackingLipTopLedge + obj.StackingLipTopChamfer,
        obj.GridSize / 2,
        obj.StackingLipBottomChamfer + obj.StackingLipVerticalSection,
    )
    st5 = FreeCAD.Vector(
        obj.Clearance + obj.StackingLipTopLedge + obj.StackingLipTopChamfer,
        obj.GridSize / 2,
        obj.StackingLipBottomChamfer,
    )
    st6 = FreeCAD.Vector(
        obj.Clearance
        + obj.StackingLipTopLedge
        + obj.StackingLipTopChamfer
        + obj.StackingLipBottomChamfer,
        obj.GridSize / 2,
        0,
    )
    st7 = FreeCAD.Vector(
        obj.Clearance
        + obj.StackingLipTopLedge
        + obj.StackingLipTopChamfer
        + obj.StackingLipBottomChamfer,
        obj.GridSize / 2,
        -obj.StackingLipVerticalSection,
    )
    st8 = FreeCAD.Vector(
        obj.Clearance + obj.WallThickness,
        obj.GridSize / 2,
        -obj.StackingLipVerticalSection
        - (
            obj.StackingLipTopLedge
            + obj.StackingLipTopChamfer
            + obj.StackingLipBottomChamfer
            - obj.WallThickness
        ),
    )
    st9 = FreeCAD.Vector(obj.Clearance + obj.WallThickness, obj.GridSize / 2, 0)

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

    stacking_lip = Part.Wire(stacking_lip_path).makePipe(wire)

    return Part.makeSolid(stacking_lip)
