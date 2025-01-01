from FreeCAD import Units
import Part
import math
import FreeCAD as App

unitmm = Units.Quantity("1 mm")
zeromm = Units.Quantity("0 mm")


def createRoundedL(A, B, C, D, xoffset, yoffset, zsketchplane, radius):
    # Starting with bottom rigth corner vertex going around L shape clockwise

    L1X = xoffset
    L1Y1 = yoffset + radius
    L1Y2 = yoffset + B + D - radius
    ARC1X = xoffset + radius - radius * math.sin(math.pi / 4)
    ARC1Y = yoffset + B + D - radius + radius * math.sin(math.pi / 4)

    L2X1 = xoffset + radius
    L2X2 = xoffset + C - radius
    L2Y = yoffset + B + D
    ARC2X = xoffset + C - radius + radius * math.sin(math.pi / 4)
    # ARC2Y = ARC1Y

    L3X = xoffset + C
    # L3Y1 = L1Y2
    L3Y2 = yoffset + B + radius
    ARC3X = xoffset + C + radius - radius * math.sin(math.pi / 4)
    ARC3Y = xoffset + B + radius - radius * math.sin(math.pi / 4)

    L4X1 = xoffset + C + radius
    L4X2 = xoffset + A - radius
    L4Y = yoffset + B
    ARC4X = xoffset + A - radius + radius * math.sin(math.pi / 4)
    ARC4Y = yoffset + B - radius + radius * math.sin(math.pi / 4)

    L5X = xoffset + A
    L5Y1 = yoffset + B - radius
    # L5Y2 = L1Y1
    # ARC5X = ARC4X
    ARC5Y = yoffset + radius - radius * math.sin(math.pi / 4)

    # L6X1 = L4X2
    # L6X2 = L2X1
    L6Y = yoffset
    # ARC6X = ARC1X
    ARC6Y = yoffset + radius - radius * math.sin(math.pi / 4)

    L1V1 = App.Vector(L1X, L1Y1, zsketchplane)
    L1V2 = App.Vector(L1X, L1Y2, zsketchplane)
    ARC1V = App.Vector(ARC1X, ARC1Y, zsketchplane)
    L2V1 = App.Vector(L2X1, L2Y, zsketchplane)
    L2V2 = App.Vector(L2X2, L2Y, zsketchplane)
    ARC2V = App.Vector(ARC2X, ARC1Y, zsketchplane)
    L3V1 = App.Vector(L3X, L1Y2, zsketchplane)
    L3V2 = App.Vector(L3X, L3Y2, zsketchplane)
    ARC3V = App.Vector(ARC3X, ARC3Y, zsketchplane)
    L4V1 = App.Vector(L4X1, L4Y, zsketchplane)
    L4V2 = App.Vector(L4X2, L4Y, zsketchplane)
    ARC4V = App.Vector(ARC4X, ARC4Y, zsketchplane)
    L5V1 = App.Vector(L5X, L5Y1, zsketchplane)
    L5V2 = App.Vector(L5X, L1Y1, zsketchplane)
    ARC5V = App.Vector(ARC4X, ARC5Y, zsketchplane)
    L6V1 = App.Vector(L4X2, L6Y, zsketchplane)
    L6V2 = App.Vector(L2X1, L6Y, zsketchplane)
    ARC6V = App.Vector(ARC1X, ARC6Y, zsketchplane)

    L1 = Part.LineSegment(L1V1, L1V2)
    ARC1 = Part.Arc(L1V2, ARC1V, L2V1)
    L2 = Part.LineSegment(L2V1, L2V2)
    ARC2 = Part.Arc(L2V2, ARC2V, L3V1)
    L3 = Part.LineSegment(L3V1, L3V2)
    ARC3 = Part.Arc(L3V2, ARC3V, L4V1)
    L4 = Part.LineSegment(L4V1, L4V2)
    ARC4 = Part.Arc(L4V2, ARC4V, L5V1)
    L5 = Part.LineSegment(L5V1, L5V2)
    ARC5 = Part.Arc(L5V2, ARC5V, L6V1)
    L6 = Part.LineSegment(L6V1, L6V2)
    ARC6 = Part.Arc(L6V2, ARC6V, L1V1)

    S1 = Part.Shape([L1, ARC1, L2, ARC2, L3, ARC3, L4, ARC4, L5, ARC5, L6, ARC6])

    wire = Part.Wire(S1.Edges)

    return wire


# def RoundedLChamfer(xwidth, ywidth, zsketchplane, height, radius):
# w1 = createRoundedRectangle(xwidth, ywidth, zsketchplane, radius)
# w2 = createRoundedRectangle(xwidth+2*height, ywidth+2*height, zsketchplane+height, radius+height)
# wires = [w1,w2]
# return Part.makeLoft(wires,True)


