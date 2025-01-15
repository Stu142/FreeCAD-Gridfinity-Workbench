"""Module containing gridfinity feature constructions."""

import math

import FreeCAD
import numpy as np
import Part
from FreeCAD import Units

unitmm = Units.Quantity("1 mm")
zeromm = Units.Quantity("0 mm")

SMALL_NUMBER = 0.01


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
    (
        -obj.StackingLipTopChamfer
        - obj.StackingLipTopLedge
        - obj.StackingLipBottomChamfer
        - obj.LabelShelfWidth
        + obj.WallThickness
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

        funcfuse = funcfuse.makeFillet(obj.BinOuterRadius - obj.WallThickness, b_edges)

    if shelf_placement == "Center":
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

        funcfuse = ls if xdiv == 1 and ydiv == 1 else Part.Solid.multiFuse(firstls, parts)

    if shelf_placement == "Left":
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

        funcfuse = funcfuse.makeFillet(obj.BinOuterRadius - obj.WallThickness, b_edges)

    if shelf_placement == "Right":
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

        funcfuse = funcfuse.makeFillet(obj.BinOuterRadius - obj.WallThickness, b_edges)

    # For all label placements
    h_edges = []
    for edge in funcfuse.Edges:
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z

        if (
            z0 == -obj.LabelShelfVerticalThickness + stackingoffset
            and z1 == -obj.LabelShelfVerticalThickness + stackingoffset
        ):
            h_edges.append(edge)

    funcfuse = funcfuse.makeFillet(
        obj.LabelShelfVerticalThickness.Value - 0.01,
        h_edges,
    )

    labelshelfheight = obj.LabelShelfVerticalThickness + side_b * unitmm
    if (labelshelfheight) > obj.UsableHeight:
        fw = obj.yTotalWidth - obj.WallThickness * 2
        ytranslate = -obj.BinUnit / 2 + obj.WallThickness
        xtranslate = zeromm
        parts = []
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

        for x in range(xdiv):
            bottomcut = bottomcutbox.copy()
            bottomcut.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

            if x == 0:
                firstbottomcut = bottomcut
            else:
                parts.append(bottomcut)

            xtranslate += xcompwidth + obj.DividerThickness

        bottomcuttotal = bottomcut if xdiv == 1 else Part.Solid.multiFuse(firstbottomcut, parts)

        funcfuse = Part.Shape.cut(funcfuse, bottomcuttotal)
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

    parts = []
    for x in range(xdiv):
        scoop = face.extrude(FreeCAD.Vector(0, obj.yTotalWidth - obj.WallThickness * 2, 0))
        scoop.translate(
            FreeCAD.Vector(-xtranslate, -obj.BinUnit / 2 + obj.WallThickness, 0),
        )

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

        if x > 0:
            parts.append(scoop)
        else:
            funcfuse = scoop
    if x > 0:
        funcfuse = funcfuse.multiFuse(parts)
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
    stacking_lip_path = create_rounded_rectangle(
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


def make_compartments(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create compartment cutout objects.

    Args:
        obj (FreeCAD.DocumentObject): Document object.

    Returns:
        Part.Shape: Compartments cutout shape.

    """
    xdivheight = obj.xDividerHeight if obj.xDividerHeight != 0 else obj.TotalHeight
    ydivheight = obj.yDividerHeight if obj.yDividerHeight != 0 else obj.TotalHeight

    stackingoffset = -obj.LabelShelfStackingOffset if obj.StackingLip else 0 * unitmm

    func_fuse = rounded_rectangle_extrude(
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

        func_fuse = func_fuse.makeFillet(obj.InsideFilletRadius, b_edges)

    else:
        xcomp_w = (
            obj.xTotalWidth - obj.WallThickness * 2 - obj.xDividers * obj.DividerThickness
        ) / (obj.xDividers + 1)
        ycomp_w = (
            obj.yTotalWidth - obj.WallThickness * 2 - obj.yDividers * obj.DividerThickness
        ) / (obj.yDividers + 1)

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

        func_fuse = func_fuse.makeFillet(obj.InsideFilletRadius, b_edges)

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
            bottom_chamfer = rounded_rectangle_chamfer(
                bt_cmf_width,
                bt_cmf_width,
                -obj.TotalHeight,
                obj.BaseProfileBottomChamfer,
                obj.BinBottomRadius,
            )

            vertical_section = rounded_rectangle_extrude(
                vert_width,
                vert_width,
                -obj.TotalHeight + obj.BaseProfileBottomChamfer,
                obj.BaseProfileVerticalSection,
                obj.BinVerticalRadius,
            )
            assembly = Part.Shape.fuse(bottom_chamfer, vertical_section)
            vertical_section = rounded_rectangle_extrude(
                vert_width,
                vert_width,
                -obj.TotalHeight + obj.BaseProfileBottomChamfer,
                obj.BaseProfileVerticalSection,
                obj.BinVerticalRadius,
            )
            assembly = Part.Shape.fuse(bottom_chamfer, vertical_section)

            top_chamfer = rounded_rectangle_chamfer(
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

    v1 = FreeCAD.Vector(-smfilloffcen, -inframedis, 0)
    v2 = FreeCAD.Vector(-magedge, -smfillins, 0)
    v3 = FreeCAD.Vector(-magedge, -magcenter, 0)
    v4 = FreeCAD.Vector(-magcenter, -magedge, 0)
    v5 = FreeCAD.Vector(-smfillins, -magedge, 0)
    v6 = FreeCAD.Vector(-inframedis, -smfilloffcen, 0)

    va1 = FreeCAD.Vector(-smfillposmag, -smfillpos, 0)
    va2 = FreeCAD.Vector(-bigfillpos, -bigfillpos, 0)
    va3 = FreeCAD.Vector(-smfillpos, -smfillposmag, 0)

    v7 = FreeCAD.Vector(-inframedis, smfilloffcen, 0)
    v8 = FreeCAD.Vector(-smfillins, magedge, 0)
    v9 = FreeCAD.Vector(-magcenter, magedge, 0)
    v10 = FreeCAD.Vector(-magedge, magcenter, 0)
    v11 = FreeCAD.Vector(-magedge, smfillins, 0)
    v12 = FreeCAD.Vector(-smfilloffcen, inframedis, 0)

    va4 = FreeCAD.Vector(-smfillpos, smfillposmag, 0)
    va5 = FreeCAD.Vector(-bigfillpos, bigfillpos, 0)
    va6 = FreeCAD.Vector(-smfillposmag, smfillpos, 0)

    v13 = FreeCAD.Vector(smfilloffcen, inframedis, 0)
    v14 = FreeCAD.Vector(magedge, smfillins, 0)
    v15 = FreeCAD.Vector(magedge, magcenter, 0)
    v16 = FreeCAD.Vector(magcenter, magedge, 0)
    v17 = FreeCAD.Vector(smfillins, magedge, 0)
    v18 = FreeCAD.Vector(inframedis, smfilloffcen, 0)

    va7 = FreeCAD.Vector(smfillposmag, smfillpos, 0)
    va8 = FreeCAD.Vector(bigfillpos, bigfillpos, 0)
    va9 = FreeCAD.Vector(smfillpos, smfillposmag, 0)

    v19 = FreeCAD.Vector(inframedis, -smfilloffcen, 0)
    v20 = FreeCAD.Vector(smfillins, -magedge, 0)
    v21 = FreeCAD.Vector(magcenter, -magedge, 0)
    v22 = FreeCAD.Vector(magedge, -magcenter, 0)
    v23 = FreeCAD.Vector(magedge, -smfillins, 0)
    v24 = FreeCAD.Vector(smfilloffcen, -inframedis, 0)

    va10 = FreeCAD.Vector(smfillpos, -smfillposmag, 0)
    va11 = FreeCAD.Vector(bigfillpos, -bigfillpos, 0)
    va12 = FreeCAD.Vector(smfillposmag, -smfillpos, 0)

    l1 = Part.LineSegment(v24, v1)
    ar1 = Part.Arc(v1, va1, v2)
    l2 = Part.LineSegment(v2, v3)
    ar2 = Part.Arc(v3, va2, v4)
    l3 = Part.LineSegment(v4, v5)
    ar3 = Part.Arc(v5, va3, v6)
    l4 = Part.LineSegment(v6, v7)
    ar4 = Part.Arc(v7, va4, v8)
    l5 = Part.LineSegment(v8, v9)
    ar5 = Part.Arc(v9, va5, v10)
    l6 = Part.LineSegment(v10, v11)
    ar6 = Part.Arc(v11, va6, v12)
    l7 = Part.LineSegment(v12, v13)
    ar7 = Part.Arc(v13, va7, v14)
    l8 = Part.LineSegment(v14, v15)
    ar8 = Part.Arc(v15, va8, v16)
    l9 = Part.LineSegment(v16, v17)
    ar9 = Part.Arc(v17, va9, v18)
    l10 = Part.LineSegment(v18, v19)
    ar10 = Part.Arc(v19, va10, v20)
    l11 = Part.LineSegment(v20, v21)
    ar11 = Part.Arc(v21, va11, v22)
    l12 = Part.LineSegment(v22, v23)
    ar12 = Part.Arc(v23, va12, v24)
    xtranslate = zeromm
    ytranslate = zeromm

    s1 = Part.Shape(
        [
            l1,
            ar1,
            l2,
            ar2,
            l3,
            ar3,
            l4,
            ar4,
            l5,
            ar5,
            l6,
            ar6,
            l7,
            ar7,
            l8,
            ar8,
            l9,
            ar9,
            l10,
            ar10,
            l11,
            ar11,
            l12,
            ar12,
        ],
    )

    wire = Part.Wire(s1.Edges)
    face = Part.Face(wire)
    hm2: Part.Shape | None = None
    hm3: Part.Shape | None = None

    for _ in range(obj.xGridUnits):
        ytranslate = zeromm
        for _ in range(obj.yGridUnits):
            hm1 = face.extrude(FreeCAD.Vector(0, 0, -obj.TotalHeight))

            hm1.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

            hm2 = hm1 if hm2 is None else hm2.fuse(hm1)
            ytranslate += obj.GridSize

        hm3 = hm2 if hm3 is None else hm3.fuse(hm2)
        xtranslate += obj.GridSize

    return hm3


def make_bottom_holes(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create bottom holes.

    Args:
        obj (FreeCAD.DocumentObject): Documentobject

    Returns:
        Part.Shape: bottom holes shape

    """
    hole_pos = obj.GridSize / 2 - obj.MagnetHoleDistanceFromEdge
    sq_bridge2_pos = -obj.GridSize / 2 + obj.MagnetHoleDistanceFromEdge + obj.ScrewHoleDiameter / 2

    sqbr1_depth = obj.MagnetHoleDepth + obj.SequentialBridgingLayerHeight
    sqbr2_depth = obj.MagnetHoleDepth + obj.SequentialBridgingLayerHeight * 2

    xtranslate = zeromm
    ytranslate = zeromm
    hm2: Part.Shape | None = None
    hm3: Part.Shape | None = None

    if obj.MagnetHoles:
        for _ in range(obj.xGridUnits):
            ytranslate = zeromm
            for _ in range(obj.yGridUnits):
                if obj.MagnetHolesShape == "Hex":
                    # Ratio of 2/sqrt(3) converts from inscribed circle radius to circumscribed
                    # circle radius
                    radius = obj.MagnetHoleDiameter / np.sqrt(3)

                    n_sides = 6

                    rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0)

                    p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
                    p.Polygon = n_sides
                    p.Circumradius = radius
                    p.Placement = FreeCAD.Placement(
                        FreeCAD.Vector(-hole_pos, -hole_pos, -obj.TotalHeight),
                        rot,
                    )
                    p.recompute()
                    f = Part.Face(Part.Wire(p.Shape.Edges))
                    c1 = f.extrude(FreeCAD.Vector(0, 0, obj.MagnetHoleDepth))
                    FreeCAD.ActiveDocument.removeObject(p.Name)

                    p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
                    p.Polygon = n_sides
                    p.Circumradius = radius
                    p.Placement = FreeCAD.Placement(
                        FreeCAD.Vector(hole_pos, -hole_pos, -obj.TotalHeight),
                        rot,
                    )
                    p.recompute()
                    f = Part.Face(Part.Wire(p.Shape.Edges))
                    c2 = f.extrude(FreeCAD.Vector(0, 0, obj.MagnetHoleDepth))
                    FreeCAD.ActiveDocument.removeObject(p.Name)

                    p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
                    p.Polygon = n_sides
                    p.Circumradius = radius
                    p.Placement = FreeCAD.Placement(
                        FreeCAD.Vector(-hole_pos, hole_pos, -obj.TotalHeight),
                        rot,
                    )
                    p.recompute()
                    f = Part.Face(Part.Wire(p.Shape.Edges))
                    c3 = f.extrude(FreeCAD.Vector(0, 0, obj.MagnetHoleDepth))
                    FreeCAD.ActiveDocument.removeObject(p.Name)

                    p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
                    p.Polygon = n_sides
                    p.Circumradius = radius
                    p.Placement = FreeCAD.Placement(
                        FreeCAD.Vector(hole_pos, hole_pos, -obj.TotalHeight),
                        rot,
                    )
                    p.recompute()
                    f = Part.Face(Part.Wire(p.Shape.Edges))
                    c4 = f.extrude(FreeCAD.Vector(0, 0, obj.MagnetHoleDepth))
                    FreeCAD.ActiveDocument.removeObject(p.Name)

                else:
                    c1 = Part.makeCylinder(
                        obj.MagnetHoleDiameter / 2,
                        obj.MagnetHoleDepth,
                        FreeCAD.Vector(-hole_pos, -hole_pos, -obj.TotalHeight),
                        FreeCAD.Vector(0, 0, 1),
                    )
                    c2 = Part.makeCylinder(
                        obj.MagnetHoleDiameter / 2,
                        obj.MagnetHoleDepth,
                        FreeCAD.Vector(hole_pos, -hole_pos, -obj.TotalHeight),
                        FreeCAD.Vector(0, 0, 1),
                    )
                    c3 = Part.makeCylinder(
                        obj.MagnetHoleDiameter / 2,
                        obj.MagnetHoleDepth,
                        FreeCAD.Vector(-hole_pos, hole_pos, -obj.TotalHeight),
                        FreeCAD.Vector(0, 0, 1),
                    )
                    c4 = Part.makeCylinder(
                        obj.MagnetHoleDiameter / 2,
                        obj.MagnetHoleDepth,
                        FreeCAD.Vector(hole_pos, hole_pos, -obj.TotalHeight),
                        FreeCAD.Vector(0, 0, 1),
                    )
                if obj.MagnetHolesShape == "Hex":
                    n_sides = 6

                    rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0)

                    p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
                    p.Polygon = n_sides
                    p.Circumradius = obj.MagnetHoleDiameter / 2
                    p.Placement = FreeCAD.Placement(
                        FreeCAD.Vector(-hole_pos, -hole_pos, -obj.TotalHeight),
                        rot,
                    )
                    p.recompute()
                    f = Part.Face(Part.Wire(p.Shape.Edges))
                    c1 = f.extrude(FreeCAD.Vector(0, 0, obj.MagnetHoleDepth))
                    FreeCAD.ActiveDocument.removeObject(p.Name)

                    p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
                    p.Polygon = n_sides
                    p.Circumradius = obj.MagnetHoleDiameter / 2
                    p.Placement = FreeCAD.Placement(
                        FreeCAD.Vector(hole_pos, -hole_pos, -obj.TotalHeight),
                        rot,
                    )
                    p.recompute()
                    f = Part.Face(Part.Wire(p.Shape.Edges))
                    c2 = f.extrude(FreeCAD.Vector(0, 0, obj.MagnetHoleDepth))
                    FreeCAD.ActiveDocument.removeObject(p.Name)

                    p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
                    p.Polygon = n_sides
                    p.Circumradius = obj.MagnetHoleDiameter / 2
                    p.Placement = FreeCAD.Placement(
                        FreeCAD.Vector(-hole_pos, hole_pos, -obj.TotalHeight),
                        rot,
                    )
                    p.recompute()
                    f = Part.Face(Part.Wire(p.Shape.Edges))
                    c3 = f.extrude(FreeCAD.Vector(0, 0, obj.MagnetHoleDepth))
                    FreeCAD.ActiveDocument.removeObject(p.Name)

                    p = FreeCAD.ActiveDocument.addObject("Part::RegularPolygon")
                    p.Polygon = n_sides
                    p.Circumradius = obj.MagnetHoleDiameter / 2
                    p.Placement = FreeCAD.Placement(
                        FreeCAD.Vector(hole_pos, hole_pos, -obj.TotalHeight),
                        rot,
                    )
                    p.recompute()
                    f = Part.Face(Part.Wire(p.Shape.Edges))
                    c4 = f.extrude(FreeCAD.Vector(0, 0, obj.MagnetHoleDepth))
                    FreeCAD.ActiveDocument.removeObject(p.Name)

                else:
                    c1 = Part.makeCylinder(
                        obj.MagnetHoleDiameter / 2,
                        obj.MagnetHoleDepth,
                        FreeCAD.Vector(-hole_pos, -hole_pos, -obj.TotalHeight),
                        FreeCAD.Vector(0, 0, 1),
                    )
                    c2 = Part.makeCylinder(
                        obj.MagnetHoleDiameter / 2,
                        obj.MagnetHoleDepth,
                        FreeCAD.Vector(hole_pos, -hole_pos, -obj.TotalHeight),
                        FreeCAD.Vector(0, 0, 1),
                    )
                    c3 = Part.makeCylinder(
                        obj.MagnetHoleDiameter / 2,
                        obj.MagnetHoleDepth,
                        FreeCAD.Vector(-hole_pos, hole_pos, -obj.TotalHeight),
                        FreeCAD.Vector(0, 0, 1),
                    )
                    c4 = Part.makeCylinder(
                        obj.MagnetHoleDiameter / 2,
                        obj.MagnetHoleDepth,
                        FreeCAD.Vector(hole_pos, hole_pos, -obj.TotalHeight),
                        FreeCAD.Vector(0, 0, 1),
                    )

                hm1 = Part.Solid.multiFuse(c1, [c2, c3, c4])

                hm1.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

                hm2 = hm1 if hm2 is None else hm2.fuse(hm1)
                ytranslate += obj.GridSize

            hm3 = hm2 if hm3 is None else hm3.fuse(hm2)
            xtranslate += obj.GridSize

    xtranslate = zeromm
    ytranslate = zeromm
    hs2: Part.Shape | None = None
    hs3: Part.Shape | None = None

    if obj.ScrewHoles:
        for _ in range(obj.xGridUnits):
            ytranslate = zeromm
            for _ in range(obj.yGridUnits):
                cs1 = Part.makeCylinder(
                    obj.ScrewHoleDiameter / 2,
                    obj.ScrewHoleDepth,
                    FreeCAD.Vector(-hole_pos, -hole_pos, -obj.TotalHeight),
                    FreeCAD.Vector(0, 0, 1),
                )
                cs2 = Part.makeCylinder(
                    obj.ScrewHoleDiameter / 2,
                    obj.ScrewHoleDepth,
                    FreeCAD.Vector(hole_pos, -hole_pos, -obj.TotalHeight),
                    FreeCAD.Vector(0, 0, 1),
                )
                cs3 = Part.makeCylinder(
                    obj.ScrewHoleDiameter / 2,
                    obj.ScrewHoleDepth,
                    FreeCAD.Vector(-hole_pos, hole_pos, -obj.TotalHeight),
                    FreeCAD.Vector(0, 0, 1),
                )
                cs4 = Part.makeCylinder(
                    obj.ScrewHoleDiameter / 2,
                    obj.ScrewHoleDepth,
                    FreeCAD.Vector(hole_pos, hole_pos, -obj.TotalHeight),
                    FreeCAD.Vector(0, 0, 1),
                )

                hm1 = Part.Solid.multiFuse(cs1, [cs2, cs3, cs4])

                hm1.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))
                hs2 = hm1 if hs2 is None else hs2.fuse(hm1)
                ytranslate += obj.GridSize

            hs3 = hs2 if hs3 is None else hs3.fuse(hs2)
            xtranslate += obj.GridSize

    xtranslate = zeromm
    ytranslate = zeromm
    hsq2: Part.Shape | None = None
    hsq3: Part.Shape | None = None

    if obj.ScrewHoles and obj.MagnetHoles:
        for _ in range(obj.xGridUnits):
            ytranslate = zeromm
            for _ in range(obj.yGridUnits):
                b1 = Part.makeBox(
                    obj.ScrewHoleDiameter,
                    obj.ScrewHoleDiameter,
                    sqbr2_depth,
                    FreeCAD.Vector(-sq_bridge2_pos, -sq_bridge2_pos, -obj.TotalHeight),
                    FreeCAD.Vector(0, 0, 1),
                )
                b2 = Part.makeBox(
                    obj.ScrewHoleDiameter,
                    obj.ScrewHoleDiameter,
                    sqbr2_depth,
                    FreeCAD.Vector(
                        -obj.GridSize / 2
                        + obj.MagnetHoleDistanceFromEdge
                        - obj.ScrewHoleDiameter / 2,
                        -sq_bridge2_pos,
                        -obj.TotalHeight,
                    ),
                    FreeCAD.Vector(0, 0, 1),
                )
                b3 = Part.makeBox(
                    obj.ScrewHoleDiameter,
                    obj.ScrewHoleDiameter,
                    sqbr2_depth,
                    FreeCAD.Vector(
                        -sq_bridge2_pos,
                        -obj.GridSize / 2
                        + obj.MagnetHoleDistanceFromEdge
                        - obj.ScrewHoleDiameter / 2,
                        -obj.TotalHeight,
                    ),
                    FreeCAD.Vector(0, 0, 1),
                )
                b4 = Part.makeBox(
                    obj.ScrewHoleDiameter,
                    obj.ScrewHoleDiameter,
                    sqbr2_depth,
                    FreeCAD.Vector(
                        -obj.GridSize / 2
                        + obj.MagnetHoleDistanceFromEdge
                        - obj.ScrewHoleDiameter / 2,
                        -obj.GridSize / 2
                        + obj.MagnetHoleDistanceFromEdge
                        - obj.ScrewHoleDiameter / 2,
                        -obj.TotalHeight,
                    ),
                    FreeCAD.Vector(0, 0, 1),
                )

                arc_pt_off_x = (
                    math.sqrt(
                        ((obj.MagnetHoleDiameter / 2) ** 2) - ((obj.ScrewHoleDiameter / 2) ** 2),
                    )
                ) * unitmm
                arc_pt_off_y = obj.ScrewHoleDiameter / 2

                va1 = FreeCAD.Vector(
                    hole_pos + arc_pt_off_x,
                    hole_pos + arc_pt_off_y,
                    -obj.TotalHeight,
                )
                va2 = FreeCAD.Vector(
                    hole_pos - arc_pt_off_x,
                    hole_pos + arc_pt_off_y,
                    -obj.TotalHeight,
                )
                va3 = FreeCAD.Vector(
                    hole_pos - arc_pt_off_x,
                    hole_pos - arc_pt_off_y,
                    -obj.TotalHeight,
                )
                va4 = FreeCAD.Vector(
                    hole_pos + arc_pt_off_x,
                    hole_pos - arc_pt_off_y,
                    -obj.TotalHeight,
                )
                var1 = FreeCAD.Vector(
                    hole_pos + obj.MagnetHoleDiameter / 2,
                    hole_pos,
                    -obj.TotalHeight,
                )
                var2 = FreeCAD.Vector(
                    hole_pos - obj.MagnetHoleDiameter / 2,
                    hole_pos,
                    -obj.TotalHeight,
                )

                va5 = FreeCAD.Vector(
                    -hole_pos + arc_pt_off_x,
                    hole_pos + arc_pt_off_y,
                    -obj.TotalHeight,
                )
                va6 = FreeCAD.Vector(
                    -hole_pos - arc_pt_off_x,
                    hole_pos + arc_pt_off_y,
                    -obj.TotalHeight,
                )
                va7 = FreeCAD.Vector(
                    -hole_pos - arc_pt_off_x,
                    hole_pos - arc_pt_off_y,
                    -obj.TotalHeight,
                )
                va8 = FreeCAD.Vector(
                    -hole_pos + arc_pt_off_x,
                    hole_pos - arc_pt_off_y,
                    -obj.TotalHeight,
                )
                var3 = FreeCAD.Vector(
                    -hole_pos + obj.MagnetHoleDiameter / 2,
                    hole_pos,
                    -obj.TotalHeight,
                )
                var4 = FreeCAD.Vector(
                    -hole_pos - obj.MagnetHoleDiameter / 2,
                    hole_pos,
                    -obj.TotalHeight,
                )

                va9 = FreeCAD.Vector(
                    hole_pos + arc_pt_off_x,
                    -hole_pos + arc_pt_off_y,
                    -obj.TotalHeight,
                )
                va10 = FreeCAD.Vector(
                    hole_pos - arc_pt_off_x,
                    -hole_pos + arc_pt_off_y,
                    -obj.TotalHeight,
                )
                va11 = FreeCAD.Vector(
                    hole_pos - arc_pt_off_x,
                    -hole_pos - arc_pt_off_y,
                    -obj.TotalHeight,
                )
                va12 = FreeCAD.Vector(
                    hole_pos + arc_pt_off_x,
                    -hole_pos - arc_pt_off_y,
                    -obj.TotalHeight,
                )
                var5 = FreeCAD.Vector(
                    hole_pos + obj.MagnetHoleDiameter / 2,
                    -hole_pos,
                    -obj.TotalHeight,
                )
                var6 = FreeCAD.Vector(
                    hole_pos - obj.MagnetHoleDiameter / 2,
                    -hole_pos,
                    -obj.TotalHeight,
                )

                va13 = FreeCAD.Vector(
                    -hole_pos + arc_pt_off_x,
                    -hole_pos + arc_pt_off_y,
                    -obj.TotalHeight,
                )
                va14 = FreeCAD.Vector(
                    -hole_pos - arc_pt_off_x,
                    -hole_pos + arc_pt_off_y,
                    -obj.TotalHeight,
                )
                va15 = FreeCAD.Vector(
                    -hole_pos - arc_pt_off_x,
                    -hole_pos - arc_pt_off_y,
                    -obj.TotalHeight,
                )
                va16 = FreeCAD.Vector(
                    -hole_pos + arc_pt_off_x,
                    -hole_pos - arc_pt_off_y,
                    -obj.TotalHeight,
                )
                var7 = FreeCAD.Vector(
                    -hole_pos + obj.MagnetHoleDiameter / 2,
                    -hole_pos,
                    -obj.TotalHeight,
                )
                var8 = FreeCAD.Vector(
                    -hole_pos - obj.MagnetHoleDiameter / 2,
                    -hole_pos,
                    -obj.TotalHeight,
                )

                line_1 = Part.LineSegment(va1, va2)
                line_2 = Part.LineSegment(va3, va4)
                line_3 = Part.LineSegment(va5, va6)
                line_4 = Part.LineSegment(va7, va8)
                line_5 = Part.LineSegment(va9, va10)
                line_6 = Part.LineSegment(va11, va12)
                line_7 = Part.LineSegment(va13, va14)
                line_8 = Part.LineSegment(va15, va16)

                ar1 = Part.Arc(va1, var1, va4)
                ar2 = Part.Arc(va2, var2, va3)
                ar3 = Part.Arc(va5, var3, va8)
                ar4 = Part.Arc(va6, var4, va7)
                ar5 = Part.Arc(va9, var5, va12)
                ar6 = Part.Arc(va10, var6, va11)
                ar7 = Part.Arc(va13, var7, va16)
                ar8 = Part.Arc(va14, var8, va15)

                s1 = Part.Shape([line_1, ar1, ar2, line_2])
                s2 = Part.Shape([line_3, ar3, ar4, line_4])
                s3 = Part.Shape([line_5, ar5, ar6, line_6])
                s4 = Part.Shape([line_7, ar7, ar8, line_8])

                w1 = Part.Wire(s1.Edges)
                w2 = Part.Wire(s2.Edges)
                w3 = Part.Wire(s3.Edges)
                w4 = Part.Wire(s4.Edges)

                sq1_1 = Part.Face(w1)
                sq1_1 = sq1_1.extrude(FreeCAD.Vector(0, 0, sqbr1_depth))

                sq1_2 = Part.Face(w2)
                sq1_2 = sq1_2.extrude(FreeCAD.Vector(0, 0, sqbr1_depth))

                sq1_3 = Part.Face(w3)
                sq1_3 = sq1_3.extrude(FreeCAD.Vector(0, 0, sqbr1_depth))

                sq1_4 = Part.Face(w4)
                sq1_4 = sq1_4.extrude(FreeCAD.Vector(0, 0, sqbr1_depth))

                hm1 = Part.Solid.multiFuse(sq1_1, [b1, b2, b3, b4, sq1_2, sq1_3, sq1_4])

                hm1.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))
                hsq2 = hm1 if hsq2 is None else hsq2.fuse(hm1)
                ytranslate += obj.GridSize

            hsq3 = hsq2 if hsq3 is None else hsq3.fuse(hsq2)
            xtranslate += obj.GridSize

    if obj.ScrewHoles and not obj.MagnetHoles:
        fusetotal = hs3
    if obj.MagnetHoles and not obj.ScrewHoles:
        fusetotal = hm3
    if obj.ScrewHoles and obj.MagnetHoles:
        fusetotal = Part.Solid.multiFuse(hm3, [hs3, hsq3])

    return fusetotal


