"""Module containing gridfinity feature constructions."""

import math

import FreeCAD as fc  # noqa: N813
import Part

from . import const, preferences, utils

unitmm = fc.Units.Quantity("1 mm")
zeromm = fc.Units.Quantity("0 mm")

SMALL_NUMBER = 0.01

GridfinityLayout = list[list[bool]]


def _label_shelf_full_width(
    obj: fc.DocumentObject,
    face: Part.Face,
    xcompwidth: float,
    label_shelf_height: float,
) -> Part.Shape:
    xdiv = obj.xDividers + 1
    fw = obj.yTotalWidth - obj.WallThickness * 2
    ytranslate = obj.Clearance + obj.WallThickness
    xtranslate = zeromm
    parts = []
    for x in range(xdiv):
        ls = face.extrude(fc.Vector(0, fw, 0))

        ls.translate(fc.Vector(xtranslate, ytranslate, 0))

        if x == 0:
            firstls = ls
        else:
            parts.append(ls)

        xtranslate += xcompwidth + obj.DividerThickness

    funcfuse = ls if xdiv == 1 else Part.Solid.multiFuse(firstls, parts)

    right_end_fillet = _label_shelf_right_fillet(obj)
    right_end_fillet = right_end_fillet.translate(
        fc.Vector(
            0,
            obj.yTotalWidth - obj.WallThickness * 2 - obj.BinOuterRadius + obj.WallThickness,
            0,
        ),
    )
    right_end_fillet = right_end_fillet.extrude(
        fc.Vector(0, 0, -label_shelf_height - obj.LabelShelfStackingOffset),
    )
    funcfuse = funcfuse.cut(right_end_fillet)

    left_end_fillet = _label_shelf_left_fillet(obj)
    left_end_fillet = left_end_fillet.extrude(
        fc.Vector(0, 0, -label_shelf_height - obj.LabelShelfStackingOffset),
    )
    return funcfuse.cut(left_end_fillet)

    return funcfuse


def _label_shelf_center(
    obj: fc.DocumentObject,
    xcompwidth: float,
    ycompwidth: float,
    face: Part.Face,
) -> Part.Shape:
    xdiv = obj.xDividers + 1
    ydiv = obj.yDividers + 1
    xtranslate = zeromm
    ysp = obj.Clearance + obj.WallThickness + ycompwidth / 2 - obj.LabelShelfLength / 2
    ytranslate = ysp
    parts = []
    for x in range(xdiv):
        ytranslate = ysp
        for y in range(ydiv):
            ls = face.extrude(fc.Vector(0, obj.LabelShelfLength, 0))

            ls.translate(fc.Vector(xtranslate, ytranslate, 0))

            if x == 0 and y == 0:
                firstls = ls
            else:
                parts.append(ls)

            ytranslate += ycompwidth + obj.DividerThickness

        xtranslate += xcompwidth + obj.DividerThickness

    return ls if xdiv == 1 and ydiv == 1 else Part.Solid.multiFuse(firstls, parts)


def _label_shelf_left(
    obj: fc.DocumentObject,
    xcompwidth: float,
    ycompwidth: float,
    face: Part.Face,
    label_shelf_height: float,
) -> Part.Shape:
    xdiv = obj.xDividers + 1
    ydiv = obj.yDividers + 1
    xtranslate = zeromm
    ysp = obj.Clearance + obj.WallThickness
    ytranslate = ysp
    parts = []
    for x in range(xdiv):
        ytranslate = ysp
        for y in range(ydiv):
            ls = face.extrude(fc.Vector(0, obj.LabelShelfLength, 0))

            ls.translate(fc.Vector(xtranslate, ytranslate, 0))

            if x == 0 and y == 0:
                firstls = ls
            else:
                parts.append(ls)

            ytranslate += ycompwidth + obj.DividerThickness

        xtranslate += xcompwidth + obj.DividerThickness

    funcfuse = ls if xdiv == 1 and ydiv == 1 else Part.Solid.multiFuse(firstls, parts)

    left_end_fillet = _label_shelf_left_fillet(obj)
    left_end_fillet = left_end_fillet.extrude(
        fc.Vector(0, 0, -label_shelf_height - obj.LabelShelfStackingOffset),
    )
    return funcfuse.cut(left_end_fillet)


def _label_shelf_right(
    obj: fc.DocumentObject,
    xcompwidth: float,
    ycompwidth: float,
    face: Part.Face,
    label_shelf_height: float,
) -> Part.Shape:
    xdiv = obj.xDividers + 1
    ydiv = obj.yDividers + 1
    xtranslate = zeromm
    ysp = obj.Clearance + obj.WallThickness + ycompwidth - obj.LabelShelfLength
    ytranslate = ysp
    parts = []
    for x in range(xdiv):
        ytranslate = ysp
        for y in range(ydiv):
            ls = face.extrude(fc.Vector(0, obj.LabelShelfLength, 0))

            ls.translate(fc.Vector(xtranslate, ytranslate, 0))

            if x == 0 and y == 0:
                firstls = ls
            else:
                parts.append(ls)

            ytranslate += ycompwidth + obj.DividerThickness

        xtranslate += xcompwidth + obj.DividerThickness

    funcfuse = ls if xdiv == 1 and ydiv == 1 else Part.Solid.multiFuse(firstls, parts)

    right_end_fillet = _label_shelf_right_fillet(obj)
    right_end_fillet = right_end_fillet.translate(
        fc.Vector(
            0,
            obj.yTotalWidth - obj.WallThickness * 2 - obj.BinOuterRadius + obj.WallThickness,
            0,
        ),
    )
    right_end_fillet = right_end_fillet.extrude(
        fc.Vector(0, 0, -label_shelf_height - obj.LabelShelfStackingOffset),
    )
    return funcfuse.cut(right_end_fillet)


def _label_shelf_front_fillet(
    obj: fc.DocumentObject,
    shape: Part.Shape,
    stackingoffset: float,
) -> Part.Shape:
    tolabelend = (
        obj.Clearance
        + obj.StackingLipTopChamfer
        + obj.StackingLipTopLedge
        + obj.StackingLipBottomChamfer
        + obj.LabelShelfWidth
    )

    h_edges = []
    for edge in shape.Edges:
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z
        x0 = edge.Vertexes[0].Point.x
        x1 = edge.Vertexes[1].Point.x

        if (
            z0 == -obj.LabelShelfVerticalThickness + stackingoffset
            and z1 == -obj.LabelShelfVerticalThickness + stackingoffset
            and x0 == tolabelend
            and x1 == tolabelend
        ):
            h_edges.append(edge)

    return shape.makeFillet(
        obj.LabelShelfVerticalThickness.Value - 0.01,
        h_edges,
    )


