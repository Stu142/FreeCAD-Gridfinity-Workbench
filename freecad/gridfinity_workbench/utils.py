"""Module containig various utility functions.

The utility functions can be used throughout the Gridfinity
workbench code.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import FreeCAD as fc  # noqa:N813
import FreeCADGui as fcg  # noqa: N813
import Part


if TYPE_CHECKING:
    from collections.abc import Sequence


GridfinityLayout = list[list[bool]]


unitmm = fc.Units.Quantity("1 mm")


def new_object(name: str) -> fc.DocumentObject:
    """Create a new FreeCAD object.

    The object is attached to PartDesign body or Part group, if they are present.

    """
    if not fc.GuiUp:
        return fc.ActiveDocument.addObject("Part::FeaturePython", name)

    # borrowed from threaded profiles
    body = fcg.ActiveDocument.ActiveView.getActiveObject("pdbody")
    part = fcg.ActiveDocument.ActiveView.getActiveObject("part")

    obj_type = "PartDesign::FeaturePython" if body else "Part::FeaturePython"
    obj = fc.ActiveDocument.addObject(obj_type, name)

    if body:
        body.addObject(obj)
    elif part:
        part.Group += [obj]

    return obj


def copy_and_translate(shape: Part.Shape, vec_list: list[fc.Vector]) -> Part.Shape:
    """Copy a shape and translates.

    This function copies and translate a shape by a vector for as many times as there are
    vectors in the list.

    Args:
        shape (Part.Shape): Shape to copy.
        vec_list (list[FreeCAD.Vector]): List of vectors where the copies should be translated
            to.

    Raises:
        ValueError: List is empty.

    Returns:
        Part.Shape: Shape consting of the copies in the locations specified by vec_list.

    """
    if not vec_list:
        raise ValueError("Vector list is empty")
    return multi_fuse([shape.translated(vec) for vec in vec_list])


def copy_in_layout(
    shape: Part.Shape,
    layout: GridfinityLayout,
    x_gird_size: float,
    y_grid_size: float,
) -> Part.Shape:
    """Copy a shape in a layout.

    Raises:
        ValueError: Layout is empty.

    """
    vec_list = [
        fc.Vector(x * x_gird_size, y * y_grid_size)
        for x, col in enumerate(layout)
        for y, cell in enumerate(col)
        if cell
    ]
    if not vec_list:
        raise ValueError("Layout is empty")
    return copy_and_translate(shape, vec_list)


def copy_in_grid(
    shape: Part.Shape,
    *,
    x_count: int,
    y_count: int,
    x_offset: float,
    y_offset: float,
) -> Part.Shape:
    """Copy a shape in a grid layout."""
    if x_count <= 0:
        raise ValueError("x_count should be > 0")
    if y_count <= 0:
        raise ValueError("y_count should be > 0")

    shapes = [
        shape.translated(fc.Vector(x * x_offset * unitmm, y * y_offset * unitmm))
        for x in range(x_count)
        for y in range(y_count)
    ]
    return multi_fuse(shapes)


def curve_to_wire(list_of_items: Sequence[Part.TrimmedCurve]) -> Part.Wire:
    """Make a wire from curves (line,linesegment,arc,ect).

    This function accepts all curves and makes it into a wire. Note that the wire should be
    closed.

    Args:
        list_of_items (list[Part.LineSegment]): List of items to convert in a wire.

    Returns:
        Part.Wire: The created wire.

    """
    if not list_of_items:
        raise ValueError("List is empty")

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
        raise ValueError("Radius should be > 0")
    if radius >= xwidth / 2 or radius >= ywidth / 2:
        raise ValueError("Radius should be smaller than xwidth/2 and ywidth/2")

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

    v1 = fc.Vector(-xclosev, yfarv, zsketchplane)
    v1 = fc.Vector(-xclosev, yfarv, zsketchplane)
    v2 = fc.Vector(xclosev, yfarv, zsketchplane)
    v3 = fc.Vector(xfarv, yclosev, zsketchplane)
    v4 = fc.Vector(xfarv, -yclosev, zsketchplane)
    v5 = fc.Vector(xclosev, -yfarv, zsketchplane)
    v6 = fc.Vector(-xclosev, -yfarv, zsketchplane)
    v7 = fc.Vector(-xfarv, -yclosev, zsketchplane)
    v8 = fc.Vector(-xfarv, yclosev, zsketchplane)

    vc1 = fc.Vector(-xarcv, yarcv, zsketchplane)
    c1 = Part.Arc(v1, vc1, v8)
    vc2 = fc.Vector(xarcv, yarcv, zsketchplane)
    c2 = Part.Arc(v2, vc2, v3)
    vc3 = fc.Vector(xarcv, -yarcv, zsketchplane)
    c3 = Part.Arc(v4, vc3, v5)
    vc4 = fc.Vector(-xarcv, -yarcv, zsketchplane)
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
    return Part.makeLoft([w1, w2], solid=True)


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
    return Part.Face(w1).extrude(fc.Vector(0, 0, height))


def multi_fuse(lst: list[Part.Shape]) -> Part.Shape:
    """Fuses all shapes in the list into a single shape.

    Raises `ValueError` if the list is empty. If there is only one shape on the list, returns
    a reference to that shape. Otherwise returns a new shape that is a fusion of all shapes from
    the list.
    """
    if not lst:
        raise ValueError("The list is empty")
    if len(lst) == 1:
        return lst[0]
    return lst[0].multiFuse(lst[1:])


def loop(lst: list[fc.Vector]) -> list[Part.LineSegment]:
    """Get a closed loop consisting of LineSegments from consecutive points."""
    if len(lst) < 3:  # noqa: PLR2004
        raise ValueError("List has to be of length at least 3")
    return [Part.LineSegment(p1, p2) for p1, p2 in zip(lst, lst[1:] + lst[:1])]


def corners(x: float, y: float, z: float = 0) -> list[fc.Vector]:
    """Get a list of four points located at (±x, ±y, z)."""
    return [fc.Vector(x_pos, y_pos, z) for x_pos, y_pos in ((-x, -y), (x, -y), (-x, y), (x, y))]
