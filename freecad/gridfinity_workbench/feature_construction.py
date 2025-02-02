"""Module containing gridfinity feature constructions."""

import math

import FreeCAD
import Part
from FreeCAD import Units

from .utils import Utils

from abc import abstractmethod
from enum import Enum

from .const import (
    X_DIVIDERS,
    Y_DIVIDERS,
    INSIDE_FILLET_RADIUS,
    DIVIDER_THICKNESS,
    CUSTOM_X_DIVIDER_HEIGHT,
    CUSTOM_Y_DIVIDER_HEIGHT,
    LABEL_SHELF_WIDTH,
    LABEL_SHELF_LENGTH,
    LABEL_SHELF_ANGLE,
    LABEL_SHELF_STACKING_OFFSET,
    LABEL_SHELF_VERTICAL_THICKNESS,
    SCOOP,
    SCOOP_RADIUS,
    ECO_DIVIDER_THICKNESS,
    BASE_WALL_THICKNESS,
    ECO_X_DIVIDERS,
    ECO_Y_DIVIDERS,
    ECO_INSIDE_FILLET_RADIUS,
)

unitmm = Units.Quantity("1 mm")
zeromm = Units.Quantity("0 mm")

SMALL_NUMBER = 0.01


class Feature:
    @abstractmethod
    def Make(obj):
        raise NotImplementedError()