def _label_shelf_left_fillet(
    obj: fc.DocumentObject,
) -> Part.Shape:
    fillet_radius = obj.BinOuterRadius - obj.WallThickness

    # Drawing fillet shape starting bottom left corner and going clockwise
    l1x = obj.Clearance + obj.WallThickness
    l1y1 = obj.Clearance + obj.WallThickness
    l1y2 = obj.Clearance + obj.WallThickness + fillet_radius

    arc1x = (
        obj.Clearance + obj.WallThickness + fillet_radius - fillet_radius * math.sin(math.pi / 4)
    )
    arc1y = arc1x

    l2x1 = l1y2
    l2x2 = l1x
    l2y = l1y1

    l1v1 = fc.Vector(l1x, l1y1, 0)
    l1v2 = fc.Vector(l1x, l1y2, 0)
    arc1v = fc.Vector(arc1x, arc1y, 0)
    l2v1 = fc.Vector(l2x1, l2y, 0)
    l2v2 = fc.Vector(l2x2, l2y, 0)

    lines = [
        Part.LineSegment(l1v1, l1v2),
        Part.Arc(l1v2, arc1v, l2v1),
        Part.LineSegment(l2v1, l2v2),
    ]

    left_fillet_wire = utils.curve_to_wire(lines)

    return Part.Face(left_fillet_wire)


def _label_shelf_right_fillet(
    obj: fc.DocumentObject,
) -> Part.Shape:
    fillet_radius = obj.BinOuterRadius - obj.WallThickness

    # Drawing fillet shape starting bottom left corner and going clockwise

    l1x = obj.Clearance + obj.WallThickness
    l1y1 = obj.Clearance + obj.WallThickness
    l1y2 = obj.Clearance + obj.WallThickness + fillet_radius

    l2x1 = l1x
    l2x2 = l1y2
    l2y = l1y2

    arc1x = (
        obj.Clearance + obj.WallThickness + fillet_radius - fillet_radius * math.sin(math.pi / 4)
    )
    arc1y = obj.Clearance + obj.WallThickness + fillet_radius * math.sin(math.pi / 4)

    l1v1 = fc.Vector(l1x, l1y1, 0)
    l1v2 = fc.Vector(l1x, l1y2, 0)
    l2v1 = fc.Vector(l2x1, l2y, 0)
    l2v2 = fc.Vector(l2x2, l2y, 0)
    arc1v = fc.Vector(arc1x, arc1y, 0)

    lines = [
        Part.LineSegment(l1v1, l1v2),
        Part.LineSegment(l2v1, l2v2),
        Part.Arc(l2v2, arc1v, l1v1),
    ]

    right_fillet_wire = utils.curve_to_wire(lines)
    return Part.Face(right_fillet_wire)


"""
def _label_shelf_profile(
    obj: FreeCAD.DocumentObject,
    v4_z: float,
    ) -> Part.Wire:


    return utils.curve_to_wire(lines)
    """


class LabelShelf(utils.Feature):
    """Create Label shelf for bins."""

    def __init__(self, obj: fc.DocumentObject, *, label_style_default: str) -> None:
        """Create bin compartments with the option for dividers.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            label_style_default (str): list of label shelf styles

        """
        ## Gridfinity Parameters
        obj.addProperty(
            "App::PropertyEnumeration",
            "LabelShelfStyle",
            "Gridfinity",
            "Choose to have the label shelf Off or a Standard or Overhang style",
        )

        obj.LabelShelfStyle = ["Off", "Standard", "Overhang"]
        obj.LabelShelfStyle = label_style_default

        obj.addProperty(
            "App::PropertyEnumeration",
            "LabelShelfPlacement",
            "Gridfinity",
            "Choose the Placement of the label shelf for each compartement",
        )

        obj.LabelShelfPlacement = ["Center", "Full Width", "Left", "Right"]

        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "LabelShelfWidth",
            "GridfinityNonStandard",
            "Width of the Label Shelf, how far it sticks out from the wall"
            " <br> <br> default = 12 mm",
        ).LabelShelfWidth = preferences.label_shelf_width()

        obj.addProperty(
            "App::PropertyLength",
            "LabelShelfLength",
            "GridfinityNonStandard",
            "Length of the Label Shelf, how long it is <br> <br> default = 42 mm",
        ).LabelShelfLength = preferences.label_shelf_length()

        obj.addProperty(
            "App::PropertyAngle",
            "LabelShelfAngle",
            "GridfinityNonStandard",
            "Angle of the bottom part of the Label Shelf <br> <br> default = 45",
        ).LabelShelfAngle = preferences.label_shelf_angle()

        ## Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "LabelShelfStackingOffset",
            "zzExpertOnly",
            "label shelf height decreased when stacking lip is enabled so bin above does not sit"
            "uneven with one end on the label shelf <br> <br> default = 0.4 mm",
        ).LabelShelfStackingOffset = preferences.label_shelf_stacking_offset()

        obj.addProperty(
            "App::PropertyLength",
            "LabelShelfVerticalThickness",
            "zzExpertOnly",
            "Vertical Thickness of the Label Shelf <br> <br> default = 2 mm",
        ).LabelShelfVerticalThickness = preferences.label_shelf_vertical_thickness()

    def make(self, obj: fc.DocumentObject) -> Part.Shape:
        """Create label shelf.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Labelshelf 3D shape.

        """
        eco_usable_height = 14
        if (
            self.bintype == "eco"
            and obj.TotalHeight < eco_usable_height
            and obj.LabelShelfStyle != "Overhang"
        ):
            obj.LabelShelfStyle = "Overhang"
            fc.Console.PrintWarning("\n")
            fc.Console.PrintWarning(
                "Label shelf style set to Overhand due to low bin height",
            )

        towall = obj.Clearance + obj.WallThickness
        tolabelend = (
            obj.Clearance
            + obj.StackingLipTopChamfer
            + obj.StackingLipTopLedge
            + obj.StackingLipBottomChamfer
            + obj.LabelShelfWidth
        )

        xdiv = obj.xDividers + 1
        ydiv = obj.yDividers + 1
        xcompwidth = (
            obj.xTotalWidth - obj.WallThickness * 2 - obj.DividerThickness * obj.xDividers
        ) / (xdiv)
        ycompwidth = (
            obj.yTotalWidth - obj.WallThickness * 2 - obj.DividerThickness * obj.yDividers
        ) / (ydiv)

        stackingoffset = -obj.LabelShelfStackingOffset if obj.StackingLip else 0 * unitmm
        shelf_angle = obj.LabelShelfAngle.Value
        shelf_placement = obj.LabelShelfPlacement

        if obj.LabelShelfStyle == "Overhang":
            shelf_angle = 0
            shelf_placement = "Full Width"

        # Calculate V4 Z coordinate by using an angle
        side_a = abs(towall - tolabelend)
        alpha = 90 - shelf_angle
        side_c = side_a / math.sin(math.radians(alpha))
        side_b = math.sqrt(-pow(side_a, 2) + pow(side_c, 2))
        v4_z = -obj.LabelShelfVerticalThickness - side_b * unitmm

        v1 = fc.Vector(towall, 0, stackingoffset)
        v2 = fc.Vector(tolabelend, 0, stackingoffset)
        v3 = fc.Vector(tolabelend, 0, -obj.LabelShelfVerticalThickness + stackingoffset)
        v4 = fc.Vector(towall, 0, v4_z + stackingoffset)

        lines = [
            Part.LineSegment(v1, v2),
            Part.LineSegment(v2, v3),
            Part.LineSegment(v3, v4),
            Part.LineSegment(v4, v1),
        ]

        wire = utils.curve_to_wire(lines)

        face = Part.Face(wire)

        label_shelf_height = obj.LabelShelfVerticalThickness + side_b * unitmm

        if obj.LabelShelfLength > ycompwidth:
            shelf_placement = "Full Width"

        # Label placement specific code
        if shelf_placement == "Full Width":
            funcfuse = _label_shelf_full_width(obj, face, xcompwidth, label_shelf_height)
        if shelf_placement == "Center":
            funcfuse = _label_shelf_center(obj, xcompwidth, ycompwidth, face)
        if shelf_placement == "Left":
            funcfuse = _label_shelf_left(obj, xcompwidth, ycompwidth, face, label_shelf_height)
        if shelf_placement == "Right":
            funcfuse = _label_shelf_right(obj, xcompwidth, ycompwidth, face, label_shelf_height)

        funcfuse = _label_shelf_front_fillet(obj, funcfuse, stackingoffset)

        if label_shelf_height > obj.UsableHeight:
            ytranslate = obj.Clearance + obj.WallThickness
            xtranslate = zeromm
            bottomcutbox = Part.makeBox(
                label_shelf_height,
                obj.StackingLipTopChamfer
                + obj.StackingLipTopLedge
                + obj.StackingLipBottomChamfer
                + obj.LabelShelfWidth
                - obj.WallThickness,
                obj.yTotalWidth,
                fc.Vector(
                    towall,
                    0,
                    -obj.UsableHeight - label_shelf_height + stackingoffset,
                ),
                fc.Vector(0, 1, 0),
            )

            vec_list = []
            for _ in range(xdiv):
                vec_list.append(fc.Vector(xtranslate, ytranslate, 0))
                xtranslate += xcompwidth + obj.DividerThickness

            funcfuse = Part.Shape.cut(funcfuse, utils.copy_and_translate(bottomcutbox, vec_list))
        return funcfuse.translate(
            fc.Vector(
                -obj.xLocationOffset,
                -obj.yLocationOffset,
                0,
            ),
        )


