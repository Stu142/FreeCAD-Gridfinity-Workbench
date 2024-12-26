from FreeCAD import Units
import Part
import math
import FreeCAD as App

unitmm = Units.Quantity("1 mm")
zeromm = Units.Quantity("0 mm")

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


def MakeLabelShelf(self, obj):

    towall = -obj.BinUnit/2 + obj.WallThickness
    tolabelend = -obj.BinUnit/2 + obj.StackingLipTopChamfer + obj.StackingLipTopLedge + obj.StackingLipBottomChamfer + obj.LabelShelfWidth
    meetswallbottom = -obj.StackingLipTopChamfer - obj.StackingLipTopLedge - obj.StackingLipBottomChamfer - obj.LabelShelfWidth + obj.WallThickness

    fwoverride = False
    xdiv = obj.xDividers + 1
    ydiv = obj.yDividers + 1
    xcompwidth = (obj.xTotalWidth - obj.WallThickness*2 - obj.DividerThickness*obj.xDividers)/(xdiv)
    ycompwidth = (obj.yTotalWidth - obj.WallThickness*2 - obj.DividerThickness*obj.yDividers)/(ydiv)

    V1 = App.Vector(towall, 0, 0)
    V2 = App.Vector(tolabelend, 0, 0)
    V3 = App.Vector(tolabelend,0, -obj.LabelShelfVerticalThickness)
    V4 = App.Vector(towall, 0, meetswallbottom)

    L1 = Part.LineSegment(V1, V2)
    L2 = Part.LineSegment(V2, V3)
    L3 = Part.LineSegment(V3, V4)
    L4 = Part.LineSegment(V4, V1)

    S1 = Part.Shape([L1,L2,L3,L4])

    wire = Part.Wire(S1.Edges)

    face = Part.Face(wire)

    if obj.LabelShelfLength > ycompwidth:
        fwoverride = True


    if obj.LabelShelfPlacement == "Full Width" or fwoverride:

        fw = obj.yTotalWidth - obj.WallThickness*2
        ytranslate = -obj.BinUnit/2 + obj.WallThickness
        xtranslate = zeromm
        parts = []
        for x in range(xdiv):

            ls = face.extrude(App.Vector(0,fw,0))

            ls.translate(App.Vector(xtranslate,ytranslate,0))

            if x == 0:
                firstls = ls
            else:
                parts.append(ls)

            xtranslate += xcompwidth + obj.DividerThickness

        if xdiv ==1:
            funcfuse = ls
        else:
            funcfuse = Part.Solid.multiFuse(firstls,parts)


        x2 = -obj.BinUnit/2 + obj.WallThickness
        b_edges = []
        for idx_edge, edge in enumerate(funcfuse.Edges):
            y0 = edge.Vertexes[0].Point.y
            y1 = edge.Vertexes[1].Point.y
            x0 = edge.Vertexes[0].Point.x
            x1 = edge.Vertexes[1].Point.x

            if (y0-y1) == 0 and x1 == x2 and x0 == x2:
                b_edges.append(edge)

        funcfuse = funcfuse.makeFillet(obj.BinOuterRadius - obj.WallThickness, b_edges)

        if obj.LabelShelfVerticalThickness > (obj.InsideFilletRadius/2):
            h_edges = []
            for idx_edge, edge in enumerate(funcfuse.Edges):
                z0 = edge.Vertexes[0].Point.z
                z1 = edge.Vertexes[1].Point.z

                if z0 == -obj.LabelShelfVerticalThickness and z1 == -obj.LabelShelfVerticalThickness:
                    h_edges.append(edge)

            funcfuse = funcfuse.makeFillet(obj.InsideFilletRadius, h_edges)


    if obj.LabelShelfPlacement == "Center" and not fwoverride:

        xtranslate = zeromm
        ysp = -obj.BinUnit/2 + obj.WallThickness + ycompwidth/2 - obj.LabelShelfLength/2
        ytranslate = ysp
        parts = []
        for x in range(xdiv):
            ytranslate = ysp
            for y in range(ydiv):

                ls = face.extrude(App.Vector(0,obj.LabelShelfLength,0))

                ls.translate(App.Vector(xtranslate,ytranslate,0))

                if x == 0 and y == 0:
                    firstls = ls
                else:
                    parts.append(ls)

                ytranslate += ycompwidth + obj.DividerThickness

            xtranslate += xcompwidth + obj.DividerThickness

        if xdiv == 1 and ydiv == 1:
            funcfuse = ls
        else:
            funcfuse = Part.Solid.multiFuse(firstls,parts)

        if obj.LabelShelfVerticalThickness > (obj.InsideFilletRadius/2):
            h_edges = []
            for idx_edge, edge in enumerate(funcfuse.Edges):
                z0 = edge.Vertexes[0].Point.z
                z1 = edge.Vertexes[1].Point.z

                if z0 == -obj.LabelShelfVerticalThickness and z1 == -obj.LabelShelfVerticalThickness:
                    h_edges.append(edge)

            funcfuse = funcfuse.makeFillet(obj.InsideFilletRadius, h_edges)


    if obj.LabelShelfPlacement == "Left" and not fwoverride:
        xtranslate = zeromm
        ysp = -obj.BinUnit/2 + obj.WallThickness
        ytranslate = ysp
        parts = []
        for x in range(xdiv):
            ytranslate = ysp
            for y in range(ydiv):

                ls = face.extrude(App.Vector(0,obj.LabelShelfLength,0))

                ls.translate(App.Vector(xtranslate,ytranslate,0))

                if x == 0 and y == 0:
                    firstls = ls
                else:
                    parts.append(ls)

                ytranslate += ycompwidth + obj.DividerThickness

            xtranslate += xcompwidth + obj.DividerThickness

        if xdiv ==1 and ydiv == 1:
            funcfuse = ls
        else:
            funcfuse = Part.Solid.multiFuse(firstls,parts)


        y2 = -obj.BinUnit/2 + obj.WallThickness
        b_edges = []
        for idx_edge, edge in enumerate(funcfuse.Edges):
            y0 = edge.Vertexes[0].Point.y
            y1 = edge.Vertexes[1].Point.y
            x0 = edge.Vertexes[0].Point.x
            x1 = edge.Vertexes[1].Point.x

            if y0 == y2 and y1 == y2 and x1 == y2 and x0 == y2:
                b_edges.append(edge)

        funcfuse = funcfuse.makeFillet(obj.BinOuterRadius - obj.WallThickness, b_edges)

        if obj.LabelShelfVerticalThickness > (obj.InsideFilletRadius/2):
            h_edges = []
            for idx_edge, edge in enumerate(funcfuse.Edges):
                z0 = edge.Vertexes[0].Point.z
                z1 = edge.Vertexes[1].Point.z

                if z0 == -obj.LabelShelfVerticalThickness and z1 == -obj.LabelShelfVerticalThickness:
                    h_edges.append(edge)

            funcfuse = funcfuse.makeFillet(obj.InsideFilletRadius, h_edges)


    if obj.LabelShelfPlacement == "Right" and not fwoverride:
        xtranslate = zeromm
        ysp = -obj.BinUnit/2 + obj.WallThickness + ycompwidth - obj.LabelShelfLength
        ytranslate = ysp
        parts = []
        for x in range(xdiv):
            ytranslate = ysp
            for y in range(ydiv):

                ls = face.extrude(App.Vector(0,obj.LabelShelfLength,0))

                ls.translate(App.Vector(xtranslate,ytranslate,0))

                if x == 0 and y == 0:
                    firstls = ls
                else:
                    parts.append(ls)

                ytranslate += ycompwidth + obj.DividerThickness

            xtranslate += xcompwidth + obj.DividerThickness

        if xdiv ==1 and ydiv == 1:
            funcfuse = ls
        else:
            funcfuse = Part.Solid.multiFuse(firstls,parts)


        y2 = obj.yTotalWidth - obj.BinUnit/2 - obj.WallThickness
        x2 = -obj.BinUnit/2 + obj.WallThickness
        b_edges = []
        for idx_edge, edge in enumerate(funcfuse.Edges):
            y0 = edge.Vertexes[0].Point.y
            y1 = edge.Vertexes[1].Point.y
            x0 = edge.Vertexes[0].Point.x
            x1 = edge.Vertexes[1].Point.x

            if y0 == y2 and y1 == y2 and x1 == x2 and x0 == x2:
                b_edges.append(edge)

        funcfuse = funcfuse.makeFillet(obj.BinOuterRadius - obj.WallThickness, b_edges)

        if obj.LabelShelfVerticalThickness > (obj.InsideFilletRadius/2):
            h_edges = []
            for idx_edge, edge in enumerate(funcfuse.Edges):
                z0 = edge.Vertexes[0].Point.z
                z1 = edge.Vertexes[1].Point.z

                if z0 == -obj.LabelShelfVerticalThickness and z1 == -obj.LabelShelfVerticalThickness:
                    h_edges.append(edge)

            funcfuse = funcfuse.makeFillet(obj.InsideFilletRadius, h_edges)


    return funcfuse

