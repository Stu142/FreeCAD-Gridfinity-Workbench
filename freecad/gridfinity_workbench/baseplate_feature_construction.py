"""Base plate feature module.

Contains implementation to conscruct baseplate features.
"""

import math

import FreeCAD as fc  # noqa: N813
import Part

from . import const, utils
from . import magnet_hole as magnet_hole_module
from .utils import GridfinityLayout


def magnet_holes_properties(obj: fc.DocumentObject) -> None:
    """Make baseplate magnet holes."""
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
    ).MagnetHolesShape = const.HOLE_SHAPES

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

    ## Gridfinity Expert Only Parameters
    obj.addProperty(
        "App::PropertyLength",
        "MagnetHoleDistanceFromEdge",
        "zzExpertOnly",
        "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",
        read_only=True,
    ).MagnetHoleDistanceFromEdge = const.MAGNET_HOLE_DISTANCE_FROM_EDGE

    ## Gridfinity Hidden Properties
    obj.addProperty(
        "App::PropertyLength",
        "BaseThickness",
        "Hidden",
        "Thickness of base under the normal baseplate  profile <br> <br> default = 6.4 mm",
        hidden=True,
    ).BaseThickness = const.BASE_THICKNESS

    obj.addProperty(
        "App::PropertyBool",
        "MagnetHoles",
        "ShouldBeHidden",
        "MagnetHoles",
        hidden=True,
    ).MagnetHoles = const.MAGNET_HOLES


def make_magnet_holes(obj: fc.DocumentObject, layout: GridfinityLayout) -> Part.Shape:
    """Create magentholes for a baseplate."""
    x_hole_pos = obj.xGridSize / 2 - obj.MagnetHoleDistanceFromEdge
    y_hole_pos = obj.yGridSize / 2 - obj.MagnetHoleDistanceFromEdge

    # Magnet holes
    shape = magnet_hole_module.from_obj(obj)
    shape = shape.translate(fc.Vector(0, 0, -obj.MagnetHoleDepth))
    screw_hole = Part.makeCylinder(
        obj.MagnetBaseHole / 2,
        obj.MagnetHoleDepth + obj.BaseThickness,
        fc.Vector(0, 0, 0),
        fc.Vector(0, 0, -1),
    )
    shape = shape.fuse(screw_hole)
    shape = utils.copy_and_translate(shape, utils.corners(x_hole_pos, y_hole_pos))

    shape.translate(fc.Vector(obj.xGridSize / 2, obj.yGridSize / 2))

    shape = utils.copy_in_layout(shape, layout, obj.xGridSize, obj.yGridSize)
    return shape.translate(fc.Vector(-obj.xLocationOffset, -obj.yLocationOffset))


def screw_bottom_chamfer_properties(obj: fc.DocumentObject) -> None:
    """Create Baseplate Connection Holes."""
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


def make_screw_bottom_chamfer(obj: fc.DocumentObject, layout: GridfinityLayout) -> Part.Shape:
    """Create screw chamfer for a baseplate."""
    x_hole_pos = obj.xGridSize / 2 - obj.MagnetHoleDistanceFromEdge
    y_hole_pos = obj.yGridSize / 2 - obj.MagnetHoleDistanceFromEdge

    ch = Part.makeCone(
        obj.ScrewHoleDiameter / 2 + obj.MagnetBottomChamfer,
        obj.ScrewHoleDiameter / 2,
        obj.MagnetBottomChamfer,
        fc.Vector(0, 0, -obj.TotalHeight + obj.BaseProfileHeight),
    )

    hm1 = utils.copy_and_translate(ch, utils.corners(x_hole_pos, y_hole_pos))
    hm2 = utils.copy_in_layout(hm1, layout, obj.xGridSize, obj.yGridSize)
    return hm2.translate(
        fc.Vector(obj.xGridSize / 2 - obj.xLocationOffset, obj.yGridSize / 2 - obj.yLocationOffset),
    )


def connection_holes_properties(obj: fc.DocumentObject) -> None:
    """Create Baseplate Connection Holes."""
    ## Gridfinity Non Standard Parameters
    obj.addProperty(
        "App::PropertyLength",
        "ConnectionHoleDiameter",
        "NonStandard",
        "Holes on the sides to connect multiple baseplates together <br> <br> default = 3.2 mm",
    ).ConnectionHoleDiameter = const.CONNECTION_HOLE_DIAMETER


def make_connection_holes(obj: fc.DocumentObject, layout: GridfinityLayout) -> Part.Shape:
    """Create connection holes for a baseplate."""
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

    vec_list = [fc.Vector(x * obj.xGridSize, 0) for x in range(len(layout))]
    hx = utils.copy_and_translate(c1.fuse(c2), vec_list)

    vec_list = [fc.Vector(0, y * obj.yGridSize) for y in range(len(layout[-1]))]
    hy = utils.copy_and_translate(c3.fuse(c4), vec_list)

    fuse_total = hx.fuse(hy)
    fuse_total = fuse_total.translate(
        fc.Vector(obj.xGridSize / 2 - obj.xLocationOffset, obj.yGridSize / 2 - obj.yLocationOffset),
    )

    return fuse_total