class Scoop(utils.Feature):
    """Create Negative for Bin Compartments."""

    def __init__(self, obj: fc.DocumentObject, *, scoop_default: bool) -> None:
        """Create bin compartments with the option for dividers.

        Args:
            obj (FreeCAD.DocumentObject): Document object
            scoop_default (bool): default state of the scoop feature

        """
        obj.addProperty(
            "App::PropertyLength",
            "ScoopRadius",
            "GridfinityNonStandard",
            "Radius of the Scoop <br> <br> default = 21 mm",
        ).ScoopRadius = preferences.scoop_radius()

        obj.addProperty(
            "App::PropertyBool",
            "Scoop",
            "Gridfinity",
            "Toggle the Scoop fillet on or off",
        ).Scoop = scoop_default

    def make(self, obj: fc.DocumentObject) -> Part.Shape:
        """Create scoop feature.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: 3d scoop object.

        """
        scooprad1 = obj.ScoopRadius + 1 * unitmm
        scooprad2 = obj.ScoopRadius + 1 * unitmm
        scooprad3 = obj.ScoopRadius + 1 * unitmm

        xcomp_w = (
            obj.xTotalWidth - obj.WallThickness * 2 - obj.xDividers * obj.DividerThickness
        ) / (obj.xDividers + 1)

        xdivscoop = obj.xDividerHeight - obj.HeightUnitValue - obj.LabelShelfStackingOffset

        if obj.ScoopRadius > xdivscoop and obj.xDividerHeight != 0:
            scooprad1 = xdivscoop - unitmm
        if obj.ScoopRadius > xcomp_w and obj.xDividers > 0:
            scooprad2 = xcomp_w - 2 * unitmm
        if obj.ScoopRadius > obj.UsableHeight > 0:
            scooprad3 = obj.UsableHeight - obj.LabelShelfStackingOffset

        scooprad = min(obj.ScoopRadius, scooprad1, scooprad2, scooprad3)

        if scooprad <= 0:
            fc.Console.PrintMessage(
                "scooop could not be made due to bin selected parameters\n",
            )
            return None

        v1 = fc.Vector(
            obj.xTotalWidth + obj.Clearance - obj.WallThickness,
            0,
            -obj.UsableHeight + scooprad,
        )
        v2 = fc.Vector(
            obj.xTotalWidth + obj.Clearance - obj.WallThickness,
            0,
            -obj.UsableHeight,
        )
        v3 = fc.Vector(
            obj.xTotalWidth + obj.Clearance - obj.WallThickness - scooprad,
            0,
            -obj.UsableHeight,
        )

        l1 = Part.LineSegment(v1, v2)
        l2 = Part.LineSegment(v2, v3)

        vc1 = fc.Vector(
            obj.xTotalWidth
            + obj.Clearance
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
        compwidth = (
            obj.xTotalWidth - obj.WallThickness * 2 - obj.DividerThickness * obj.xDividers
        ) / (xdiv)

        scoopbox = Part.makeBox(
            obj.StackingLipBottomChamfer
            + obj.StackingLipTopChamfer
            + obj.StackingLipTopLedge
            - obj.WallThickness,
            obj.yTotalWidth - obj.WallThickness * 2,
            obj.UsableHeight,
            fc.Vector(
                obj.xTotalWidth + obj.Clearance - obj.WallThickness,
                +obj.Clearance + obj.WallThickness,
                0,
            ),
            fc.Vector(0, 0, -1),
        )

        scoop = face.extrude(fc.Vector(0, obj.yTotalWidth - obj.WallThickness * 2, 0))

        vec_list = []
        for x in range(xdiv):
            vec_list.append(fc.Vector(-xtranslate, obj.Clearance + obj.WallThickness, 0))

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

        funcfuse = utils.copy_and_translate(scoop, vec_list)
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

        fuse_total = funcfuse.makeFillet(
            obj.StackingLipBottomChamfer
            + obj.StackingLipTopChamfer
            + obj.StackingLipTopLedge
            - obj.WallThickness
            - 0.01 * unitmm,
            b_edges,
        )
        return fuse_total.translate(
            fc.Vector(
                -obj.xLocationOffset,
                -obj.yLocationOffset,
                0,
            ),
        )


def _make_compartments_no_deviders(
    obj: fc.DocumentObject,
    func_fuse: Part.Shape,
) -> Part.Shape:
    # Fillet Bottom edges
    b_edges = []
    for edge in func_fuse.Edges:
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z

        if z0 < 0 and z1 < 0:
            b_edges.append(edge)

    return func_fuse.makeFillet(obj.InsideFilletRadius, b_edges)


def _make_compartments_with_deviders(
    obj: fc.DocumentObject,
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
            fc.Vector(
                obj.Clearance + obj.DividerThickness,
                obj.Clearance,
                -obj.TotalHeight,
            ),
            fc.Vector(0, 0, 1),
        )
        comp.translate(fc.Vector(xtranslate, 0, 0))
        xdiv = comp if xdiv is None else xdiv.fuse(comp)
        xtranslate += xcomp_w + obj.DividerThickness

    # dividers in y direction
    ydiv: Part.Shape | None = None
    for _ in range(obj.yDividers):
        comp = Part.makeBox(
            obj.xTotalWidth,
            obj.DividerThickness,
            ydivheight + stackingoffset,
            fc.Vector(obj.Clearance, obj.Clearance, -obj.TotalHeight),
            fc.Vector(0, 0, 1),
        )

        comp.translate(fc.Vector(0, ytranslate, 0))
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


class Compartments(utils.Feature):
    """Create Negative for Bin Compartments."""

    def __init__(
        self,
        obj: fc.DocumentObject,
        x_div_default: int,
        y_div_default: int,
    ) -> None:
        """Create bin compartments with the option for dividers.

        Args:
            obj (FreeCAD.DocumentObject): Document object
            x_div_default (int): default value or set as input parameter
            y_div_default (int): default value or set as input parameter

        """
        ## Gridfinity Parameters

        obj.addProperty(
            "App::PropertyInteger",
            "xDividers",
            "Gridfinity",
            "Number of Dividers in the x direction",
        ).xDividers = x_div_default

        obj.addProperty(
            "App::PropertyInteger",
            "yDividers",
            "Gridfinity",
            "Number of Dividers in the y direction",
        ).yDividers = y_div_default

        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "InsideFilletRadius",
            "GridfinityNonStandard",
            "inside fillet at the bottom of the bin <br> <br> default = 1.85 mm",
        ).InsideFilletRadius = preferences.divider_fillet_radius()

        obj.addProperty(
            "App::PropertyLength",
            "DividerThickness",
            "GridfinityNonStandard",
            (
                "Thickness of the dividers, ideally an even multiple of printer layer width"
                "<br> <br> default = 1.2 mm"
            ),
        ).DividerThickness = preferences.divider_thickness()

        obj.addProperty(
            "App::PropertyLength",
            "xDividerHeight",
            "GridfinityNonStandard",
            "Custom Height of x dividers <br> <br> default = 0 mm = full height",
        ).xDividerHeight = preferences.divider_custom_x_height()

        obj.addProperty(
            "App::PropertyLength",
            "yDividerHeight",
            "GridfinityNonStandard",
            "Custom Height of y dividers <br> <br> default = 0 mm = full height",
        ).yDividerHeight = preferences.divider_custom_y_height()

        ## Referance Parameters
        obj.addProperty(
            "App::PropertyLength",
            "UsableHeight",
            "ReferenceParameters",
            (
                "Height of the bin minus the bottom unit, "
                "the amount of the bin that can be effectively used"
            ),
            1,
        )

    def make(self, obj: fc.DocumentObject, bin_inside_shape: Part.Wire) -> Part.Shape:
        """Create compartment cutout objects.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            bin_inside_shape (Part.Wire): Profile of bin inside wall

        Returns:
            Part.Shape: Compartments cutout shape.

        """
        ## Calculated Parameters
        obj.UsableHeight = obj.TotalHeight - obj.HeightUnitValue

        ## Error Checks
        divmin = (
            obj.HeightUnitValue
            + obj.InsideFilletRadius
            + 0.05 * unitmm
            + obj.LabelShelfStackingOffset
        )

        if obj.xDividerHeight < divmin and obj.xDividerHeight != 0:
            obj.xDividerHeight = divmin

            fc.Console.PrintWarning(
                "Divider Height must be equal to or greater than:  ",
            )

            fc.Console.PrintWarning(divmin)

            fc.Console.PrintWarning("\n")

        if obj.yDividerHeight < divmin and obj.yDividerHeight != 0:
            obj.yDividerHeight = divmin

            fc.Console.PrintWarning(
                "Divider Height must be equal to or greater than:  ",
            )

            fc.Console.PrintWarning(divmin)

            fc.Console.PrintWarning("\n")

        if (
            obj.xDividerHeight < obj.TotalHeight
            and obj.LabelShelfStyle != "Off"
            and obj.xDividerHeight != 0
            and obj.xDividers != 0
        ):
            obj.LabelShelfStyle = "Off"

            fc.Console.PrintWarning(
                "Label Shelf turned off for less than full height x dividers",
            )
        ## Compartment Generation
        face = Part.Face(bin_inside_shape)

        func_fuse = face.extrude(fc.Vector(0, 0, -obj.UsableHeight))

        if obj.xDividers == 0 and obj.yDividers == 0:
            func_fuse = _make_compartments_no_deviders(obj, func_fuse)

        else:
            func_fuse = _make_compartments_with_deviders(obj, func_fuse)

        return func_fuse.translate(
            fc.Vector(
                -obj.xLocationOffset,
                -obj.yLocationOffset,
                0,
            ),
        )