def MakeScoop(self, obj):
    scooprad1 = obj.ScoopRadius+1*unitmm
    scooprad2 = obj.ScoopRadius+1*unitmm
    scooprad3 = obj.ScoopRadius+1*unitmm

    xcomp_w = (obj.xTotalWidth-obj.WallThickness*2-obj.xDividers*obj.DividerThickness)/(obj.xDividers+1)

    xdivscoop = obj.xDividerHeight - obj.HeightUnitValue

    if obj.ScoopRadius > xdivscoop and obj.xDividerHeight != 0:
        scooprad1 = xdivscoop-unitmm
    if obj.ScoopRadius > xcomp_w and obj.xDividers > 0:
        scooprad2 = xcomp_w-2*unitmm
    if obj.ScoopRadius > obj.UsableHeight > 0:
        scooprad3 = obj.UsableHeight

    scooprad = min(obj.ScoopRadius,scooprad1,scooprad2,scooprad3)

    if scooprad <= 0:
        App.Console.PrintMessage("scooop could not be made due to bin selected parameters\n")
        return

    V1 = App.Vector(obj.xTotalWidth-obj.BinUnit/2-obj.WallThickness, 0, -obj.UsableHeight + scooprad)
    V2 = App.Vector(obj.xTotalWidth-obj.BinUnit/2-obj.WallThickness, 0, -obj.UsableHeight)
    V3 = App.Vector(obj.xTotalWidth-obj.BinUnit/2-obj.WallThickness - scooprad, 0, -obj.UsableHeight)

    L1 = Part.LineSegment(V1, V2)
    L2 = Part.LineSegment(V2, V3)

    VC1 = App.Vector(obj.xTotalWidth-obj.BinUnit/2-obj.WallThickness - scooprad + scooprad * math.sin(math.pi/4),0,-obj.UsableHeight + scooprad - scooprad * math.sin(math.pi/4))

    C1 = Part.Arc(V1, VC1, V3)

    S1 = Part.Shape([L1,L2,C1])

    wire = Part.Wire(S1.Edges)

    face = Part.Face(wire)

    xdiv = obj.xDividers + 1
    xtranslate = 0 * unitmm -obj.WallThickness + obj.StackingLipTopLedge + obj.StackingLipTopChamfer + obj.StackingLipBottomChamfer
    compwidth = (obj.xTotalWidth - obj.WallThickness*2 - obj.DividerThickness*obj.xDividers)/(xdiv)

    scoopbox = Part.makeBox(obj.StackingLipBottomChamfer + obj.StackingLipTopChamfer + obj.StackingLipTopLedge - obj.WallThickness ,obj.yTotalWidth-obj.WallThickness*2,obj.UsableHeight,App.Vector(obj.xTotalWidth - obj.BinUnit/2 - obj.WallThickness,-obj.BinUnit/2 + obj.WallThickness,0),App.Vector(0,0,-1))

    parts = []
    for x in range(xdiv):
        scoop = face.extrude(App.Vector(0,obj.yTotalWidth - obj.WallThickness*2,0))
        scoop.translate(App.Vector(-xtranslate,-obj.BinUnit/2 + obj.WallThickness,0))

        if x > 0:
            xtranslate += compwidth + obj.DividerThickness
        else:
            xtranslate += + obj.WallThickness - obj.StackingLipTopLedge - obj.StackingLipTopChamfer - obj.StackingLipBottomChamfer + compwidth + obj.DividerThickness



        if x > 0:
            parts.append(scoop)
        else:
            funcfuse = scoop
    if x > 0:
        funcfuse = funcfuse.multiFuse(parts)
    funcfuse = funcfuse.fuse(scoopbox)

    b_edges = []
    for idx_edge, edge in enumerate(funcfuse.Edges):
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z
        x0 = edge.Vertexes[0].Point.x
        x1 = edge.Vertexes[1].Point.x

        hdif = abs(z0-z1)
        if hdif == obj.UsableHeight and x0 == x1:
            b_edges.append(edge)

    funcfuse = funcfuse.makeFillet(obj.StackingLipBottomChamfer + obj.StackingLipTopChamfer + obj.StackingLipTopLedge - obj.WallThickness - 0.01*unitmm, b_edges)

    return funcfuse

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

