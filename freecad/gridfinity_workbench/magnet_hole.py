"""A module for making magnet holes."""

from __future__ import annotations

import math

import FreeCAD as fc  # noqa: N813
import Part

from . import utils

unitmm = fc.Units.Quantity("1 mm")


def _crush_ribs(radius: fc.Units.Quantity, *, n: int, beta: float) -> tuple[Part.Face, float]:
    """Make crush ribs inner face.

    Args:
        radius (fc.Units.Quantity): Inner radius.
        n (int): Number of ribs.
        beta (float): Waviness of the ribs. It is the angle at wich inner at outer arcs meet.
        A value of 0 would result in a perfect circle.

    """
    alpha = math.pi / n / 2

    def get_midpoint(beta: float) -> float:
        return (math.sin(beta) - math.sin(alpha)) / math.sin(beta - alpha)

    r1 = radius.Value
    r2 = radius.Value / get_midpoint(beta)
    r3 = r2 * get_midpoint(-beta)

    p1 = fc.Vector(r2, 0)
    p2 = fc.Vector(r2 * math.cos(2 * alpha), r2 * math.sin(2 * alpha))
    q = r1 * fc.Vector(math.cos(alpha), math.sin(alpha))
    r = r3 * fc.Vector(math.cos(alpha), math.sin(alpha))

    lines = []
    for _ in range(n):
        lines.append(Part.Arc(p1, q, p2))
        lines.append(Part.Arc(p1, r, p2))
    for i, arc in enumerate(lines):
        placement = fc.Placement(
            fc.Vector(0, 0, 0),
            fc.Vector(0, 0, 1),
            math.degrees((i + 0.5) / len(lines) * 2 * math.pi),
        )
        arc.rotate(placement)
    return utils.curve_to_face(lines), r3 - r1


def _hex_shape(radius: fc.Units.Quantity) -> Part.Shape:
    # Ratio of 2/sqrt(3) converts from inscribed circle radius to circumscribed
    # circle radius
    radius = 2 * radius / math.sqrt(3)

    p = fc.ActiveDocument.addObject("Part::RegularPolygon")
    p.Polygon = 6
    p.Circumradius = radius
    p.recompute()

    p_wire: Part.Wire = p.Shape
    shape = Part.Face(p_wire)
    fc.ActiveDocument.removeObject(p.Name)
    return shape


def from_obj(obj: fc.DocumentObject) -> Part.Shape:
    """Create a single magnet hole from object properties."""
    if not obj.MagnetHoles:
        raise ValueError("Object doesn't have magnet holes enables")

    hole_shape = obj.MagnetHolesShape
    radius = obj.MagnetHoleDiameter / 2
    depth = obj.MagnetHoleDepth
    chamfer_depth = depth / 8

    if hole_shape == "Hex":
        shape = _hex_shape(radius)
        chamfer_width = (2 / math.sqrt(3) - 1) * radius
    elif hole_shape == "Crush ribs":
        shape, ch = _crush_ribs(radius, n=8, beta=0.5 * math.pi / 2)
        chamfer_width = ch * unitmm
    elif hole_shape == "Round":
        shape = Part.Face(Part.Wire(Part.makeCircle(radius)))
        chamfer_width = chamfer_depth
    else:
        raise ValueError(f"Unrecognised magnet hole shape {hole_shape:!r}")

    shape = shape.extrude(fc.Vector(0, 0, depth))

    if obj.Baseplate:
        chamfer_shape = utils.round_chamfer(
            radius,
            radius + chamfer_width,
            chamfer_depth,
            pPnt=fc.Vector(0, 0, depth - chamfer_depth),
        )
        shape = shape.fuse(chamfer_shape)

    return shape


def relief(obj: fc.DocumentObject) -> Part.Shape:
    """Create a magnet relief shape for four magnets from object properties."""
    x_hole_pos = obj.xGridSize / 2 - obj.MagnetHoleDistanceFromEdge
    y_hole_pos = obj.yGridSize / 2 - obj.MagnetHoleDistanceFromEdge
    alpha = math.pi / 8

    r = obj.MagnetHoleDiameter / 2
    x1 = r * math.cos(alpha)
    y1 = r * math.sin(alpha)
    p1 = fc.Vector(x1, y1)
    p2 = fc.Vector(x1 + 2 * y1, y1)
    p3 = fc.Vector(x1 + 3 * y1, 0)
    p4 = fc.Vector(x1 + 2 * y1, -y1)
    p5 = fc.Vector(x1, -y1)
    lines = [
        Part.LineSegment(p1, p2),
        Part.Arc(p2, p3, p4),
        Part.LineSegment(p4, p5),
        Part.LineSegment(p5, p1),
    ]
    face = utils.curve_to_face(lines)
    shape = face.extrude(fc.Vector(0, 0, obj.MagnetHoleDepth))

    positions = [
        (45, -x_hole_pos, -y_hole_pos),
        (135, x_hole_pos, -y_hole_pos),
        (225, x_hole_pos, y_hole_pos),
        (315, -x_hole_pos, y_hole_pos),
    ]
    return utils.multi_fuse(
        [
            shape.rotated(fc.Vector(0, 0, 0), fc.Vector(0, 0, 1), angle).translate(fc.Vector(x, y))
            for angle, x, y in positions
        ],
    )
