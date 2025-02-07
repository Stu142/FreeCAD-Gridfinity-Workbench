"""Module containig various utility functions.

The utility functions can be used throughout the Gridfinity
workbench code.
"""

import math
from abc import abstractmethod
from dataclasses import dataclass

import FreeCAD
import Part


class Feature:
    """Gloabal feature class."""

    @abstractmethod
    def make(self, obj: FreeCAD.DocumentObject) -> None:
        """Make a Gridfinity Feature."""
        raise NotImplementedError


def copy_and_translate(shape: Part.Shape, vec_list: list[FreeCAD.Vector]) -> Part.Shape:
    """Copy a shape and translates.

    This function copies and translate a shape by a vector for as many times as there are
    vectors in the list.

    Args:
        shape (Part.Shape): Shape to copy.
        vec_list (list[FreeCAD.Vector]): List of vectors wher the copies should be translated
            to.

    Raises:
        ValueError: List is empty
        RuntimeError: Nothing copied.

    Returns:
        Part.Shape: Shape consting of the copies in the locations specified by vec_list.

    """
    if not vec_list:
        msg = "Vector list is empty"
        raise ValueError(msg)

    final_shape: Part.Shape | None = None
    for vec in vec_list:
        tmp = shape.copy()
        tmp = tmp.translate(vec)
        final_shape = tmp if final_shape is None else final_shape.fuse(tmp)

    if final_shape is None:
        msg = "Nothing has been copied"
        raise RuntimeError(msg)

    return final_shape


def curve_to_wire(list_of_items: list[Part.LineSegment]) -> Part.Wire:
    """Make a wire from curves (line,linesegment,arc,ect).

    This function accepts all curves and makes it into a wire. Note that the wire should be
    closed.

    Args:
        list_of_items (list[Part.LineSegment]): List of items to convert in a wire.

    Returns:
        Part.Wire: The created wire

    """
    if not list_of_items:
        msg = "List is empty"
        raise ValueError(msg)

    return Part.Wire([item.toShape() for item in list_of_items])


def create_rounded_rectangle(
    xwidth: float,
    ywidth: float,
    zsketchplane: float,
    radius: float,
) -> Part.Wire:
    """Create rounded rectangle.

    Args:
        xwidth (float): Width of the rectangle in X direction.
        ywidth (float): Width of the rectangle in Y direction.
        zsketchplane (float): Z heigt where the wire should be.
        radius (float): Radius of the corners.

    Returns:
        Part.Wire: Wire representing a rounded rectangle.

    """
    if radius <= 0:
        msg = "Radius should be > 0"
        raise ValueError(msg)
    if radius >= xwidth / 2 or radius >= ywidth / 2:
        msg = "Radius should be smaller than xwidth /2 or ywidth / 2"
        raise ValueError(msg)

    xfarv = xwidth / 2
    yfarv = ywidth / 2
    xclosev = xwidth / 2 - radius
    yclosev = ywidth / 2 - radius
    xarcv = xwidth / 2 - radius + radius * math.sin(math.pi / 4)
    yarcv = ywidth / 2 - radius + radius * math.sin(math.pi / 4)
    xfarv = xwidth / 2
    yfarv = ywidth / 2
    xclosev = xwidth / 2 - radius
    yclosev = ywidth / 2 - radius
    xarcv = xwidth / 2 - radius + radius * math.sin(math.pi / 4)
    yarcv = ywidth / 2 - radius + radius * math.sin(math.pi / 4)

    v1 = FreeCAD.Vector(-xclosev, yfarv, zsketchplane)
    v1 = FreeCAD.Vector(-xclosev, yfarv, zsketchplane)
    v2 = FreeCAD.Vector(xclosev, yfarv, zsketchplane)
    v3 = FreeCAD.Vector(xfarv, yclosev, zsketchplane)
    v4 = FreeCAD.Vector(xfarv, -yclosev, zsketchplane)
    v5 = FreeCAD.Vector(xclosev, -yfarv, zsketchplane)
    v6 = FreeCAD.Vector(-xclosev, -yfarv, zsketchplane)
    v7 = FreeCAD.Vector(-xfarv, -yclosev, zsketchplane)
    v8 = FreeCAD.Vector(-xfarv, yclosev, zsketchplane)

    vc1 = FreeCAD.Vector(-xarcv, yarcv, zsketchplane)
    c1 = Part.Arc(v1, vc1, v8)
    vc2 = FreeCAD.Vector(xarcv, yarcv, zsketchplane)
    c2 = Part.Arc(v2, vc2, v3)
    vc3 = FreeCAD.Vector(xarcv, -yarcv, zsketchplane)
    c3 = Part.Arc(v4, vc3, v5)
    vc4 = FreeCAD.Vector(-xarcv, -yarcv, zsketchplane)
    c4 = Part.Arc(v6, vc4, v7)

    l1 = Part.LineSegment(v1, v2)
    l2 = Part.LineSegment(v3, v4)
    l3 = Part.LineSegment(v5, v6)
    l4 = Part.LineSegment(v7, v8)

    s1 = Part.Shape([c1, l1, c2, l2, c3, l3, c4, l4])

    return Part.Wire(s1.Edges)


