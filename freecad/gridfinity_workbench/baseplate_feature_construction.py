from FreeCAD import Units
import Part
import FreeCAD as App

unitmm = Units.Quantity("1 mm")

zeromm = Units.Quantity("0 mm")

def MakeBaseplateMagnetHoles(self, obj):

    hole_pos = obj.GridSize/2-obj.MagnetHoleDistanceFromEdge


    C1 = Part.makeCylinder(obj.MagnetHoleDiameter/2, obj.MagnetHoleDepth, App.Vector(-hole_pos,-hole_pos,-obj.BaseProfileHeight), App.Vector(0,0,-1))
    C2 = Part.makeCylinder(obj.MagnetHoleDiameter/2, obj.MagnetHoleDepth, App.Vector(hole_pos,-hole_pos,-obj.BaseProfileHeight), App.Vector(0,0,-1))
    C3 = Part.makeCylinder(obj.MagnetHoleDiameter/2, obj.MagnetHoleDepth, App.Vector(-hole_pos,hole_pos,-obj.BaseProfileHeight), App.Vector(0,0,-1))
    C4 = Part.makeCylinder(obj.MagnetHoleDiameter/2, obj.MagnetHoleDepth, App.Vector(hole_pos,hole_pos,-obj.BaseProfileHeight), App.Vector(0,0,-1))

    CA1 = Part.makeCylinder(obj.MagnetBaseHole/2, obj.MagnetHoleDepth+obj.BaseThickness, App.Vector(-hole_pos,-hole_pos,-obj.BaseProfileHeight), App.Vector(0,0,-1))
    CA2 = Part.makeCylinder(obj.MagnetBaseHole/2, obj.MagnetHoleDepth+obj.BaseThickness, App.Vector(hole_pos,-hole_pos,-obj.BaseProfileHeight), App.Vector(0,0,-1))
    CA3 = Part.makeCylinder(obj.MagnetBaseHole/2, obj.MagnetHoleDepth+obj.BaseThickness, App.Vector(-hole_pos,hole_pos,-obj.BaseProfileHeight), App.Vector(0,0,-1))
    CA4 = Part.makeCylinder(obj.MagnetBaseHole/2, obj.MagnetHoleDepth+obj.BaseThickness, App.Vector(hole_pos,hole_pos,-obj.BaseProfileHeight), App.Vector(0,0,-1))

    CT1 = Part.makeCircle(obj.MagnetHoleDiameter/2+obj.MagnetChamfer, App.Vector(-hole_pos,-hole_pos,-obj.BaseProfileHeight), App.Vector(0,0,1))
    CT2 = Part.makeCircle(obj.MagnetHoleDiameter/2+obj.MagnetChamfer, App.Vector(hole_pos,-hole_pos,-obj.BaseProfileHeight), App.Vector(0,0,1))
    CT3 = Part.makeCircle(obj.MagnetHoleDiameter/2+obj.MagnetChamfer, App.Vector(-hole_pos,hole_pos,-obj.BaseProfileHeight), App.Vector(0,0,1))
    CT4 = Part.makeCircle(obj.MagnetHoleDiameter/2+obj.MagnetChamfer, App.Vector(hole_pos,hole_pos,-obj.BaseProfileHeight), App.Vector(0,0,1))

    CB1 = Part.makeCircle(obj.MagnetHoleDiameter/2, App.Vector(-hole_pos,-hole_pos,-obj.BaseProfileHeight-obj.MagnetChamfer), App.Vector(0,0,1))
    CB2 = Part.makeCircle(obj.MagnetHoleDiameter/2, App.Vector(hole_pos,-hole_pos,-obj.BaseProfileHeight-obj.MagnetChamfer), App.Vector(0,0,1))
    CB3 = Part.makeCircle(obj.MagnetHoleDiameter/2, App.Vector(-hole_pos,hole_pos,-obj.BaseProfileHeight-obj.MagnetChamfer), App.Vector(0,0,1))
    CB4 = Part.makeCircle(obj.MagnetHoleDiameter/2, App.Vector(hole_pos,hole_pos,-obj.BaseProfileHeight-obj.MagnetChamfer), App.Vector(0,0,1))

    CH1 = [CT1,CB1]
    CH1 = Part.makeLoft(CH1,True)
    CH2 = [CT2,CB2]
    CH2 = Part.makeLoft(CH2,True)
    CH3 = [CT3,CB3]
    CH3 = Part.makeLoft(CH3,True)
    CH4 = [CT4,CB4]
    CH4 = Part.makeLoft(CH4,True)

    xtranslate = zeromm
    ytranslate = zeromm

    for x in range(obj.xGridUnits):
        ytranslate = zeromm
        for y in range(obj.yGridUnits):

            HM1 = Part.Solid.multiFuse(C1,[C2,C3,C4,CA1,CA2,CA3,CA4,CH1,CH2,CH3,CH4])

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

