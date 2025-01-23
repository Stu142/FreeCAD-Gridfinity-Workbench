"""Module containing gridfinity feature constructions."""

import math

import FreeCAD
import Part
from FreeCAD import Units

from .utils import Utils

unitmm = Units.Quantity("1 mm")
zeromm = Units.Quantity("0 mm")

SMALL_NUMBER = 0.01


def _label_shelf_full_width(
    obj: FreeCAD.DocumentObject,
    face: Part.Face,
    xcompwidth: float,
) -> Part.Shape:
    xdiv = obj.xDividers + 1
    fw = obj.yTotalWidth - obj.WallThickness * 2
    ytranslate = -obj.BinUnit / 2 + obj.WallThickness
    xtranslate = zeromm
    parts = []
    for x in range(xdiv):
        ls = face.extrude(FreeCAD.Vector(0, fw, 0))

        ls.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

        if x == 0:
            firstls = ls
        else:
            parts.append(ls)

        xtranslate += xcompwidth + obj.DividerThickness

    funcfuse = ls if xdiv == 1 else Part.Solid.multiFuse(firstls, parts)

    x2 = -obj.BinUnit / 2 + obj.WallThickness
    b_edges = []
    for edge in funcfuse.Edges:
        y0 = edge.Vertexes[0].Point.y
        y1 = edge.Vertexes[1].Point.y
        x0 = edge.Vertexes[0].Point.x
        x1 = edge.Vertexes[1].Point.x

        if (y0 - y1) == 0 and x1 == x2 and x0 == x2:
            b_edges.append(edge)

    return funcfuse.makeFillet(obj.BinOuterRadius - obj.WallThickness, b_edges)


def _label_shelf_center(
    obj: FreeCAD.DocumentObject,
    xcompwidth: float,
    ycompwidth: float,
    face: Part.Face,
) -> Part.Shape:
    xdiv = obj.xDividers + 1
    ydiv = obj.yDividers + 1
    xtranslate = zeromm
    ysp = -obj.BinUnit / 2 + obj.WallThickness + ycompwidth / 2 - obj.LabelShelfLength / 2
    ytranslate = ysp
    parts = []
    for x in range(xdiv):
        ytranslate = ysp
        for y in range(ydiv):
            ls = face.extrude(FreeCAD.Vector(0, obj.LabelShelfLength, 0))

            ls.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

            if x == 0 and y == 0:
                firstls = ls
            else:
                parts.append(ls)

            ytranslate += ycompwidth + obj.DividerThickness

        xtranslate += xcompwidth + obj.DividerThickness

    return ls if xdiv == 1 and ydiv == 1 else Part.Solid.multiFuse(firstls, parts)


def _label_shelf_left(
    obj: FreeCAD.DocumentObject,
    xcompwidth: float,
    ycompwidth: float,
    face: Part.Face,
) -> Part.Shape:
    xdiv = obj.xDividers + 1
    ydiv = obj.yDividers + 1
    xtranslate = zeromm
    ysp = -obj.BinUnit / 2 + obj.WallThickness
    ytranslate = ysp
    parts = []
    for x in range(xdiv):
        ytranslate = ysp
        for y in range(ydiv):
            ls = face.extrude(FreeCAD.Vector(0, obj.LabelShelfLength, 0))

            ls.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

            if x == 0 and y == 0:
                firstls = ls
            else:
                parts.append(ls)

            ytranslate += ycompwidth + obj.DividerThickness

        xtranslate += xcompwidth + obj.DividerThickness

    funcfuse = ls if xdiv == 1 and ydiv == 1 else Part.Solid.multiFuse(firstls, parts)

    y2 = -obj.BinUnit / 2 + obj.WallThickness
    b_edges = []
    for edge in funcfuse.Edges:
        y0 = edge.Vertexes[0].Point.y
        y1 = edge.Vertexes[1].Point.y
        x0 = edge.Vertexes[0].Point.x
        x1 = edge.Vertexes[1].Point.x

        if y0 == y2 and y1 == y2 and x1 == y2 and x0 == y2:
            b_edges.append(edge)

    return funcfuse.makeFillet(obj.BinOuterRadius - obj.WallThickness, b_edges)


def _label_shelf_right(
    obj: FreeCAD.DocumentObject,
    xcompwidth: float,
    ycompwidth: float,
    face: Part.Face,
) -> Part.Shape:
    xdiv = obj.xDividers + 1
    ydiv = obj.yDividers + 1
    xtranslate = zeromm
    ysp = -obj.BinUnit / 2 + obj.WallThickness + ycompwidth - obj.LabelShelfLength
    ytranslate = ysp
    parts = []
    for x in range(xdiv):
        ytranslate = ysp
        for y in range(ydiv):
            ls = face.extrude(FreeCAD.Vector(0, obj.LabelShelfLength, 0))

            ls.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

            if x == 0 and y == 0:
                firstls = ls
            else:
                parts.append(ls)

            ytranslate += ycompwidth + obj.DividerThickness

        xtranslate += xcompwidth + obj.DividerThickness

    funcfuse = ls if xdiv == 1 and ydiv == 1 else Part.Solid.multiFuse(firstls, parts)

    y2 = obj.yTotalWidth - obj.BinUnit / 2 - obj.WallThickness
    x2 = -obj.BinUnit / 2 + obj.WallThickness
    b_edges = []
    for edge in funcfuse.Edges:
        y0 = edge.Vertexes[0].Point.y
        y1 = edge.Vertexes[1].Point.y
        x0 = edge.Vertexes[0].Point.x
        x1 = edge.Vertexes[1].Point.x

        if y0 == y2 and y1 == y2 and x1 == x2 and x0 == x2:
            b_edges.append(edge)

    return funcfuse.makeFillet(obj.BinOuterRadius - obj.WallThickness, b_edges)