def _center_cut_face(obj: fc.DocumentObject) -> Part.Face:
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

    return utils.curve_to_face([l1, ar1, l2, ar2, l3, ar3, l4, l5, l6])


def center_cut_properties(obj: fc.DocumentObject) -> None:
    """Cut out the  center section of each baseplate grid."""
    obj.addProperty(
        "App::PropertyLength",
        "SmallFillet",
        "NonStandard",
        "Fillets of the main cutout in each grid of the baseplate <br> <br> default = 1 mm",
    ).SmallFillet = const.BASEPLATE_SMALL_FILLET


def make_center_cut(obj: fc.DocumentObject, layout: GridfinityLayout) -> Part.Shape:
    """Create baseplate center cutout."""
    face = _center_cut_face(obj)

    partial_shape1 = face.extrude(fc.Vector(0, 0, -obj.TotalHeight))
    partial_shape2 = partial_shape1.mirror(fc.Vector(0, 0, 0), fc.Vector(0, 1, 0))
    partial_shape3 = partial_shape1.mirror(fc.Vector(0, 0, 0), fc.Vector(1, 0, 0))
    partial_shape4 = partial_shape2.mirror(fc.Vector(0, 0, 0), fc.Vector(1, 0, 0))

    shape = partial_shape1.multiFuse([partial_shape2, partial_shape3, partial_shape4])

    fuse_total = utils.copy_in_layout(shape, layout, obj.xGridSize, obj.yGridSize)

    return fuse_total.translate(
        fc.Vector(obj.xGridSize / 2 - obj.xLocationOffset, obj.yGridSize / 2 - obj.yLocationOffset),
    )


def base_values_properties(obj: fc.DocumentObject) -> None:
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
        read_only=True,
    )

    ## Expert Only Parameters
    obj.addProperty(
        "App::PropertyLength",
        "BaseProfileBottomChamfer",
        "zzExpertOnly",
        "height of chamfer in bottom of bin base profile <br> <br> default = 0.8 mm",
        read_only=True,
    ).BaseProfileBottomChamfer = const.BASEPLATE_BOTTOM_CHAMFER

    obj.addProperty(
        "App::PropertyLength",
        "BaseProfileVerticalSection",
        "zzExpertOnly",
        "Height of the vertical section in bin base profile",
        read_only=True,
    ).BaseProfileVerticalSection = const.BASEPLATE_VERTICAL_SECTION

    obj.addProperty(
        "App::PropertyLength",
        "BaseProfileTopChamfer",
        "zzExpertOnly",
        "Height of the top chamfer in the bin base profile",
        read_only=True,
    ).BaseProfileTopChamfer = const.BASEPLATE_TOP_CHAMFER

    obj.addProperty(
        "App::PropertyLength",
        "BinOuterRadius",
        "zzExpertOnly",
        "Outer radius of the bin",
        read_only=True,
    ).BinOuterRadius = const.BASEPLATE_OUTER_RADIUS

    obj.addProperty(
        "App::PropertyLength",
        "BinVerticalRadius",
        "zzExpertOnly",
        "Radius of the base profile Vertical section",
        read_only=True,
    ).BinVerticalRadius = const.BASEPLATE_VERTICAL_RADIUS

    obj.addProperty(
        "App::PropertyLength",
        "BinBottomRadius",
        "zzExpertOnly",
        "bottom of bin corner radius",
        read_only=True,
    ).BinBottomRadius = const.BASEPLATE_BOTTOM_RADIUS

    obj.addProperty(
        "App::PropertyLength",
        "Clearance",
        "zzExpertOnly",
        "The Clearance between bin and baseplate <br> <br>default = 0.25 mm",
    ).Clearance = const.CLEARANCE

    obj.addProperty(
        "App::PropertyLength",
        "BaseplateTopLedgeWidth",
        "zzExpertOnly",
        "Top ledge of baseplate, doubled between grids <br> <br> default = 0.4 mm",
        read_only=True,
    ).BaseplateTopLedgeWidth = const.BASEPLATE_TOP_LEDGE_WIDTH

    ## Expressions
    obj.setExpression(
        "BaseProfileHeight",
        "BaseProfileBottomChamfer + BaseProfileVerticalSection + BaseProfileTopChamfer",
    )


def solid_shape_properties(obj: fc.DocumentObject) -> None:
    """Make solid which the baseplate is cut from."""
    obj.addProperty(
        "App::PropertyLength",
        "TotalHeight",
        "ReferenceDimensions",
        "total height of the bin",
        read_only=True,
    )


def make_solid_shape(
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
