"""Base plate feature module.

Contains implementation to conscruct baseplate features.
"""

import math

import FreeCAD
import Part
from FreeCAD import Units

from abc import abstractmethod
from enum import Enum

from .utils import Utils

from .const import (
    BASEPLATE_BOTTOM_CHAMFER,
    BASEPLATE_VERTICAL_SECTION,
    BASEPLATE_TOP_CHAMFER,
    BASEPLATE_OUTER_RADIUS,
    BASEPLATE_VERTICAL_RADIUS,
    BASEPLATE_BOTTOM_RADIUS,
    CLEARANCE,
    BASEPLATE_TOP_LEDGE_WIDTH,
    MAGNET_HOLES,
    BASEPLATE_SMALL_FILLET,
    MAGNET_HOLE_DIAMETER,
    MAGNET_HOLE_DEPTH,
    MAGNET_EDGE_THICKNESS,
    MAGNET_BASE,
    MAGNET_BASE_HOLE,
    MAGNET_CHAMFER,
    MAGNET_HOLE_DISTANCE_FROM_EDGE,
    BASE_THICKNESS,
    CONNECTION_HOLE_DIAMETER,
    SCREW_HOLE_DIAMETER,
    MAGNET_BOTTOM_CHAMFER,
)

HOLE_SHAPES = ["Round", "Hex"]


class Feature:
    @abstractmethod
    def Make(obj):
        raise NotImplementedError()


unitmm = Units.Quantity("1 mm")

zeromm = Units.Quantity("0 mm")


def _baseplate_magnet_hole_hex(
    obj: FreeCAD.DocumentObject, x_hole_pos: float, y_hole_pos: float
) -> Part.Shape:
    # Ratio of 2/sqrt(3) converts from inscribed circle radius to circumscribed circle radius
    radius = obj.MagnetHoleDiameter / math.sqrt(3)

    n_sides = 6
    rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0)

    p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
    p.Polygon = n_sides
    p.Circumradius = radius
    p.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-x_hole_pos, -y_hole_pos, 0),
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
        FreeCAD.Vector(x_hole_pos, -y_hole_pos, 0),
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
        FreeCAD.Vector(-x_hole_pos, y_hole_pos, 0),
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
        FreeCAD.Vector(x_hole_pos, y_hole_pos, 0),
        rot,
    )
    p.recompute()
    f = Part.Face(Part.Wire(p.Shape.Edges))
    c4 = f.extrude(FreeCAD.Vector(0, 0, -obj.MagnetHoleDepth))
    FreeCAD.ActiveDocument.removeObject(p.Name)

    return Part.Solid.multiFuse(c1, [c2, c3, c4])