def MakeBPScrewBottomCham(self,obj):

    hole_pos = obj.GridSize/2-obj.MagnetHoleDistanceFromEdge

    CT1 = Part.makeCircle(obj.ScrewHoleDiameter/2+obj.MagnetBottomChamfer, App.Vector(-hole_pos,-hole_pos,-obj.TotalHeight), App.Vector(0,0,1))
    CT2 = Part.makeCircle(obj.ScrewHoleDiameter/2+obj.MagnetBottomChamfer, App.Vector(hole_pos,-hole_pos,-obj.TotalHeight), App.Vector(0,0,1))
    CT3 = Part.makeCircle(obj.ScrewHoleDiameter/2+obj.MagnetBottomChamfer, App.Vector(-hole_pos,hole_pos,-obj.TotalHeight), App.Vector(0,0,1))
    CT4 = Part.makeCircle(obj.ScrewHoleDiameter/2+obj.MagnetBottomChamfer, App.Vector(hole_pos,hole_pos,-obj.TotalHeight), App.Vector(0,0,1))

    CB1 = Part.makeCircle(obj.ScrewHoleDiameter/2, App.Vector(-hole_pos,-hole_pos,-obj.TotalHeight+obj.MagnetBottomChamfer), App.Vector(0,0,1))
    CB2 = Part.makeCircle(obj.ScrewHoleDiameter/2, App.Vector(hole_pos,-hole_pos,-obj.TotalHeight+obj.MagnetBottomChamfer), App.Vector(0,0,1))
    CB3 = Part.makeCircle(obj.ScrewHoleDiameter/2, App.Vector(-hole_pos,hole_pos,-obj.TotalHeight+obj.MagnetBottomChamfer), App.Vector(0,0,1))
    CB4 = Part.makeCircle(obj.ScrewHoleDiameter/2, App.Vector(hole_pos,hole_pos,-obj.TotalHeight+obj.MagnetBottomChamfer), App.Vector(0,0,1))

    CH1 = [CT1,CB1]
    CH1 = Part.makeLoft(CH1,True)
    CH2 = [CT2,CB2]
    CH2 = Part.makeLoft(CH2,True)
    CH3 = [CT3,CB3]
    CH3 = Part.makeLoft(CH3,True)
    CH4 = [CT4,CB4]
    CH4 = Part.makeLoft(CH4,True)

    xtranslate = zeromm
    ytranslate = zeromm

    for x in range(obj.xGridUnits):
        ytranslate = zeromm
        for y in range(obj.yGridUnits):

            HM1 = Part.Solid.multiFuse(CH1,[CH2,CH3,CH4])

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

def MakeBPConnectionHoles(self,obj):

    C1 = Part.makeCylinder(obj.ConnectionHoleDiameter/2, obj.BaseThickness, App.Vector(0,-obj.GridSize/2,-obj.TotalHeight+obj.BaseThickness/2), App.Vector(0,1,0))
    C2 = Part.makeCylinder(obj.ConnectionHoleDiameter/2, obj.BaseThickness, App.Vector(0,-obj.GridSize/2+obj.yTotalWidth-obj.BaseThickness,-obj.TotalHeight+obj.BaseThickness/2), App.Vector(0,1,0))


    C3 = Part.makeCylinder(obj.ConnectionHoleDiameter/2, obj.BaseThickness, App.Vector(-obj.GridSize/2,0,-obj.TotalHeight+obj.BaseThickness/2), App.Vector(1,0,0))
    C4 = Part.makeCylinder(obj.ConnectionHoleDiameter/2, obj.BaseThickness, App.Vector(-obj.GridSize/2+obj.xTotalWidth-obj.BaseThickness,0,-obj.TotalHeight+obj.BaseThickness/2), App.Vector(1,0,0))

    xtranslate = zeromm
    ytranslate = zeromm

    for x in range(obj.xGridUnits):
        ytranslate = zeromm

        HX1 = Part.Solid.fuse(C1,C2)

        HX1.translate(App.Vector(xtranslate,ytranslate,0))
        if x>0:
            HX2 = Part.Solid.fuse(HX1,HX2)
        else:
            HX2 = HX1

        xtranslate += obj.GridSize

    xtranslate = zeromm
    ytranslate = zeromm

    for x in range(obj.yGridUnits):
        xtranslate = zeromm

        HY1 = Part.Solid.fuse(C3,C4)

        HY1.translate(App.Vector(xtranslate,ytranslate,0))
        if x>0:
            HY2 = Part.Solid.fuse(HY1,HY2)
        else:
            HY2 = HY1

        ytranslate += obj.GridSize

    con_holes = Part.Solid.fuse(HX2,HY2)
    return con_holes
