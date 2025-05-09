"""A module for making magnet holes."""

from __future__ import annotations

import math

import FreeCAD as fc  # noqa: N813
import Part

from . import const, utils

unitmm = fc.Units.Quantity("1 mm")


def add_properties(
    obj: fc.DocumentObject,
    *,
    relief: bool,
    chamfer: bool,
    magnet_holes_default: bool,
) -> None:
    """Add magnet holes properties to an object.

    Args:
        obj (FreeCAD.DocumentObject): Document object.
        relief (bool): Does the object support magnet relief.
        chamfer (bool): Does the object support hole chamfer.
        magnet_holes_default (bool): Should magnet holes be enabled by default.

    """
    ## Gridfinity Parameters
    obj.addProperty(
        "App::PropertyBool",
        "MagnetHoles",
        "Gridfinity",
        "Toggle the magnet holes on or off",
    ).MagnetHoles = magnet_holes_default

    ## Gridfinity Non Standard Parameters
    obj.addProperty(
        "App::PropertyLength",
        "MagnetHoleDepth",
        "GridfinityNonStandard",
        "Depth of Magnet Holes <br> <br> default = 2.4 mm",
    ).MagnetHoleDepth = const.MAGNET_HOLE_DEPTH

    obj.addProperty(
        "App::PropertyLength",
        "MagnetHoleDiameter",
        "GridfinityNonStandard",
        (
            "Diameter of Magnet Holes. Press fit by default, increase to 6.5 mm if using glue."
            "For crush ribs, 5.7mm is recommended. <br> <br> default = 6.2 mm"
        ),
    ).MagnetHoleDiameter = const.MAGNET_HOLE_DIAMETER

    obj.addProperty(
        "App::PropertyEnumeration",
        "MagnetHolesShape",
        "GridfinityNonStandard",
        (
            "Shape of magnet holes, change to suit your printers capabilities which might require"
            "testing."
            "<br> Round is press fit by default, increase to 6.5 mm if using glue."
            "<br> <br> Crush ribs are an alternative press fit style."
            "<br> <br> Hex is a legacy press fit style."
        ),
    ).MagnetHolesShape = const.HOLE_SHAPES

    if chamfer:
        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleChamfer",
            "GridfinityNonStandard",
            "The depth at which magnet hole chamfer starts.",
        ).MagnetHoleChamfer = 0.25

    if relief:
        obj.addProperty(
            "App::PropertyBool",
            "MagnetRelief",
            "GridfinityNonStandard",
            "Toggle the magnet relief on or off",
        ).MagnetRelief = False

    obj.addProperty(
        "App::PropertyInteger",
        "CrushRibsCount",
        "GridfinityNonStandard",
        "Number of crush ribs <br><br> default = 12",
    ).CrushRibsCount = const.CRUSH_RIB_N

    obj.addProperty(
        "App::PropertyFloatConstraint",
        "CrushRibsWaviness",
        "GridfinityNonStandard",
        "Waviness of crush ribs, from range [0, 1]",
    ).CrushRibsWaviness = (const.CRUSH_RIB_WAVINESS, 0, 1, 0.05)

    ## Expert Only Parameters
    obj.addProperty(
        "App::PropertyLength",
        "MagnetHoleDistanceFromEdge",
        "zzExpertOnly",
        "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",
        read_only=True,
    ).MagnetHoleDistanceFromEdge = const.MAGNET_HOLE_DISTANCE_FROM_EDGE


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
    chamfer_depth = obj.MagnetHoleChamfer if hasattr(obj, "MagnetHoleChamfer") else None

    if hole_shape == "Hex":
        shape = _hex_shape(radius)
        chamfer_width = (2 / math.sqrt(3) - 1) * radius
    elif hole_shape == "Crush ribs":
        shape, ch = _crush_ribs(
            radius,
            n=obj.CrushRibsCount,
            beta=obj.CrushRibsWaviness * math.pi / 2,
        )
        chamfer_width = ch * unitmm
    elif hole_shape == "Round":
        shape = Part.Face(Part.Wire(Part.makeCircle(radius)))
        chamfer_width = chamfer_depth
    else:
        raise ValueError(f"Unrecognised magnet hole shape {hole_shape:!r}")

    shape = shape.extrude(fc.Vector(0, 0, depth))

    if obj.Baseplate:
        assert chamfer_depth is not None
        chamfer_shape = Part.makeCone(
            radius,
            radius + chamfer_width,
            chamfer_depth,
            fc.Vector(0, 0, depth - chamfer_depth),
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