def _baseplate_magnet_hole_round(
    obj: FreeCAD.DocumentObject, x_hole_pos: float, y_hole_pos: float
) -> Part.Shape:
    c1 = Part.makeCylinder(
        obj.MagnetHoleDiameter / 2,
        obj.MagnetHoleDepth,
        FreeCAD.Vector(-x_hole_pos, -y_hole_pos, 0),
        FreeCAD.Vector(0, 0, -1),
    )
    c2 = Part.makeCylinder(
        obj.MagnetHoleDiameter / 2,
        obj.MagnetHoleDepth,
        FreeCAD.Vector(x_hole_pos, -y_hole_pos, 0),
        FreeCAD.Vector(0, 0, -1),
    )
    c3 = Part.makeCylinder(
        obj.MagnetHoleDiameter / 2,
        obj.MagnetHoleDepth,
        FreeCAD.Vector(-x_hole_pos, y_hole_pos, 0),
        FreeCAD.Vector(0, 0, -1),
    )
    c4 = Part.makeCylinder(
        obj.MagnetHoleDiameter / 2,
        obj.MagnetHoleDepth,
        FreeCAD.Vector(x_hole_pos, y_hole_pos, 0),
        FreeCAD.Vector(0, 0, -1),
    )

    # Chamfer
    ct1 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2 + obj.MagnetChamfer,
        FreeCAD.Vector(-x_hole_pos, -y_hole_pos, 0),
        FreeCAD.Vector(0, 0, 1),
    )
    ct2 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2 + obj.MagnetChamfer,
        FreeCAD.Vector(x_hole_pos, -y_hole_pos, 0),
        FreeCAD.Vector(0, 0, 1),
    )
    ct3 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2 + obj.MagnetChamfer,
        FreeCAD.Vector(-x_hole_pos, y_hole_pos, 0),
        FreeCAD.Vector(0, 0, 1),
    )
    ct4 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2 + obj.MagnetChamfer,
        FreeCAD.Vector(x_hole_pos, y_hole_pos, 0),
        FreeCAD.Vector(0, 0, 1),
    )

    cb1 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2,
        FreeCAD.Vector(
            -x_hole_pos,
            -y_hole_pos,
            -obj.MagnetChamfer,
        ),
        FreeCAD.Vector(0, 0, 1),
    )
    cb2 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2,
        FreeCAD.Vector(x_hole_pos, -y_hole_pos, -obj.MagnetChamfer),
        FreeCAD.Vector(0, 0, 1),
    )
    cb3 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2,
        FreeCAD.Vector(-x_hole_pos, y_hole_pos, -obj.MagnetChamfer),
        FreeCAD.Vector(0, 0, 1),
    )
    cb4 = Part.makeCircle(
        obj.MagnetHoleDiameter / 2,
        FreeCAD.Vector(x_hole_pos, y_hole_pos, -obj.MagnetChamfer),
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


class BaseplateMagnetHoles(Feature):
    """Creates baseplate magnet holes"""

    def __init__(self, obj: FreeCAD.DocumentObject):
        """Makes baseplate magnet holes

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """

        ## Gridfinity Parameters
        obj.addProperty(
            "App::PropertyBool",
            "MagnetHoles",
            "Gridfinity",
            "MagnetHoles",
        ).MagnetHoles = MAGNET_HOLES

        ## Gridfinity Non Standard Parameters

        obj.addProperty(
            "App::PropertyEnumeration",
            "MagnetHolesShape",
            "NonStandard",
            (
                "Shape of magnet holes. <br> <br> Hex meant to be press fit. <br> "
                "Round meant to be glued"
            ),
        )

        obj.MagnetHolesShape = HOLE_SHAPES

        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDiameter",
            "NonStandard",
            (
                "Diameter of Magnet Holes <br>For Hex holes, inscribed diameter<br> <br> "
                "default = 6.5 mm"
            ),
        ).MagnetHoleDiameter = MAGNET_HOLE_DIAMETER

        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDepth",
            "NonStandard",
            "Depth of Magnet Holes <br> <br> default = 2.4 mm",
        ).MagnetHoleDepth = MAGNET_HOLE_DEPTH

        obj.addProperty(
            "App::PropertyLength",
            "MagnetEdgeThickness",
            "NonStandard",
            "Thickness of edge holding magnets in place <br> <br> default = 1.2 mm",
        ).MagnetEdgeThickness = MAGNET_EDGE_THICKNESS

        obj.addProperty(
            "App::PropertyLength",
            "MagnetBase",
            "NonStandard",
            "Thickness of base under the magnets <br> <br> default = 0.4 mm",
        ).MagnetBase = MAGNET_BASE

        obj.addProperty(
            "App::PropertyLength",
            "MagnetBaseHole",
            "NonStandard",
            "Diameter of the hole at the bottom of the magnet cutout <br> <br> default = 3 mm",
        ).MagnetBaseHole = MAGNET_BASE_HOLE

        obj.addProperty(
            "App::PropertyLength",
            "MagnetChamfer",
            "NonStandard",
            "Chamfer at top of magnet hole <br> <br> default = 0.4 mm",
        ).MagnetChamfer = MAGNET_CHAMFER

        ## Gridfinity Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDistanceFromEdge",
            "zzExpertOnly",
            "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",
            1,
        ).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE

        ## Gridfinity Hidden Properties
        obj.addProperty(
            "App::PropertyLength",
            "BaseThickness",
            "Hidden",
            "Thickness of base under the normal baseplate  profile <br> <br> default = 6.4 mm",
        ).BaseThickness = BASE_THICKNESS

        obj.setEditorMode("BaseThickness", 2)

    def Make(obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Create magentholes for a baseplate.

        Args:
            obj (FreeCAD.DocumentObject): FreeCAD config object

        Returns:
            Part.Shape: 3d object geometry.

        """
        x_hole_pos = obj.xGridSize / 2 - obj.MagnetHoleDistanceFromEdge
        y_hole_pos = obj.yGridSize / 2 - obj.MagnetHoleDistanceFromEdge

        # Magnet holes
        if obj.MagnetHolesShape == "Hex":
            hm1 = _baseplate_magnet_hole_hex(obj, x_hole_pos, y_hole_pos)
        elif obj.MagnetHolesShape == "Round":
            hm1 = _baseplate_magnet_hole_round(obj, x_hole_pos, y_hole_pos)
        else:
            msg = f"Unexpected hole shape: {obj.MagnetHolesShape}"
            raise ValueError(msg)

        # Screw holes
        ca1 = Part.makeCylinder(
            obj.MagnetBaseHole / 2,
            obj.MagnetHoleDepth + obj.BaseThickness,
            FreeCAD.Vector(-x_hole_pos, -y_hole_pos, 0),
            FreeCAD.Vector(0, 0, -1),
        )
        ca2 = Part.makeCylinder(
            obj.MagnetBaseHole / 2,
            obj.MagnetHoleDepth + obj.BaseThickness,
            FreeCAD.Vector(x_hole_pos, -y_hole_pos, 0),
            FreeCAD.Vector(0, 0, -1),
        )
        ca3 = Part.makeCylinder(
            obj.MagnetBaseHole / 2,
            obj.MagnetHoleDepth + obj.BaseThickness,
            FreeCAD.Vector(-x_hole_pos, y_hole_pos, 0),
            FreeCAD.Vector(0, 0, -1),
        )
        ca4 = Part.makeCylinder(
            obj.MagnetBaseHole / 2,
            obj.MagnetHoleDepth + obj.BaseThickness,
            FreeCAD.Vector(x_hole_pos, y_hole_pos, 0),
            FreeCAD.Vector(0, 0, -1),
        )

        hm1 = hm1.multiFuse([ca1, ca2, ca3, ca4])

        hm1.translate(
            FreeCAD.Vector(
                obj.xGridSize / 2,
                obj.yGridSize / 2,
                0,
            )
        )

        xtranslate = zeromm
        ytranslate = zeromm
        hm2: Part.Shape | None = None
        hm3: Part.Shape | None = None

        for _ in range(obj.xMaxGrids):
            ytranslate = zeromm

            for _ in range(obj.yMaxGrids):
                hm1_copy = hm1.copy()

                # Translate for next hole
                hm1_copy.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))
                hm2 = hm1_copy if hm2 is None else hm2.fuse(hm1_copy)
                ytranslate += obj.yGridSize  # Track position

            hm3 = hm2 if hm3 is None else hm3.fuse(hm2)
            xtranslate += obj.xGridSize

        return hm3.translate(FreeCAD.Vector(-obj.xLocationOffset,-obj.yLocationOffset,0,))


class BaseplateScrewBottomChamfer(Feature):
    """Creates Baseplate Connection Holes"""

    def __init__(self, obj: FreeCAD.DocumentObject):
        """Creates Baseplate Connection Holes

        Args:
            obj (FreeCAD.DocumentObject): Document object.
        """

        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "ScrewHoleDiameter",
            "NonStandard",
            "Diameter of screw holes inside magnet holes <br> <br> default = 3 mm",
        ).ScrewHoleDiameter = SCREW_HOLE_DIAMETER

        ## Gridfinity Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "MagnetBottomChamfer",
            "zzExpertOnly",
            "Diameter of screw holes inside magnet holes <br> <br> default = 3 mm",
        ).MagnetBottomChamfer = MAGNET_BOTTOM_CHAMFER

    def Make(obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Create screw chamfer for a baseplate.

        Args:
            obj (FreeCAD.DocumentObject): FreeCAD config object.

        Returns:
            Part.Shape: 3d Shape.

        """
        x_hole_pos = obj.xGridSize / 2 - obj.MagnetHoleDistanceFromEdge
        y_hole_pos = obj.yGridSize / 2 - obj.MagnetHoleDistanceFromEdge

        ct1 = Part.makeCircle(
            obj.ScrewHoleDiameter / 2 + obj.MagnetBottomChamfer,
            FreeCAD.Vector(-x_hole_pos, -y_hole_pos, -obj.TotalHeight + obj.BaseProfileHeight),
            FreeCAD.Vector(0, 0, 1),
        )
        ct2 = Part.makeCircle(
            obj.ScrewHoleDiameter / 2 + obj.MagnetBottomChamfer,
            FreeCAD.Vector(x_hole_pos, -y_hole_pos, -obj.TotalHeight + obj.BaseProfileHeight),
            FreeCAD.Vector(0, 0, 1),
        )
        ct3 = Part.makeCircle(
            obj.ScrewHoleDiameter / 2 + obj.MagnetBottomChamfer,
            FreeCAD.Vector(-x_hole_pos, y_hole_pos, -obj.TotalHeight + obj.BaseProfileHeight),
            FreeCAD.Vector(0, 0, 1),
        )
        ct4 = Part.makeCircle(
            obj.ScrewHoleDiameter / 2 + obj.MagnetBottomChamfer,
            FreeCAD.Vector(x_hole_pos, y_hole_pos, -obj.TotalHeight + obj.BaseProfileHeight),
            FreeCAD.Vector(0, 0, 1),
        )

        cb1 = Part.makeCircle(
            obj.ScrewHoleDiameter / 2,
            FreeCAD.Vector(
                -x_hole_pos,
                -y_hole_pos,
                -obj.TotalHeight + obj.MagnetBottomChamfer + obj.BaseProfileHeight,
            ),
            FreeCAD.Vector(0, 0, 1),
        )
        cb2 = Part.makeCircle(
            obj.ScrewHoleDiameter / 2,
            FreeCAD.Vector(
                x_hole_pos,
                -y_hole_pos,
                -obj.TotalHeight + obj.MagnetBottomChamfer + obj.BaseProfileHeight,
            ),
            FreeCAD.Vector(0, 0, 1),
        )
        cb3 = Part.makeCircle(
            obj.ScrewHoleDiameter / 2,
            FreeCAD.Vector(
                -x_hole_pos,
                y_hole_pos,
                -obj.TotalHeight + obj.MagnetBottomChamfer + obj.BaseProfileHeight,
            ),
            FreeCAD.Vector(0, 0, 1),
        )
        cb4 = Part.makeCircle(
            obj.ScrewHoleDiameter / 2,
            FreeCAD.Vector(
                x_hole_pos,
                y_hole_pos,
                -obj.TotalHeight + obj.MagnetBottomChamfer + obj.BaseProfileHeight,
            ),
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

        for _ in range(obj.xMaxGrids):
            ytranslate = zeromm
            for _ in range(obj.yMaxGrids):
                hm1_copy = hm1.copy()

                hm1_copy.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))
                hm2 = hm1_copy if hm2 is None else hm2.fuse(hm1_copy)
                ytranslate += obj.yGridSize
            hm3 = hm2 if hm3 is None else hm3.fuse(hm2)
            xtranslate += obj.xGridSize

        return hm3.translate(
            FreeCAD.Vector(
                obj.xGridSize / 2 - obj.xLocationOffset,
                obj.yGridSize / 2 - obj.yLocationOffset,
                0,
            )
        )

