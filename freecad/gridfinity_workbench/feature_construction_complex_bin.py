from FreeCAD import Units
import Part
import math
import FreeCAD as App

unitmm = Units.Quantity("1 mm")
zeromm = Units.Quantity("0 mm")

def createRoundedL(A, B, C, D, xoffset, yoffset, zsketchplane, radius):

#Starting with bottom rigth corner vertex going around L shape clockwise

    L1X = xoffset
    L1Y1 = yoffset + radius
    L1Y2 = yoffset + B + D - radius
    ARC1X = xoffset + radius - radius * math.sin(math.pi/4)
    ARC1Y = yoffset + B + D - radius + radius * math.sin(math.pi/4)


    L2X1 = xoffset + radius
    L2X2 = xoffset + C - radius
    L2Y = yoffset + B + D
    ARC2X = xoffset + C - radius + radius * math.sin(math.pi/4)
    # ARC2Y = ARC1Y

    L3X = xoffset + C
    # L3Y1 = L1Y2
    L3Y2 = yoffset + B + radius
    ARC3X = xoffset + C + radius - radius * math.sin(math.pi/4)
    ARC3Y = xoffset + B + radius - radius * math.sin(math.pi/4)


    L4X1 = xoffset + C + radius
    L4X2 = xoffset + A - radius
    L4Y = yoffset + B
    ARC4X = xoffset + A - radius + radius * math.sin(math.pi/4)
    ARC4Y = yoffset + B - radius + radius * math.sin(math.pi/4)

    L5X = xoffset + A
    L5Y1 = yoffset + B - radius
    # L5Y2 = L1Y1
    #ARC5X = ARC4X
    ARC5Y = yoffset + radius - radius * math.sin(math.pi/4)

    #L6X1 = L4X2
    #L6X2 = L2X1
    L6Y = yoffset
    # ARC6X = ARC1X
    ARC6Y = yoffset + radius - radius * math.sin(math.pi/4)

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

    #xfarv = xwidth/2
    #yfarv = ywidth/2
    #xclosev = xwidth/2-radius
    #yclosev = ywidth/2-radius
    #xarcv = xwidth / 2 - radius + radius * math.sin(math.pi/4)
    #yarcv = ywidth / 2 - radius + radius * math.sin(math.pi/4)

    #V1 = App.Vector(-xclosev,yfarv, zsketchplane)
    #V2 = App.Vector(xclosev, yfarv, zsketchplane)
    #V3 = App.Vector(xfarv, yclosev, zsketchplane)
    #V4 = App.Vector(xfarv, -yclosev, zsketchplane)
    #V5 = App.Vector(xclosev, -yfarv, zsketchplane)
    #V6 = App.Vector(-xclosev, -yfarv, zsketchplane)
    #V7 = App.Vector(-xfarv, -yclosev, zsketchplane)
    #V8 = App.Vector(-xfarv, yclosev, zsketchplane)


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

#def RoundedLChamfer(xwidth, ywidth, zsketchplane, height, radius):
    #w1 = createRoundedRectangle(xwidth, ywidth, zsketchplane, radius)
    #w2 = createRoundedRectangle(xwidth+2*height, ywidth+2*height, zsketchplane+height, radius+height)
    #wires = [w1,w2]
    #return Part.makeLoft(wires,True)

def RoundedLExtrude(A, B, C, D, xoffset, yoffset, zsketchplane, radius, height):
    w1 = createRoundedL(A, B, C, D, xoffset, yoffset, zsketchplane, radius)
    face = Part.Face(w1)
    return face.extrude(App.Vector(0,0,height))


def MakeLBinBlank(self, obj):

    binlayout = [[None for x in range(obj.BGridUnits + obj.DGridUnits)] for y in range(obj.AGridUnits)]

    for x in range(obj.AGridUnits):
        for y in range(obj.BGridUnits + obj.DGridUnits):
            if x < obj.CGridUnits:
                binlayout[x][y] = 1
            if y < obj.BGridUnits:
                binlayout[x][y] = 1


    components=[]
    basecomp = []
    bt_cmf_width = obj.BinUnit - 2*obj.BaseProfileBottomChamfer-2*obj.BaseProfileTopChamfer
    vert_width = obj.BinUnit - 2*obj.BaseProfileTopChamfer
    xtranslate = zeromm
    ytranslate = zeromm
    for x in range(obj.AGridUnits):
        ytranslate = zeromm
        for y in range(obj.BGridUnits + obj.DGridUnits):

            if binlayout[x][y]:

                bottom_chamfer = RoundedRectangleChamfer(bt_cmf_width, bt_cmf_width, -obj.TotalHeight,obj.BaseProfileBottomChamfer, obj.BinBottomRadius)

                vertical_section = RoundedRectangleExtrude(vert_width, vert_width, -obj.TotalHeight +obj.BaseProfileBottomChamfer, obj.BaseProfileVerticalSection, obj.BinVerticalRadius)
                assembly = Part.Shape.fuse(bottom_chamfer,vertical_section)

                top_chamfer = RoundedRectangleChamfer(vert_width, vert_width, -obj.TotalHeight+obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection, obj.BaseProfileTopChamfer, obj.BinVerticalRadius)
                assembly = Part.Solid.fuse(assembly,top_chamfer)


                assembly.translate(App.Vector(xtranslate,ytranslate,0))


            if y>0:
                totalassembly1 = Part.Solid.fuse(assembly,totalassembly1)
            else:
                totalassembly1 = assembly
            ytranslate += obj.GridSize
        if x>0:
            totalassembly2 = Part.Solid.fuse(totalassembly2,totalassembly1)
        else:
            totalassembly2 = totalassembly1
        xtranslate += obj.GridSize

    return totalassembly2

    L = RoundedLExtrude(obj.AGridUnits * obj.GridSize, obj.BGridUnits * obj.GridSize, obj.CGridUnits * obj.GridSize, obj.DGridUnits * obj.GridSize, obj.Clearance, obj.Clearance, 0 * unitmm, obj.BinOuterRadius, obj.TotalHeight)

    return L

def createRoundedRectangle(xwidth, ywidth, zsketchplane, radius):
    xfarv = xwidth/2
    yfarv = ywidth/2
    xclosev = xwidth/2-radius
    yclosev = ywidth/2-radius
    xarcv = xwidth / 2 - radius + radius * math.sin(math.pi/4)
    yarcv = ywidth / 2 - radius + radius * math.sin(math.pi/4)

    V1 = App.Vector(-xclosev,yfarv, zsketchplane)
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
    w2 = createRoundedRectangle(xwidth+2*height, ywidth+2*height, zsketchplane+height, radius+height)
    wires = [w1,w2]
    return Part.makeLoft(wires,True)
def RoundedRectangleExtrude(xwidth, ywidth, zsketchplane, height, radius):
    w1 = createRoundedRectangle(xwidth, ywidth, zsketchplane, radius)
    face = Part.Face(w1)
    return face.extrude(App.Vector(0,0,height))