def _label_shelf_fillet(
    obj: FreeCAD.DocumentObject,
    shape: Part.Shape,
    stackingoffset: float,
) -> Part.Shape:
    h_edges = []
    for edge in shape.Edges:
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z

        if (
            z0 == -obj.LabelShelfVerticalThickness + stackingoffset
            and z1 == -obj.LabelShelfVerticalThickness + stackingoffset
        ):
            h_edges.append(edge)

    return shape.makeFillet(
        obj.LabelShelfVerticalThickness.Value - 0.01,
        h_edges,
    )


def make_label_shelf(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create label shelf.

    Args:
        obj (FreeCAD.DocumentObject): Document object.

    Returns:
        Part.Shape: Labelshelf 3D shape.

    """
    towall = -obj.BinUnit / 2 + obj.WallThickness
    tolabelend = (
        -obj.BinUnit / 2
        + obj.StackingLipTopChamfer
        + obj.StackingLipTopLedge
        + obj.StackingLipBottomChamfer
        + obj.LabelShelfWidth
    )
    stackingoffset = -obj.LabelShelfStackingOffset if obj.StackingLip else 0 * unitmm
    shelf_angle = obj.LabelShelfAngle.Value
    shelf_placement = obj.LabelShelfPlacement

    xdiv = obj.xDividers + 1
    ydiv = obj.yDividers + 1
    xcompwidth = (
        obj.xTotalWidth - obj.WallThickness * 2 - obj.DividerThickness * obj.xDividers
    ) / (xdiv)
    ycompwidth = (
        obj.yTotalWidth - obj.WallThickness * 2 - obj.DividerThickness * obj.yDividers
    ) / (ydiv)

    if obj.LabelShelfStyle == "Overhang":
        shelf_angle = 0
        shelf_placement = "Full Width"

    # Calculate V4 Z coordinate by using an angle
    side_a = abs(towall - tolabelend)
    beta = shelf_angle
    alpha = 90 - beta
    side_c = side_a / math.sin(math.radians(alpha))
    side_b = math.sqrt(-pow(side_a, 2) + pow(side_c, 2))
    v4_z = -obj.LabelShelfVerticalThickness - side_b * unitmm

    v1 = FreeCAD.Vector(towall, 0, stackingoffset)
    v2 = FreeCAD.Vector(tolabelend, 0, stackingoffset)
    v3 = FreeCAD.Vector(tolabelend, 0, -obj.LabelShelfVerticalThickness + stackingoffset)
    v4 = FreeCAD.Vector(towall, 0, v4_z + stackingoffset)

    l1 = Part.LineSegment(v1, v2)
    l2 = Part.LineSegment(v2, v3)
    l3 = Part.LineSegment(v3, v4)
    l4 = Part.LineSegment(v4, v1)

    s1 = Part.Shape([l1, l2, l3, l4])

    wire = Part.Wire(s1.Edges)

    face = Part.Face(wire)

    if obj.LabelShelfLength > ycompwidth:
        shelf_placement = "Full Width"

    # Label placement specific code
    if shelf_placement == "Full Width":
        funcfuse = _label_shelf_full_width(obj, face, xcompwidth)
    if shelf_placement == "Center":
        funcfuse = _label_shelf_center(obj, xcompwidth, ycompwidth, face)
    if shelf_placement == "Left":
        funcfuse = _label_shelf_left(obj, xcompwidth, ycompwidth, face)
    if shelf_placement == "Right":
        funcfuse = _label_shelf_right(obj, xcompwidth, ycompwidth, face)

    # For all label placements
    funcfuse = _label_shelf_fillet(obj, funcfuse, stackingoffset)

    labelshelfheight = obj.LabelShelfVerticalThickness + side_b * unitmm
    if (labelshelfheight) > obj.UsableHeight:
        ytranslate = -obj.BinUnit / 2 + obj.WallThickness
        xtranslate = zeromm
        bottomcutbox = Part.makeBox(
            labelshelfheight,
            obj.StackingLipTopChamfer
            + obj.StackingLipTopLedge
            + obj.StackingLipBottomChamfer
            + obj.LabelShelfWidth
            - obj.WallThickness,
            obj.yTotalWidth,
            FreeCAD.Vector(
                towall,
                0,
                -obj.UsableHeight - labelshelfheight + stackingoffset,
            ),
            FreeCAD.Vector(0, 1, 0),
        )

        vec_list = []
        for _ in range(xdiv):
            vec_list.append(FreeCAD.Vector(xtranslate, ytranslate, 0))
            xtranslate += xcompwidth + obj.DividerThickness

        funcfuse = Part.Shape.cut(funcfuse, Utils.copy_and_translate(bottomcutbox, vec_list))
    return funcfuse


def make_scoop(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create scoop feature.

    Args:
        obj (FreeCAD.DocumentObject): Document object.

    Returns:
        Part.Shape: 3d scoop object.

    """
    scooprad1 = obj.ScoopRadius + 1 * unitmm
    scooprad2 = obj.ScoopRadius + 1 * unitmm
    scooprad3 = obj.ScoopRadius + 1 * unitmm

    xcomp_w = (obj.xTotalWidth - obj.WallThickness * 2 - obj.xDividers * obj.DividerThickness) / (
        obj.xDividers + 1
    )

    xdivscoop = obj.xDividerHeight - obj.HeightUnitValue

    if obj.ScoopRadius > xdivscoop and obj.xDividerHeight != 0:
        scooprad1 = xdivscoop - unitmm
    if obj.ScoopRadius > xcomp_w and obj.xDividers > 0:
        scooprad2 = xcomp_w - 2 * unitmm
    if obj.ScoopRadius > obj.UsableHeight > 0:
        scooprad3 = obj.UsableHeight

    scooprad = min(obj.ScoopRadius, scooprad1, scooprad2, scooprad3)

    if scooprad <= 0:
        FreeCAD.Console.PrintMessage(
            "scooop could not be made due to bin selected parameters\n",
        )
        return None

    v1 = FreeCAD.Vector(
        obj.xTotalWidth - obj.BinUnit / 2 - obj.WallThickness,
        0,
        -obj.UsableHeight + scooprad,
    )
    v2 = FreeCAD.Vector(
        obj.xTotalWidth - obj.BinUnit / 2 - obj.WallThickness,
        0,
        -obj.UsableHeight,
    )
    v3 = FreeCAD.Vector(
        obj.xTotalWidth - obj.BinUnit / 2 - obj.WallThickness - scooprad,
        0,
        -obj.UsableHeight,
    )

    l1 = Part.LineSegment(v1, v2)
    l2 = Part.LineSegment(v2, v3)

    vc1 = FreeCAD.Vector(
        obj.xTotalWidth
        - obj.BinUnit / 2
        - obj.WallThickness
        - scooprad
        + scooprad * math.sin(math.pi / 4),
        0,
        -obj.UsableHeight + scooprad - scooprad * math.sin(math.pi / 4),
    )

    c1 = Part.Arc(v1, vc1, v3)

    s1 = Part.Shape([l1, l2, c1])

    wire = Part.Wire(s1.Edges)

    face = Part.Face(wire)

    xdiv = obj.xDividers + 1
    xtranslate = (
        0 * unitmm
        - obj.WallThickness
        + obj.StackingLipTopLedge
        + obj.StackingLipTopChamfer
        + obj.StackingLipBottomChamfer
    )
    compwidth = (obj.xTotalWidth - obj.WallThickness * 2 - obj.DividerThickness * obj.xDividers) / (
        xdiv
    )

    scoopbox = Part.makeBox(
        obj.StackingLipBottomChamfer
        + obj.StackingLipTopChamfer
        + obj.StackingLipTopLedge
        - obj.WallThickness,
        obj.yTotalWidth - obj.WallThickness * 2,
        obj.UsableHeight,
        FreeCAD.Vector(
            obj.xTotalWidth - obj.BinUnit / 2 - obj.WallThickness,
            -obj.BinUnit / 2 + obj.WallThickness,
            0,
        ),
        FreeCAD.Vector(0, 0, -1),
    )

    scoop = face.extrude(FreeCAD.Vector(0, obj.yTotalWidth - obj.WallThickness * 2, 0))

    vec_list = []
    for x in range(xdiv):
        vec_list.append(FreeCAD.Vector(-xtranslate, -obj.BinUnit / 2 + obj.WallThickness, 0))

        if x > 0:
            xtranslate += compwidth + obj.DividerThickness
        else:
            xtranslate += (
                +obj.WallThickness
                - obj.StackingLipTopLedge
                - obj.StackingLipTopChamfer
                - obj.StackingLipBottomChamfer
                + compwidth
                + obj.DividerThickness
            )

    funcfuse = Utils.copy_and_translate(scoop, vec_list)
    funcfuse = funcfuse.fuse(scoopbox)

    b_edges = []
    for edge in funcfuse.Edges:
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z
        x0 = edge.Vertexes[0].Point.x
        x1 = edge.Vertexes[1].Point.x

        hdif = abs(z0 - z1)
        if hdif == obj.UsableHeight and x0 == x1:
            b_edges.append(edge)

    return funcfuse.makeFillet(
        obj.StackingLipBottomChamfer
        + obj.StackingLipTopChamfer
        + obj.StackingLipTopLedge
        - obj.WallThickness
        - 0.01 * unitmm,
        b_edges,
    )


def make_stacking_lip(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create stacking lip.

    Args:
        obj (FreeCAD.DocumentObject): Document object.

    Returns:
        Part.Shape: Stackinglip 3D object.

    """
    stacking_lip_path = Utils.create_rounded_rectangle(
        obj.xTotalWidth,
        obj.yTotalWidth,
        0,
        obj.BinOuterRadius,
    )
    stacking_lip_path.translate(
        FreeCAD.Vector(
            obj.xTotalWidth / 2 - obj.BinUnit / 2,
            obj.yTotalWidth / 2 - obj.BinUnit / 2,
            0,
        ),
    )
    st1 = FreeCAD.Vector(-obj.BinUnit / 2, 0, 0)
    st2 = FreeCAD.Vector(
        -obj.BinUnit / 2,
        0,
        obj.StackingLipBottomChamfer + obj.StackingLipVerticalSection + obj.StackingLipTopChamfer,
    )
    st3 = FreeCAD.Vector(
        -obj.BinUnit / 2 + obj.StackingLipTopLedge,
        0,
        obj.StackingLipBottomChamfer + obj.StackingLipVerticalSection + obj.StackingLipTopChamfer,
    )
    st4 = FreeCAD.Vector(
        -obj.BinUnit / 2 + obj.StackingLipTopLedge + obj.StackingLipTopChamfer,
        0,
        obj.StackingLipBottomChamfer + obj.StackingLipVerticalSection,
    )
    st5 = FreeCAD.Vector(
        -obj.BinUnit / 2 + obj.StackingLipTopLedge + obj.StackingLipTopChamfer,
        0,
        obj.StackingLipBottomChamfer,
    )
    st6 = FreeCAD.Vector(
        -obj.BinUnit / 2
        + obj.StackingLipTopLedge
        + obj.StackingLipTopChamfer
        + obj.StackingLipBottomChamfer,
        0,
        0,
    )
    st7 = FreeCAD.Vector(
        -obj.BinUnit / 2
        + obj.StackingLipTopLedge
        + obj.StackingLipTopChamfer
        + obj.StackingLipBottomChamfer,
        0,
        -obj.StackingLipVerticalSection,
    )
    st8 = FreeCAD.Vector(
        -obj.BinUnit / 2 + obj.WallThickness,
        0,
        -obj.StackingLipVerticalSection
        - (
            obj.StackingLipTopLedge
            + obj.StackingLipTopChamfer
            + obj.StackingLipBottomChamfer
            - obj.WallThickness
        ),
    )
    st9 = FreeCAD.Vector(-obj.BinUnit / 2 + obj.WallThickness, 0, 0)

    stl1 = Part.LineSegment(st1, st2)
    stl2 = Part.LineSegment(st2, st3)
    stl3 = Part.LineSegment(st3, st4)
    stl4 = Part.LineSegment(st4, st5)
    stl5 = Part.LineSegment(st5, st6)
    stl6 = Part.LineSegment(st6, st7)
    stl7 = Part.LineSegment(st7, st8)
    stl8 = Part.LineSegment(st8, st9)
    stl9 = Part.LineSegment(st9, st1)

    sts1 = Part.Shape([stl1, stl2, stl3, stl4, stl5, stl6, stl7, stl8, stl9])

    wire = Part.Wire(sts1.Edges)

    stacking_lip = Part.Wire(stacking_lip_path).makePipe(wire)

    return Part.makeSolid(stacking_lip)


def _make_compartments_no_deviders(
    obj: FreeCAD.DocumentObject,
    func_fuse: Part.Shape,
) -> Part.Shape:
    # Fillet Bottom edges
    b_edges = []
    for edge in func_fuse.Edges:
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z
    # Fillet Bottom edges
    b_edges = []
    for edge in func_fuse.Edges:
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z

        if z0 < 0 and z1 < 0:
            b_edges.append(edge)

    return func_fuse.makeFillet(obj.InsideFilletRadius, b_edges)


def _make_compartments_with_deviders(
    obj: FreeCAD.DocumentObject,
    func_fuse: Part.Shape,
) -> Part.Shape:
    xdivheight = obj.xDividerHeight if obj.xDividerHeight != 0 else obj.TotalHeight
    ydivheight = obj.yDividerHeight if obj.yDividerHeight != 0 else obj.TotalHeight

    stackingoffset = -obj.LabelShelfStackingOffset if obj.StackingLip else 0 * unitmm

    xcomp_w = (obj.xTotalWidth - obj.WallThickness * 2 - obj.xDividers * obj.DividerThickness) / (
        obj.xDividers + 1
    )
    ycomp_w = (obj.yTotalWidth - obj.WallThickness * 2 - obj.yDividers * obj.DividerThickness) / (
        obj.yDividers + 1
    )

    xtranslate = zeromm + xcomp_w + obj.WallThickness - obj.DividerThickness
    ytranslate = zeromm + ycomp_w + obj.WallThickness

    # dividers in x direction
    xdiv: Part.Shape | None = None
    for _ in range(obj.xDividers):
        comp = Part.makeBox(
            obj.DividerThickness,
            obj.yTotalWidth,
            xdivheight + stackingoffset,
            FreeCAD.Vector(
                -obj.BinUnit / 2 + obj.DividerThickness,
                -obj.BinUnit / 2,
                -obj.TotalHeight,
            ),
            FreeCAD.Vector(0, 0, 1),
        )
        comp.translate(FreeCAD.Vector(xtranslate, 0, 0))
        xdiv = comp if xdiv is None else xdiv.fuse(comp)
        xtranslate += xcomp_w + obj.DividerThickness

    # dividers in y direction
    ydiv: Part.Shape | None = None
    for _ in range(obj.yDividers):
        comp = Part.makeBox(
            obj.xTotalWidth,
            obj.DividerThickness,
            ydivheight + stackingoffset,
            FreeCAD.Vector(-obj.BinUnit / 2, -obj.BinUnit / 2, -obj.TotalHeight),
            FreeCAD.Vector(0, 0, 1),
        )

        comp.translate(FreeCAD.Vector(0, ytranslate, 0))
        ydiv = comp if ydiv is None else ydiv.fuse(comp)
        ytranslate += ycomp_w + obj.DividerThickness

    if xdiv:
        func_fuse = func_fuse.cut(xdiv)
    if ydiv:
        func_fuse = func_fuse.cut(ydiv)
    b_edges = []
    for edge in func_fuse.Edges:
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z

        if z0 != z1:
            b_edges.append(edge)

        if z0 <= -obj.UsableHeight and z1 <= -obj.UsableHeight:
            b_edges.append(edge)

    return func_fuse.makeFillet(obj.InsideFilletRadius, b_edges)


def make_compartments(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create compartment cutout objects.

    Args:
        obj (FreeCAD.DocumentObject): Document object.

    Returns:
        Part.Shape: Compartments cutout shape.

    """
    func_fuse = Utils.rounded_rectangle_extrude(
        obj.xTotalWidth - obj.WallThickness * 2,
        obj.yTotalWidth - obj.WallThickness * 2,
        -obj.UsableHeight,
        obj.UsableHeight,
        obj.BinOuterRadius - obj.WallThickness,
    )
    func_fuse.translate(
        FreeCAD.Vector(
            obj.xTotalWidth / 2 - obj.BinUnit / 2,
            obj.yTotalWidth / 2 - obj.BinUnit / 2,
            0,
        ),
    )

    if obj.xDividers == 0 and obj.yDividers == 0:
        func_fuse = _make_compartments_no_deviders(obj, func_fuse)

    else:
        func_fuse = _make_compartments_with_deviders(obj, func_fuse)

    return func_fuse


def make_bin_base(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create bin base.

    Args:
        obj (FreeCAD.DocumentObject): Document object.

    Returns:
        Part.Shape: Binbase 3D shape.

    """
    bt_cmf_width = obj.BinUnit - 2 * obj.BaseProfileBottomChamfer - 2 * obj.BaseProfileTopChamfer
    vert_width = obj.BinUnit - 2 * obj.BaseProfileTopChamfer
    xtranslate = zeromm
    ytranslate = zeromm
    assembly1: Part.Shape | None = None
    assembly2: Part.Shape | None = None

    for _ in range(obj.xGridUnits):
        ytranslate = zeromm
        for _ in range(obj.yGridUnits):
            bottom_chamfer = Utils.rounded_rectangle_chamfer(
                bt_cmf_width,
                bt_cmf_width,
                -obj.TotalHeight,
                obj.BaseProfileBottomChamfer,
                obj.BinBottomRadius,
            )

            vertical_section = Utils.rounded_rectangle_extrude(
                vert_width,
                vert_width,
                -obj.TotalHeight + obj.BaseProfileBottomChamfer,
                obj.BaseProfileVerticalSection,
                obj.BinVerticalRadius,
            )
            assembly = Part.Shape.fuse(bottom_chamfer, vertical_section)
            vertical_section = Utils.rounded_rectangle_extrude(
                vert_width,
                vert_width,
                -obj.TotalHeight + obj.BaseProfileBottomChamfer,
                obj.BaseProfileVerticalSection,
                obj.BinVerticalRadius,
            )
            assembly = Part.Shape.fuse(bottom_chamfer, vertical_section)

            top_chamfer = Utils.rounded_rectangle_chamfer(
                vert_width,
                vert_width,
                -obj.TotalHeight + obj.BaseProfileBottomChamfer + obj.BaseProfileVerticalSection,
                obj.BaseProfileTopChamfer,
                obj.BinVerticalRadius,
            )
            assembly = Part.Solid.fuse(assembly, top_chamfer)

            assembly.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

            assembly1 = assembly if assembly1 is None else assembly1.fuse(assembly)
            ytranslate += obj.GridSize

        assembly2 = assembly1 if assembly2 is None else assembly2.fuse(assembly1)
        xtranslate += obj.GridSize

    return assembly2


def make_baseplate_center_cut(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create baseplate center cutout.

    Args:
        obj (FreeCAD.DocumentObject): Document object.

    Returns:
        Part.Shape: Baseplate center cutout shape.

    """
    inframedis = (
        obj.GridSize / 2
        - obj.BaseProfileTopChamfer
        - obj.BaseProfileBottomChamfer
        - obj.BaseplateTopLedgeWidth
    )
    magedge = (
        obj.GridSize / 2
        - obj.MagnetHoleDistanceFromEdge
        - obj.MagnetHoleDiameter / 2
        - obj.MagnetEdgeThickness
    )
    magcenter = obj.GridSize / 2 - obj.MagnetHoleDistanceFromEdge
    smfillpos = inframedis - obj.SmallFillet + obj.SmallFillet * math.sin(math.pi / 4)
    smfillposmag = magedge - obj.SmallFillet + obj.SmallFillet * math.sin(math.pi / 4)
    smfilloffcen = (
        obj.GridSize / 2
        - obj.MagnetHoleDistanceFromEdge
        - obj.MagnetHoleDiameter / 2
        - obj.MagnetEdgeThickness
        - obj.SmallFillet
    )
    smfillins = inframedis - obj.SmallFillet
    bigfillpos = (
        obj.GridSize / 2
        - obj.MagnetHoleDistanceFromEdge
        - (obj.MagnetHoleDiameter / 2 + obj.MagnetEdgeThickness) * math.sin(math.pi / 4)
    )
    mec_middle = FreeCAD.Vector(0, 0, 0)

    v1 = FreeCAD.Vector(0, -inframedis, 0)
    v2 = FreeCAD.Vector(-smfilloffcen, -inframedis, 0)
    v3 = FreeCAD.Vector(-magedge, -smfillins, 0)
    v4 = FreeCAD.Vector(-magedge, -magcenter, 0)
    v5 = FreeCAD.Vector(-magcenter, -magedge, 0)
    v6 = FreeCAD.Vector(-smfillins, -magedge, 0)
    v7 = FreeCAD.Vector(-inframedis, -smfilloffcen, 0)
    v8 = FreeCAD.Vector(-inframedis, 0, 0)

    va1 = FreeCAD.Vector(-smfillposmag, -smfillpos, 0)
    va2 = FreeCAD.Vector(-bigfillpos, -bigfillpos, 0)
    va3 = FreeCAD.Vector(-smfillpos, -smfillposmag, 0)

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
            ytranslate += obj.GridSize.Value
        xtranslate += obj.GridSize.Value

    return Utils.copy_and_translate(shape, vec_list)


def make_bottom_hole_shape(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create bottom hole shape.

    Return one combined shape containing of the different hole types.

    Args:
        obj (FreeCAD.DocumentObject): DocumentObject

    Returns:
        Part.Shape: Combined hole shape.

    """
    sqbr1_depth = obj.MagnetHoleDepth + obj.SequentialBridgingLayerHeight
    sqbr2_depth = obj.MagnetHoleDepth + obj.SequentialBridgingLayerHeight * 2

    bottom_hole_shape: Part.Shape | None = None

    if obj.MagnetHoles:
        if obj.MagnetHolesShape == "Hex":
            # Ratio of 2/sqrt(3) converts from inscribed circle radius to circumscribed
            # circle radius
            radius = obj.MagnetHoleDiameter / math.sqrt(3)
            p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
            p.Polygon = 6
            p.Circumradius = radius
            p.recompute()

            p_wire: Part.Wire = p.Shape
            magnet_hole_shape = Part.Face(p_wire).extrude(FreeCAD.Vector(0, 0, obj.MagnetHoleDepth))
            FreeCAD.ActiveDocument.removeObject(p.Name)
        else:
            magnet_hole_shape = Part.makeCylinder(
                obj.MagnetHoleDiameter / 2,
                obj.MagnetHoleDepth,
                FreeCAD.Vector(0, 0, 0),
                FreeCAD.Vector(0, 0, 1),
            )

        bottom_hole_shape = (
            magnet_hole_shape
            if bottom_hole_shape is None
            else bottom_hole_shape.fuse(magnet_hole_shape)
        )

    if obj.ScrewHoles:
        screw_hole_shape = Part.makeCylinder(
            obj.ScrewHoleDiameter / 2,
            obj.ScrewHoleDepth,
            FreeCAD.Vector(0, 0, 0),
            FreeCAD.Vector(0, 0, 1),
        )

        bottom_hole_shape = (
            screw_hole_shape
            if bottom_hole_shape is None
            else bottom_hole_shape.fuse(screw_hole_shape)
        )

    if obj.ScrewHoles and obj.MagnetHoles:
        b1 = Part.makeBox(
            obj.ScrewHoleDiameter,
            obj.ScrewHoleDiameter,
            sqbr2_depth,
            FreeCAD.Vector(-obj.ScrewHoleDiameter / 2, -obj.ScrewHoleDiameter / 2, 0),
            FreeCAD.Vector(0, 0, 1),
        )
        arc_pt_off_x = (
            math.sqrt(
                ((obj.MagnetHoleDiameter / 2) ** 2) - ((obj.ScrewHoleDiameter / 2) ** 2),
            )
        ) * unitmm
        arc_pt_off_y = obj.ScrewHoleDiameter / 2

        va1 = FreeCAD.Vector(
            arc_pt_off_x,
            arc_pt_off_y,
            0,
        )
        va2 = FreeCAD.Vector(
            -arc_pt_off_x,
            arc_pt_off_y,
            0,
        )
        va3 = FreeCAD.Vector(
            -arc_pt_off_x,
            -arc_pt_off_y,
            0,
        )
        va4 = FreeCAD.Vector(
            arc_pt_off_x,
            -arc_pt_off_y,
            0,
        )
        var1 = FreeCAD.Vector(
            obj.MagnetHoleDiameter / 2,
            0,
            0,
        )
        var2 = FreeCAD.Vector(
            -obj.MagnetHoleDiameter / 2,
            0,
            0,
        )
        line_1 = Part.LineSegment(va1, va2)
        line_2 = Part.LineSegment(va3, va4)
        ar1 = Part.Arc(va1, var1, va4)
        ar2 = Part.Arc(va2, var2, va3)
        s1 = Part.Shape([line_1, ar1, ar2, line_2])
        w1 = Part.Wire(s1.Edges)
        sq1_1 = Part.Face(w1)
        sq1_1 = sq1_1.extrude(FreeCAD.Vector(0, 0, sqbr1_depth))
        holes_interface_shape = Part.Solid.fuse(sq1_1, b1)

        bottom_hole_shape = (
            holes_interface_shape
            if bottom_hole_shape is None
            else bottom_hole_shape.fuse(holes_interface_shape)
        )
    return bottom_hole_shape


def make_bottom_holes(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create bottom holes.

    Args:
        obj (FreeCAD.DocumentObject): Documentobject

    Returns:
        Part.Shape: bottom holes shape

    """
    bottom_hole_shape = make_bottom_hole_shape(obj)

    hole_pos = obj.GridSize / 2 - obj.MagnetHoleDistanceFromEdge

    hole_shape_sub_array = Utils.copy_and_translate(
        bottom_hole_shape,
        [
            FreeCAD.Vector(-hole_pos, -hole_pos, -obj.TotalHeight),
            FreeCAD.Vector(hole_pos, -hole_pos, -obj.TotalHeight),
            FreeCAD.Vector(-hole_pos, hole_pos, -obj.TotalHeight),
            FreeCAD.Vector(hole_pos, hole_pos, -obj.TotalHeight),
        ],
    )
    vec_list = []
    xtranslate = 0
    for _ in range(obj.xGridUnits):
        ytranslate = 0
        for _ in range(obj.yGridUnits):
            vec_list.append(FreeCAD.Vector(xtranslate, ytranslate, 0))
            ytranslate += obj.GridSize.Value
        xtranslate += obj.GridSize.Value

    return Utils.copy_and_translate(hole_shape_sub_array, vec_list)


def _eco_bin_cut_fillet_edges_filter(obj: FreeCAD.DocumentObject, edge: Part.Edge) -> bool:
    divfil = -obj.TotalHeight + obj.BaseProfileHeight + obj.BaseWallThickness + 1 * unitmm
    z0 = edge.Vertexes[0].Point.z
    z1 = edge.Vertexes[1].Point.z
    return z1 != z0 and (z1 >= divfil or z0 >= divfil)


def _eco_bin_deviders(obj: FreeCAD.DocumentObject) -> Part.Shape:
    xcomp_w = (obj.xTotalWidth - obj.WallThickness * 2 - obj.xDividers * obj.DividerThickness) / (
        obj.xDividers + 1
    )
    ycomp_w = (obj.yTotalWidth - obj.WallThickness * 2 - obj.yDividers * obj.DividerThickness) / (
        obj.yDividers + 1
    )

    xdivheight = obj.xDividerHeight if obj.xDividerHeight != 0 else obj.TotalHeight
    ydivheight = obj.yDividerHeight if obj.yDividerHeight != 0 else obj.TotalHeight

    xtranslate = zeromm + xcomp_w + obj.WallThickness - obj.DividerThickness
    ytranslate = zeromm + ycomp_w + obj.WallThickness

    assembly: Part.Shape | None = None

    # dividers in x direction
    for _ in range(obj.xDividers):
        comp = Part.makeBox(
            obj.DividerThickness,
            obj.yTotalWidth,
            xdivheight,
            FreeCAD.Vector(
                -obj.BinUnit / 2 + obj.DividerThickness,
                -obj.BinUnit / 2,
                -obj.TotalHeight,
            ),
            FreeCAD.Vector(0, 0, 1),
        )
        comp.translate(FreeCAD.Vector(xtranslate, 0, 0))

        assembly = comp if assembly is None else assembly.fuse(comp)
        xtranslate += xcomp_w + obj.DividerThickness

    # dividers in y direction
    for _ in range(obj.yDividers):
        comp = Part.makeBox(
            obj.xTotalWidth,
            obj.DividerThickness,
            ydivheight,
            FreeCAD.Vector(-obj.BinUnit / 2, -obj.BinUnit / 2, -obj.TotalHeight),
            FreeCAD.Vector(0, 0, 1),
        )
        comp.translate(FreeCAD.Vector(0, ytranslate, 0))
        assembly = comp if assembly is None else assembly.fuse(comp)
        ytranslate += ycomp_w + obj.DividerThickness

    return assembly


def make_eco_bin_cut(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create eco bin cutouts.

    Args:
        obj (FreeCAD.DocumentObject): Document object.

    Returns:
        Part.Shape: Eco bin cutout shape.

    """
    func_fuse = Utils.rounded_rectangle_extrude(
        obj.xTotalWidth - obj.WallThickness * 2,
        obj.yTotalWidth - obj.WallThickness * 2,
        -obj.TotalHeight + obj.BaseProfileHeight + obj.BaseWallThickness,
        obj.TotalHeight - obj.BaseProfileHeight - obj.BaseWallThickness,
        obj.BinOuterRadius - obj.WallThickness,
    )
    func_fuse.translate(
        FreeCAD.Vector(
            obj.xTotalWidth / 2 - obj.BinUnit / 2,
            obj.yTotalWidth / 2 - obj.BinUnit / 2,
            0,
        ),
    )

    base_offset = obj.BaseWallThickness * math.tan(math.pi / 8)
    bt_cmf_width = (
        obj.BinUnit - 2 * obj.BaseProfileTopChamfer - obj.BaseWallThickness * 2 - 0.4 * unitmm * 2
    )
    vert_width = obj.BinUnit - 2 * obj.BaseProfileTopChamfer - obj.BaseWallThickness * 2
    bt_chf_rad = obj.BinVerticalRadius - 0.4 * unitmm - obj.BaseWallThickness
    bt_chf_rad = 0.01 * unitmm if bt_chf_rad <= SMALL_NUMBER else bt_chf_rad

    v_chf_rad = obj.BinVerticalRadius - obj.BaseWallThickness
    v_chf_rad = 0.01 * unitmm if v_chf_rad <= SMALL_NUMBER else v_chf_rad

    magoffset, tp_chf_offset = zeromm, zeromm
    if obj.MagnetHoles:
        magoffset = obj.MagnetHoleDepth
        if (obj.MagnetHoleDepth + obj.BaseWallThickness) > (
            obj.BaseProfileBottomChamfer + obj.BaseProfileVerticalSection + base_offset
        ):
            tp_chf_offset = (obj.MagnetHoleDepth + obj.BaseWallThickness) - (
                obj.BaseProfileBottomChamfer + obj.BaseProfileVerticalSection + base_offset
            )

    bottom_chamfer = Utils.rounded_rectangle_chamfer(
        bt_cmf_width,
        bt_cmf_width,
        -obj.TotalHeight + obj.BaseWallThickness + magoffset,
        0.4 * unitmm,
        bt_chf_rad,
    )

    vertical_section = Utils.rounded_rectangle_extrude(
        vert_width,
        vert_width,
        -obj.TotalHeight + obj.BaseWallThickness + 0.4 * unitmm + magoffset,
        obj.BaseProfileVerticalSection
        + obj.BaseProfileBottomChamfer
        + base_offset
        - obj.BaseWallThickness
        - 0.4 * unitmm,
        v_chf_rad,
    )

    top_chamfer = Utils.rounded_rectangle_chamfer(
        vert_width + tp_chf_offset,
        vert_width + tp_chf_offset,
        -obj.TotalHeight
        + obj.BaseProfileBottomChamfer
        + obj.BaseProfileVerticalSection
        + base_offset
        + tp_chf_offset,
        obj.BaseProfileTopChamfer + obj.BaseWallThickness - tp_chf_offset,
        v_chf_rad,
    )
    assembly = bottom_chamfer.multiFuse([vertical_section, top_chamfer])

    xtranslate, ytranslate = zeromm, zeromm
    vec_list = []
    for _ in range(obj.xGridUnits):
        ytranslate = zeromm
        for _ in range(obj.yGridUnits):
            vec_list.append(FreeCAD.Vector(xtranslate, ytranslate, 0))
            ytranslate += obj.GridSize
        xtranslate += obj.GridSize

    func_fuse = func_fuse.fuse(Utils.copy_and_translate(assembly, vec_list))

    outer_trim1 = Utils.rounded_rectangle_extrude(
        obj.xTotalWidth - obj.WallThickness * 2,
        obj.yTotalWidth - obj.WallThickness * 2,
        -obj.TotalHeight,
        obj.TotalHeight,
        obj.BinOuterRadius - obj.WallThickness,
    ).translate(
        FreeCAD.Vector(
            obj.xTotalWidth / 2 - obj.BinUnit / 2,
            obj.yTotalWidth / 2 - obj.BinUnit / 2,
            0,
        ),
    )

    outer_trim2 = Utils.rounded_rectangle_extrude(
        obj.xTotalWidth + 20 * unitmm,
        obj.yTotalWidth + 20 * unitmm,
        -obj.TotalHeight,
        obj.TotalHeight - obj.BaseProfileHeight,
        obj.BinOuterRadius,
    ).translate(
        FreeCAD.Vector(
            obj.xTotalWidth / 2 - obj.BinUnit / 2,
            obj.yTotalWidth / 2 - obj.BinUnit / 2,
            0,
        ),
    )

    outer_trim2 = outer_trim2.cut(outer_trim1)

    func_fuse = func_fuse.cut(outer_trim2)

    deviders = _eco_bin_deviders(obj)
    func_fuse = func_fuse.cut(deviders) if deviders else func_fuse

    b_edges = []
    divfil = -obj.TotalHeight + obj.BaseProfileHeight + obj.BaseWallThickness + 1 * unitmm
    for edge in func_fuse.Edges:
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z

        if z1 != z0 and (z1 >= divfil or z0 >= divfil):
            b_edges.append(edge)
    return func_fuse.makeFillet(obj.InsideFilletRadius, b_edges) if deviders else func_fuse