class BaseplateConnectionHoles(Feature):
    """Creates Baseplate Connection Holes"""

    def __init__(self, obj: FreeCAD.DocumentObject):
        """Creates Baseplate Connection Holes

        Args:
            obj (FreeCAD.DocumentObject): Document object.
        """
        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "ConnectionHoleDiameter",
            "NonStandard",
            "Holes on the sides to connect multiple baseplates together <br> <br> default = 3.2 mm",
        ).ConnectionHoleDiameter = CONNECTION_HOLE_DIAMETER

    def Make(obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Create connection holes for a baseplate.

        Args:
            obj (FreeCAD.DocumentObject): FreeCAD config object.
            layout: 2d python matrix

        Returns:
            Part.Shape: 3d Shape.

        """
        c1 = Part.makeCylinder(
            obj.ConnectionHoleDiameter / 2,
            obj.BaseThickness,
            FreeCAD.Vector(0, -obj.yGridSize / 2, -obj.BaseThickness / 2),
            FreeCAD.Vector(0, 1, 0),
        )
        c2 = Part.makeCylinder(
            obj.ConnectionHoleDiameter / 2,
            obj.BaseThickness,
            FreeCAD.Vector(
                0,
                -obj.yGridSize / 2 + obj.yTotalWidth - obj.BaseThickness,
                -obj.BaseThickness / 2,
            ),
            FreeCAD.Vector(0, 1, 0),
        )

        c3 = Part.makeCylinder(
            obj.ConnectionHoleDiameter / 2,
            obj.BaseThickness,
            FreeCAD.Vector(-obj.xGridSize / 2, 0, -obj.BaseThickness / 2),
            FreeCAD.Vector(1, 0, 0),
        )
        c4 = Part.makeCylinder(
            obj.ConnectionHoleDiameter / 2,
            obj.BaseThickness,
            FreeCAD.Vector(
                -obj.xGridSize / 2 + obj.xTotalWidth - obj.BaseThickness,
                0,
                -obj.BaseThickness / 2,
            ),
            FreeCAD.Vector(1, 0, 0),
        )

        xtranslate = zeromm
        ytranslate = zeromm
        hx1 = Part.Solid.fuse(c1, c2)
        hx2: Part.Shape | None = None

        for _ in range(obj.xMaxGrids):
            ytranslate = zeromm

            hx1 = hx1.copy()
            hx1.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))
            hx2 = hx1 if hx2 is None else hx2.fuse(hx1)

            xtranslate += obj.xGridSize

        xtranslate = zeromm
        ytranslate = zeromm
        hy1 = Part.Solid.fuse(c3, c4)
        hy2: Part.Shape | None = None

        for _ in range(obj.yMaxGrids):
            xtranslate = zeromm

            hy1_copy = hy1.copy()
            hy1_copy.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))
            hy2 = hy1_copy if hy2 is None else hy2.fuse(hy1_copy)
            ytranslate += obj.yGridSize

        fuse_total = Part.Solid.fuse(hx2, hy2)

        return fuse_total.translate(
            FreeCAD.Vector(
                obj.xGridSize / 2 - obj.xLocationOffset,
                obj.yGridSize / 2 - obj.yLocationOffset,
                0,
            )
        )


class BaseplateCenterCut(Feature):
    def __init__(self, obj: FreeCAD.DocumentObject):
        """makes L layout

        Args:
            obj (FreeCAD.DocumentObject): Document object.
        """
        obj.addProperty(
            "App::PropertyLength",
            "SmallFillet",
            "NonStandard",
            "Small fillet on iside of baseplate <br> <br> default = 1 mm",
        ).SmallFillet = BASEPLATE_SMALL_FILLET

    def Make(obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Create baseplate center cutout.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Baseplate center cutout shape.

        """
        x_inframedis = (
            obj.xGridSize / 2
            - obj.BaseProfileTopChamfer
            - obj.BaseProfileBottomChamfer
            - obj.BaseplateTopLedgeWidth
        )

        y_inframedis = (
            obj.yGridSize / 2
            - obj.BaseProfileTopChamfer
            - obj.BaseProfileBottomChamfer
            - obj.BaseplateTopLedgeWidth
        )

        x_magedge = (
            obj.xGridSize / 2
            - obj.MagnetHoleDistanceFromEdge
            - obj.MagnetHoleDiameter / 2
            - obj.MagnetEdgeThickness
        )

        y_magedge = (
            obj.yGridSize / 2
            - obj.MagnetHoleDistanceFromEdge
            - obj.MagnetHoleDiameter / 2
            - obj.MagnetEdgeThickness
        )

        x_magcenter = obj.xGridSize / 2 - obj.MagnetHoleDistanceFromEdge

        y_magcenter = obj.yGridSize / 2 - obj.MagnetHoleDistanceFromEdge

        x_smfillpos = x_inframedis - obj.SmallFillet + obj.SmallFillet * math.sin(math.pi / 4)

        y_smfillpos = y_inframedis - obj.SmallFillet + obj.SmallFillet * math.sin(math.pi / 4)

        x_smfillposmag = x_magedge - obj.SmallFillet + obj.SmallFillet * math.sin(math.pi / 4)

        y_smfillposmag = y_magedge - obj.SmallFillet + obj.SmallFillet * math.sin(math.pi / 4)

        x_smfilloffcen = (
            obj.xGridSize / 2
            - obj.MagnetHoleDistanceFromEdge
            - obj.MagnetHoleDiameter / 2
            - obj.MagnetEdgeThickness
            - obj.SmallFillet
        )

        y_smfilloffcen = (
            obj.yGridSize / 2
            - obj.MagnetHoleDistanceFromEdge
            - obj.MagnetHoleDiameter / 2
            - obj.MagnetEdgeThickness
            - obj.SmallFillet
        )

        x_smfillins = x_inframedis - obj.SmallFillet

        y_smfillins = y_inframedis - obj.SmallFillet

        x_bigfillpos = (
            obj.xGridSize / 2
            - obj.MagnetHoleDistanceFromEdge
            - (obj.MagnetHoleDiameter / 2 + obj.MagnetEdgeThickness) * math.sin(math.pi / 4)
        )

        y_bigfillpos = (
            obj.yGridSize / 2
            - obj.MagnetHoleDistanceFromEdge
            - (obj.MagnetHoleDiameter / 2 + obj.MagnetEdgeThickness) * math.sin(math.pi / 4)
        )

        mec_middle = FreeCAD.Vector(0, 0, 0)

        v1 = FreeCAD.Vector(0, -y_inframedis, 0)
        v2 = FreeCAD.Vector(-x_smfilloffcen, -y_inframedis, 0)
        v3 = FreeCAD.Vector(-x_magedge, -y_smfillins, 0)
        v4 = FreeCAD.Vector(-x_magedge, -y_magcenter, 0)
        v5 = FreeCAD.Vector(-x_magcenter, -y_magedge, 0)
        v6 = FreeCAD.Vector(-x_smfillins, -y_magedge, 0)
        v7 = FreeCAD.Vector(-x_inframedis, -y_smfilloffcen, 0)
        v8 = FreeCAD.Vector(-x_inframedis, 0, 0)

        va1 = FreeCAD.Vector(-x_smfillposmag, -y_smfillpos, 0)
        va2 = FreeCAD.Vector(-x_bigfillpos, -y_bigfillpos, 0)
        va3 = FreeCAD.Vector(-x_smfillpos, -y_smfillposmag, 0)

        l1 = Part.LineSegment(v1, v2)
        ar1 = Part.Arc(l1.EndPoint, va1, v3)
        l2 = Part.LineSegment(ar1.EndPoint, v4)
        ar2 = Part.Arc(l2.EndPoint, va2, v5)
        l3 = Part.LineSegment(ar2.EndPoint, v6)
        ar3 = Part.Arc(l3.EndPoint, va3, v7)
        l4 = Part.LineSegment(ar3.EndPoint, v8)
        l5 = Part.LineSegment(l4.EndPoint, mec_middle)
        l6 = Part.LineSegment(l5.EndPoint, l1.StartPoint)

        wire = Utils.curve_to_wire([l1, ar1, l2, ar2, l3, ar3, l4, l5, l6])
        partial_shape1 = Part.Face(wire).extrude(FreeCAD.Vector(0, 0, -obj.TotalHeight))
        partial_shape2 = partial_shape1.mirror(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0))
        partial_shape3 = partial_shape1.mirror(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0))
        partial_shape4 = partial_shape2.mirror(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0))

        shape = partial_shape1.multiFuse([partial_shape2, partial_shape3, partial_shape4])

        vec_list: list[FreeCAD.Vector] = []
        xtranslate = 0
        ytranslate = 0

        for _ in range(obj.xGridUnits):
            ytranslate = 0
            for _ in range(obj.yGridUnits):
                vec_list.append(FreeCAD.Vector(xtranslate, ytranslate, 0))
                ytranslate += obj.yGridSize.Value
            xtranslate += obj.xGridSize.Value

        fuse_total = Utils.copy_and_translate(shape, vec_list)

        return fuse_total.translate(
            FreeCAD.Vector(
                obj.xGridSize / 2 - obj.xLocationOffset,
                obj.yGridSize / 2 - obj.yLocationOffset,
                0,
            )
        )


