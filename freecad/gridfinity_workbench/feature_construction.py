from FreeCAD import Base, Units
import FreeCAD, Part, math
import FreeCADGui
import FreeCADGui as Gui
import FreeCAD as App


unitmm = Units.Quantity("1 mm")


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


def MakeStackingLip(self, obj):

    stacking_lip_path = createRoundedRectangle(obj.xTotalWidth, obj.yTotalWidth, 0, obj.BinOuterRadius)
    stacking_lip_path.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))
    ST1 = App.Vector(-obj.BinUnit/2,0,0)
    ST2 = App.Vector(-obj.BinUnit/2,0,obj.StackingLipBottomChamfer+obj.StackingLipVerticalSection+obj.StackingLipTopChamfer)
    ST3 = App.Vector(-obj.BinUnit/2+obj.StackingLipTopLedge,0,obj.StackingLipBottomChamfer+obj.StackingLipVerticalSection+obj.StackingLipTopChamfer)
    ST4 = App.Vector(-obj.BinUnit/2+obj.StackingLipTopLedge+obj.StackingLipTopChamfer,0,obj.StackingLipBottomChamfer+obj.StackingLipVerticalSection)
    ST5 = App.Vector(-obj.BinUnit/2+obj.StackingLipTopLedge+obj.StackingLipTopChamfer,0,obj.StackingLipBottomChamfer)
    ST6 = App.Vector(-obj.BinUnit/2+obj.StackingLipTopLedge+obj.StackingLipTopChamfer+obj.StackingLipBottomChamfer,0,0)
    ST7 = App.Vector(-obj.BinUnit/2+obj.StackingLipTopLedge+obj.StackingLipTopChamfer+obj.StackingLipBottomChamfer,0,-obj.StackingLipVerticalSection)
    ST8 = App.Vector(-obj.BinUnit/2+obj.WallThickness,0,-obj.StackingLipVerticalSection-(obj.StackingLipTopLedge+obj.StackingLipTopChamfer+obj.StackingLipBottomChamfer-obj.WallThickness))
    ST9 = App.Vector(-obj.BinUnit/2+obj.WallThickness,0,0)

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

def MakeBinWall(self, obj):

    bin_wall_path = createRoundedRectangle(obj.xTotalWidth, obj.yTotalWidth, 0, obj.BinOuterRadius)
    bin_wall_path.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))
    ST1 = App.Vector(-obj.BinUnit/2,0,-obj.TotalHeight+obj.BaseProfileHeight)
    ST2 = App.Vector(-obj.BinUnit/2,0,0)
    ST3 = App.Vector(-obj.BinUnit/2+obj.WallThickness,0,0)
    ST4 = App.Vector(-obj.BinUnit/2+obj.WallThickness,0,-obj.TotalHeight+obj.HeightUnitValue+obj.InsideFilletRadius)
    ST5 = App.Vector(-obj.BinUnit/2+obj.WallThickness+obj.InsideFilletRadius,0,-obj.TotalHeight+obj.HeightUnitValue)
    ST6 = App.Vector(-obj.BinUnit/2+obj.WallThickness+obj.InsideFilletRadius,0,-obj.TotalHeight+obj.BaseProfileHeight)

    VC1 = App.Vector(-obj.BinUnit/2+obj.WallThickness+obj.InsideFilletRadius-obj.InsideFilletRadius * math.sin(math.pi/4),0,-obj.TotalHeight+obj.HeightUnitValue+obj.InsideFilletRadius-+obj.InsideFilletRadius * math.sin(math.pi/4))

    STL1 = Part.LineSegment(ST1, ST2)
    STL2 = Part.LineSegment(ST2, ST3)
    STL3 = Part.LineSegment(ST3, ST4)
    STL4 = Part.Arc(ST4, VC1, ST5)
    STL5 = Part.LineSegment(ST5, ST6)
    STL6 = Part.LineSegment(ST6, ST1)

    STS1 = Part.Shape([STL1, STL2, STL3, STL4, STL5, STL6])

    wire = Part.Wire(STS1.Edges)

    bin_wall = Part.Wire(bin_wall_path).makePipe(wire)

    bin_wall = Part.makeSolid(bin_wall)
    return bin_wall