def MakeCompartements(self, obj):

    xdivheight = obj.xDividerHeight if obj.xDividerHeight !=0 else obj.TotalHeight
    ydivheight = obj.yDividerHeight if obj.yDividerHeight !=0 else obj.TotalHeight

    func_fuse= RoundedRectangleExtrude(obj.xTotalWidth-obj.WallThickness*2, obj.yTotalWidth-obj.WallThickness*2, -obj.UsableHeight, obj.UsableHeight, obj.BinOuterRadius-obj.WallThickness)
    func_fuse.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))

    if obj.xDividers == 0 and obj.yDividers == 0:
            #Fillet Bottom edges
            b_edges = []
            for idx_edge, edge in enumerate(func_fuse.Edges):
                z0 = edge.Vertexes[0].Point.z
                z1 = edge.Vertexes[1].Point.z

                if z0 < 0 and z1 < 0:
                    b_edges.append(edge)

            func_fuse = func_fuse.makeFillet(obj.InsideFilletRadius, b_edges)

    else:
        xcomp_w = (obj.xTotalWidth-obj.WallThickness*2-obj.xDividers*obj.DividerThickness)/(obj.xDividers+1)
        ycomp_w = (obj.yTotalWidth-obj.WallThickness*2-obj.yDividers*obj.DividerThickness)/(obj.yDividers+1)


        xtranslate = zeromm + xcomp_w + obj.WallThickness - obj.DividerThickness
        ytranslate = zeromm + ycomp_w + obj.WallThickness

        # dividers in x direction
        for x in range(obj.xDividers):
            comp = Part.makeBox(obj.DividerThickness,obj.yTotalWidth,xdivheight,App.Vector(-obj.BinUnit/2+obj.DividerThickness,-obj.BinUnit/2,-obj.TotalHeight),App.Vector(0,0,1))
            comp.translate(App.Vector(xtranslate,0,0))
            if x>0:
                xdiv = xdiv.fuse(comp)

            else:
                xdiv = comp
            xtranslate += xcomp_w +obj.DividerThickness

        # dividers in y direction
        for y in range(obj.yDividers):
            comp = Part.makeBox(obj.xTotalWidth,obj.DividerThickness,ydivheight,App.Vector(-obj.BinUnit/2,-obj.BinUnit/2,-obj.TotalHeight),App.Vector(0,0,1))

            comp.translate(App.Vector(0,ytranslate,0))
            if y>0:
                ydiv = ydiv.fuse(comp)
            else:
                ydiv = comp
            ytranslate += ycomp_w +obj.DividerThickness

        if obj.xDividers > 0:
            func_fuse = func_fuse.cut(xdiv)
        if obj.yDividers > 0:
            func_fuse = func_fuse.cut(ydiv)
        b_edges = []
        for idx_edge, edge in enumerate(func_fuse.Edges):
            z0 = edge.Vertexes[0].Point.z
            z1 = edge.Vertexes[1].Point.z

            if z0 != z1:
                b_edges.append(edge)

            if z0 <= -obj.UsableHeight and z1 <= -obj.UsableHeight:
                b_edges.append(edge)

        func_fuse = func_fuse.makeFillet(obj.InsideFilletRadius, b_edges)

    return func_fuse

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
    xtranslate = zeromm
    ytranslate = zeromm
    for x in range(obj.xGridUnits):
        ytranslate = zeromm
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
            ytranslate += obj.GridSize
        if x>0:
            totalassembly2 = Part.Solid.fuse(totalassembly2,totalassembly1)
        else:
            totalassembly2 = totalassembly1
        xtranslate += obj.GridSize

    return totalassembly2