def make_bottom_hole_shape(obj: fc.DocumentObject) -> Part.Shape:
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
            p = fc.ActiveDocument.addObject("Part::RegularPolygon")
            p.Polygon = 6
            p.Circumradius = radius
            p.recompute()

            p_wire: Part.Wire = p.Shape
            magnet_hole_shape = Part.Face(p_wire).extrude(fc.Vector(0, 0, obj.MagnetHoleDepth))
            fc.ActiveDocument.removeObject(p.Name)
        else:
            magnet_hole_shape = Part.makeCylinder(
                obj.MagnetHoleDiameter / 2,
                obj.MagnetHoleDepth,
                fc.Vector(0, 0, 0),
                fc.Vector(0, 0, 1),
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
            fc.Vector(0, 0, 0),
            fc.Vector(0, 0, 1),
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
            fc.Vector(-obj.ScrewHoleDiameter / 2, -obj.ScrewHoleDiameter / 2, 0),
            fc.Vector(0, 0, 1),
        )
        arc_pt_off_x = (
            math.sqrt(
                ((obj.MagnetHoleDiameter / 2) ** 2) - ((obj.ScrewHoleDiameter / 2) ** 2),
            )
        ) * unitmm
        arc_pt_off_y = obj.ScrewHoleDiameter / 2

        va1 = fc.Vector(
            arc_pt_off_x,
            arc_pt_off_y,
            0,
        )
        va2 = fc.Vector(
            -arc_pt_off_x,
            arc_pt_off_y,
            0,
        )
        va3 = fc.Vector(
            -arc_pt_off_x,
            -arc_pt_off_y,
            0,
        )
        va4 = fc.Vector(
            arc_pt_off_x,
            -arc_pt_off_y,
            0,
        )
        var1 = fc.Vector(
            obj.MagnetHoleDiameter / 2,
            0,
            0,
        )
        var2 = fc.Vector(
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
        sq1_1 = sq1_1.extrude(fc.Vector(0, 0, sqbr1_depth))
        holes_interface_shape = Part.Solid.fuse(sq1_1, b1)

        bottom_hole_shape = (
            holes_interface_shape
            if bottom_hole_shape is None
            else bottom_hole_shape.fuse(holes_interface_shape)
        )
    return bottom_hole_shape


def _eco_bin_cut_fillet_edges_filter(obj: fc.DocumentObject, edge: Part.Edge) -> bool:
    divfil = -obj.TotalHeight + obj.BaseProfileHeight + obj.BaseWallThickness + 1 * unitmm
    z0 = edge.Vertexes[0].Point.z
    z1 = edge.Vertexes[1].Point.z
    return z1 != z0 and (z1 >= divfil or z0 >= divfil)


def _eco_bin_deviders(obj: fc.DocumentObject) -> Part.Shape:
    xcomp_w = (obj.xTotalWidth - obj.WallThickness * 2 - obj.xDividers * obj.DividerThickness) / (
        obj.xDividers + 1
    )
    ycomp_w = (obj.yTotalWidth - obj.WallThickness * 2 - obj.yDividers * obj.DividerThickness) / (
        obj.yDividers + 1
    )

    stackingoffset = -obj.LabelShelfStackingOffset if obj.StackingLip else 0 * unitmm

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
            xdivheight + stackingoffset,
            fc.Vector(
                -obj.xGridSize / 2 + obj.Clearance + obj.DividerThickness,
                -obj.yGridSize / 2 + obj.Clearance,
                -obj.TotalHeight,
            ),
            fc.Vector(0, 0, 1),
        )
        comp.translate(fc.Vector(xtranslate, 0, 0))

        assembly = comp if assembly is None else assembly.fuse(comp)
        xtranslate += xcomp_w + obj.DividerThickness

    # dividers in y direction
    for _ in range(obj.yDividers):
        comp = Part.makeBox(
            obj.xTotalWidth,
            obj.DividerThickness,
            ydivheight + stackingoffset,
            fc.Vector(
                -obj.xGridSize / 2 + obj.Clearance,
                -obj.yGridSize / 2 + obj.Clearance,
                -obj.TotalHeight,
            ),
            fc.Vector(0, 0, 1),
        )
        comp.translate(fc.Vector(0, ytranslate, 0))
        assembly = comp if assembly is None else assembly.fuse(comp)
        ytranslate += ycomp_w + obj.DividerThickness

    return assembly.translate(
        fc.Vector(
            obj.xGridSize / 2,
            obj.yGridSize / 2,
            0,
        ),
    )