def MakeBinBase(self, obj):
    components=[]
    basecomp = []
    bt_cmf_width = obj.BinUnit - 2*obj.BaseProfileBottomChamfer-2*obj.BaseProfileTopChamfer
    vert_width = obj.BinUnit - 2*obj.BaseProfileTopChamfer
    xtranslate = 0
    ytranslate = 0
    for x in range(obj.xGridUnits):
        ytranslate = 0
        for y in range(obj.yGridUnits):
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
            ytranslate += 42
        if x>0:
            totalassembly2 = Part.Solid.fuse(totalassembly2,totalassembly1)
        else:
            totalassembly2 = totalassembly1
        xtranslate += 42

    return totalassembly2
"""
def FunctionBinBase(self, obj):

    comp2 = BinBase(self, obj)
    comptotal = Part.Shape.fuse(stacking_lip,comp2)
    return comptotal
"""
def MakeBottomHoles(self, obj):
    hole_pos = obj.GridSize/2-obj.MagnetHoleDistanceFromEdge
    sq_bridge2_pos = -obj.GridSize/2+obj.MagnetHoleDistanceFromEdge+obj.ScrewHoleDiameter/2

    sqbr1_depth = obj.MagnetHoleDepth+obj.SequentialBridgingLayerHeight
    sqbr2_depth = obj.MagnetHoleDepth+obj.SequentialBridgingLayerHeight*2

    xtranslate = 0
    ytranslate = 0
    if obj.MagnetHoles == True:
        for x in range(obj.xGridUnits):
            ytranslate = 0
            for y in range(obj.yGridUnits):
                C1 = Part.makeCylinder(obj.MagnetHoleDiameter/2, obj.MagnetHoleDepth, App.Vector(-hole_pos,-hole_pos,-obj.TotalHeight), App.Vector(0,0,1))
                C2 = Part.makeCylinder(obj.MagnetHoleDiameter/2, obj.MagnetHoleDepth, App.Vector(hole_pos,-hole_pos,-obj.TotalHeight), App.Vector(0,0,1))
                C3 = Part.makeCylinder(obj.MagnetHoleDiameter/2, obj.MagnetHoleDepth, App.Vector(-hole_pos,hole_pos,-obj.TotalHeight), App.Vector(0,0,1))
                C4 = Part.makeCylinder(obj.MagnetHoleDiameter/2, obj.MagnetHoleDepth, App.Vector(hole_pos,hole_pos,-obj.TotalHeight), App.Vector(0,0,1))


                HM1 = Part.Solid.multiFuse(C1,[C2,C3,C4])


                HM1.translate(App.Vector(xtranslate,ytranslate,0))
                if y>0:
                    HM2 = Part.Solid.fuse(HM1,HM2)
                else:
                    HM2 = HM1
                ytranslate += 42
            if x>0:
                HM3 = Part.Solid.fuse(HM3,HM2)
            else:
                HM3 = HM2
            xtranslate += 42

    xtranslate = 0
    ytranslate = 0

    if obj.ScrewHoles == True:
        for x in range(obj.xGridUnits):
            ytranslate = 0
            for y in range(obj.yGridUnits):
                CS1 = Part.makeCylinder(obj.ScrewHoleDiameter/2, obj.ScrewHoleDepth, App.Vector(-hole_pos,-hole_pos,-obj.TotalHeight), App.Vector(0,0,1))
                CS2 = Part.makeCylinder(obj.ScrewHoleDiameter/2, obj.ScrewHoleDepth, App.Vector(hole_pos,-hole_pos,-obj.TotalHeight), App.Vector(0,0,1))
                CS3 = Part.makeCylinder(obj.ScrewHoleDiameter/2, obj.ScrewHoleDepth, App.Vector(-hole_pos,hole_pos,-obj.TotalHeight), App.Vector(0,0,1))
                CS4 = Part.makeCylinder(obj.ScrewHoleDiameter/2, obj.ScrewHoleDepth, App.Vector(hole_pos,hole_pos,-obj.TotalHeight), App.Vector(0,0,1))

                HM1 = Part.Solid.multiFuse(CS1,[CS2,CS3,CS4])


                HM1.translate(App.Vector(xtranslate,ytranslate,0))
                if y>0:
                    HS2 = Part.Solid.fuse(HM1,HS2)
                else:
                    HS2 = HM1
                ytranslate += 42
            if x>0:
                HS3 = Part.Solid.fuse(HS3,HS2)
            else:
                HS3 = HS2
            xtranslate += 42

    xtranslate = 0
    ytranslate = 0
    if obj.ScrewHoles == True and obj.MagnetHoles == True:
        for x in range(obj.xGridUnits):
            ytranslate = 0
            for y in range(obj.yGridUnits):
                B1 = Part.makeBox(obj.ScrewHoleDiameter, obj.ScrewHoleDiameter, sqbr2_depth, App.Vector(-sq_bridge2_pos,-sq_bridge2_pos,-obj.TotalHeight), App.Vector(0,0,1))
                B2 = Part.makeBox(obj.ScrewHoleDiameter, obj.ScrewHoleDiameter, sqbr2_depth, App.Vector(-obj.GridSize/2+obj.MagnetHoleDistanceFromEdge-obj.ScrewHoleDiameter/2,-sq_bridge2_pos,-obj.TotalHeight), App.Vector(0,0,1))
                B3 = Part.makeBox(obj.ScrewHoleDiameter, obj.ScrewHoleDiameter, sqbr2_depth, App.Vector(-sq_bridge2_pos,-obj.GridSize/2+obj.MagnetHoleDistanceFromEdge-obj.ScrewHoleDiameter/2,-obj.TotalHeight), App.Vector(0,0,1))
                B4 = Part.makeBox(obj.ScrewHoleDiameter, obj.ScrewHoleDiameter, sqbr2_depth, App.Vector(-obj.GridSize/2+obj.MagnetHoleDistanceFromEdge-obj.ScrewHoleDiameter/2,-obj.GridSize/2+obj.MagnetHoleDistanceFromEdge-obj.ScrewHoleDiameter/2,-obj.TotalHeight), App.Vector(0,0,1))

                arc_pt_off_x = (math.sqrt(((obj.MagnetHoleDiameter/2)**2)-((obj.ScrewHoleDiameter/2)**2)))*unitmm
                arc_pt_off_y = obj.ScrewHoleDiameter/2

                VA1 = App.Vector(hole_pos+arc_pt_off_x, hole_pos+arc_pt_off_y, -obj.TotalHeight)
                VA2 = App.Vector(hole_pos-arc_pt_off_x, hole_pos+arc_pt_off_y, -obj.TotalHeight)
                VA3 = App.Vector(hole_pos-arc_pt_off_x, hole_pos-arc_pt_off_y, -obj.TotalHeight)
                VA4 = App.Vector(hole_pos+arc_pt_off_x, hole_pos-arc_pt_off_y, -obj.TotalHeight)
                VAR1 = App.Vector(hole_pos+obj.MagnetHoleDiameter/2, hole_pos,-obj.TotalHeight)
                VAR2 = App.Vector(hole_pos-obj.MagnetHoleDiameter/2, hole_pos,-obj.TotalHeight)

                VA5 = App.Vector(-hole_pos+arc_pt_off_x, hole_pos+arc_pt_off_y, -obj.TotalHeight)
                VA6 = App.Vector(-hole_pos-arc_pt_off_x, hole_pos+arc_pt_off_y, -obj.TotalHeight)
                VA7 = App.Vector(-hole_pos-arc_pt_off_x, hole_pos-arc_pt_off_y, -obj.TotalHeight)
                VA8 = App.Vector(-hole_pos+arc_pt_off_x, hole_pos-arc_pt_off_y, -obj.TotalHeight)
                VAR3 = App.Vector(-hole_pos+obj.MagnetHoleDiameter/2, hole_pos,-obj.TotalHeight)
                VAR4 = App.Vector(-hole_pos-obj.MagnetHoleDiameter/2, hole_pos,-obj.TotalHeight)

                VA9 = App.Vector(hole_pos+arc_pt_off_x, -hole_pos+arc_pt_off_y, -obj.TotalHeight)
                VA10 = App.Vector(hole_pos-arc_pt_off_x, -hole_pos+arc_pt_off_y, -obj.TotalHeight)
                VA11= App.Vector(hole_pos-arc_pt_off_x, -hole_pos-arc_pt_off_y, -obj.TotalHeight)
                VA12= App.Vector(hole_pos+arc_pt_off_x, -hole_pos-arc_pt_off_y, -obj.TotalHeight)
                VAR5 = App.Vector(hole_pos+obj.MagnetHoleDiameter/2, -hole_pos,-obj.TotalHeight)
                VAR6 = App.Vector(hole_pos-obj.MagnetHoleDiameter/2, -hole_pos,-obj.TotalHeight)

                VA13 = App.Vector(-hole_pos+arc_pt_off_x, -hole_pos+arc_pt_off_y, -obj.TotalHeight)
                VA14= App.Vector(-hole_pos-arc_pt_off_x, -hole_pos+arc_pt_off_y, -obj.TotalHeight)
                VA15= App.Vector(-hole_pos-arc_pt_off_x, -hole_pos-arc_pt_off_y, -obj.TotalHeight)
                VA16= App.Vector(-hole_pos+arc_pt_off_x, -hole_pos-arc_pt_off_y, -obj.TotalHeight)
                VAR7 = App.Vector(-hole_pos+obj.MagnetHoleDiameter/2, -hole_pos,-obj.TotalHeight)
                VAR8 = App.Vector(-hole_pos-obj.MagnetHoleDiameter/2, -hole_pos,-obj.TotalHeight)


                L1 = Part.LineSegment(VA1,VA2)
                L2 = Part.LineSegment(VA3,VA4)
                L3 = Part.LineSegment(VA5,VA6)
                L4 = Part.LineSegment(VA7,VA8)
                L5 = Part.LineSegment(VA9,VA10)
                L6 = Part.LineSegment(VA11,VA12)
                L7 = Part.LineSegment(VA13,VA14)
                L8 = Part.LineSegment(VA15,VA16)


                AR1 = Part.Arc(VA1,VAR1,VA4)
                AR2 = Part.Arc(VA2,VAR2,VA3)
                AR3 = Part.Arc(VA5,VAR3,VA8)
                AR4 = Part.Arc(VA6,VAR4,VA7)
                AR5 = Part.Arc(VA9,VAR5,VA12)
                AR6 = Part.Arc(VA10,VAR6,VA11)
                AR7 = Part.Arc(VA13,VAR7,VA16)
                AR8 = Part.Arc(VA14,VAR8,VA15)

                S1 = Part.Shape([L1, AR1, AR2, L2])
                S2 = Part.Shape([L3, AR3, AR4, L4])
                S3 = Part.Shape([L5, AR5, AR6, L6])
                S4 = Part.Shape([L7, AR7, AR8, L8])

                w1 = Part.Wire(S1.Edges)
                w2 = Part.Wire(S2.Edges)
                w3 = Part.Wire(S3.Edges)
                w4 = Part.Wire(S4.Edges)

                sq1_1 = Part.Face(w1)
                sq1_1 = sq1_1.extrude(App.Vector(0,0,sqbr1_depth))

                sq1_2 = Part.Face(w2)
                sq1_2 = sq1_2.extrude(App.Vector(0,0,sqbr1_depth))

                sq1_3 = Part.Face(w3)
                sq1_3 = sq1_3.extrude(App.Vector(0,0,sqbr1_depth))

                sq1_4 = Part.Face(w4)
                sq1_4 = sq1_4.extrude(App.Vector(0,0,sqbr1_depth))


                HM1 = Part.Solid.multiFuse(sq1_1,[B1,B2,B3,B4,sq1_2,sq1_3,sq1_4])


                HM1.translate(App.Vector(xtranslate,ytranslate,0))
                if y>0:
                    HSQ2 = Part.Solid.fuse(HM1,HSQ2)
                else:
                    HSQ2 = HM1
                ytranslate += 42
            if x>0:
                HSQ3 = Part.Solid.fuse(HSQ3,HSQ2)
            else:
                HSQ3 = HSQ2
            xtranslate += 42

    if obj.ScrewHoles == True and obj.MagnetHoles == False:
        fusetotal = HS3
    if obj.MagnetHoles == True and obj.ScrewHoles == False:
        fusetotal = HM3
    if obj.ScrewHoles == True and obj.MagnetHoles == True:
        fusetotal = Part.Solid.multiFuse(HM3,[HS3,HSQ3])

    return fusetotal


