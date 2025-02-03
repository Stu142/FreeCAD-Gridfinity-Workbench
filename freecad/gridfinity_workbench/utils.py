"""Module containig various utility functions.

The utility functions can be used throughout the Gridfinity
workbench code.
"""

import math

import Part

import FreeCAD


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
    """Make a wire from cuvers (line,linesegment,arc,ect).

    This function accepts all curves and makes it into a wire. Note that the wire should be
    closed.

    Args:
        list_of_items (list[Part.LineSegment]): List of items to convert in a wire.

    Returns:
        Part.Wire: The created wire

    """
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