def make_eco_bin_cut(obj: FreeCAD.DocumentObject) -> Part.Shape:
    """Create eco bin cutouts.

    Args:
        obj (FreeCAD.DocumentObject): Document object.

    Returns:
        Part.Shape: Eco bin cutout shape.

    """
    func_fuse = rounded_rectangle_extrude(
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

    func_fuse = rounded_rectangle_extrude(
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
    v_chf_rad = obj.BinVerticalRadius - obj.BaseWallThickness

    if obj.MagnetHoles:
        magoffset = obj.MagnetHoleDepth
        if (obj.MagnetHoleDepth + obj.BaseWallThickness) > (
            obj.BaseProfileBottomChamfer + obj.BaseProfileVerticalSection + base_offset
        ):
            tp_chf_offset = (obj.MagnetHoleDepth + obj.BaseWallThickness) - (
                obj.BaseProfileBottomChamfer + obj.BaseProfileVerticalSection + base_offset
            )
        else:
            tp_chf_offset = 0 * unitmm
    else:
        magoffset = 0 * unitmm
        tp_chf_offset = 0 * unitmm

    if bt_chf_rad <= SMALL_NUMBER:
        bt_chf_rad = 0.01 * unitmm

    if v_chf_rad <= SMALL_NUMBER:
        v_chf_rad = 0.01 * unitmm

    xtranslate = zeromm
    ytranslate = zeromm
    assembly1: Part.Shape | None = None
    assembly2: Part.Shape | None = None

    for _ in range(obj.xGridUnits):
        ytranslate = zeromm
        for _ in range(obj.yGridUnits):
            bottom_chamfer = rounded_rectangle_chamfer(
                bt_cmf_width,
                bt_cmf_width,
                -obj.TotalHeight + obj.BaseWallThickness + magoffset,
                0.4 * unitmm,
                bt_chf_rad,
            )

            bottom_chamfer = rounded_rectangle_chamfer(
                bt_cmf_width,
                bt_cmf_width,
                -obj.TotalHeight + obj.BaseWallThickness + magoffset,
                0.4 * unitmm,
                bt_chf_rad,
            )

            vertical_section = rounded_rectangle_extrude(
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
            assembly = Part.Shape.fuse(bottom_chamfer, vertical_section)

            top_chamfer = rounded_rectangle_chamfer(
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
            assembly = Part.Solid.fuse(assembly, top_chamfer)

            assembly.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

            assembly1 = assembly if assembly1 is None else assembly1.fuse(assembly)
            ytranslate += obj.GridSize

        assembly2 = assembly1 if assembly2 is None else assembly2.fuse(assembly1)
        xtranslate += obj.GridSize

    func_fuse = func_fuse.fuse(assembly2)

    outer_trim1 = rounded_rectangle_extrude(
        obj.xTotalWidth - obj.WallThickness * 2,
        obj.yTotalWidth - obj.WallThickness * 2,
        -obj.TotalHeight,
        obj.TotalHeight,
        obj.BinOuterRadius - obj.WallThickness,
    )
    outer_trim1.translate(
        FreeCAD.Vector(
            obj.xTotalWidth / 2 - obj.BinUnit / 2,
            obj.yTotalWidth / 2 - obj.BinUnit / 2,
            0,
        ),
    )

    outer_trim2 = rounded_rectangle_extrude(
        obj.xTotalWidth + 20 * unitmm,
        obj.yTotalWidth + 20 * unitmm,
        -obj.TotalHeight,
        obj.TotalHeight - obj.BaseProfileHeight,
        obj.BinOuterRadius,
    )
    outer_trim2.translate(
        FreeCAD.Vector(
            obj.xTotalWidth / 2 - obj.BinUnit / 2,
            obj.yTotalWidth / 2 - obj.BinUnit / 2,
            0,
        ),
    )

    outer_trim2 = outer_trim2.cut(outer_trim1)

    func_fuse = func_fuse.cut(outer_trim2)
    # Dividers

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

    # dividers in x direction
    xdiv: Part.Shape | None = None
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

        xdiv = comp if xdiv is None else xdiv.fuse(comp)
        xtranslate += xcomp_w + obj.DividerThickness

    # dividers in y direction
    ydiv: Part.Shape | None = None
    for _ in range(obj.yDividers):
        comp = Part.makeBox(
            obj.xTotalWidth,
            obj.DividerThickness,
            ydivheight,
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

    divfil = -obj.TotalHeight + obj.BaseProfileHeight + obj.BaseWallThickness + 1 * unitmm
    for edge in func_fuse.Edges:
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z

        if z1 != z0 and (z1 >= divfil or z0 >= divfil):
            b_edges.append(edge)

    if obj.xDividers != 0 or obj.yDividers != 0:
        func_fuse = func_fuse.makeFillet(obj.InsideFilletRadius, b_edges)

    return func_fuse