def _label_shelf_full_width(
    obj: FreeCAD.DocumentObject,
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
        face.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

        ls = face.extrude(FreeCAD.Vector(0, fw, 0))



        if x == 0:
            firstls = ls
        else:
            parts.append(ls)

        xtranslate += xcompwidth + obj.DividerThickness

    funcfuse = ls if xdiv == 1 else Part.Solid.multiFuse(firstls, parts)

    right_end_fillet = _label_shelf_right_fillet(obj)
    right_end_fillet = right_end_fillet.translate(FreeCAD.Vector(0, obj.yTotalWidth - obj.WallThickness * 2 - obj.BinOuterRadius + obj.WallThickness, 0))
    right_end_fillet = right_end_fillet.extrude(FreeCAD.Vector(0, 0, -label_shelf_height - obj.LabelShelfStackingOffset))
    funcfuse = funcfuse.cut(right_end_fillet)

    left_end_fillet = _label_shelf_left_fillet(obj)
    left_end_fillet = left_end_fillet.extrude(FreeCAD.Vector(0, 0, -label_shelf_height - obj.LabelShelfStackingOffset))
    return funcfuse.cut(left_end_fillet)


    return funcfuse
    #return funcfuse.makeFillet(obj.BinOuterRadius - obj.WallThickness, b_edges)


def _label_shelf_center(
    obj: FreeCAD.DocumentObject,
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
            ls = face.extrude(FreeCAD.Vector(0, obj.LabelShelfLength, 0))

            ls.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

            if x == 0 and y == 0:
                firstls = ls
            else:
                parts.append(ls)

            ytranslate += ycompwidth + obj.DividerThickness

        xtranslate += xcompwidth + obj.DividerThickness

    funcfuse = ls if xdiv == 1 and ydiv == 1 else Part.Solid.multiFuse(firstls, parts)

    y2 = obj.Clearance + obj.WallThickness
    b_edges = []
    for edge in funcfuse.Edges:
        y0 = edge.Vertexes[0].Point.y
        y1 = edge.Vertexes[1].Point.y
        x0 = edge.Vertexes[0].Point.x
        x1 = edge.Vertexes[1].Point.x

        if y0 == y2 and y1 == y2 and x1 == y2 and x0 == y2:
            b_edges.append(edge)

    left_end_fillet = _label_shelf_left_fillet(obj)
    left_end_fillet = left_end_fillet.extrude(FreeCAD.Vector(0, 0, -label_shelf_height - obj.LabelShelfStackingOffset))
    return funcfuse.cut(left_end_fillet)



def _label_shelf_right(
    obj: FreeCAD.DocumentObject,
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
            ls = face.extrude(FreeCAD.Vector(0, obj.LabelShelfLength, 0))

            ls.translate(FreeCAD.Vector(xtranslate, ytranslate, 0))

            if x == 0 and y == 0:
                firstls = ls
            else:
                parts.append(ls)

            ytranslate += ycompwidth + obj.DividerThickness

        xtranslate += xcompwidth + obj.DividerThickness

    funcfuse = ls if xdiv == 1 and ydiv == 1 else Part.Solid.multiFuse(firstls, parts)

    y2 = obj.yTotalWidth + obj.Clearance - obj.WallThickness
    x2 = obj.Clearance + obj.WallThickness
    b_edges = []
    for edge in funcfuse.Edges:
        y0 = edge.Vertexes[0].Point.y
        y1 = edge.Vertexes[1].Point.y
        x0 = edge.Vertexes[0].Point.x
        x1 = edge.Vertexes[1].Point.x

        if y0 == y2 and y1 == y2 and x1 == x2 and x0 == x2:
            b_edges.append(edge)

    right_end_fillet = _label_shelf_right_fillet(obj)
    right_end_fillet = right_end_fillet.translate(FreeCAD.Vector(0, obj.yTotalWidth - obj.WallThickness * 2 - obj.BinOuterRadius + obj.WallThickness, 0))
    right_end_fillet = right_end_fillet.extrude(FreeCAD.Vector(0, 0, -label_shelf_height - obj.LabelShelfStackingOffset))
    return funcfuse.cut(right_end_fillet)




def _label_shelf_front_fillet(
    obj: FreeCAD.DocumentObject,
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

def _label_shelf_left_fillet(obj: FreeCAD.DocumentObject,)-> Part.Shape:

    fillet_radius = obj.BinOuterRadius - obj.WallThickness

    # Drawing fillet shape starting bottom left corner and going clockwise
    l1x = obj.Clearance + obj.WallThickness
    l1y1 = obj.Clearance + obj.WallThickness
    l1y2 = obj.Clearance + obj.WallThickness + fillet_radius

    arc1x = obj.Clearance + obj.WallThickness + fillet_radius - fillet_radius * math.sin(math.pi / 4)
    arc1y = arc1x

    l2x1 = l1y2
    l2x2 = l1x
    l2y = l1y1

    l1v1 = FreeCAD.Vector(l1x, l1y1, 0)
    l1v2 = FreeCAD.Vector(l1x, l1y2, 0)
    arc1v = FreeCAD.Vector(arc1x, arc1y, 0)
    l2v1 = FreeCAD.Vector(l2x1, l2y, 0)
    l2v2 = FreeCAD.Vector(l2x2, l2y, 0)

    lines = [
        Part.LineSegment(l1v1, l1v2),
        Part.Arc(l1v2, arc1v, l2v1),
        Part.LineSegment(l2v1, l2v2),
    ]

    left_fillet_wire = Utils.curve_to_wire(lines)

    return Part.Face(left_fillet_wire)


def _label_shelf_right_fillet(obj: FreeCAD.DocumentObject,)-> Part.Shape:

    fillet_radius = obj.BinOuterRadius - obj.WallThickness

    # Drawing fillet shape starting bottom left corner and going clockwise

    l1x = obj.Clearance + obj.WallThickness
    l1y1 = obj.Clearance + obj.WallThickness
    l1y2 = obj.Clearance + obj.WallThickness + fillet_radius

    l2x1 = l1x
    l2x2 = l1y2
    l2y = l1y2

    arc1x = obj.Clearance + obj.WallThickness + fillet_radius - fillet_radius * math.sin(math.pi / 4)
    arc1y = obj.Clearance + obj.WallThickness + fillet_radius * math.sin(math.pi / 4)

    l1v1 = FreeCAD.Vector(l1x, l1y1, 0)
    l1v2 = FreeCAD.Vector(l1x, l1y2, 0)
    l2v1 = FreeCAD.Vector(l2x1, l2y, 0)
    l2v2 = FreeCAD.Vector(l2x2, l2y, 0)
    arc1v = FreeCAD.Vector(arc1x, arc1y, 0)

    lines = [
        Part.LineSegment(l1v1, l1v2),
        Part.LineSegment(l2v1, l2v2),
        Part.Arc(l2v2, arc1v, l1v1),
    ]

    right_fillet_wire = Utils.curve_to_wire(lines)
    return Part.Face(right_fillet_wire)




class LabelShelf(Feature):
    """Create Label shelf for bins"""

    def __init__(self, obj: FreeCAD.DocumentObject, label_style_default="Standard"):
        """create bin compartments with the option for dividers.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
        """
        ## Gridfinity Parameters
        obj.addProperty(
            "App::PropertyEnumeration",
            "LabelShelfStyle",
            "Gridfinity",
            "Choose to turn the label shelf on or off",
        )

        obj.LabelShelfStyle = ["Off", "Standard", "Overhang"]
        obj.LabelShelfStyle = label_style_default

        obj.addProperty(
            "App::PropertyEnumeration",
            "LabelShelfPlacement",
            "Gridfinity",
            "Choose the style of the label shelf",
        )

        obj.LabelShelfPlacement = ["Center", "Full Width", "Left", "Right"]

        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "LabelShelfWidth",
            "GridfinityNonStandard",
            "Thickness of the Label Shelf <br> <br> default = 12 mm",
        ).LabelShelfWidth = LABEL_SHELF_WIDTH

        obj.addProperty(
            "App::PropertyLength",
            "LabelShelfLength",
            "GridfinityNonStandard",
            "Length of the Label Shelf <br> <br> default = 42 mm",
        ).LabelShelfLength = LABEL_SHELF_LENGTH

        obj.addProperty(
            "App::PropertyAngle",
            "LabelShelfAngle",
            "GridfinityNonStandard",
            "Angle of the bottom part of the Label Shelf <br> <br> default = 45",
        ).LabelShelfAngle = LABEL_SHELF_ANGLE

        ## Expert Only Parameters
        obj.addProperty(
            "App::PropertyLength",
            "LabelShelfStackingOffset",
            "zzExpertOnly",
            "Vertical Thickness of the Label Shelf <br> <br> default = 0.4 mm",
        ).LabelShelfStackingOffset = LABEL_SHELF_STACKING_OFFSET

        obj.addProperty(
            "App::PropertyLength",
            "LabelShelfVerticalThickness",
            "zzExpertOnly",
            "Vertical Thickness of the Label Shelf <br> <br> default = 2 mm",
        ).LabelShelfVerticalThickness = LABEL_SHELF_VERTICAL_THICKNESS

    def Make(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Create label shelf.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Labelshelf 3D shape.

        """

        towall = obj.Clearance + obj.WallThickness
        tolabelend = (
            obj.Clearance
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




        if self.bintype == "eco" and obj.TotalHeight < 15 and obj.LabelShelfStyle != "Overhang":
            obj.LabelShelfStyle = "Overhang"
            FreeCAD.Console.PrintWarning("\n")
            FreeCAD.Console.PrintWarning(
                "Label shelf style set to Overhand due to low bin height",
            )

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
                FreeCAD.Vector(
                    towall,
                    0,
                    -obj.UsableHeight - label_shelf_height + stackingoffset,
                ),
                FreeCAD.Vector(0, 1, 0),
            )

            vec_list = []
            for _ in range(xdiv):
                vec_list.append(FreeCAD.Vector(xtranslate, ytranslate, 0))
                xtranslate += xcompwidth + obj.DividerThickness

            funcfuse = Part.Shape.cut(funcfuse, Utils.copy_and_translate(bottomcutbox, vec_list))
        return funcfuse.translate(FreeCAD.Vector(-obj.xLocationOffset,-obj.yLocationOffset,0,))


class Scoop(Feature):
    """Create Negative for Bin Compartments"""

    def __init__(self, obj: FreeCAD.DocumentObject, scoop_default=SCOOP):
        """create bin compartments with the option for dividers.

        Args:
            obj (FreeCAD.DocumentObject): Document object
            scoop_default: default state of the scoop feature

        """

        obj.addProperty(
            "App::PropertyLength",
            "ScoopRadius",
            "GridfinityNonStandard",
            "Radius of the Scoop <br> <br> default = 21 mm",
        ).ScoopRadius = SCOOP_RADIUS

        obj.addProperty(
            "App::PropertyBool",
            "Scoop",
            "Gridfinity",
            "Toggle the Scoop fillet on or off",
        ).Scoop = scoop_default

    def Make(obj: FreeCAD.DocumentObject) -> Part.Shape:
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
            FreeCAD.Console.PrintMessage(
                "scooop could not be made due to bin selected parameters\n",
            )
            return None

        v1 = FreeCAD.Vector(
            obj.xTotalWidth + obj.Clearance - obj.WallThickness,
            0,
            -obj.UsableHeight + scooprad,
        )
        v2 = FreeCAD.Vector(
            obj.xTotalWidth + obj.Clearance - obj.WallThickness,
            0,
            -obj.UsableHeight,
        )
        v3 = FreeCAD.Vector(
            obj.xTotalWidth + obj.Clearance - obj.WallThickness - scooprad,
            0,
            -obj.UsableHeight,
        )

        l1 = Part.LineSegment(v1, v2)
        l2 = Part.LineSegment(v2, v3)

        vc1 = FreeCAD.Vector(
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
            FreeCAD.Vector(
                obj.xTotalWidth + obj.Clearance - obj.WallThickness,
                +obj.Clearance + obj.WallThickness,
                0,
            ),
            FreeCAD.Vector(0, 0, -1),
        )

        scoop = face.extrude(FreeCAD.Vector(0, obj.yTotalWidth - obj.WallThickness * 2, 0))

        vec_list = []
        for x in range(xdiv):
            vec_list.append(FreeCAD.Vector(-xtranslate, obj.Clearance + obj.WallThickness, 0))

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

        fuse_total = funcfuse.makeFillet(
            obj.StackingLipBottomChamfer
            + obj.StackingLipTopChamfer
            + obj.StackingLipTopLedge
            - obj.WallThickness
            - 0.01 * unitmm,
            b_edges,
        )
        return fuse_total.translate(FreeCAD.Vector(-obj.xLocationOffset,-obj.yLocationOffset,0,))


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
    # b_edges = []
    # for edge in func_fuse.Edges:
    # z0 = edge.Vertexes[0].Point.z
    # z1 = edge.Vertexes[1].Point.z

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
                obj.Clearance + obj.DividerThickness,
                obj.Clearance,
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
            FreeCAD.Vector(obj.Clearance, obj.Clearance, -obj.TotalHeight),
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


class Compartments(Feature):
    """Create Negative for Bin Compartments"""

    def __init__(
        self, obj: FreeCAD.DocumentObject, x_div_default=X_DIVIDERS, y_div_default=Y_DIVIDERS
    ):
        """create bin compartments with the option for dividers.

        Args:
            obj (FreeCAD.DocumentObject): Document object
            x_div_default: default value or set as input parameter
            y_div_default: default value or set as input parameter

        """

        ## Gridfinity Parameters

        obj.addProperty(
            "App::PropertyInteger",
            "xDividers",
            "Gridfinity",
            "Select the Number of Dividers in the x direction",
        ).xDividers = x_div_default

        obj.addProperty(
            "App::PropertyInteger",
            "yDividers",
            "Gridfinity",
            "Select the number of Dividers in the y direction",
        ).yDividers = y_div_default

        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "InsideFilletRadius",
            "GridfinityNonStandard",
            "inside fillet at the bottom of the bin <br> <br> default = 1.85 mm",
        ).InsideFilletRadius = INSIDE_FILLET_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "DividerThickness",
            "GridfinityNonStandard",
            (
                "Thickness of the dividers, ideally an even multiple of layer width <br> <br> "
                "default = 1.2 mm"
            ),
        ).DividerThickness = DIVIDER_THICKNESS

        obj.addProperty(
            "App::PropertyLength",
            "xDividerHeight",
            "GridfinityNonStandard",
            "Custom Height of x dividers <br> <br> default = 0 mm = full height",
        ).xDividerHeight = CUSTOM_X_DIVIDER_HEIGHT

        obj.addProperty(
            "App::PropertyLength",
            "yDividerHeight",
            "GridfinityNonStandard",
            "Custom Height of y dividers <br> <br> default = 0 mm = full height",
        ).yDividerHeight = CUSTOM_Y_DIVIDER_HEIGHT

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

    def Make(obj: FreeCAD.DocumentObject, bin_inside_shape) -> Part.Shape:
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

            FreeCAD.Console.PrintWarning(
                "Divider Height must be equal to or greater than:  ",
            )

            FreeCAD.Console.PrintWarning(divmin)

            FreeCAD.Console.PrintWarning("\n")

        if obj.yDividerHeight < divmin and obj.yDividerHeight != 0:
            obj.yDividerHeight = divmin

            FreeCAD.Console.PrintWarning(
                "Divider Height must be equal to or greater than:  ",
            )

            FreeCAD.Console.PrintWarning(divmin)

            FreeCAD.Console.PrintWarning("\n")

        if (
            obj.xDividerHeight < obj.TotalHeight
            and obj.LabelShelfStyle != "Off"
            and obj.xDividerHeight != 0
            and obj.xDividers != 0
        ):
            obj.LabelShelfStyle = "Off"

            FreeCAD.Console.PrintWarning(
                "Label Shelf turned off for less than full height x dividers",
            )
        ## Compartment Generation
        face = Part.Face(bin_inside_shape)

        func_fuse = face.extrude(FreeCAD.Vector(0, 0, -obj.UsableHeight))
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
        """
        if obj.xDividers == 0 and obj.yDividers == 0:
            func_fuse = _make_compartments_no_deviders(obj, func_fuse)

        else:
            func_fuse = _make_compartments_with_deviders(obj, func_fuse)

        return func_fuse.translate(FreeCAD.Vector(-obj.xLocationOffset,-obj.yLocationOffset,0,))


def make_bin_base(obj: FreeCAD.DocumentObject, layout) -> Part.Shape:
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
                -obj.xGridSize / 2 + obj.Clearance + obj.DividerThickness,
                -obj.yGridSize / 2 + obj.Clearance,
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
            FreeCAD.Vector(
                -obj.xGridSize / 2 + obj.Clearance,
                -obj.yGridSize / 2 + obj.Clearance,
                -obj.TotalHeight,
            ),
            FreeCAD.Vector(0, 0, 1),
        )
        comp.translate(FreeCAD.Vector(0, ytranslate, 0))
        assembly = comp if assembly is None else assembly.fuse(comp)
        ytranslate += ycomp_w + obj.DividerThickness

    return assembly.translate(
        FreeCAD.Vector(
            obj.xGridSize / 2,
            obj.yGridSize / 2,
            0,
        )
    )


class EcoCompartments(Feature):
    """Create Eco bin main cut and dividers"""

    def __init__(self, obj: FreeCAD.DocumentObject):
        """Create Eco bin dividers

        Args:
            obj (FreeCAD.DocumentObject): Document object.
        """

        ## Gridfinity Parameters
        obj.addProperty(
            "App::PropertyLength",
            "BaseWallThickness",
            "Gridfinity",
            "The thickness of the bin at the base",
        ).BaseWallThickness = BASE_WALL_THICKNESS

        obj.addProperty(
            "App::PropertyInteger",
            "xDividers",
            "Gridfinity",
            "Select the Number of Dividers in the x direction",
        ).xDividers = ECO_X_DIVIDERS

        obj.addProperty(
            "App::PropertyInteger",
            "yDividers",
            "Gridfinity",
            "Select the number of Dividers in the y direction",
        ).yDividers = ECO_Y_DIVIDERS

        ## Gridfinity Non Standard Parameters
        obj.addProperty(
            "App::PropertyLength",
            "InsideFilletRadius",
            "GridfinityNonStandard",
            "inside fillet at the bottom of the bin <br> <br> default = 1.5 mm",
        ).InsideFilletRadius = ECO_INSIDE_FILLET_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "DividerThickness",
            "GridfinityNonStandard",
            (
                "Thickness of the dividers, ideally an even multiple of layer width <br> <br> "
                "default = 0.8 mm"
            ),
        ).DividerThickness = ECO_DIVIDER_THICKNESS

        obj.addProperty(
            "App::PropertyLength",
            "xDividerHeight",
            "GridfinityNonStandard",
            "Custom Height of x dividers <br> <br> default = 0 mm = full height",
        ).xDividerHeight = CUSTOM_X_DIVIDER_HEIGHT

        obj.addProperty(
            "App::PropertyLength",
            "yDividerHeight",
            "GridfinityNonStandard",
            "Custom Height of y dividers <br> <br> default = 0 mm = full height",
        ).yDividerHeight = CUSTOM_Y_DIVIDER_HEIGHT

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

    def Make(obj: FreeCAD.DocumentObject, bin_inside_shape) -> Part.Shape:
        """Create eco bin cutouts.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            bin_inside_shape (Part.Wire): Profile of bin inside wall

        Returns:
            Part.Shape: Eco bin cutout shape.

        """
        ## Parameter Calculation

        obj.UsableHeight = obj.TotalHeight - obj.HeightUnitValue
        ## Error Checking

        # Divider Minimum Height

        divmin = obj.HeightUnitValue + obj.InsideFilletRadius + 0.05 * unitmm

        if obj.xDividerHeight < divmin and obj.xDividerHeight != 0:
            obj.xDividerHeight = divmin

            FreeCAD.Console.PrintWarning(
                "Divider Height must be equal to or greater than:  ",
            )

            FreeCAD.Console.PrintWarning(divmin)

            FreeCAD.Console.PrintWarning("\n")

        if obj.yDividerHeight < divmin and obj.yDividerHeight != 0:
            obj.yDividerHeight = divmin

            FreeCAD.Console.PrintWarning(
                "Divider Height must be equal to or greater than:  ",
            )

            FreeCAD.Console.PrintWarning(divmin)

            FreeCAD.Console.PrintWarning("\n")

        if obj.InsideFilletRadius > (1.6 * unitmm):
            obj.InsideFilletRadius = 1.6 * unitmm

            FreeCAD.Console.PrintWarning(
                "Inside Fillet Radius must be equal to or less than:  1.6 mm\n",
            )

        ## Eco Compartement Generation
        face = Part.Face(bin_inside_shape)

        func_fuse = face.extrude(
            FreeCAD.Vector(0, 0, -obj.TotalHeight + obj.BaseProfileHeight + obj.BaseWallThickness)
        )

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
        """

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

        bottom_chamfer = Utils.rounded_rectangle_chamfer(
            x_bt_cmf_width,
            y_bt_cmf_width,
            -obj.TotalHeight + obj.BaseWallThickness + magoffset,
            0.4 * unitmm,
            bt_chf_rad,
        )

        vertical_section = Utils.rounded_rectangle_extrude(
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

        top_chamfer = Utils.rounded_rectangle_chamfer(
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
        for _ in range(obj.xMaxGrids):
            ytranslate = zeromm
            for _ in range(obj.yMaxGrids):
                vec_list.append(FreeCAD.Vector(xtranslate, ytranslate, 0))
                ytranslate += obj.yGridSize
            xtranslate += obj.xGridSize

        eco_base_cut = Utils.copy_and_translate(assembly, vec_list)

        eco_base_cut.translate(
            FreeCAD.Vector(
                obj.xGridSize / 2,
                obj.yGridSize / 2,
                0,
            )
        )

        func_fuse = func_fuse.fuse(eco_base_cut)

        outer_trim1 = Utils.rounded_rectangle_extrude(
            obj.xTotalWidth - obj.WallThickness * 2,
            obj.yTotalWidth - obj.WallThickness * 2,
            -obj.TotalHeight,
            obj.TotalHeight,
            obj.BinOuterRadius - obj.WallThickness,
        ).translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
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
        return func_fuse.translate(FreeCAD.Vector(-obj.xLocationOffset,-obj.yLocationOffset,0,))
