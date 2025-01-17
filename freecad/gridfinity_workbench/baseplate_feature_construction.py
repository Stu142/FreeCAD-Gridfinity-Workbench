"""Base plate feature module.

Contains implementation to conscruct baseplate features.
"""

import math

import FreeCAD
import Part
from FreeCAD import Units

unitmm = Units.Quantity("1 mm")

zeromm = Units.Quantity("0 mm")


def _baseplate_magnet_hole_hex(obj: FreeCAD.DocumentObject, hole_pos: float) -> Part.Shape:
    # Ratio of 2/sqrt(3) converts from inscribed circle radius to circumscribed circle radius
    radius = obj.MagnetHoleDiameter / math.sqrt(3)

    n_sides = 6
    rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0)

    p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
    p.Polygon = n_sides
    p.Circumradius = radius
    p.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-hole_pos, -hole_pos, -obj.BaseProfileHeight),
        rot,
    )
    p.recompute()
    f = Part.Face(Part.Wire(p.Shape.Edges))
    c1 = f.extrude(FreeCAD.Vector(0, 0, -obj.MagnetHoleDepth))
    FreeCAD.ActiveDocument.removeObject(p.Name)

    p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
    p.Polygon = n_sides
    p.Circumradius = radius
    p.Placement = FreeCAD.Placement(
        FreeCAD.Vector(hole_pos, -hole_pos, -obj.BaseProfileHeight),
        rot,
    )
    p.recompute()
    f = Part.Face(Part.Wire(p.Shape.Edges))
    c2 = f.extrude(FreeCAD.Vector(0, 0, -obj.MagnetHoleDepth))
    FreeCAD.ActiveDocument.removeObject(p.Name)

    p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
    p.Polygon = n_sides
    p.Circumradius = radius
    p.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-hole_pos, hole_pos, -obj.BaseProfileHeight),
        rot,
    )
    p.recompute()
    f = Part.Face(Part.Wire(p.Shape.Edges))
    c3 = f.extrude(FreeCAD.Vector(0, 0, -obj.MagnetHoleDepth))
    FreeCAD.ActiveDocument.removeObject(p.Name)

    p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
    p.Polygon = n_sides
    p.Circumradius = radius
    p.Placement = FreeCAD.Placement(
        FreeCAD.Vector(hole_pos, hole_pos, -obj.BaseProfileHeight),
        rot,
    )
    p.recompute()
    f = Part.Face(Part.Wire(p.Shape.Edges))
    c4 = f.extrude(FreeCAD.Vector(0, 0, -obj.MagnetHoleDepth))
    FreeCAD.ActiveDocument.removeObject(p.Name)

    return Part.Solid.multiFuse(c1, [c2, c3, c4])


def _baseplate_magnet_hole_round(obj: FreeCAD.DocumentObject, hole_pos: float) -> Part.Shape:
    c1 = Part.makeCylinder(
        obj.MagnetHoleDiameter / 2,
        obj.MagnetHoleDepth,
        FreeCAD.Vector(-hole_pos, -hole_pos, -obj.BaseProfileHeight),
        FreeCAD.Vector(0, 0, -1),
    )
    c2 = Part.makeCylinder(
        obj.MagnetHoleDiameter / 2,
        obj.MagnetHoleDepth,
        FreeCAD.Vector(hole_pos, -hole_pos, -obj.BaseProfileHeight),
        FreeCAD.Vector(0, 0, -1),
    )
    c3 = Part.makeCylinder(
        obj.MagnetHoleDiameter / 2,
        obj.MagnetHoleDepth,
        FreeCAD.Vector(-hole_pos, hole_pos, -obj.BaseProfileHeight),
        FreeCAD.Vector(0, 0, -1),
    )
    c4 = Part.makeCylinder(
        obj.MagnetHoleDiameter / 2,
        obj.MagnetHoleDepth,
        FreeCAD.Vector(hole_pos, hole_pos, -obj.BaseProfileHeight),
        FreeCAD.Vector(0, 0, -1),
    )

    # Chamfer
    ct1 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2 + obj.MagnetChamfer,
        FreeCAD.Vector(-hole_pos, -hole_pos, -obj.BaseProfileHeight),
        FreeCAD.Vector(0, 0, 1),
    )
    ct2 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2 + obj.MagnetChamfer,
        FreeCAD.Vector(hole_pos, -hole_pos, -obj.BaseProfileHeight),
        FreeCAD.Vector(0, 0, 1),
    )
    ct3 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2 + obj.MagnetChamfer,
        FreeCAD.Vector(-hole_pos, hole_pos, -obj.BaseProfileHeight),
        FreeCAD.Vector(0, 0, 1),
    )
    ct4 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2 + obj.MagnetChamfer,
        FreeCAD.Vector(hole_pos, hole_pos, -obj.BaseProfileHeight),
        FreeCAD.Vector(0, 0, 1),
    )

    cb1 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2,
        FreeCAD.Vector(
            -hole_pos,
            -hole_pos,
            -obj.BaseProfileHeight - obj.MagnetChamfer,
        ),
        FreeCAD.Vector(0, 0, 1),
    )
    cb2 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2,
        FreeCAD.Vector(hole_pos, -hole_pos, -obj.BaseProfileHeight - obj.MagnetChamfer),
        FreeCAD.Vector(0, 0, 1),
    )
    cb3 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2,
        FreeCAD.Vector(-hole_pos, hole_pos, -obj.BaseProfileHeight - obj.MagnetChamfer),
        FreeCAD.Vector(0, 0, 1),
    )
    cb4 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2,
        FreeCAD.Vector(hole_pos, hole_pos, -obj.BaseProfileHeight - obj.MagnetChamfer),
        FreeCAD.Vector(0, 0, 1),
    )

    ch1 = [ct1, cb1]
    ch1 = Part.makeLoft(ch1, solid=True)
    ch2 = [ct2, cb2]
    ch2 = Part.makeLoft(ch2, solid=True)
    ch3 = [ct3, cb3]
    ch3 = Part.makeLoft(ch3, solid=True)
    ch4 = [ct4, cb4]
    ch4 = Part.makeLoft(ch4, solid=True)

    return Part.Solid.multiFuse(
        c1,
        [c2, c3, c4, ch1, ch2, ch3, ch4],
    )


