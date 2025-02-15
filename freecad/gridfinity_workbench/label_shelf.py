"""A module for making label shelves."""

import math

import FreeCAD as fc  # noqa: N813
import Part

from . import utils

unitmm = fc.Units.Quantity("1 mm")


def _front_fillet(
    shape: Part.Shape,
    thickness: fc.Units.Quantity,
    tolabelend: float,
) -> Part.Shape:
    def fillet_point(p: Part.Point) -> bool:
        return p.z == -thickness and p.x == tolabelend

    h_edges = [
        edge
        for edge in shape.Edges
        if fillet_point(edge.Vertexes[0].Point) and fillet_point(edge.Vertexes[1].Point)
    ]
    assert h_edges

    return shape.makeFillet(thickness.Value - 0.01, h_edges)


def _corner_fillet(radius: float) -> Part.Face:
    arc1 = radius - radius * math.sin(math.pi / 4)

    l1v1 = fc.Vector(0, 0)
    l1v2 = fc.Vector(0, radius)
    arc1v = fc.Vector(arc1, arc1)
    l2v1 = fc.Vector(radius, 0)
    l2v2 = fc.Vector(0, 0)

    lines = [
        Part.LineSegment(l1v1, l1v2),
        Part.Arc(l1v2, arc1v, l2v1),
        Part.LineSegment(l2v1, l2v2),
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
    right_end_fillet = _corner_fillet(radius)
    right_end_fillet.rotate(fc.Vector(0, 0, 0), fc.Vector(0, 0, 1), -90)
    right_end_fillet.translate(
        fc.Vector(offset, y_width),
    )
    right_end_fillet = right_end_fillet.extrude(
        fc.Vector(0, 0, -height),
    )
    shape = shape.cut(right_end_fillet)

    left_end_fillet = _corner_fillet(radius)
    left_end_fillet.translate(fc.Vector(offset, offset))
    left_end_fillet = left_end_fillet.extrude(
        fc.Vector(0, 0, -height),
    )
    shape = shape.cut(left_end_fillet)

    return shape


def label_shelf(
    *,
    length: fc.Units.Quantity,
    width: fc.Units.Quantity,
    height: fc.Units.Quantity,
    thickness: fc.Units.Quantity,
) -> Part.Shape:
    """Create a label shelf with given dimensions.

    Args:
        length: Total length of the shelf.
        width: Total width of the shelf.
        height: Height of the back of the shelf.
        thickness: Height of the front of the shelf.

    """
    v = [
        fc.Vector(0, 0, 0),
        fc.Vector(width, 0, 0),
        fc.Vector(width, 0, -thickness),
        fc.Vector(0, 0, -height),
    ]

    face = Part.Face(utils.curve_to_wire(utils.loop(v)))
    shape = face.extrude(fc.Vector(0, length))
    shape = _front_fillet(shape, thickness, width)

    return shape
