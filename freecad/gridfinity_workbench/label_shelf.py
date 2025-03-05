"""A module for making label shelves."""

import math

import FreeCAD as fc  # noqa: N813
import Part

from . import utils

unitmm = fc.Units.Quantity("1 mm")


def _corner_fillet(radius: float) -> Part.Face:
    arc = radius - radius * math.sin(math.pi / 4)

    v1 = fc.Vector(0, 0)
    v2 = fc.Vector(0, radius)
    v_arc = fc.Vector(arc, arc)
    v3 = fc.Vector(radius, 0)

    lines = [
        Part.LineSegment(v1, v2),
        Part.Arc(v2, v_arc, v3),
        Part.LineSegment(v3, v1),
    ]

    return Part.Face(utils.curve_to_wire(lines))


def outside_fillet(
    shape: Part.Shape,
    *,
    offset: float,
    radius: float,
    height: float,
    y_width: float,
) -> Part.Shape:
    """Fillets a label shelves corners that stick out from bins corners."""
    right_fillet = _corner_fillet(radius)
    right_fillet.rotate(fc.Vector(0, 0, 0), fc.Vector(0, 0, 1), -90)
    right_fillet.translate(fc.Vector(offset, y_width))
    right_fillet = right_fillet.extrude(fc.Vector(0, 0, -height))
    shape = shape.cut(right_fillet)

    left_fillet = _corner_fillet(radius)
    left_fillet.translate(fc.Vector(offset, offset))
    left_fillet = left_fillet.extrude(fc.Vector(0, 0, -height))
    shape = shape.cut(left_fillet)

    return shape


def from_dimensions(
    *,
    length: fc.Units.Quantity,
    width: fc.Units.Quantity,
    thickness: fc.Units.Quantity,
    height: fc.Units.Quantity,
    center: bool = False,
) -> Part.Shape:
    """Create a label shelf with given dimensions.

    Args:
        length: Total length of the shelf.
        width: Total width of the shelf.
        thickness: Height of the front of the shelf.
        height: Height of the back of the shelf.
        center: If the origin should be placed in the center of top-back edge, or on its left end.

    """
    yoffset: fc.Units.Quantity = -length / 2 if center else 0 * unitmm
    v = [
        fc.Vector(0, yoffset, 0),
        fc.Vector(width, yoffset, 0),
        fc.Vector(width, yoffset, -thickness),
        fc.Vector(0, yoffset, -height),
    ]

    face = Part.Face(utils.curve_to_wire(utils.loop(v)))
    shape = face.extrude(fc.Vector(0, length))

    # Front fillet
    def fillet_point(p: Part.Vertex) -> bool:
        return p.Z == -thickness and p.X == width

    h_edges = [
        edge
        for edge in shape.Edges
        if fillet_point(edge.Vertexes[0]) and fillet_point(edge.Vertexes[1])
    ]
    assert len(h_edges) == 1
    shape = shape.makeFillet(thickness.Value - 0.01, h_edges)

    return shape


def from_angle(
    *,
    length: fc.Units.Quantity,
    width: fc.Units.Quantity,
    thickness: fc.Units.Quantity,
    angle: fc.Units.Quantity,
    center: bool = False,
) -> Part.Shape:
    """Create a label shelf with given width and angle.

    Args:
        length: Total length of the shelf.
        width: Total width of the shelf.
        thickness: Height of the front of the shelf.
        angle: Angle of the shelf.
        center: If the origin should be placed in the center of top-back edge, or on its left end.

    """
    return from_dimensions(
        length=length,
        width=width,
        thickness=thickness,
        height=thickness + math.tan(angle.Value) * width.Value,
        center=center,
    )