def make_baseplate_magnet_holes(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create magentholes for a baseplate.

    Args:
        obj (FreeCAD.DocumentObject): FreeCAD config object

    Returns:
        Part.Shape: 3d object geometry.

    """
    hole_pos = obj.GridSize / 2 - obj.MagnetHoleDistanceFromEdge

    # Magnet holes
    if obj.MagnetHolesShape == "Hex":
        hm1 = _baseplate_magnet_hole_hex(obj, hole_pos)
    elif obj.MagnetHolesShape == "Round":
        hm1 = _baseplate_magnet_hole_round(obj, hole_pos)
    else:
        msg = f"Unexpected hole shape: {obj.MagnetHolesShape}"
        raise ValueError(msg)

    # Screw holes
    ca1 = Part.makeCylinder(
        obj.MagnetBaseHole / 2,
        obj.MagnetHoleDepth + obj.BaseThickness,
        FreeCAD.Vector(-hole_pos, -hole_pos, -obj.BaseProfileHeight),
        FreeCAD.Vector(0, 0, -1),
    )
    ca2 = Part.makeCylinder(
        obj.MagnetBaseHole / 2,
        obj.MagnetHoleDepth + obj.BaseThickness,
        FreeCAD.Vector(hole_pos, -hole_pos, -obj.BaseProfileHeight),
        FreeCAD.Vector(0, 0, -1),
    )
    ca3 = Part.makeCylinder(
        obj.MagnetBaseHole / 2,
        obj.MagnetHoleDepth + obj.BaseThickness,
        FreeCAD.Vector(-hole_pos, hole_pos, -obj.BaseProfileHeight),
        FreeCAD.Vector(0, 0, -1),
    )
    ca4 = Part.makeCylinder(
        obj.MagnetBaseHole / 2,
        obj.MagnetHoleDepth + obj.BaseThickness,
        FreeCAD.Vector(hole_pos, hole_pos, -obj.BaseProfileHeight),
        FreeCAD.Vector(0, 0, -1),
    )

    hm1 = hm1.multiFuse([ca1, ca2, ca3, ca4])

    xtranslate = zeromm
    ytranslate = zeromm
    hm2: Part.Shape | None = None
    hm3: Part.Shape | None = None

    for _ in range(obj.xGridUnits):
        ytranslate = zeromm

        for _ in range(obj.yGridUnits):
            hm1_copy = hm1.copy()

            # Translate for next hole
            hm1_copy.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))
            hm2 = hm1_copy if hm2 is None else hm2.fuse(hm1_copy)
            ytranslate += obj.GridSize  # Track position

        hm3 = hm2 if hm3 is None else hm3.fuse(hm2)
        xtranslate += obj.GridSize

    return hm3


def make_baseplate_screw_bottom_chamfer(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create screw chamfer for a baseplate.

    Args:
        obj (FreeCAD.DocumentObject): FreeCAD config object.

    Returns:
        Part.Shape: 3d Shape.

    """
    hole_pos = obj.GridSize / 2 - obj.MagnetHoleDistanceFromEdge

    ct1 = Part.makeCircle(
        obj.ScrewHoleDiameter / 2 + obj.MagnetBottomChamfer,
        FreeCAD.Vector(-hole_pos, -hole_pos, -obj.TotalHeight),
        FreeCAD.Vector(0, 0, 1),
    )
    ct2 = Part.makeCircle(
        obj.ScrewHoleDiameter / 2 + obj.MagnetBottomChamfer,
        FreeCAD.Vector(hole_pos, -hole_pos, -obj.TotalHeight),
        FreeCAD.Vector(0, 0, 1),
    )
    ct3 = Part.makeCircle(
        obj.ScrewHoleDiameter / 2 + obj.MagnetBottomChamfer,
        FreeCAD.Vector(-hole_pos, hole_pos, -obj.TotalHeight),
        FreeCAD.Vector(0, 0, 1),
    )
    ct4 = Part.makeCircle(
        obj.ScrewHoleDiameter / 2 + obj.MagnetBottomChamfer,
        FreeCAD.Vector(hole_pos, hole_pos, -obj.TotalHeight),
        FreeCAD.Vector(0, 0, 1),
    )

    cb1 = Part.makeCircle(
        obj.ScrewHoleDiameter / 2,
        FreeCAD.Vector(-hole_pos, -hole_pos, -obj.TotalHeight + obj.MagnetBottomChamfer),
        FreeCAD.Vector(0, 0, 1),
    )
    cb2 = Part.makeCircle(
        obj.ScrewHoleDiameter / 2,
        FreeCAD.Vector(hole_pos, -hole_pos, -obj.TotalHeight + obj.MagnetBottomChamfer),
        FreeCAD.Vector(0, 0, 1),
    )
    cb3 = Part.makeCircle(
        obj.ScrewHoleDiameter / 2,
        FreeCAD.Vector(-hole_pos, hole_pos, -obj.TotalHeight + obj.MagnetBottomChamfer),
        FreeCAD.Vector(0, 0, 1),
    )
    cb4 = Part.makeCircle(
        obj.ScrewHoleDiameter / 2,
        FreeCAD.Vector(hole_pos, hole_pos, -obj.TotalHeight + obj.MagnetBottomChamfer),
        FreeCAD.Vector(0, 0, 1),
    )

    ch1 = [ct1, cb1]
    ch1 = Part.makeLoft(ch1, solid=True)
    ch2 = [ct2, cb2]
    ch2 = Part.makeLoft(ch2, solid=True)
    ch3 = [ct3, cb3]
    ch3 = Part.makeLoft(ch3, solid=True)
    ch4 = [ct4, cb4]
    ch4 = Part.makeLoft(ch4, solid=True)

    xtranslate = zeromm
    ytranslate = zeromm

    hm1 = Part.Solid.multiFuse(ch1, [ch2, ch3, ch4])
    hm2: Part.Shape | None = None
    hm3: Part.Shape | None = None

    for _ in range(obj.xGridUnits):
        ytranslate = zeromm
        for _ in range(obj.yGridUnits):
            hm1_copy = hm1.copy()

            hm1_copy.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))
            hm2 = hm1_copy if hm2 is None else hm2.fuse(hm1_copy)
            ytranslate += obj.GridSize
        hm3 = hm2 if hm3 is None else hm3.fuse(hm2)
        xtranslate += obj.GridSize

    return hm3