def _eco_error_check(obj: fc.DocumentObject) -> None:
    # Divider Minimum Height

    divmin = obj.HeightUnitValue + obj.InsideFilletRadius + 0.05 * unitmm

    if obj.xDividerHeight < divmin and obj.xDividerHeight != 0:
        obj.xDividerHeight = divmin

        fc.Console.PrintWarning(
            "Divider Height must be equal to or greater than:  ",
        )

        fc.Console.PrintWarning(divmin)

        fc.Console.PrintWarning("\n")

    if obj.yDividerHeight < divmin and obj.yDividerHeight != 0:
        obj.yDividerHeight = divmin

        fc.Console.PrintWarning(
            "Divider Height must be equal to or greater than:  ",
        )

        fc.Console.PrintWarning(divmin)

        fc.Console.PrintWarning("\n")

    if obj.InsideFilletRadius > (1.6 * unitmm):
        obj.InsideFilletRadius = 1.6 * unitmm

        fc.Console.PrintWarning(
            "Inside Fillet Radius must be equal to or less than:  1.6 mm\n",
        )


class EcoCompartments(utils.Feature):
    """Create Eco bin main cut and dividers."""

    def __init__(self, obj: fc.DocumentObject) -> None:
        """Create Eco bin dividers.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """
        ## Gridfinity Parameters
        obj.addProperty(
            "App::PropertyLength",
            "BaseWallThickness",
            "Gridfinity",
            "Wall thickness of the bin base",
        ).BaseWallThickness = preferences.eco_bin_base_wall_thickness()

        obj.addProperty(
            "App::PropertyInteger",
            "xDividers",
            "Gridfinity",
            "Number of Dividers in the x direction",
        ).xDividers = preferences.eco_bin_dividers_x()

        obj.addProperty(
            "App::PropertyInteger",
            "yDividers",
            "Gridfinity",
            "Number of Dividers in the y direction",
        ).yDividers = preferences.eco_bin_dividers_y()

        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "InsideFilletRadius",
            "GridfinityNonStandard",
            "inside fillet at the bottom of the bin <br> <br> default = 1.5 mm",
        ).InsideFilletRadius = preferences.eco_bin_inside_fillet_radius()

        obj.addProperty(
            "App::PropertyLength",
            "DividerThickness",
            "GridfinityNonStandard",
            (
                "Thickness of the dividers, ideally an even multiple of layer width <br> <br> "
                "default = 0.8 mm"
            ),
        ).DividerThickness = preferences.eco_bin_divider_thickness()

        obj.addProperty(
            "App::PropertyLength",
            "xDividerHeight",
            "GridfinityNonStandard",
            "Custom Height of x dividers <br> <br> default = 0 mm = full height",
        ).xDividerHeight = preferences.divider_custom_x_height()

        obj.addProperty(
            "App::PropertyLength",
            "yDividerHeight",
            "GridfinityNonStandard",
            "Custom Height of y dividers <br> <br> default = 0 mm = full height",
        ).yDividerHeight = preferences.divider_custom_y_height()

        ## Reference Parameters
        obj.addProperty(
            "App::PropertyLength",
            "UsableHeight",
            "ReferenceParameters",
            (
                "Height of the bin minus the bottom unit, "
                "the amount of the bin that can be effectively used"
            ),
            1,
        )
        ## Hidden Parameters
        obj.setEditorMode("ScrewHoles", 2)

    def make(
        self,
        obj: fc.DocumentObject,
        layout: GridfinityLayout,
        bin_inside_shape: Part.Wire,
    ) -> Part.Shape:
        """Create eco bin cutouts.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            layout (GridfinityLayout): 2 dimentional list of feature locations.
            bin_inside_shape (Part.Wire): Profile of bin inside wall

        Returns:
            Part.Shape: Eco bin cutout shape.

        """
        ## Parameter Calculation

        obj.UsableHeight = obj.TotalHeight - obj.HeightUnitValue
        ## Error Checking

        _eco_error_check(obj)

        ## Eco Compartement Generation
        face = Part.Face(bin_inside_shape)

        func_fuse = face.extrude(
            fc.Vector(0, 0, -obj.TotalHeight + obj.BaseProfileHeight + obj.BaseWallThickness),
        )

        base_offset = obj.BaseWallThickness * math.tan(math.pi / 8)

        x_bt_cmf_width = (
            obj.xGridSize
            - obj.Clearance * 2
            - 2 * obj.BaseProfileTopChamfer
            - obj.BaseWallThickness * 2
            - 0.4 * unitmm * 2
        )
        y_bt_cmf_width = (
            obj.yGridSize
            - obj.Clearance * 2
            - 2 * obj.BaseProfileTopChamfer
            - obj.BaseWallThickness * 2
            - 0.4 * unitmm * 2
        )

        x_vert_width = (
            obj.xGridSize
            - obj.Clearance * 2
            - 2 * obj.BaseProfileTopChamfer
            - obj.BaseWallThickness * 2
        )
        y_vert_width = (
            obj.yGridSize
            - obj.Clearance * 2
            - 2 * obj.BaseProfileTopChamfer
            - obj.BaseWallThickness * 2
        )

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

        bottom_chamfer = utils.rounded_rectangle_chamfer(
            x_bt_cmf_width,
            y_bt_cmf_width,
            -obj.TotalHeight + obj.BaseWallThickness + magoffset,
            0.4 * unitmm,
            bt_chf_rad,
        )

        vertical_section = utils.rounded_rectangle_extrude(
            x_vert_width,
            y_vert_width,
            -obj.TotalHeight + obj.BaseWallThickness + 0.4 * unitmm + magoffset,
            obj.BaseProfileVerticalSection
            + obj.BaseProfileBottomChamfer
            + base_offset
            - obj.BaseWallThickness
            - 0.4 * unitmm,
            v_chf_rad,
        )

        top_chamfer = utils.rounded_rectangle_chamfer(
            x_vert_width + tp_chf_offset,
            y_vert_width + tp_chf_offset,
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
        for x in range(obj.xMaxGrids):
            ytranslate = zeromm
            for y in range(obj.yMaxGrids):
                if layout[x][y]:
                    vec_list.append(fc.Vector(xtranslate, ytranslate, 0))
                ytranslate += obj.yGridSize
            xtranslate += obj.xGridSize

        eco_base_cut = utils.copy_and_translate(assembly, vec_list)

        eco_base_cut.translate(
            fc.Vector(
                obj.xGridSize / 2,
                obj.yGridSize / 2,
                0,
            ),
        )

        func_fuse = func_fuse.fuse(eco_base_cut)

        outer_trim1 = utils.rounded_rectangle_extrude(
            obj.xTotalWidth - obj.WallThickness * 2,
            obj.yTotalWidth - obj.WallThickness * 2,
            -obj.TotalHeight,
            obj.TotalHeight,
            obj.BinOuterRadius - obj.WallThickness,
        ).translate(
            fc.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        outer_trim2 = utils.rounded_rectangle_extrude(
            obj.xTotalWidth + 20 * unitmm,
            obj.yTotalWidth + 20 * unitmm,
            -obj.TotalHeight,
            obj.TotalHeight - obj.BaseProfileHeight,
            obj.BinOuterRadius,
        ).translate(
            fc.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        outer_trim2 = outer_trim2.cut(outer_trim1)

        func_fuse = func_fuse.cut(outer_trim2)

        if obj.xDividers > 0 or obj.yDividers > 0:
            deviders = _eco_bin_deviders(obj)

            func_fuse = func_fuse.cut(deviders)

            b_edges = []
            divfil = -obj.TotalHeight + obj.BaseProfileHeight + obj.BaseWallThickness + 1 * unitmm
            for edge in func_fuse.Edges:
                z0 = edge.Vertexes[0].Point.z
                z1 = edge.Vertexes[1].Point.z

                if z1 != z0 and (z1 >= divfil or z0 >= divfil):
                    b_edges.append(edge)

            func_fuse = func_fuse.makeFillet(obj.InsideFilletRadius / 2, b_edges)
        return func_fuse.translate(
            fc.Vector(
                -obj.xLocationOffset,
                -obj.yLocationOffset,
                0,
            ),
        )


class BinBaseValues(utils.Feature):
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
            "Height of the Gridfinity Base Profile, bottom of the bin",
            1,
        )

        ## Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileBottomChamfer",
            "zzExpertOnly",
            "height of chamfer in bottom of bin base profile <br> <br> default = 0.8 mm",
            1,
        ).BaseProfileBottomChamfer = preferences.bin_base_bottom_chamfer()

        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileVerticalSection",
            "zzExpertOnly",
            "Height of the vertical section in bin base profile",
            1,
        ).BaseProfileVerticalSection = preferences.bin_base_vertical_section()

        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileTopChamfer",
            "zzExpertOnly",
            "Height of the top chamfer in the bin base profile",
            1,
        ).BaseProfileTopChamfer = preferences.bin_base_top_chamfer()

        obj.addProperty(
            "App::PropertyLength",
            "BinOuterRadius",
            "zzExpertOnly",
            "Outer radius of the bin",
            1,
        ).BinOuterRadius = preferences.bin_outer_radius()

        obj.addProperty(
            "App::PropertyLength",
            "BinVerticalRadius",
            "zzExpertOnly",
            "Radius of the base profile Vertical section",
            1,
        ).BinVerticalRadius = preferences.bin_base_vertical_radius()

        obj.addProperty(
            "App::PropertyLength",
            "BinBottomRadius",
            "zzExpertOnly",
            "bottom of bin corner radius",
            1,
        ).BinBottomRadius = preferences.bin_base_bottom_radius()

        obj.addProperty(
            "App::PropertyLength",
            "Clearance",
            "zzExpertOnly",
            (
                "The clearance on each side of a bin between before the edge of the grid,"
                "gives some clearance between bins <br> <br>"
                "default = 0.25 mm"
            ),
        ).Clearance = preferences.clearance()

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