def RoundedLExtrude(A, B, C, D, xoffset, yoffset, zsketchplane, radius, height):
    w1 = createRoundedL(A, B, C, D, xoffset, yoffset, zsketchplane, radius)
    face = Part.Face(w1)
    return face.extrude(App.Vector(0, 0, height))


def MakeLBinBlank(self, obj):
    binlayout = [
        [None for x in range(obj.bGridUnits + obj.dGridUnits)]
        for y in range(obj.aGridUnits)
    ]

    for x in range(obj.aGridUnits):
        for y in range(obj.bGridUnits + obj.dGridUnits):
            if x < obj.cGridUnits:
                binlayout[x][y] = 1
            if y < obj.bGridUnits:
                binlayout[x][y] = 1

    components = []
    basecomp = []
    x_bt_cmf_width = (
        obj.xBinUnit - 2 * obj.BaseProfileBottomChamfer - 2 * obj.BaseProfileTopChamfer
    )
    y_bt_cmf_width = (
        obj.yBinUnit - 2 * obj.BaseProfileBottomChamfer - 2 * obj.BaseProfileTopChamfer
    )
    x_vert_width = obj.xBinUnit - 2 * obj.BaseProfileTopChamfer
    y_vert_width = obj.yBinUnit - 2 * obj.BaseProfileTopChamfer
    xtranslate = zeromm
    ytranslate = zeromm

    bottom_chamfer = RoundedRectangleChamfer(
        x_bt_cmf_width,
        y_bt_cmf_width,
        -obj.TotalHeight,
        obj.BaseProfileBottomChamfer,
        obj.BinBottomRadius,
    )

    vertical_section = RoundedRectangleExtrude(
        x_vert_width,
        y_vert_width,
        -obj.TotalHeight + obj.BaseProfileBottomChamfer,
        obj.BaseProfileVerticalSection,
        obj.BinVerticalRadius,
    )
    assembly = Part.Shape.fuse(bottom_chamfer, vertical_section)

    top_chamfer = RoundedRectangleChamfer(
        x_vert_width,
        y_vert_width,
        -obj.TotalHeight
        + obj.BaseProfileBottomChamfer
        + obj.BaseProfileVerticalSection,
        obj.BaseProfileTopChamfer,
        obj.BinVerticalRadius,
    )
    assembly = Part.Solid.fuse(assembly, top_chamfer)

    for x in range(obj.aGridUnits):
        ytranslate = zeromm
        for y in range(obj.bGridUnits + obj.dGridUnits):
            if binlayout[x][y]:
                b = assembly.copy()

                b.translate(App.Vector(xtranslate, ytranslate, 0))

            if y > 0:
                totalassembly1 = Part.Solid.fuse(b, totalassembly1)
            else:
                totalassembly1 = b
            ytranslate += obj.yGridSize
        if x > 0:
            func_fuse = Part.Solid.fuse(func_fuse, totalassembly1)
        else:
            func_fuse = totalassembly1
        xtranslate += obj.xGridSize

    func_fuse.translate(
        App.Vector(
            obj.xBinUnit / 2 + obj.Clearance, obj.yBinUnit / 2 + obj.Clearance, 0
        )
    )

    lsolid = RoundedLExtrude(
        obj.aTotalDimension,
        obj.bTotalDimension,
        obj.cTotalDimension,
        obj.dTotalDimension,
        obj.Clearance,
        obj.Clearance,
        0 * unitmm,
        obj.BinOuterRadius,
        -obj.TotalHeight + obj.BaseProfileHeight,
    )

    func_fuse = func_fuse.fuse(lsolid)

    return func_fuse


def createRoundedRectangle(xwidth, ywidth, zsketchplane, radius):
    xfarv = xwidth / 2
    yfarv = ywidth / 2
    xclosev = xwidth / 2 - radius
    yclosev = ywidth / 2 - radius
    xarcv = xwidth / 2 - radius + radius * math.sin(math.pi / 4)
    yarcv = ywidth / 2 - radius + radius * math.sin(math.pi / 4)

    V1 = App.Vector(-xclosev, yfarv, zsketchplane)
    V2 = App.Vector(xclosev, yfarv, zsketchplane)
    V3 = App.Vector(xfarv, yclosev, zsketchplane)
    V4 = App.Vector(xfarv, -yclosev, zsketchplane)
    V5 = App.Vector(xclosev, -yfarv, zsketchplane)
    V6 = App.Vector(-xclosev, -yfarv, zsketchplane)
    V7 = App.Vector(-xfarv, -yclosev, zsketchplane)
    V8 = App.Vector(-xfarv, yclosev, zsketchplane)

    VC1 = App.Vector(-xarcv, yarcv, zsketchplane)
    C1 = Part.Arc(V1, VC1, V8)
    VC2 = App.Vector(xarcv, yarcv, zsketchplane)
    C2 = Part.Arc(V2, VC2, V3)
    VC3 = App.Vector(xarcv, -yarcv, zsketchplane)
    C3 = Part.Arc(V4, VC3, V5)
    VC4 = App.Vector(-xarcv, -yarcv, zsketchplane)
    C4 = Part.Arc(V6, VC4, V7)

    L1 = Part.LineSegment(V1, V2)
    L2 = Part.LineSegment(V3, V4)
    L3 = Part.LineSegment(V5, V6)
    L4 = Part.LineSegment(V7, V8)

    S1 = Part.Shape([C1, L1, C2, L2, C3, L3, C4, L4])

    wire = Part.Wire(S1.Edges)

    return wire