def MakeBaseplateCenterCut(self, obj):

    inframedis = obj.GridSize/2-obj.BaseProfileTopChamfer-obj.BaseProfileBottomChamfer - obj.BaseplateTopLedgeWidth
    magedge = obj.GridSize/2 - obj.MagnetHoleDistanceFromEdge - obj.MagnetHoleDiameter/2 - obj.MagnetEdgeThickness
    magcenter = obj.GridSize/2 - obj.MagnetHoleDistanceFromEdge
    smfillpos = inframedis - obj.SmallFillet +obj.SmallFillet * math.sin(math.pi/4)
    smfillposmag = magedge- obj.SmallFillet + obj.SmallFillet * math.sin(math.pi/4)
    smfilloffcen = obj.GridSize/2 - obj.MagnetHoleDistanceFromEdge - obj.MagnetHoleDiameter/2 -obj.MagnetEdgeThickness - obj.SmallFillet
    smfillins = inframedis - obj.SmallFillet
    bigfillpos =obj.GridSize/2 - obj.MagnetHoleDistanceFromEdge - (obj.MagnetHoleDiameter/2+obj.MagnetEdgeThickness) * math.sin(math.pi/4)


    V1 = App.Vector(-smfilloffcen,-inframedis,0)
    V2 = App.Vector(-magedge,-smfillins,0)
    V3 = App.Vector(-magedge,-magcenter,0)
    V4 = App.Vector(-magcenter,-magedge,0)
    V5 = App.Vector(-smfillins,-magedge,0)
    V6 = App.Vector(-inframedis,-smfilloffcen,0)

    VA1 = App.Vector(-smfillposmag,-smfillpos,0)
    VA2 = App.Vector(-bigfillpos,-bigfillpos,0)
    VA3 = App.Vector(-smfillpos,-smfillposmag,0)

    V7 = App.Vector(-inframedis,smfilloffcen,0)
    V8 = App.Vector(-smfillins,magedge,0)
    V9 = App.Vector(-magcenter,magedge,0)
    V10 = App.Vector(-magedge,magcenter,0)
    V11 = App.Vector(-magedge,smfillins,0)
    V12 = App.Vector(-smfilloffcen,inframedis,0)

    VA4 = App.Vector(-smfillpos,smfillposmag,0)
    VA5 = App.Vector(-bigfillpos,bigfillpos,0)
    VA6 = App.Vector(-smfillposmag,smfillpos,0)

    V13 = App.Vector(smfilloffcen,inframedis,0)
    V14= App.Vector(magedge,smfillins,0)
    V15= App.Vector(magedge,magcenter,0)
    V16= App.Vector(magcenter,magedge,0)
    V17= App.Vector(smfillins,magedge,0)
    V18= App.Vector(inframedis,smfilloffcen,0)

    VA7 = App.Vector(smfillposmag,smfillpos,0)
    VA8 = App.Vector(bigfillpos, bigfillpos,0)
    VA9 = App.Vector(smfillpos,smfillposmag,0)

    V19= App.Vector(inframedis,-smfilloffcen,0)
    V20= App.Vector(smfillins,-magedge,0)
    V21= App.Vector(magcenter,-magedge,0)
    V22 = App.Vector(magedge,-magcenter,0)
    V23= App.Vector(magedge,-smfillins,0)
    V24 = App.Vector(smfilloffcen,-inframedis,0)

    VA10 = App.Vector(smfillpos,-smfillposmag,0)
    VA11= App.Vector(bigfillpos,-bigfillpos,0)
    VA12 = App.Vector(smfillposmag,-smfillpos,0)

    L1 = Part.LineSegment(V24,V1)
    AR1 = Part.Arc(V1,VA1,V2)
    L2 = Part.LineSegment(V2,V3)
    AR2 = Part.Arc(V3,VA2,V4)
    L3 = Part.LineSegment(V4,V5)
    AR3 = Part.Arc(V5,VA3,V6)
    L4 = Part.LineSegment(V6,V7)
    AR4 = Part.Arc(V7,VA4,V8)
    L5 = Part.LineSegment(V8,V9)
    AR5 = Part.Arc(V9,VA5,V10)
    L6 = Part.LineSegment(V10,V11)
    AR6 = Part.Arc(V11,VA6,V12)
    L7 = Part.LineSegment(V12,V13)
    AR7 = Part.Arc(V13,VA7,V14)
    L8 = Part.LineSegment(V14,V15)
    AR8 = Part.Arc(V15,VA8,V16)
    L9 = Part.LineSegment(V16,V17)
    AR9 = Part.Arc(V17,VA9,V18)
    L10 = Part.LineSegment(V18,V19)
    AR10 = Part.Arc(V19,VA10,V20)
    L11 = Part.LineSegment(V20,V21)
    AR11 = Part.Arc(V21,VA11,V22)
    L12 = Part.LineSegment(V22,V23)
    AR12 = Part.Arc(V23,VA12,V24)
    xtranslate = zeromm
    ytranslate = zeromm

    S1 = Part.Shape([L1,AR1,L2,AR2,L3,AR3,L4,AR4,L5,AR5,L6,AR6,L7,AR7,L8,AR8,L9,AR9,L10,AR10,L11,AR11,L12,AR12])

    wire = Part.Wire(S1.Edges)

    face = Part.Face(wire)



    for x in range(obj.xGridUnits):
        ytranslate = zeromm
        for y in range(obj.yGridUnits):

            HM1 = face.extrude(App.Vector(0,0,-obj.TotalHeight))

            HM1.translate(App.Vector(xtranslate,ytranslate,0))
            if y>0:
                HM2 = Part.Solid.fuse(HM1,HM2)
            else:
                HM2 = HM1
            ytranslate += obj.GridSize
        if x>0:
            HM3 = Part.Solid.fuse(HM3,HM2)
        else:
            HM3 = HM2
        xtranslate += obj.GridSize

    return HM3