class BaseplateBaseValues(Feature):
    """Add bin base properties and calculate values"""

    def __init__(self, obj: FreeCAD.DocumentObject):
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
        ).BaseProfileBottomChamfer = BASEPLATE_BOTTOM_CHAMFER

        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileVerticalSection",
            "zzExpertOnly",
            "Height of the vertical section in bin base profile",
            1,
        ).BaseProfileVerticalSection = BASEPLATE_VERTICAL_SECTION

        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileTopChamfer",
            "zzExpertOnly",
            "Height of the top chamfer in the bin base profile",
            1,
        ).BaseProfileTopChamfer = BASEPLATE_TOP_CHAMFER

        obj.addProperty(
            "App::PropertyLength",
            "BinOuterRadius",
            "zzExpertOnly",
            "Outer radius of the bin",
            1,
        ).BinOuterRadius = BASEPLATE_OUTER_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "BinVerticalRadius",
            "zzExpertOnly",
            "Radius of the base profile Vertical section",
            1,
        ).BinVerticalRadius = BASEPLATE_VERTICAL_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "BinBottomRadius",
            "zzExpertOnly",
            "bottom of bin corner radius",
            1,
        ).BinBottomRadius = BASEPLATE_BOTTOM_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "Clearance",
            "zzExpertOnly",
            (
                "The tolerance on each side of a bin between before the edge of the grid <br> <br>"
                "default = 0.25 mm"
            ),
        ).Clearance = CLEARANCE

        obj.addProperty(
            "App::PropertyLength",
            "BaseplateTopLedgeWidth",
            "zzExpertOnly",
            "Top ledge of baseplate",
            1,
        ).BaseplateTopLedgeWidth = BASEPLATE_TOP_LEDGE_WIDTH

    def Make(self, obj: FreeCAD.DocumentObject) -> None:
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