def rounded_rectangle_chamfer(
    xwidth: float,
    ywidth: float,
    zsketchplane: float,
    height: float,
    radius: float,
) -> Part.Shape:
    """Create rounded rectangle shpae with a chamfer.

    Args:
        xwidth (float): Width of the rectangle in X direction.
        ywidth (float): Width of the rectangle in Y direction.
        zsketchplane (float): Z heigt where the part should be.
        height (float): Height of the part
        radius (float): Radius of the corners.

    Returns:
        Part.Shape: Rounded rectangle chanfer shape.

    """
    w1 = create_rounded_rectangle(xwidth, ywidth, zsketchplane, radius)
    w2 = create_rounded_rectangle(
        xwidth + 2 * height,
        ywidth + 2 * height,
        zsketchplane + height,
        radius + height,
    )
    wires = [w1, w2]
    return Part.makeLoft(wires, solid=True)


def rounded_rectangle_extrude(
    xwidth: float,
    ywidth: float,
    zsketchplane: float,
    height: float,
    radius: float,
) -> Part.Shape:
    """Create an extruded rounded rectangle.

    Args:
        xwidth (float): Width of the rectangle in X direction.
        ywidth (float): Width of the rectangle in Y direction.
        zsketchplane (float): Z heigt where the part should be.
        height (float): Height of the part
        radius (float): Radius of the corners.

    Returns:
        Part.Shape: Rounded rectangle shape.

    """
    w1 = create_rounded_rectangle(xwidth, ywidth, zsketchplane, radius)
    face = Part.Face(w1)
    return face.extrude(FreeCAD.Vector(0, 0, height))


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

    x1: float
    y1: float
    x2: float
    y2: float


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
    l1y2 = yoffset + shape_data.y1 - radius
    arc1x = xoffset + radius - radius * math.sin(math.pi / 4)
    arc1y = yoffset + shape_data.y1 - radius + radius * math.sin(math.pi / 4)

    l2x1 = xoffset + radius
    l2x2 = xoffset + shape_data.x2 - radius
    l2y = yoffset + shape_data.y1
    arc2x = xoffset + shape_data.x2 - radius + radius * math.sin(math.pi / 4)
    arc2y = arc1y

    l3x = xoffset + shape_data.x2
    l3y1 = l1y2
    l3y2 = yoffset + shape_data.y2 + radius
    arc3x = xoffset + shape_data.x2 + radius - radius * math.sin(math.pi / 4)
    arc3y = xoffset + shape_data.y2 + radius - radius * math.sin(math.pi / 4)

    l4x1 = xoffset + shape_data.x2 + radius
    l4x2 = xoffset + shape_data.x1 - radius
    l4y = yoffset + shape_data.y2
    arc4x = xoffset + shape_data.x1 - radius + radius * math.sin(math.pi / 4)
    arc4y = yoffset + shape_data.y2 - radius + radius * math.sin(math.pi / 4)

    l5x = xoffset + shape_data.x1
    lsy1 = yoffset + shape_data.y2 - radius
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

    return curve_to_wire(lines)


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