def MakeBottomHoles(self, obj):
    hole_pos = obj.GridSize/2-obj.MagnetHoleDistanceFromEdge
    sq_bridge2_pos = -obj.GridSize/2+obj.MagnetHoleDistanceFromEdge+obj.ScrewHoleDiameter/2

    sqbr1_depth = obj.MagnetHoleDepth+obj.SequentialBridgingLayerHeight
    sqbr2_depth = obj.MagnetHoleDepth+obj.SequentialBridgingLayerHeight*2

    xtranslate = zeromm
    ytranslate = zeromm
    if obj.MagnetHoles:
        for x in range(obj.xGridUnits):
            ytranslate = zeromm
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
                ytranslate += obj.GridSize
            if x>0:
                HM3 = Part.Solid.fuse(HM3,HM2)
            else:
                HM3 = HM2
            xtranslate += obj.GridSize

    xtranslate = zeromm
    ytranslate = zeromm

    if obj.ScrewHoles:
        for x in range(obj.xGridUnits):
            ytranslate = zeromm
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
                ytranslate += obj.GridSize
            if x>0:
                HS3 = Part.Solid.fuse(HS3,HS2)
            else:
                HS3 = HS2
            xtranslate += obj.GridSize

    xtranslate = zeromm
    ytranslate = zeromm
    if obj.ScrewHoles and obj.MagnetHoles:
        for x in range(obj.xGridUnits):
            ytranslate = zeromm
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
                ytranslate += obj.GridSize
            if x>0:
                HSQ3 = Part.Solid.fuse(HSQ3,HSQ2)
            else:
                HSQ3 = HSQ2
            xtranslate += obj.GridSize

    if obj.ScrewHoles and not obj.MagnetHoles:
        fusetotal = HS3
    if obj.MagnetHoles and not obj.ScrewHoles:
        fusetotal = HM3
    if obj.ScrewHoles and obj.MagnetHoles:
        fusetotal = Part.Solid.multiFuse(HM3,[HS3,HSQ3])

    return fusetotal

