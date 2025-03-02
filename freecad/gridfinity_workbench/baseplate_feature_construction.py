"""Base plate feature module.

Contains implementation to conscruct baseplate features.
"""

import math

import FreeCAD as fc  # noqa: N813
import Part

from . import const, utils

GridfinityLayout = list[list[bool]]

unitmm = fc.Units.Quantity("1 mm")

zeromm = fc.Units.Quantity("0 mm")


def _baseplate_magnet_hole_hex(
    obj: fc.DocumentObject,
    x_hole_pos: float,
    y_hole_pos: float,
) -> Part.Shape:
    # Ratio of 2/sqrt(3) converts from inscribed circle radius to circumscribed circle radius
    radius = obj.MagnetHoleDiameter / math.sqrt(3)

    n_sides = 6
    rot = fc.Rotation(fc.Vector(0, 0, 1), 0)

    p = fc.ActiveDocument.addObject("Part::RegularPolygon")
    p.Polygon = n_sides
    p.Circumradius = radius
    p.Placement = fc.Placement(fc.Vector(-x_hole_pos, -y_hole_pos), rot)
    p.recompute()
    f = Part.Face(Part.Wire(p.Shape.Edges))
    c1 = f.extrude(fc.Vector(0, 0, -obj.MagnetHoleDepth))
    fc.ActiveDocument.removeObject(p.Name)

    p = fc.ActiveDocument.addObject("Part::RegularPolygon")
    p.Polygon = n_sides
    p.Circumradius = radius
    p.Placement = fc.Placement(
        fc.Vector(x_hole_pos, -y_hole_pos),
        rot,
    )
    p.recompute()
    f = Part.Face(Part.Wire(p.Shape.Edges))
    c2 = f.extrude(fc.Vector(0, 0, -obj.MagnetHoleDepth))
    fc.ActiveDocument.removeObject(p.Name)

    p = fc.ActiveDocument.addObject("Part::RegularPolygon")
    p.Polygon = n_sides
    p.Circumradius = radius
    p.Placement = fc.Placement(fc.Vector(-x_hole_pos, y_hole_pos), rot)
    p.recompute()
    f = Part.Face(Part.Wire(p.Shape.Edges))
    c3 = f.extrude(fc.Vector(0, 0, -obj.MagnetHoleDepth))
    fc.ActiveDocument.removeObject(p.Name)

    p = fc.ActiveDocument.addObject("Part::RegularPolygon")
    p.Polygon = n_sides
    p.Circumradius = radius
    p.Placement = fc.Placement(fc.Vector(x_hole_pos, y_hole_pos), rot)
    p.recompute()
    f = Part.Face(Part.Wire(p.Shape.Edges))
    c4 = f.extrude(fc.Vector(0, 0, -obj.MagnetHoleDepth))
    fc.ActiveDocument.removeObject(p.Name)

    return c1.multiFuse([c2, c3, c4])


def _baseplate_magnet_hole_round(
    obj: fc.DocumentObject,
    x_hole_pos: float,
    y_hole_pos: float,
) -> Part.Shape:
    c = [
        Part.makeCylinder(
            obj.MagnetHoleDiameter / 2,
            obj.MagnetHoleDepth,
            pos,
            fc.Vector(0, 0, -1),
        )
        for pos in utils.corners(x_hole_pos, y_hole_pos)
    ]

    # Chamfer
    ct = [
        Part.makeCircle(
            obj.MagnetHoleDiameter / 2 + obj.MagnetChamfer,
            pos,
            fc.Vector(0, 0, 1),
        )
        for pos in utils.corners(x_hole_pos, y_hole_pos)
    ]
    cb = [
        Part.makeCircle(
            obj.MagnetHoleDiameter / 2,
            pos,
            fc.Vector(0, 0, 1),
        )
        for pos in utils.corners(x_hole_pos, y_hole_pos, -obj.MagnetChamfer)
    ]

    ch = [Part.makeLoft([t, b], solid=True) for t, b in zip(ct, cb)]

    return utils.multi_fuse(c + ch)