def make_baseplate_connection_holes(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create connection holes for a baseplate.

    Args:
        obj (FreeCAD.DocumentObject): FreeCAD config object.

    Returns:
        Part.Shape: 3d Shape.

    """
    c1 = Part.makeCylinder(
        obj.ConnectionHoleDiameter / 2,
        obj.BaseThickness,
        FreeCAD.Vector(0, -obj.GridSize / 2, -obj.TotalHeight + obj.BaseThickness / 2),
        FreeCAD.Vector(0, 1, 0),
    )
    c2 = Part.makeCylinder(
        obj.ConnectionHoleDiameter / 2,
        obj.BaseThickness,
        FreeCAD.Vector(
            0,
            -obj.GridSize / 2 + obj.yTotalWidth - obj.BaseThickness,
            -obj.TotalHeight + obj.BaseThickness / 2,
        ),
        FreeCAD.Vector(0, 1, 0),
    )

    c3 = Part.makeCylinder(
        obj.ConnectionHoleDiameter / 2,
        obj.BaseThickness,
        FreeCAD.Vector(-obj.GridSize / 2, 0, -obj.TotalHeight + obj.BaseThickness / 2),
        FreeCAD.Vector(1, 0, 0),
    )
    c4 = Part.makeCylinder(
        obj.ConnectionHoleDiameter / 2,
        obj.BaseThickness,
        FreeCAD.Vector(
            -obj.GridSize / 2 + obj.xTotalWidth - obj.BaseThickness,
            0,
            -obj.TotalHeight + obj.BaseThickness / 2,
        ),
        FreeCAD.Vector(1, 0, 0),
    )

    xtranslate = zeromm
    ytranslate = zeromm
    hx1 = Part.Solid.fuse(c1, c2)
    hx2: Part.Shape | None = None

    for _ in range(obj.xGridUnits):
        ytranslate = zeromm

        hx1 = hx1.copy()
        hx1.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))
        hx2 = hx1 if hx2 is None else hx2.fuse(hx1)

        xtranslate += obj.GridSize

    xtranslate = zeromm
    ytranslate = zeromm
    hy1 = Part.Solid.fuse(c3, c4)
    hy2: Part.Shape | None = None

    for _ in range(obj.yGridUnits):
        xtranslate = zeromm

        hy1_copy = hy1.copy()
        hy1_copy.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))
        hy2 = hy1_copy if hy2 is None else hy2.fuse(hy1_copy)
        ytranslate += obj.GridSize

    return Part.Solid.fuse(hx2, hy2)