def MakeEcoBinCut(self, obj):

    func_fuse= RoundedRectangleExtrude(obj.xTotalWidth-obj.WallThickness*2, obj.yTotalWidth-obj.WallThickness*2, -obj.TotalHeight + obj.BaseProfileHeight + obj.BaseWallThickness, obj.TotalHeight - obj.BaseProfileHeight - obj.BaseWallThickness, obj.BinOuterRadius-obj.WallThickness)
    func_fuse.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))

    base_offset = obj.BaseWallThickness * math.tan(math.pi/8)
    bt_cmf_width = obj.BinUnit - 2*obj.BaseProfileTopChamfer - obj.BaseWallThickness*2 - 0.4*unitmm*2
    vert_width = obj.BinUnit - 2*obj.BaseProfileTopChamfer - obj.BaseWallThickness*2
    bt_chf_rad = obj.BinVerticalRadius - 0.4*unitmm - obj.BaseWallThickness
    v_chf_rad = obj.BinVerticalRadius - obj.BaseWallThickness

    if obj.MagnetHoles:
        magoffset = obj.MagnetHoleDepth
        if (obj.MagnetHoleDepth+obj.BaseWallThickness) > (obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection+base_offset):
            tp_chf_offset = (obj.MagnetHoleDepth+obj.BaseWallThickness) - (obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection+base_offset)
        else:
            tp_chf_offset = 0*unitmm
    else:
        magoffset = 0*unitmm
        tp_chf_offset = 0*unitmm

    if bt_chf_rad <= 0.01 :
        bt_chf_rad = 0.01*unitmm

    if v_chf_rad <= 0.01 :
        v_chf_rad = 0.01*unitmm


    xtranslate = zeromm
    ytranslate = zeromm

    for x in range(obj.xGridUnits):
        ytranslate = zeromm
        for y in range(obj.yGridUnits):

            bottom_chamfer = RoundedRectangleChamfer(bt_cmf_width, bt_cmf_width, -obj.TotalHeight + obj.BaseWallThickness + magoffset,0.4*unitmm, bt_chf_rad)

            vertical_section = RoundedRectangleExtrude(vert_width, vert_width, -obj.TotalHeight + obj.BaseWallThickness + 0.4*unitmm + magoffset, obj.BaseProfileVerticalSection + obj.BaseProfileBottomChamfer + base_offset - obj.BaseWallThickness - 0.4*unitmm, v_chf_rad)
            assembly = Part.Shape.fuse(bottom_chamfer,vertical_section)

            top_chamfer = RoundedRectangleChamfer(vert_width+tp_chf_offset, vert_width+tp_chf_offset, -obj.TotalHeight + obj.BaseProfileBottomChamfer + obj.BaseProfileVerticalSection + base_offset+tp_chf_offset, obj.BaseProfileTopChamfer+ obj.BaseWallThickness - tp_chf_offset, v_chf_rad)
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

    func_fuse = func_fuse.fuse(totalassembly2)

    outer_trim1= RoundedRectangleExtrude(obj.xTotalWidth-obj.WallThickness*2, obj.yTotalWidth-obj.WallThickness*2, -obj.TotalHeight, obj.TotalHeight, obj.BinOuterRadius-obj.WallThickness)
    outer_trim1.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))

    outer_trim2= RoundedRectangleExtrude(obj.xTotalWidth+20*unitmm, obj.yTotalWidth+20*unitmm, -obj.TotalHeight , obj.TotalHeight - obj.BaseProfileHeight, obj.BinOuterRadius)
    outer_trim2.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))

    outer_trim2= outer_trim2.cut(outer_trim1)

    func_fuse = func_fuse.cut(outer_trim2)
    # Dividers

    xcomp_w = (obj.xTotalWidth-obj.WallThickness*2-obj.xDividers*obj.DividerThickness)/(obj.xDividers+1)
    ycomp_w = (obj.yTotalWidth-obj.WallThickness*2-obj.yDividers*obj.DividerThickness)/(obj.yDividers+1)

    xdivheight = obj.xDividerHeight if obj.xDividerHeight !=0 else obj.TotalHeight
    ydivheight = obj.yDividerHeight if obj.yDividerHeight !=0 else obj.TotalHeight

    xtranslate = zeromm + xcomp_w + obj.WallThickness - obj.DividerThickness
    ytranslate = zeromm + ycomp_w + obj.WallThickness

    # dividers in x direction
    for x in range(obj.xDividers):
        comp = Part.makeBox(obj.DividerThickness,obj.yTotalWidth,xdivheight,App.Vector(-obj.BinUnit/2+obj.DividerThickness,-obj.BinUnit/2,-obj.TotalHeight),App.Vector(0,0,1))
        comp.translate(App.Vector(xtranslate,0,0))
        if x>0:
            xdiv = xdiv.fuse(comp)

        else:
            xdiv = comp
        xtranslate += xcomp_w+obj.DividerThickness

    # dividers in y direction
    for y in range(obj.yDividers):
        comp = Part.makeBox(obj.xTotalWidth,obj.DividerThickness,ydivheight,App.Vector(-obj.BinUnit/2,-obj.BinUnit/2,-obj.TotalHeight),App.Vector(0,0,1))
        comp.translate(App.Vector(0,ytranslate,0))
        if y>0:
            ydiv = ydiv.fuse(comp)
        else:
            ydiv = comp
        ytranslate += ycomp_w+obj.DividerThickness

    if obj.xDividers > 0:
        func_fuse = func_fuse.cut(xdiv)
    if obj.yDividers > 0:
        func_fuse = func_fuse.cut(ydiv)
    b_edges = []

    divfil = -obj.TotalHeight + obj.BaseProfileHeight + obj.BaseWallThickness + 1*unitmm
    for idx_edge, edge in enumerate(func_fuse.Edges):
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z

        if z1 != z0:
            if z1 >= divfil or z0 >= divfil:
                b_edges.append(edge)

    if obj.xDividers != 0 or obj.yDividers != 0:
        func_fuse = func_fuse.makeFillet(obj.InsideFilletRadius, b_edges)

    return func_fuse