class BaseplateSolidShape(Feature):
    """Creates Solid which the baseplate is cut from"""

    def __init__(
        self,
        obj: FreeCAD.DocumentObject,
        magnet_baseplate_default=False,
        screw_together_baseplate_default=False,
    ):
        """Makes solid which the baseplate is cut from

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            magnet_baseplate_default: boolean
            screw_together_baseplate_default: boolean
        """
        obj.addProperty(
            "App::PropertyLength",
            "TotalHeight",
            "ReferenceDimensions",
            "total height of the bin",
            1,
        )

        ## Hidden Parameters
        obj.addProperty(
            "App::PropertyBool",
            "MagnetBaseplate",
            "Hidden",
            "Thickness of base under the normal baseplate  profile <br> <br> default = 6.4 mm",
        ).MagnetBaseplate = magnet_baseplate_default

        obj.setEditorMode("MagnetBaseplate", 1)

        obj.addProperty(
            "App::PropertyBool",
            "ScrewTogetherBaseplate",
            "Hidden",
            "Thickness of base under the normal baseplate  profile <br> <br> default = 6.4 mm",
        ).ScrewTogetherBaseplate = screw_together_baseplate_default

        obj.setEditorMode("ScrewTogetherBaseplate", 1)

    def Make(self, obj: FreeCAD.DocumentObject, baseplate_outside_shape):
        """Creates solid which baseplate is cut from

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            baseplate_outside_shape (Part.Wire): outside profile of the baseplate shape

        Returns:
            Part.Shape: Extruded part for the baseplate to be cut from.

        """
        ## Calculated Parameters
        if obj.MagnetBaseplate:
            obj.TotalHeight = obj.BaseProfileHeight + obj.MagnetHoleDepth + obj.MagnetBase
        elif obj.ScrewTogetherBaseplate:
            obj.TotalHeight = obj.BaseProfileHeight + obj.BaseThickness
        else:
            obj.TotalHeight = obj.BaseProfileHeight

        ## Baseplate Solid Shape Generation
        face = Part.Face(baseplate_outside_shape)

        fuse_total = face.extrude(FreeCAD.Vector(0, 0, obj.TotalHeight))

        return fuse_total.translate(
            FreeCAD.Vector(
                -obj.xLocationOffset,
                -obj.yLocationOffset,
                0,
            )
        )