def make_complex_bin_base(
    obj: fc.DocumentObject,
    layout: GridfinityLayout,
) -> Part.Shape:
    """Creaet complex shaped bin base.

    Args:
        obj (FreeCAD.DocumentObject): Document object.mro
        layout (GridfinityLayout): 2 dimentional list of feature locations.

    Returns:
        Part.Shape: Complex bin base shape.

    """
    if obj.Baseplate:
        baseplate_size_adjustment = obj.BaseplateTopLedgeWidth - obj.Clearance
    else:
        baseplate_size_adjustment = 0 * unitmm

    x_bt_cmf_width = (
        (obj.xGridSize - obj.Clearance * 2)
        - 2 * obj.BaseProfileBottomChamfer
        - 2 * obj.BaseProfileTopChamfer
        - 2 * baseplate_size_adjustment
    )
    y_bt_cmf_width = (
        (obj.yGridSize - obj.Clearance * 2)
        - 2 * obj.BaseProfileBottomChamfer
        - 2 * obj.BaseProfileTopChamfer
        - 2 * baseplate_size_adjustment
    )
    x_vert_width = (
        (obj.xGridSize - obj.Clearance * 2)
        - 2 * obj.BaseProfileTopChamfer
        - 2 * baseplate_size_adjustment
    )
    y_vert_width = (
        (obj.yGridSize - obj.Clearance * 2)
        - 2 * obj.BaseProfileTopChamfer
        - 2 * baseplate_size_adjustment
    )
    xtranslate = zeromm
    ytranslate = zeromm

    bottom_chamfer = utils.rounded_rectangle_chamfer(
        x_bt_cmf_width,
        y_bt_cmf_width,
        -obj.TotalHeight,
        obj.BaseProfileBottomChamfer,
        obj.BinBottomRadius,
    )

    vertical_section = utils.rounded_rectangle_extrude(
        x_vert_width,
        y_vert_width,
        -obj.TotalHeight + obj.BaseProfileBottomChamfer,
        obj.BaseProfileVerticalSection,
        obj.BinVerticalRadius,
    )
    assembly = Part.Shape.fuse(bottom_chamfer, vertical_section)

    top_chamfer = utils.rounded_rectangle_chamfer(
        x_vert_width,
        y_vert_width,
        -obj.TotalHeight + obj.BaseProfileBottomChamfer + obj.BaseProfileVerticalSection,
        obj.BaseProfileTopChamfer,
        obj.BinVerticalRadius,
    )

    assembly = Part.Solid.multiFuse(bottom_chamfer, [vertical_section, top_chamfer])

    parts = []

    for x in range(obj.xMaxGrids):
        ytranslate = zeromm
        for y in range(obj.yMaxGrids):
            if layout[x][y]:
                b = assembly.copy()
                b.translate(fc.Vector(xtranslate, ytranslate, 0))

            if x == 0 and y == 0:
                b1 = b
            else:
                parts.append(b)

            ytranslate += obj.yGridSize

        xtranslate += obj.xGridSize

    larger_than_single_grid = 2
    fuse_total = (
        b1
        if obj.xMaxGrids < larger_than_single_grid and obj.yMaxGrids < larger_than_single_grid
        else Part.Solid.multiFuse(b1, parts)
    )

    return fuse_total.translate(
        fc.Vector(
            obj.xGridSize / 2 - obj.xLocationOffset,
            obj.yGridSize / 2 - obj.yLocationOffset,
            0,
        ),
    )