def RoundedRectangleChamfer(xwidth, ywidth, zsketchplane, height, radius):
    w1 = createRoundedRectangle(xwidth, ywidth, zsketchplane, radius)
    w2 = createRoundedRectangle(
        xwidth + 2 * height, ywidth + 2 * height, zsketchplane + height, radius + height
    )
    wires = [w1, w2]
    return Part.makeLoft(wires, True)


def RoundedRectangleExtrude(xwidth, ywidth, zsketchplane, height, radius):
    w1 = createRoundedRectangle(xwidth, ywidth, zsketchplane, radius)
    face = Part.Face(w1)
    return face.extrude(App.Vector(0, 0, height))


def MakeComplexStackingLip(self, obj):
    stacking_lip_path = createRoundedL(
        obj.aTotalDimension,
        obj.bTotalDimension,
        obj.cTotalDimension,
        obj.dTotalDimension,
        obj.Clearance,
        obj.Clearance,
        0 * unitmm,
        obj.BinOuterRadius,
    )

    # stacking_lip_path = createRoundedRectangle(obj.xTotalWidth, obj.yTotalWidth, 0, obj.BinOuterRadius)

    stacking_lip_path.translate(App.Vector(0, 0, 20))

    ST1 = App.Vector(obj.Clearance, obj.yGridSize / 2, 0)
    ST2 = App.Vector(
        obj.Clearance,
        obj.yGridSize / 2,
        obj.StackingLipBottomChamfer
        + obj.StackingLipVerticalSection
        + obj.StackingLipTopChamfer,
    )
    ST3 = App.Vector(
        obj.Clearance + obj.StackingLipTopLedge,
        obj.yGridSize / 2,
        obj.StackingLipBottomChamfer
        + obj.StackingLipVerticalSection
        + obj.StackingLipTopChamfer,
    )
    ST4 = App.Vector(
        obj.Clearance + obj.StackingLipTopLedge + obj.StackingLipTopChamfer,
        obj.yGridSize / 2,
        obj.StackingLipBottomChamfer + obj.StackingLipVerticalSection,
    )
    ST5 = App.Vector(
        obj.Clearance + obj.StackingLipTopLedge + obj.StackingLipTopChamfer,
        obj.yGridSize / 2,
        obj.StackingLipBottomChamfer,
    )
    ST6 = App.Vector(
        obj.Clearance
        + obj.StackingLipTopLedge
        + obj.StackingLipTopChamfer
        + obj.StackingLipBottomChamfer,
        obj.yGridSize / 2,
        0,
    )
    ST7 = App.Vector(
        obj.Clearance
        + obj.StackingLipTopLedge
        + obj.StackingLipTopChamfer
        + obj.StackingLipBottomChamfer,
        obj.yGridSize / 2,
        -obj.StackingLipVerticalSection,
    )
    ST8 = App.Vector(
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
    ST9 = App.Vector(obj.Clearance + obj.WallThickness, obj.yGridSize / 2, 0)

    STL1 = Part.LineSegment(ST1, ST2)
    STL2 = Part.LineSegment(ST2, ST3)
    STL3 = Part.LineSegment(ST3, ST4)
    STL4 = Part.LineSegment(ST4, ST5)
    STL5 = Part.LineSegment(ST5, ST6)
    STL6 = Part.LineSegment(ST6, ST7)
    STL7 = Part.LineSegment(ST7, ST8)
    STL8 = Part.LineSegment(ST8, ST9)
    STL9 = Part.LineSegment(ST9, ST1)

    STS1 = Part.Shape([STL1, STL2, STL3, STL4, STL5, STL6, STL7, STL8, STL9])

    wire = Part.Wire(STS1.Edges)

    stacking_lip = Part.Wire(stacking_lip_path).makePipe(wire)

    stacking_lip = Part.makeSolid(stacking_lip)
    return stacking_lip