class BaseplateMagnetHoles:
    """Create baseplate magnet holes."""

    def __init__(self, obj: fc.DocumentObject) -> None:
        """Make baseplate magnet holes.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """
        ## Gridfinity Non Standard Parameters

        obj.addProperty(
            "App::PropertyEnumeration",
            "MagnetHolesShape",
            "NonStandard",
            (
                "Shape of magnet holes, change to suit your printers capabilities which"
                "might require testing."
                "<br> Round press fit by default, increase to 6.5 mm if using glue"
                "<br> <br> Hex is alternative press fit style."
                "<br> <br> default = 6.2 mm"
            ),
        )

        obj.MagnetHolesShape = const.HOLE_SHAPES

        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDiameter",
            "NonStandard",
            (
                "Diameter of Magnet Holes"
                "<br> Round press fit by default, increase to 6.5 mm if using glue"
                "<br> <br> Hex is alternative press fit style, inscribed diameter<br> <br>"
                "<br> <br> default = 6.2 mm"
            ),
        ).MagnetHoleDiameter = const.MAGNET_HOLE_DIAMETER

        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDepth",
            "NonStandard",
            "Depth of Magnet Holes <br> <br> default = 2.4 mm",
        ).MagnetHoleDepth = const.MAGNET_HOLE_DEPTH

        obj.addProperty(
            "App::PropertyLength",
            "MagnetEdgeThickness",
            "NonStandard",
            "Thickness of edge around magnets <br> <br> default = 1.2 mm",
        ).MagnetEdgeThickness = const.MAGNET_EDGE_THICKNESS

        obj.addProperty(
            "App::PropertyLength",
            "MagnetBase",
            "NonStandard",
            "Thickness of base under the magnets <br> <br> default = 0.4 mm",
        ).MagnetBase = const.MAGNET_BASE

        obj.addProperty(
            "App::PropertyLength",
            "MagnetBaseHole",
            "NonStandard",
            "Diameter of the hole at the bottom of the magnet cutout"
            "<br> Set to zero to make disapear"
            "<br> <br> default = 3 mm",
        ).MagnetBaseHole = const.MAGNET_BASE_HOLE

        obj.addProperty(
            "App::PropertyLength",
            "MagnetChamfer",
            "NonStandard",
            "Chamfer at top of magnet hole <br> <br> default = 0.4 mm",
        ).MagnetChamfer = const.MAGNET_CHAMFER

        ## Gridfinity Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDistanceFromEdge",
            "zzExpertOnly",
            "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",
            1,
        ).MagnetHoleDistanceFromEdge = const.MAGNET_HOLE_DISTANCE_FROM_EDGE

        ## Gridfinity Hidden Properties
        obj.addProperty(
            "App::PropertyLength",
            "BaseThickness",
            "Hidden",
            "Thickness of base under the normal baseplate  profile <br> <br> default = 6.4 mm",
        ).BaseThickness = const.BASE_THICKNESS
        obj.setEditorMode("BaseThickness", 2)

        obj.addProperty(
            "App::PropertyBool",
            "MagnetHoles",
            "ShouldBeHidden",
            "MagnetHoles",
        ).MagnetHoles = const.MAGNET_HOLES
        obj.setEditorMode("MagnetHoles", 2)

    def make(self, obj: fc.DocumentObject, layout: GridfinityLayout) -> Part.Shape:
        """Create magentholes for a baseplate.

        Args:
            obj (FreeCAD.DocumentObject): FreeCAD config object
            layout (GridfinityLayout): 2 dimentional list of feature locations.

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
            raise ValueError(f"Unexpected hole shape: {obj.MagnetHolesShape}")

        # Screw holes
        ca = [
            Part.makeCylinder(
                obj.MagnetBaseHole / 2,
                obj.MagnetHoleDepth + obj.BaseThickness,
                pos,
                fc.Vector(0, 0, -1),
            )
            for pos in utils.corners(x_hole_pos, -y_hole_pos)
        ]

        hm1 = hm1.multiFuse(ca)
        hm1.translate(fc.Vector(obj.xGridSize / 2, obj.yGridSize / 2))

        xtranslate = zeromm
        ytranslate = zeromm
        hm2: Part.Shape | None = None
        hm3: Part.Shape | None = None

        for col in layout:
            ytranslate = zeromm
            for cell in col:
                if cell:
                    hm1_copy = hm1.copy()

                    # Translate for next hole
                    hm1_copy.translate(fc.Vector(xtranslate, ytranslate))
                hm2 = hm1_copy if hm2 is None else hm2.fuse(hm1_copy)
                ytranslate += obj.yGridSize  # Track position

            hm3 = hm2 if hm3 is None else hm3.fuse(hm2)
            xtranslate += obj.xGridSize

        return hm3.translate(fc.Vector(-obj.xLocationOffset, -obj.yLocationOffset))


class BaseplateScrewBottomChamfer:
    """Create Baseplate Connection Holes."""

    def __init__(self, obj: fc.DocumentObject) -> None:
        """Create Baseplate Connection Holes.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """
        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "ScrewHoleDiameter",
            "NonStandard",
            "Diameter of screw holes inside magnet holes <br> <br> default = 3 mm",
        ).ScrewHoleDiameter = const.SCREW_HOLE_DIAMETER

        ## Gridfinity Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "MagnetBottomChamfer",
            "zzExpertOnly",
            "Chamfer of screwholes on the bottom of the baseplate, allows the use of countersuck"
            "m3 screws in the bottom up to a bin <br> <br> default = 3 mm",
        ).MagnetBottomChamfer = const.MAGNET_BOTTOM_CHAMFER

    def make(self, obj: fc.DocumentObject, layout: GridfinityLayout) -> Part.Shape:
        """Create screw chamfer for a baseplate.

        Args:
            obj (FreeCAD.DocumentObject): FreeCAD config object.
            layout (GridfinityLayout): 2 dimentional list of feature locations.

        Returns:
            Part.Shape: 3d Shape.

        """
        x_hole_pos = obj.xGridSize / 2 - obj.MagnetHoleDistanceFromEdge
        y_hole_pos = obj.yGridSize / 2 - obj.MagnetHoleDistanceFromEdge

        ct_z = -obj.TotalHeight + obj.BaseProfileHeight
        ct = [
            Part.makeCircle(
                obj.ScrewHoleDiameter / 2 + obj.MagnetBottomChamfer,
                pos,
                fc.Vector(0, 0, 1),
            )
            for pos in utils.corners(x_hole_pos, y_hole_pos, ct_z)
        ]
        cb_z = -obj.TotalHeight + obj.MagnetBottomChamfer + obj.BaseProfileHeight
        cb = [
            Part.makeCircle(
                obj.ScrewHoleDiameter / 2,
                pos,
                fc.Vector(0, 0, 1),
            )
            for pos in utils.corners(x_hole_pos, y_hole_pos, cb_z)
        ]

        ch = [Part.makeLoft([t, b], solid=True) for t, b in zip(ct, cb)]

        xtranslate = zeromm
        ytranslate = zeromm

        hm1 = utils.multi_fuse(ch)
        hm2: Part.Shape | None = None
        hm3: Part.Shape | None = None

        for col in layout:
            ytranslate = zeromm
            for cell in col:
                if cell:
                    hm1_copy = hm1.copy()
                    hm1_copy.translate(fc.Vector(xtranslate, ytranslate))
                hm2 = hm1_copy if hm2 is None else hm2.fuse(hm1_copy)
                ytranslate += obj.yGridSize
            hm3 = hm2 if hm3 is None else hm3.fuse(hm2)
            xtranslate += obj.xGridSize

        return hm3.translate(
            fc.Vector(
                obj.xGridSize / 2 - obj.xLocationOffset,
                obj.yGridSize / 2 - obj.yLocationOffset,
            ),
        )


class BaseplateConnectionHoles:
    """Create Baseplate Connection Holes."""

    def __init__(self, obj: fc.DocumentObject) -> None:
        """Create Baseplate Connection Holes.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """
        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "ConnectionHoleDiameter",
            "NonStandard",
            "Holes on the sides to connect multiple baseplates together <br> <br> default = 3.2 mm",
        ).ConnectionHoleDiameter = const.CONNECTION_HOLE_DIAMETER

    def make(self, obj: fc.DocumentObject) -> Part.Shape:
        """Create connection holes for a baseplate.

        Args:
            obj (FreeCAD.DocumentObject): FreeCAD config object.

        Returns:
            Part.Shape: 3d Shape.

        """
        c1 = Part.makeCylinder(
            obj.ConnectionHoleDiameter / 2,
            obj.BaseThickness,
            fc.Vector(0, -obj.yGridSize / 2, -obj.BaseThickness / 2),
            fc.Vector(0, 1, 0),
        )
        c2 = Part.makeCylinder(
            obj.ConnectionHoleDiameter / 2,
            obj.BaseThickness,
            fc.Vector(
                0,
                -obj.yGridSize / 2 + obj.yTotalWidth - obj.BaseThickness,
                -obj.BaseThickness / 2,
            ),
            fc.Vector(0, 1, 0),
        )

        c3 = Part.makeCylinder(
            obj.ConnectionHoleDiameter / 2,
            obj.BaseThickness,
            fc.Vector(-obj.xGridSize / 2, 0, -obj.BaseThickness / 2),
            fc.Vector(1, 0, 0),
        )
        c4 = Part.makeCylinder(
            obj.ConnectionHoleDiameter / 2,
            obj.BaseThickness,
            fc.Vector(
                -obj.xGridSize / 2 + obj.xTotalWidth - obj.BaseThickness,
                0,
                -obj.BaseThickness / 2,
            ),
            fc.Vector(1, 0, 0),
        )

        hx1 = c1.fuse(c2)
        hx2: Part.Shape | None = None

        xtranslate = zeromm
        for _ in range(int(obj.xTotalWidth.Value / obj.xGridSize.Value)):
            hx1 = hx1.copy()
            hx1.translate(fc.Vector(xtranslate, zeromm))
            hx2 = hx1 if hx2 is None else hx2.fuse(hx1)
            xtranslate += obj.xGridSize

        hy1 = c3.fuse(c4)
        hy2: Part.Shape | None = None

        ytranslate = zeromm
        for _ in range(int(obj.yTotalWidth.Value / obj.yGridSize.Value)):
            hy1_copy = hy1.copy()
            hy1_copy.translate(fc.Vector(zeromm, ytranslate))
            hy2 = hy1_copy if hy2 is None else hy2.fuse(hy1_copy)
            ytranslate += obj.yGridSize

        fuse_total = hx2.fuse(hy2)
        fuse_total = fuse_total.translate(
            fc.Vector(
                obj.xGridSize / 2 - obj.xLocationOffset,
                obj.yGridSize / 2 - obj.yLocationOffset,
            ),
        )

        return fuse_total


def _center_cut_wire(obj: fc.DocumentObject) -> Part.Wire:
    """Create wire for the baseplate center cut."""
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

    mec_middle = fc.Vector(0, 0, 0)

    v1 = fc.Vector(0, -y_inframedis)
    v2 = fc.Vector(-x_smfilloffcen, -y_inframedis)
    v3 = fc.Vector(-x_magedge, -y_smfillins)
    v4 = fc.Vector(-x_magedge, -y_magcenter)
    v5 = fc.Vector(-x_magcenter, -y_magedge)
    v6 = fc.Vector(-x_smfillins, -y_magedge)
    v7 = fc.Vector(-x_inframedis, -y_smfilloffcen)
    v8 = fc.Vector(-x_inframedis, 0)

    va1 = fc.Vector(-x_smfillposmag, -y_smfillpos)
    va2 = fc.Vector(-x_bigfillpos, -y_bigfillpos)
    va3 = fc.Vector(-x_smfillpos, -y_smfillposmag)

    l1 = Part.LineSegment(v1, v2)
    ar1 = Part.Arc(l1.EndPoint, va1, v3)
    l2 = Part.LineSegment(ar1.EndPoint, v4)
    ar2 = Part.Arc(l2.EndPoint, va2, v5)
    l3 = Part.LineSegment(ar2.EndPoint, v6)
    ar3 = Part.Arc(l3.EndPoint, va3, v7)
    l4 = Part.LineSegment(ar3.EndPoint, v8)
    l5 = Part.LineSegment(l4.EndPoint, mec_middle)
    l6 = Part.LineSegment(l5.EndPoint, l1.StartPoint)

    return utils.curve_to_wire([l1, ar1, l2, ar2, l3, ar3, l4, l5, l6])


class BaseplateCenterCut:
    """Cut out the center section of each baseplate grid."""

    def __init__(self, obj: fc.DocumentObject) -> None:
        """Cut out the  center section of each baseplate grid.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """
        obj.addProperty(
            "App::PropertyLength",
            "SmallFillet",
            "NonStandard",
            "Fillets of the main cutout in each grid of the baseplate <br> <br> default = 1 mm",
        ).SmallFillet = const.BASEPLATE_SMALL_FILLET

    def make(self, obj: fc.DocumentObject, layout: GridfinityLayout) -> Part.Shape:
        """Create baseplate center cutout.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            layout (GridfinityLayout): 2 dimentional list of feature locations.

        Returns:
            Part.Shape: Baseplate center cutout shape.

        """
        wire = _center_cut_wire(obj)

        partial_shape1 = Part.Face(wire).extrude(fc.Vector(0, 0, -obj.TotalHeight))
        partial_shape2 = partial_shape1.mirror(fc.Vector(0, 0, 0), fc.Vector(0, 1, 0))
        partial_shape3 = partial_shape1.mirror(fc.Vector(0, 0, 0), fc.Vector(1, 0, 0))
        partial_shape4 = partial_shape2.mirror(fc.Vector(0, 0, 0), fc.Vector(1, 0, 0))

        shape = partial_shape1.multiFuse([partial_shape2, partial_shape3, partial_shape4])

        vec_list: list[fc.Vector] = []
        xtranslate = 0
        ytranslate = 0

        for col in layout:
            ytranslate = 0
            for cell in col:
                if cell:
                    vec_list.append(fc.Vector(xtranslate, ytranslate))
                ytranslate += obj.yGridSize.Value
            xtranslate += obj.xGridSize.Value

        fuse_total = utils.copy_and_translate(shape, vec_list)

        return fuse_total.translate(
            fc.Vector(
                obj.xGridSize / 2 - obj.xLocationOffset,
                obj.yGridSize / 2 - obj.yLocationOffset,
            ),
        )


class BaseplateBaseValues:
    """Add bin base properties and calculate values."""

    def __init__(self, obj: fc.DocumentObject) -> None:
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
        ).BaseProfileBottomChamfer = const.BASEPLATE_BOTTOM_CHAMFER

        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileVerticalSection",
            "zzExpertOnly",
            "Height of the vertical section in bin base profile",
            1,
        ).BaseProfileVerticalSection = const.BASEPLATE_VERTICAL_SECTION

        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileTopChamfer",
            "zzExpertOnly",
            "Height of the top chamfer in the bin base profile",
            1,
        ).BaseProfileTopChamfer = const.BASEPLATE_TOP_CHAMFER

        obj.addProperty(
            "App::PropertyLength",
            "BinOuterRadius",
            "zzExpertOnly",
            "Outer radius of the bin",
            1,
        ).BinOuterRadius = const.BASEPLATE_OUTER_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "BinVerticalRadius",
            "zzExpertOnly",
            "Radius of the base profile Vertical section",
            1,
        ).BinVerticalRadius = const.BASEPLATE_VERTICAL_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "BinBottomRadius",
            "zzExpertOnly",
            "bottom of bin corner radius",
            1,
        ).BinBottomRadius = const.BASEPLATE_BOTTOM_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "Clearance",
            "zzExpertOnly",
            ("The Clearance between bin and baseplate <br> <br>default = 0.25 mm"),
        ).Clearance = const.CLEARANCE

        obj.addProperty(
            "App::PropertyLength",
            "BaseplateTopLedgeWidth",
            "zzExpertOnly",
            "Top ledge of baseplate, doubled between grids <br> <br> default = 0.4 mm",
            1,
        ).BaseplateTopLedgeWidth = const.BASEPLATE_TOP_LEDGE_WIDTH

    def make(self, obj: fc.DocumentObject) -> None:
        """Generate Rectanble layout and calculate relevant parameters.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """
        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )


class BaseplateSolidShape:
    """Create Solid which the baseplate is cut from."""

    def __init__(
        self,
        obj: fc.DocumentObject,
    ) -> None:
        """Make solid which the baseplate is cut from.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            baseplate_type (str): is the object a mbaseplate with magnets
            screw_together_baseplate_default: boolean

        """
        obj.addProperty(
            "App::PropertyLength",
            "TotalHeight",
            "ReferenceDimensions",
            "total height of the bin",
            1,
        )

    def make(
        self,
        obj: fc.DocumentObject,
        baseplate_outside_shape: Part.Wire,
        *,
        baseplate_type: str,
    ) -> Part.Shape:
        """Create solid which baseplate is cut from.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            baseplate_outside_shape (Part.Wire): outside profile of the baseplate shape
            baseplate_type (str): type of baseplate being generated

        Returns:
            Part.Shape: Extruded part for the baseplate to be cut from.

        """
        ## Calculated Parameters
        if baseplate_type == "magnet":
            obj.TotalHeight = obj.BaseProfileHeight + obj.MagnetHoleDepth + obj.MagnetBase
        elif baseplate_type == "screw_together":
            obj.TotalHeight = obj.BaseProfileHeight + obj.BaseThickness
        else:
            obj.TotalHeight = obj.BaseProfileHeight

        ## Baseplate Solid Shape Generation
        face = Part.Face(baseplate_outside_shape)

        fuse_total = face.extrude(fc.Vector(0, 0, obj.TotalHeight))
        fuse_total = fuse_total.translate(fc.Vector(-obj.xLocationOffset, -obj.yLocationOffset))

        return fuse_total