class BlankBinRecessedTop(utils.Feature):
    """Cut into blank bin to create recessed bin top."""

    def __init__(self, obj: fc.DocumentObject) -> None:
        """Create blank bin recessed top section.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        """
        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "RecessedTopDepth",
            "GridfinityNonStandard",
            "height per unit <br> <br> default = 0 mm",
        ).RecessedTopDepth = preferences.blank_bin_recessed_top_depth()

    def make(self, obj: fc.DocumentObject, bin_inside_shape: Part.Wire) -> Part.Shape:
        """Generate Rectanble layout and calculate relevant parameters.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            bin_inside_shape (Part.Wire): shape of the bin inside the walls

        Returns:
            Part.Shape: Extruded part to cut out inside of bin.

        """
        face = Part.Face(bin_inside_shape)

        fuse_total = face.extrude(fc.Vector(0, 0, -obj.RecessedTopDepth))

        return fuse_total.translate(
            fc.Vector(
                -obj.xLocationOffset,
                -obj.yLocationOffset,
                0,
            ),
        )


class BinBottomHoles(utils.Feature):
    """Cut into blank bin to create recessed bin top."""

    def __init__(
        self,
        obj: fc.DocumentObject,
        *,
        magnet_holes_default: bool,
    ) -> None:
        """Create bin solid mid section.

        Args:
            obj (FreeCAD.DocumentObject): Document object
            magnet_holes_default (bool): does the object have magnet holes

        """
        ## Gridfinity Parameters
        obj.addProperty(
            "App::PropertyBool",
            "MagnetHoles",
            "Gridfinity",
            "Toggle the magnet holes on or off",
        ).MagnetHoles = magnet_holes_default

        obj.addProperty(
            "App::PropertyBool",
            "ScrewHoles",
            "Gridfinity",
            "Toggle the screw holes on or off",
        ).ScrewHoles = preferences.bin_screw_holes()

        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "SequentialBridgingLayerHeight",
            "GridfinityNonStandard",
            "Layer Height that you print in for optimal print results,"
            "used for screw holes bridging with magnet holes also on",
        ).SequentialBridgingLayerHeight = preferences.sequential_bridging_layer_height()

        obj.addProperty(
            "App::PropertyEnumeration",
            "MagnetHolesShape",
            "GridfinityNonStandard",
            (
                "Shape of magnet holes, change to suit your printers capabilities"
                "which might require testing."
                "<br> Round press fit by default, increase to 6.5 mm if using glue"
                "<br> <br> Hex is alternative press fit style."
                "<br> <br> default = 6.2 mm"
            ),
        )
        obj.MagnetHolesShape = const.HOLE_SHAPES

        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDiameter",
            "GridfinityNonStandard",
            (
                "Diameter of Magnet Holes "
                "<br> Round press fit by default, increase to 6.5 mm if using glue"
                "<br> <br> Hex is alternative press fit style, inscribed diameter<br> <br>"
                "<br> <br> default = 6.2 mm"
            ),
        ).MagnetHoleDiameter = preferences.magnet_hole_diameter()

        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDepth",
            "GridfinityNonStandard",
            "Depth of Magnet Holes <br> <br> default = 2.4 mm",
        ).MagnetHoleDepth = preferences.magnet_hole_depth()

        obj.addProperty(
            "App::PropertyLength",
            "ScrewHoleDiameter",
            "GridfinityNonStandard",
            "Diameter of Screw Holes, used to put screws in bin to secure in place"
            "<br> <br> default = 3.0 mm",
        ).ScrewHoleDiameter = preferences.screw_hole_diameter()

        obj.addProperty(
            "App::PropertyLength",
            "ScrewHoleDepth",
            "GridfinityNonStandard",
            "Depth of Screw Holes <br> <br> default = 6.0 mm",
        ).ScrewHoleDepth = preferences.screw_hole_depth()

        ## Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDistanceFromEdge",
            "zzExpertOnly",
            "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",
            1,
        ).MagnetHoleDistanceFromEdge = preferences.magnet_hole_distance_from_edge()

    def make(
        self,
        obj: fc.DocumentObject,
        layout: GridfinityLayout,
    ) -> Part.Shape:
        """Make bin bottom holes.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject
            layout (GridfinityLayout): Layout of the gridfinity grid.

        Returns:
            Part.Shape: Shape containing negatives of all holes.

        """
        bottom_hole_shape = make_bottom_hole_shape(obj)

        x_hole_pos = obj.xGridSize / 2 - obj.MagnetHoleDistanceFromEdge
        y_hole_pos = obj.yGridSize / 2 - obj.MagnetHoleDistanceFromEdge

        hole_shape_sub_array = utils.copy_and_translate(
            bottom_hole_shape,
            [
                fc.Vector(-x_hole_pos, -y_hole_pos, -obj.TotalHeight),
                fc.Vector(x_hole_pos, -y_hole_pos, -obj.TotalHeight),
                fc.Vector(-x_hole_pos, y_hole_pos, -obj.TotalHeight),
                fc.Vector(x_hole_pos, y_hole_pos, -obj.TotalHeight),
            ],
        )
        vec_list = []
        xtranslate = 0
        for x in range(obj.xMaxGrids):
            ytranslate = 0
            for y in range(obj.yMaxGrids):
                if layout[x][y]:
                    vec_list.append(fc.Vector(xtranslate, ytranslate, 0))
                ytranslate += obj.yGridSize.Value
            xtranslate += obj.xGridSize.Value

        fuse_total = utils.copy_and_translate(hole_shape_sub_array, vec_list).translate(
            fc.Vector(obj.xGridSize / 2, obj.yGridSize / 2, 0),
        )
        return fuse_total.translate(
            fc.Vector(
                -obj.xLocationOffset,
                -obj.yLocationOffset,
                0,
            ),
        )


class StackingLip(utils.Feature):
    """Create bin stacking lip."""

    def __init__(
        self,
        obj: fc.DocumentObject,
        *,
        stacking_lip_default: bool,
    ) -> None:
        """Create bin stacking lip.

        Args:
            obj (FreeCAD.DocumentObject): Document object
            stacking_lip_default (bool): stacking lip on or off

        """
        ## Gridfinity Parameters
        obj.addProperty(
            "App::PropertyBool",
            "StackingLip",
            "Gridfinity",
            "Toggle the stacking lip on or off",
        ).StackingLip = stacking_lip_default

        ## Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "StackingLipTopLedge",
            "zzExpertOnly",
            "Top Ledge of the stacking lip <br> <br> default = 0.4 mm",
            1,
        ).StackingLipTopLedge = preferences.stacking_lip_top_ledge()

        obj.addProperty(
            "App::PropertyLength",
            "StackingLipTopChamfer",
            "zzExpertOnly",
            "Top Chamfer of the Stacking lip",
            1,
        )

        obj.addProperty(
            "App::PropertyLength",
            "StackingLipBottomChamfer",
            "zzExpertOnly",
            "Bottom Chamfer of the Stacking lip<br> <br> default = 0.7 mm",
            1,
        ).StackingLipBottomChamfer = preferences.stacking_lip_bottom_chamfer()

        obj.addProperty(
            "App::PropertyLength",
            "StackingLipVerticalSection",
            "zzExpertOnly",
            "vertical section of the Stacking lip<br> <br> default = 1.8 mm",
            1,
        ).StackingLipVerticalSection = preferences.stacking_lip_vertical_section()

    def make(self, obj: fc.DocumentObject, bin_outside_shape: Part.Wire) -> Part.Shape:
        """Create stacking lip based on input bin shape.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject
            bin_outside_shape (Part.Wire): exterior wall of the bin

        Returns:
            Part.Shape: Stacking lip shape.

        """
        ## Calculated Values
        obj.StackingLipTopChamfer = (
            obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
        )

        ## Stacking Lip Generation
        st1 = fc.Vector(obj.Clearance, obj.yGridSize / 2, 0)
        st2 = fc.Vector(
            obj.Clearance,
            obj.yGridSize / 2,
            obj.StackingLipBottomChamfer
            + obj.StackingLipVerticalSection
            + obj.StackingLipTopChamfer,
        )
        st3 = fc.Vector(
            obj.Clearance + obj.StackingLipTopLedge,
            obj.yGridSize / 2,
            obj.StackingLipBottomChamfer
            + obj.StackingLipVerticalSection
            + obj.StackingLipTopChamfer,
        )
        st4 = fc.Vector(
            obj.Clearance + obj.StackingLipTopLedge + obj.StackingLipTopChamfer,
            obj.yGridSize / 2,
            obj.StackingLipBottomChamfer + obj.StackingLipVerticalSection,
        )
        st5 = fc.Vector(
            obj.Clearance + obj.StackingLipTopLedge + obj.StackingLipTopChamfer,
            obj.yGridSize / 2,
            obj.StackingLipBottomChamfer,
        )
        st6 = fc.Vector(
            obj.Clearance
            + obj.StackingLipTopLedge
            + obj.StackingLipTopChamfer
            + obj.StackingLipBottomChamfer,
            obj.yGridSize / 2,
            0,
        )
        st7 = fc.Vector(
            obj.Clearance
            + obj.StackingLipTopLedge
            + obj.StackingLipTopChamfer
            + obj.StackingLipBottomChamfer,
            obj.yGridSize / 2,
            -obj.StackingLipVerticalSection,
        )
        st8 = fc.Vector(
            obj.Clearance + obj.WallThickness,
            obj.yGridSize / 2,
            -obj.StackingLipVerticalSection
            - (
                obj.StackingLipTopLedge
                + obj.StackingLipTopChamfer
                + obj.StackingLipBottomChamfer
                - obj.WallThickness
            ),
        )
        st9 = fc.Vector(obj.Clearance + obj.WallThickness, obj.yGridSize / 2, 0)

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

        stacking_lip = Part.Wire(bin_outside_shape).makePipe(wire)

        stacking_lip = Part.makeSolid(stacking_lip)

        return stacking_lip.translate(
            fc.Vector(
                -obj.xLocationOffset,
                -obj.yLocationOffset,
                0,
            ),
        )


class BinSolidMidSection(utils.Feature):
    """Generate bin mid section and add relevant properties."""

    def __init__(
        self,
        obj: fc.DocumentObject,
        default_height_units: int,
        default_wall_thickness: int,
    ) -> None:
        """Create bin solid mid section and add properties.

        Args:
            obj (FreeCAD.DocumentObject): Document object
            default_height_units (int): height units of the bin at generation
            default_wall_thickness (int): Wall thickness of the bin at generation

        """
        ## Gridfinity Standard Parameters
        obj.addProperty(
            "App::PropertyInteger",
            "HeightUnits",
            "Gridfinity",
            "Height of the bin in units, each is 7 mm",
        ).HeightUnits = default_height_units

        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "CustomHeight",
            "GridfinityNonStandard",
            "total height of the bin using the custom height instead of increments of 7 mm",
        ).CustomHeight = 42

        obj.addProperty(
            "App::PropertyBool",
            "NonStandardHeight",
            "GridfinityNonStandard",
            "use a custom height if selected",
        ).NonStandardHeight = False

        obj.addProperty(
            "App::PropertyLength",
            "WallThickness",
            "GridfinityNonStandard",
            "for stacking lip",
        ).WallThickness = default_wall_thickness

        ## Reference Parameters
        obj.addProperty(
            "App::PropertyLength",
            "TotalHeight",
            "ReferenceParameters",
            "total height of the bin",
            1,
        )
        ## Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "HeightUnitValue",
            "zzExpertOnly",
            "height per unit, default is 7mm",
            1,
        ).HeightUnitValue = preferences.grid_height()

    def make(self, obj: fc.DocumentObject, bin_outside_shape: Part.Wire) -> Part.Shape:
        """Generate bin solid mid section.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            bin_outside_shape (Part.Wire): shape of the bin

        Returns:
            Part.Shape: Extruded bin mid section of the input shape

        """
        ## Calculated Values
        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight

        else:
            obj.TotalHeight = obj.HeightUnits * obj.HeightUnitValue

        ## Bin Solid Mid Section Generation
        face = Part.Face(bin_outside_shape)

        fuse_total = face.extrude(fc.Vector(0, 0, -obj.TotalHeight + obj.BaseProfileHeight))

        return fuse_total.translate(
            fc.Vector(
                -obj.xLocationOffset,
                -obj.yLocationOffset,
                0,
            ),
        )
