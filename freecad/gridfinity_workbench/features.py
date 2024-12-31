from __future__ import division
import os
import FreeCAD as App
import Part
from FreeCAD import Units
from .version import __version__
from .feature_construction import MakeStackingLip, MakeBinBase, RoundedRectangleExtrude, MakeBottomHoles, MakeBaseplateCenterCut, MakeCompartements, MakeEcoBinCut, MakeScoop, MakeLabelShelf
from .baseplate_feature_construction import MakeBaseplateMagnetHoles, MakeBPScrewBottomCham, MakeBPConnectionHoles

from .const import BIN_BASE_TOP_CHAMFER, BIN_BASE_BOTTOM_CHAMFER, BIN_BASE_VERTICAL_SECTION, GRID_SIZE, BIN_OUTER_RADIUS, BIN_UNIT, BIN_BASE_VERTICAL_RADIUS, BIN_BASE_BOTTOM_RADIUS, TOLERANCE, MAGNET_HOLE_DIAMETER, MAGNET_HOLE_DEPTH, MAGNET_HOLE_DISTANCE_FROM_EDGE, SCREW_HOLE_DIAMETER, SCREW_HOLE_DEPTH, BASEPLATE_BOTTOM_CHAMFER, BASEPLATE_VERTICAL_SECTION, BASEPLATE_TOP_CHAMFER, BASEPLATE_TOP_LEDGE_WIDTH, BASEPLATE_OUTER_RADIUS, BASEPLATE_VERTICAL_RADIUS, BASEPLATE_BOTTOM_RADIUS, STACKING_LIP_TOP_LEDGE,STACKING_LIP_BOTTOM_CHAMFER,STACKING_LIP_VERTICAL_SECTION, HEIGHT_UNIT, BASEPLATE_SMALL_FILLET, MAGNET_BASE, MAGNET_EDGE_THICKNESS, MAGNET_BASE_HOLE, MAGNET_CHAMFER, BASE_THICKNESS, MAGNET_BOTTOM_CHAMFER, CONNECTION_HOLE_DIAMETER, LABEL_SHELF_WIDTH, LABEL_SHELF_VERTICAL_THICKNESS, LABEL_SHELF_LENGTH, LABEL_SHELF_ANGLE, SCOOP_RADIUS

unitmm = Units.Quantity("1 mm")

__all__ = ["BinBlank",
           "SimpleStorageBin",
           "PartsBin",
           "Baseplate",
           "MagnetBaseplate",
           "ScrewTogetherBaseplate",
           "EcoBin"]


def fcvec(x):
    if len(x) == 2:
        return(App.Vector(x[0], x[1], 0))
    else:
        return(App.Vector(x[0], x[1], x[2]))


class ViewProviderGridfinity(object):
    def __init__(self, obj, icon_fn=None):
        # Set this object to the proxy object of the actual view provider
        obj.Proxy = self
        self._check_attr()
        dirname = os.path.dirname(__file__)
        self.icon_fn = icon_fn or os.path.join(dirname, "icons", "gridfinity_workbench_icon.svg")
        App.Console.PrintMessage("works until here\n")
    def _check_attr(self):
        ''' Check for missing attributes. '''
        if not hasattr(self, "icon_fn"):
            setattr(self, "icon_fn", os.path.join(os.path.dirname(__file__), "icons", "gridfinity_workbench_icon.svg"))

    def attach(self, vobj):
        self.vobj = vobj

    def getIcon(self):
        self._check_attr()
        return self.icon_fn

    def __getstate__(self):
        self._check_attr()
        return {"icon_fn": self.icon_fn}

    def __setstate__(self, state):
        if state and "icon_fn" in state:
            self.icon_fn = state["icon_fn"]

class FoundationGridfinity(object):
    def __init__(self, obj):
        obj.addProperty("App::PropertyString", "version", "version", "Gridfinity Workbench Version", 1)
        obj.version = __version__
        self.make_attachable(obj)
    def make_attachable(self, obj):
        # Needed to make this object attachable
        pass

    def execute(self, fp):
        gridfinity_shape = self.generate_gridfinity_shape(fp)
        if hasattr(fp, "BaseFeature") and fp.BaseFeature is not None:
            # we're inside a PartDesign Body, thus need to fuse with the base feature
            gridfinity_shape.Placement = fp.Placement # ensure the bin is placed correctly before fusing
            result_shape = fp.BaseFeature.Shape.fuse(gridfinity_shape)
            result_shape.transformShape(fp.Placement.inverse().toMatrix(), True)
            fp.Shape = result_shape
        else:
            fp.Shape = gridfinity_shape

    def generate_gridfinity_shape(self, fp):
        """
        This method has to return the TopoShape of the object.
        """
        raise NotImplementedError("generate_gridfinity_shape not implemented")

class BinBlank(FoundationGridfinity):

    def __init__(self, obj):
        super(BinBlank, self).__init__(obj)

        obj.addProperty("App::PropertyPythonObject",
                        "Bin", "base", "python gridfinity object")

        self.add_bin_properties(obj)
        self.add_custom_bin_properties(obj)
        self.add_reference_properties(obj)
        self.add_expert_properties(obj)
        self.add_hidden_properties(obj)

        obj.Proxy = self

    def add_bin_properties(self, obj):

        obj.addProperty("App::PropertyInteger","xGridUnits","Gridfinity","Length of the edges of the outline").xGridUnits=2
        obj.addProperty("App::PropertyInteger","yGridUnits","Gridfinity","Height of the extrusion").yGridUnits=2
        obj.addProperty("App::PropertyInteger","HeightUnits","Gridfinity","height of the bin in units, each is 7 mm").HeightUnits=6
        obj.addProperty("App::PropertyBool","StackingLip","Gridfinity","Toggle the stacking lip on or off").StackingLip=True
        obj.addProperty("App::PropertyBool","MagnetHoles","Gridfinity","Toggle the magnet holes on or off").MagnetHoles = True
        obj.addProperty("App::PropertyBool","ScrewHoles","Gridfinity","Toggle the screw holes on or off").ScrewHoles = True


    def add_custom_bin_properties(self, obj):
        obj.addProperty("App::PropertyLength","CustomHeight","GridfinityNonStandard","total height of the bin using the custom heignt instead of incraments of 7 mm").CustomHeight = 42
        obj.addProperty("App::PropertyLength","SequentialBridgingLayerHeight","GridfinityNonStandard","Layer Height that you print in for optimal print results").SequentialBridgingLayerHeight = 0.2
        obj.addProperty("App::PropertyBool","NonStandardHeight","GridfinityNonStandard","use a custom height if selected").NonStandardHeight=False
        obj.addProperty("App::PropertyLength","MagnetHoleDiameter", "GridfinityNonStandard", "Diameter of Magnet Holes <br> <br> default = 6.5 mm").MagnetHoleDiameter = MAGNET_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","MagnetHoleDepth", "GridfinityNonStandard", "Depth of Magnet Holes <br> <br> default = 2.4 mm").MagnetHoleDepth = MAGNET_HOLE_DEPTH
        obj.addProperty("App::PropertyLength","ScrewHoleDiameter", "GridfinityNonStandard", "Diameter of Screw Holes <br> <br> default = 3.0 mm").ScrewHoleDiameter = SCREW_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","ScrewHoleDepth", "GridfinityNonStandard", "Depth of Screw Holes <br> <br> default = 6.0 mm").ScrewHoleDepth = SCREW_HOLE_DEPTH

    def add_reference_properties(self, obj):
        obj.addProperty("App::PropertyLength","xTotalWidth","ReferenceDimensions","total width of bin in x direction", 1)
        obj.addProperty("App::PropertyLength","yTotalWidth","ReferenceDimensions","total width of bin in y direction", 1)
        obj.addProperty("App::PropertyLength","TotalHeight","ReferenceDimensions","total height of the bin", 1)
        obj.addProperty("App::PropertyLength","BaseProfileHeight","ReferenceDimensions","Height of the Gridfinity Base Profile", 1)
        obj.addProperty("App::PropertyLength","BinUnit", "ReferenceDimensions", "Width of a single bin unit",1).BinUnit = BIN_UNIT

    def add_expert_properties(self, obj):
        obj.addProperty("App::PropertyLength","BaseProfileBottomChamfer", "zzExpertOnly", "height of chamfer in bottom of bin                                                                                                         base profile <br> <br> default = 0.8 mm",1).BaseProfileBottomChamfer=BIN_BASE_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","BaseProfileVerticalSection", "zzExpertOnly", "Height of the vertical section in bin base profile",1).BaseProfileVerticalSection=BIN_BASE_VERTICAL_SECTION
        obj.addProperty("App::PropertyLength","BaseProfileTopChamfer", "zzExpertOnly", "Height of the top chamfer in the bin base profile",1).BaseProfileTopChamfer=BIN_BASE_TOP_CHAMFER
        obj.addProperty("App::PropertyLength","GridSize", "zzExpertOnly", "Size of the Grid").GridSize = GRID_SIZE
        obj.addProperty("App::PropertyLength","HeightUnitValue", "zzExpertOnly", "height per unit, default is 7mm",1).HeightUnitValue = 7
        obj.addProperty("App::PropertyLength","BinOuterRadius", "zzExpertOnly", "Outer radius of the bin",1).BinOuterRadius = BIN_OUTER_RADIUS
        obj.addProperty("App::PropertyLength","BinVerticalRadius", "zzExpertOnly", "Radius of the base profile Vertical section",1).BinVerticalRadius = BIN_BASE_VERTICAL_RADIUS
        obj.addProperty("App::PropertyLength","BinBottomRadius", "zzExpertOnly", "bottom of bin corner radius",1).BinBottomRadius = BIN_BASE_BOTTOM_RADIUS

        obj.addProperty("App::PropertyLength","Tolerance", "zzExpertOnly", "The tolerance on each side of a bin between before the edge of the grid <br> <br> default = 0.25 mm",1).Tolerance = TOLERANCE
        obj.addProperty("App::PropertyLength","MagnetHoleDistanceFromEdge", "zzExpertOnly", "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",1).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE
        obj.addProperty("App::PropertyLength","StackingLipTopLedge", "zzExpertOnly", "Top Ledge of the stacking lip <br> <br> default = 0.4 mm",1).StackingLipTopLedge = STACKING_LIP_TOP_LEDGE
        obj.addProperty("App::PropertyLength","StackingLipTopChamfer", "zzExpertOnly", "Top Chamfer of the Stacking lip",1)
        obj.addProperty("App::PropertyLength","StackingLipBottomChamfer", "zzExpertOnly", "Bottom Chamfer of the Stacking lip<br> <br> default = 0.7 mm",1).StackingLipBottomChamfer = STACKING_LIP_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","StackingLipVerticalSection", "zzExpertOnly", "vertical section of the Stacking lip<br> <br> default = 1.8 mm",1).StackingLipVerticalSection= STACKING_LIP_VERTICAL_SECTION

    def add_hidden_properties(self, obj):
        obj.addProperty("App::PropertyLength","WallThickness", "GridfinityNonStandard", "for stacking lip").WallThickness = 1
        obj.setEditorMode("WallThickness",2)

    def generate_gridfinity_shape(self, obj):

        obj.xTotalWidth = obj.xGridUnits*obj.GridSize-obj.Tolerance*2
        obj.yTotalWidth = obj.yGridUnits*obj.GridSize-obj.Tolerance*2
        obj.BaseProfileHeight = obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection+obj.BaseProfileTopChamfer
        obj.StackingLipTopChamfer = obj.BaseProfileTopChamfer - obj.Tolerance - obj.StackingLipTopLedge
        obj.BinUnit = obj.GridSize - TOLERANCE*2*unitmm

        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight
        else:
            obj.TotalHeight = obj.HeightUnits*obj.HeightUnitValue


        fuse_total = MakeBinBase(self, obj)
        solid_center= RoundedRectangleExtrude(obj.xTotalWidth, obj.yTotalWidth, -obj.TotalHeight+obj.BaseProfileHeight, obj.TotalHeight-obj.BaseProfileHeight, obj.BinOuterRadius)
        solid_center.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))

        fuse_total = Part.Shape.fuse(fuse_total, solid_center )

        if obj.StackingLip:
            stacking_lip = MakeStackingLip(self, obj)
            fuse_total = Part.Shape.fuse(stacking_lip,fuse_total)
        if obj.ScrewHoles or obj.MagnetHoles:
            holes = MakeBottomHoles(self, obj)
            fuse_total = Part.Shape.cut(fuse_total, holes)

        return fuse_total

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class BinBase(FoundationGridfinity):

    def __init__(self, obj):
        super(BinBase, self).__init__(obj)

        obj.addProperty("App::PropertyPythonObject",
                        "Bin", "base", "python gridfinity object")

        self.add_bin_properties(obj)
        self.add_custom_bin_properties(obj)
        self.add_reference_properties(obj)
        self.add_expert_properties(obj)
        self.add_hidden_properties(obj)

        obj.Proxy = self

    def add_bin_properties(self, obj):

        obj.addProperty("App::PropertyInteger","xGridUnits","Gridfinity","Length of the edges of the outline").xGridUnits=2
        obj.addProperty("App::PropertyInteger","yGridUnits","Gridfinity","Height of the extrusion").yGridUnits=2
        obj.addProperty("App::PropertyInteger","HeightUnits","Gridfinity","height of the bin in units, each is 7 mm").HeightUnits=1
        obj.addProperty("App::PropertyBool","StackingLip","Gridfinity","Toggle the stacking lip on or off").StackingLip=False
        obj.addProperty("App::PropertyBool","MagnetHoles","Gridfinity","Toggle the magnet holes on or off").MagnetHoles = True
        obj.addProperty("App::PropertyBool","ScrewHoles","Gridfinity","Toggle the screw holes on or off").ScrewHoles = True


    def add_custom_bin_properties(self, obj):
        obj.addProperty("App::PropertyLength","CustomHeight","GridfinityNonStandard","total height of the bin using the custom heignt instead of incraments of 7 mm").CustomHeight = 42
        obj.addProperty("App::PropertyLength","SequentialBridgingLayerHeight","GridfinityNonStandard","Layer Height that you print in for optimal print results").SequentialBridgingLayerHeight = 0.2
        obj.addProperty("App::PropertyBool","NonStandardHeight","GridfinityNonStandard","use a custom height if selected").NonStandardHeight=False
        obj.addProperty("App::PropertyLength","MagnetHoleDiameter", "GridfinityNonStandard", "Diameter of Magnet Holes <br> <br> default = 6.5 mm").MagnetHoleDiameter = MAGNET_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","MagnetHoleDepth", "GridfinityNonStandard", "Depth of Magnet Holes <br> <br> default = 2.4 mm").MagnetHoleDepth = MAGNET_HOLE_DEPTH
        obj.addProperty("App::PropertyLength","ScrewHoleDiameter", "GridfinityNonStandard", "Diameter of Screw Holes <br> <br> default = 3.0 mm").ScrewHoleDiameter = SCREW_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","ScrewHoleDepth", "GridfinityNonStandard", "Depth of Screw Holes <br> <br> default = 6.0 mm").ScrewHoleDepth = SCREW_HOLE_DEPTH

    def add_reference_properties(self, obj):
        obj.addProperty("App::PropertyLength","xTotalWidth","ReferenceDimensions","total width of bin in x direction", 1)
        obj.addProperty("App::PropertyLength","yTotalWidth","ReferenceDimensions","total width of bin in y direction", 1)
        obj.addProperty("App::PropertyLength","TotalHeight","ReferenceDimensions","total height of the bin", 1)
        obj.addProperty("App::PropertyLength","BaseProfileHeight","ReferenceDimensions","Height of the Gridfinity Base Profile", 1)
        obj.addProperty("App::PropertyLength","BinUnit", "ReferenceDimensions", "Width of a single bin unit",1).BinUnit = BIN_UNIT

    def add_expert_properties(self, obj):
        obj.addProperty("App::PropertyLength","BaseProfileBottomChamfer", "zzExpertOnly", "height of chamfer in bottom of bin                                                                                                         base profile <br> <br> default = 0.8 mm",1).BaseProfileBottomChamfer=BIN_BASE_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","BaseProfileVerticalSection", "zzExpertOnly", "Height of the vertical section in bin base profile",1).BaseProfileVerticalSection=BIN_BASE_VERTICAL_SECTION
        obj.addProperty("App::PropertyLength","BaseProfileTopChamfer", "zzExpertOnly", "Height of the top chamfer in the bin base profile",1).BaseProfileTopChamfer=BIN_BASE_TOP_CHAMFER
        obj.addProperty("App::PropertyLength","GridSize", "zzExpertOnly", "Size of the Grid").GridSize = GRID_SIZE
        obj.addProperty("App::PropertyLength","HeightUnitValue", "zzExpertOnly", "height per unit, default is 7mm",1).HeightUnitValue = 7
        obj.addProperty("App::PropertyLength","BinOuterRadius", "zzExpertOnly", "Outer radius of the bin",1).BinOuterRadius = BIN_OUTER_RADIUS
        obj.addProperty("App::PropertyLength","BinVerticalRadius", "zzExpertOnly", "Radius of the base profile Vertical section",1).BinVerticalRadius = BIN_BASE_VERTICAL_RADIUS
        obj.addProperty("App::PropertyLength","BinBottomRadius", "zzExpertOnly", "bottom of bin corner radius",1).BinBottomRadius = BIN_BASE_BOTTOM_RADIUS

        obj.addProperty("App::PropertyLength","Tolerance", "zzExpertOnly", "The tolerance on each side of a bin between before the edge of the grid <br> <br> default = 0.25 mm",1).Tolerance = TOLERANCE
        obj.addProperty("App::PropertyLength","MagnetHoleDistanceFromEdge", "zzExpertOnly", "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",1).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE
        obj.addProperty("App::PropertyLength","StackingLipTopLedge", "zzExpertOnly", "Top Ledge of the stacking lip <br> <br> default = 0.4 mm",1).StackingLipTopLedge = STACKING_LIP_TOP_LEDGE
        obj.addProperty("App::PropertyLength","StackingLipTopChamfer", "zzExpertOnly", "Top Chamfer of the Stacking lip",1)
        obj.addProperty("App::PropertyLength","StackingLipBottomChamfer", "zzExpertOnly", "Bottom Chamfer of the Stacking lip<br> <br> default = 0.7 mm",1).StackingLipBottomChamfer = STACKING_LIP_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","StackingLipVerticalSection", "zzExpertOnly", "vertical section of the Stacking lip<br> <br> default = 1.8 mm",1).StackingLipVerticalSection= STACKING_LIP_VERTICAL_SECTION

    def add_hidden_properties(self, obj):
        obj.addProperty("App::PropertyLength","WallThickness", "GridfinityNonStandard", "for stacking lip").WallThickness = 1
        obj.setEditorMode("WallThickness",2)

    def generate_gridfinity_shape(self, obj):

        obj.xTotalWidth = obj.xGridUnits*obj.GridSize-obj.Tolerance*2
        obj.yTotalWidth = obj.yGridUnits*obj.GridSize-obj.Tolerance*2
        obj.BaseProfileHeight = obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection+obj.BaseProfileTopChamfer
        obj.StackingLipTopChamfer = obj.BaseProfileTopChamfer - obj.Tolerance - obj.StackingLipTopLedge
        obj.BinUnit = obj.GridSize - TOLERANCE*2*unitmm

        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight
        else:
            obj.TotalHeight = obj.HeightUnits*obj.HeightUnitValue


        fuse_total = MakeBinBase(self, obj)
        solid_center= RoundedRectangleExtrude(obj.xTotalWidth, obj.yTotalWidth, -obj.TotalHeight+obj.BaseProfileHeight, obj.TotalHeight-obj.BaseProfileHeight, obj.BinOuterRadius)
        solid_center.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))

        fuse_total = Part.Shape.fuse(fuse_total, solid_center )

        if obj.StackingLip:
            stacking_lip = MakeStackingLip(self, obj)
            fuse_total = Part.Shape.fuse(stacking_lip,fuse_total)
        if obj.ScrewHoles or obj.MagnetHoles:
            holes = MakeBottomHoles(self, obj)
            fuse_total = Part.Shape.cut(fuse_total, holes)

        #fuse_total.translate(App.Vector(obj.BinUnit/2*4,obj.BinUnit/2*4,0))

        return fuse_total

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

class SimpleStorageBin(FoundationGridfinity):

    def __init__(self, obj):
        super(SimpleStorageBin, self).__init__(obj)

        obj.addProperty("App::PropertyPythonObject",
                        "Bin", "base", "python gridfinity object")

        self.add_bin_properties(obj)
        self.add_custom_bin_properties(obj)
        self.add_reference_properties(obj)
        self.add_expert_properties(obj)

        obj.Proxy = self

    def add_bin_properties(self, obj):

        obj.addProperty("App::PropertyInteger","xGridUnits","Gridfinity","Length of the edges of the outline").xGridUnits=2
        obj.addProperty("App::PropertyInteger","yGridUnits","Gridfinity","Height of the extrusion").yGridUnits=2
        obj.addProperty("App::PropertyInteger","HeightUnits","Gridfinity","height of the bin in units, each unit is 7 mm").HeightUnits=6
        obj.addProperty("App::PropertyBool","StackingLip","Gridfinity","Toggle the stacking lip on or off").StackingLip=True
        obj.addProperty("App::PropertyBool","MagnetHoles","Gridfinity","Toggle the magnet holes on or off").MagnetHoles = True
        obj.addProperty("App::PropertyBool","ScrewHoles","Gridfinity","Toggle the screw holes on or off").ScrewHoles = True
        obj.addProperty("App::PropertyBool","Scoop","Gridfinity","Toggle the Scoop fillet on or off").Scoop = False
        obj.addProperty("App::PropertyInteger","xDividers","Gridfinity","Select the Number of Dividers in the x direction").xDividers = 0
        obj.addProperty("App::PropertyInteger","yDividers","Gridfinity","Select the number of Dividers in the y direction").yDividers = 0
        obj.addProperty("App::PropertyEnumeration", "LabelShelfPlacement", "Gridfinity", "Choose the style of the label shelf")
        obj.LabelShelfPlacement = ["Center", "Full Width", "Left", "Right"]
        obj.addProperty("App::PropertyEnumeration", "LabelShelfStyle", "Gridfinity", "Choose to turn the label shelf on or off")
        obj.LabelShelfStyle = [ "Off", "Standard", "Overhang"]

    def add_custom_bin_properties(self, obj):
        obj.addProperty("App::PropertyLength","CustomHeight","GridfinityNonStandard","total height of the bin using the custom heignt instead of incraments of 7 mm").CustomHeight = 42
        obj.addProperty("App::PropertyLength","SequentialBridgingLayerHeight","GridfinityNonStandard","Layer Height that you print in for optimal print results").SequentialBridgingLayerHeight = 0.2
        obj.addProperty("App::PropertyBool","NonStandardHeight","GridfinityNonStandard","use a custom height if selected").NonStandardHeight=False
        obj.addProperty("App::PropertyLength","MagnetHoleDiameter", "GridfinityNonStandard", "Diameter of Magnet Holes <br> <br> default = 6.5 mm").MagnetHoleDiameter = MAGNET_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","MagnetHoleDepth", "GridfinityNonStandard", "Depth of Magnet Holes <br> <br> default = 2.4 mm").MagnetHoleDepth = MAGNET_HOLE_DEPTH
        obj.addProperty("App::PropertyLength","ScrewHoleDiameter", "GridfinityNonStandard", "Diameter of Screw Holes <br> <br> default = 3.0 mm").ScrewHoleDiameter = SCREW_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","ScrewHoleDepth", "GridfinityNonStandard", "Depth of Screw Holes <br> <br> default = 6.0 mm").ScrewHoleDepth = SCREW_HOLE_DEPTH
        obj.addProperty("App::PropertyLength","WallThickness", "GridfinityNonStandard", "Wall thickness of the bin <br> <br> default = 1.0 mm").WallThickness = 1.0
        obj.addProperty("App::PropertyLength","InsideFilletRadius", "GridfinityNonStandard", "inside fillet at the bottom of the bin <br> <br> default = 1.85 mm").InsideFilletRadius = 1.85
        obj.addProperty("App::PropertyLength","DividerThickness", "GridfinityNonStandard", "Thickness of the dividers, ideally an even multiple of layer width <br> <br> default = 1.2 mm").DividerThickness = 1.2
        obj.addProperty("App::PropertyLength","LabelShelfWidth", "GridfinityNonStandard", "Thickness of the Label Shelf <br> <br> default = 1.2 mm").LabelShelfWidth = LABEL_SHELF_WIDTH
        obj.addProperty("App::PropertyLength","LabelShelfLength", "GridfinityNonStandard", "Length of the Label Shelf <br> <br> default = 1.2 mm").LabelShelfLength = LABEL_SHELF_LENGTH
        obj.addProperty("App::PropertyAngle","LabelShelfAngle", "GridfinityNonStandard", "Angle of the bottom part of the Label <br> <br> default = 42º").LabelShelfAngle = LABEL_SHELF_ANGLE
        obj.addProperty("App::PropertyLength","ScoopRadius", "GridfinityNonStandard", "Radius of the Scoop <br> <br> default = 21 mm").ScoopRadius = SCOOP_RADIUS
        obj.addProperty("App::PropertyLength","xDividerHeight", "GridfinityNonStandard", "Custom Height of x dividers <br> <br> default = 0 mm = full height").xDividerHeight = 0
        obj.addProperty("App::PropertyLength","yDividerHeight", "GridfinityNonStandard", "Custom Height of y dividers <br> <br> default = 0 mm = full height").yDividerHeight = 0

    def add_reference_properties(self, obj):
        obj.addProperty("App::PropertyLength","xTotalWidth","ReferenceDimensions","total width of bin in x direction", 1)
        obj.addProperty("App::PropertyLength","yTotalWidth","ReferenceDimensions","total width of bin in y direction", 1)
        obj.addProperty("App::PropertyLength","TotalHeight","ReferenceDimensions","total height of the bin", 1)
        obj.addProperty("App::PropertyLength","BaseProfileHeight","ReferenceDimensions","Height of the Gridfinity Base Profile", 1)
        obj.addProperty("App::PropertyLength","UsableHeight","ReferenceDimensions","Height of the bin minus the bottom unit, the amount of the bin that can be effectively used", 1)
        obj.addProperty("App::PropertyLength","BinUnit", "ReferenceDimensions", "Width of a single bin unit",1).BinUnit = BIN_UNIT

    def add_expert_properties(self, obj):
        obj.addProperty("App::PropertyLength","BaseProfileBottomChamfer", "zzExpertOnly", "height of chamfer in bottom of bin                                                                                                         base profile <br> <br> default = 0.8 mm",1).BaseProfileBottomChamfer=BIN_BASE_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","BaseProfileVerticalSection", "zzExpertOnly", "Height of the vertical section in bin base profile",1).BaseProfileVerticalSection=BIN_BASE_VERTICAL_SECTION
        obj.addProperty("App::PropertyLength","BaseProfileTopChamfer", "zzExpertOnly", "Height of the top chamfer in the bin base profile",1).BaseProfileTopChamfer=BIN_BASE_TOP_CHAMFER
        obj.addProperty("App::PropertyLength","GridSize", "zzExpertOnly", "Size of the Grid").GridSize = GRID_SIZE
        obj.addProperty("App::PropertyLength","HeightUnitValue", "zzExpertOnly", "height per unit, default is 7mm",1).HeightUnitValue = HEIGHT_UNIT
        obj.addProperty("App::PropertyLength","BinOuterRadius", "zzExpertOnly", "Outer radius of the bin",1).BinOuterRadius = BIN_OUTER_RADIUS
        obj.addProperty("App::PropertyLength","BinVerticalRadius", "zzExpertOnly", "Radius of the base profile Vertical section",1).BinVerticalRadius = BIN_BASE_VERTICAL_RADIUS
        obj.addProperty("App::PropertyLength","BinBottomRadius", "zzExpertOnly", "bottom of bin corner radius",1).BinBottomRadius = BIN_BASE_BOTTOM_RADIUS

        obj.addProperty("App::PropertyLength","Tolerance", "zzExpertOnly", "The tolerance on each side of a bin between before the edge of the grid <br> <br> default = 0.25 mm",1).Tolerance = TOLERANCE
        obj.addProperty("App::PropertyLength","MagnetHoleDistanceFromEdge", "zzExpertOnly", "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",1).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE
        obj.addProperty("App::PropertyLength","StackingLipTopLedge", "zzExpertOnly", "Top Ledge of the stacking lip <br> <br> default = 0.4 mm",1).StackingLipTopLedge = STACKING_LIP_TOP_LEDGE
        obj.addProperty("App::PropertyLength","StackingLipTopChamfer", "zzExpertOnly", "Top Chamfer of the Stacking lip",1)
        obj.addProperty("App::PropertyLength","StackingLipBottomChamfer", "zzExpertOnly", "Bottom Chamfer of the Stacking lip<br> <br> default = 0.7 mm",1).StackingLipBottomChamfer = STACKING_LIP_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","StackingLipVerticalSection", "zzExpertOnly", "vertical section of the Stacking lip<br> <br> default = 1.8 mm",1).StackingLipVerticalSection = STACKING_LIP_VERTICAL_SECTION
        obj.addProperty("App::PropertyLength","LabelShelfVerticalThickness", "zzExpertOnly", "Vertical Thickness of the Label Shelf <br> <br> default = 2 mm").LabelShelfVerticalThickness = LABEL_SHELF_VERTICAL_THICKNESS



    def generate_gridfinity_shape(self, obj):

        ## Parameter Calculations

        obj.xTotalWidth = obj.xGridUnits*obj.GridSize-obj.Tolerance*2
        obj.yTotalWidth = obj.yGridUnits*obj.GridSize-obj.Tolerance*2
        obj.BaseProfileHeight = obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection+obj.BaseProfileTopChamfer
        obj.StackingLipTopChamfer = obj.BaseProfileTopChamfer - obj.Tolerance - obj.StackingLipTopLedge
        obj.BinUnit = obj.GridSize - TOLERANCE*2*unitmm

        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight
        else:
            obj.TotalHeight = obj.HeightUnits*obj.HeightUnitValue
        obj.UsableHeight = obj.TotalHeight - obj.HeightUnitValue

        ## Error Checking


        divmin = obj.HeightUnitValue + obj.InsideFilletRadius + 0.05*unitmm
        if obj.xDividerHeight < divmin and obj.xDividerHeight != 0:
            obj.xDividerHeight = divmin
            App.Console.PrintWarning("Divider Height must be equal to or greater than:  ")
            App.Console.PrintWarning(divmin)
            App.Console.PrintWarning("\n")

        if obj.yDividerHeight < divmin and obj.yDividerHeight != 0:
            obj.yDividerHeight = divmin
            App.Console.PrintWarning("Divider Height must be equal to or greater than:  ")
            App.Console.PrintWarning(divmin)
            App.Console.PrintWarning("\n")

        ## Bin Construction
        fuse_total = MakeBinBase(self, obj)

        solid_center= RoundedRectangleExtrude(obj.xTotalWidth, obj.yTotalWidth, -obj.TotalHeight+obj.BaseProfileHeight, obj.TotalHeight-obj.BaseProfileHeight, obj.BinOuterRadius)
        solid_center.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))
        fuse_total = fuse_total.fuse(solid_center)

        compartements = MakeCompartements(self, obj)

        fuse_total = fuse_total.cut(compartements)

        if obj.StackingLip:
            stacking_lip = MakeStackingLip(self, obj)
            fuse_total = Part.Shape.fuse(stacking_lip,fuse_total)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = MakeBottomHoles(self, obj)
            fuse_total = Part.Shape.cut(fuse_total, holes)

        if obj.LabelShelfStyle != "Off":
            label_shelf = MakeLabelShelf(self, obj)
            fuse_total = fuse_total.fuse(label_shelf)

        if obj.Scoop:
            scoop = MakeScoop(self, obj)
            fuse_total = fuse_total.fuse(scoop)

        fuse_total = Part.Solid.removeSplitter(fuse_total)

        #fuse_total.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))

        return fuse_total

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class EcoBin(FoundationGridfinity):

    def __init__(self, obj):
        super(EcoBin, self).__init__(obj)

        obj.addProperty("App::PropertyPythonObject",
                        "Bin", "base", "python gridfinity object")

        self.add_bin_properties(obj)
        self.add_custom_bin_properties(obj)
        self.add_reference_properties(obj)
        self.add_expert_properties(obj)

        obj.Proxy = self

    def add_bin_properties(self, obj):

        obj.addProperty("App::PropertyInteger","xGridUnits","Gridfinity","Length of the edges of the outline").xGridUnits=2
        obj.addProperty("App::PropertyInteger","yGridUnits","Gridfinity","Height of the extrusion").yGridUnits=2
        obj.addProperty("App::PropertyInteger","HeightUnits","Gridfinity","height of the bin in units, each unit is 7 mm").HeightUnits=6
        obj.addProperty("App::PropertyBool","StackingLip","Gridfinity","Toggle the stacking lip on or off").StackingLip=True
        obj.addProperty("App::PropertyBool","MagnetHoles","Gridfinity","Toggle the magnet holes on or off").MagnetHoles = False

        obj.addProperty("App::PropertyInteger","xDividers","Gridfinity","Select the Number of Dividers in the x direction").xDividers = 0
        obj.addProperty("App::PropertyInteger","yDividers","Gridfinity","Select the number of Dividers in the y direction").yDividers = 0
        obj.addProperty("App::PropertyLength","BaseWallThickness","Gridfinity","The thickness of the bin at the base").BaseWallThickness = 0.8

    def add_custom_bin_properties(self, obj):
        obj.addProperty("App::PropertyLength","CustomHeight","GridfinityNonStandard","total height of the bin using the custom heignt instead of incraments of 7 mm").CustomHeight = 42
        obj.addProperty("App::PropertyLength","SequentialBridgingLayerHeight","GridfinityNonStandard","Layer Height that you print in for optimal print results").SequentialBridgingLayerHeight = 0.2
        obj.addProperty("App::PropertyBool","NonStandardHeight","GridfinityNonStandard","use a custom height if selected").NonStandardHeight=False
        obj.addProperty("App::PropertyLength","MagnetHoleDiameter", "GridfinityNonStandard", "Diameter of Magnet Holes <br> <br> default = 6.5 mm").MagnetHoleDiameter = MAGNET_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","MagnetHoleDepth", "GridfinityNonStandard", "Depth of Magnet Holes <br> <br> default = 2.4 mm").MagnetHoleDepth = MAGNET_HOLE_DEPTH
        obj.addProperty("App::PropertyLength","WallThickness", "GridfinityNonStandard", "Wall thickness of the bin <br> <br> default = 0.8 mm").WallThickness = 0.8
        obj.addProperty("App::PropertyLength","InsideFilletRadius", "GridfinityNonStandard", "inside fillet at the bottom of the bin <br> <br> default = 1.5 mm").InsideFilletRadius = 1.5
        obj.addProperty("App::PropertyLength","DividerThickness", "GridfinityNonStandard", "Thickness of the dividers, ideally an even multiple of layer width <br> <br> default = 0.8 mm").DividerThickness = 0.8
        obj.addProperty("App::PropertyLength","xDividerHeight", "GridfinityNonStandard", "Custom Height of x dividers <br> <br> default = 0 mm = full height").xDividerHeight = 0
        obj.addProperty("App::PropertyLength","yDividerHeight", "GridfinityNonStandard", "Custom Height of y dividers <br> <br> default = 0 mm = full height").yDividerHeight = 0

    def add_reference_properties(self, obj):
        obj.addProperty("App::PropertyLength","xTotalWidth","ReferenceDimensions","total width of bin in x direction", 1)
        obj.addProperty("App::PropertyLength","yTotalWidth","ReferenceDimensions","total width of bin in y direction", 1)
        obj.addProperty("App::PropertyLength","TotalHeight","ReferenceDimensions","total height of the bin", 1)
        obj.addProperty("App::PropertyLength","BaseProfileHeight","ReferenceDimensions","Height of the Gridfinity Base Profile", 1)
        obj.addProperty("App::PropertyLength","BinUnit", "ReferenceDimensions", "Width of a single bin unit",1).BinUnit = BIN_UNIT

    def add_expert_properties(self, obj):
        obj.addProperty("App::PropertyLength","BaseProfileBottomChamfer", "zzExpertOnly", "height of chamfer in bottom of bin                                                                                                         base profile <br> <br> default = 0.8 mm",1).BaseProfileBottomChamfer=BIN_BASE_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","BaseProfileVerticalSection", "zzExpertOnly", "Height of the vertical section in bin base profile",1).BaseProfileVerticalSection=BIN_BASE_VERTICAL_SECTION
        obj.addProperty("App::PropertyLength","BaseProfileTopChamfer", "zzExpertOnly", "Height of the top chamfer in the bin base profile",1).BaseProfileTopChamfer=BIN_BASE_TOP_CHAMFER
        obj.addProperty("App::PropertyLength","GridSize", "zzExpertOnly", "Size of the Grid").GridSize = GRID_SIZE
        obj.addProperty("App::PropertyLength","HeightUnitValue", "zzExpertOnly", "height per unit, default is 7mm",1).HeightUnitValue = HEIGHT_UNIT
        obj.addProperty("App::PropertyLength","BinOuterRadius", "zzExpertOnly", "Outer radius of the bin",1).BinOuterRadius = BIN_OUTER_RADIUS
        obj.addProperty("App::PropertyLength","BinVerticalRadius", "zzExpertOnly", "Radius of the base profile Vertical section",1).BinVerticalRadius = BIN_BASE_VERTICAL_RADIUS
        obj.addProperty("App::PropertyLength","BinBottomRadius", "zzExpertOnly", "bottom of bin corner radius",1).BinBottomRadius = BIN_BASE_BOTTOM_RADIUS

        obj.addProperty("App::PropertyLength","Tolerance", "zzExpertOnly", "The tolerance on each side of a bin between before the edge of the grid <br> <br> default = 0.25 mm",1).Tolerance = TOLERANCE
        obj.addProperty("App::PropertyLength","MagnetHoleDistanceFromEdge", "zzExpertOnly", "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",1).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE
        obj.addProperty("App::PropertyLength","StackingLipTopLedge", "zzExpertOnly", "Top Ledge of the stacking lip <br> <br> default = 0.4 mm",1).StackingLipTopLedge = STACKING_LIP_TOP_LEDGE
        obj.addProperty("App::PropertyLength","StackingLipTopChamfer", "zzExpertOnly", "Top Chamfer of the Stacking lip",1)
        obj.addProperty("App::PropertyLength","StackingLipBottomChamfer", "zzExpertOnly", "Bottom Chamfer of the Stacking lip<br> <br> default = 0.7 mm",1).StackingLipBottomChamfer = STACKING_LIP_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","StackingLipVerticalSection", "zzExpertOnly", "vertical section of the Stacking lip<br> <br> default = 1.8 mm",1).StackingLipVerticalSection = STACKING_LIP_VERTICAL_SECTION


        obj.addProperty("App::PropertyBool","ScrewHoles","Gridfinity","Toggle the screw holes on or off").ScrewHoles = False
        obj.setEditorMode("ScrewHoles",2)

        obj.addProperty("App::PropertyLength","ScrewHoleDiameter", "GridfinityNonStandard", "Diameter of Screw Holes <br> <br> default = 3.0 mm").ScrewHoleDiameter = SCREW_HOLE_DIAMETER
        obj.setEditorMode("ScrewHoleDiameter",2)
        obj.addProperty("App::PropertyLength","ScrewHoleDepth", "GridfinityNonStandard", "Depth of Screw Holes <br> <br> default = 6.0 mm").ScrewHoleDepth = SCREW_HOLE_DEPTH
        obj.setEditorMode("ScrewHoleDepth",2)

    def generate_gridfinity_shape(self, obj):
        ## Parameter Calculation

        obj.xTotalWidth = obj.xGridUnits*obj.GridSize-obj.Tolerance*2
        obj.yTotalWidth = obj.yGridUnits*obj.GridSize-obj.Tolerance*2
        obj.BaseProfileHeight = obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection+obj.BaseProfileTopChamfer
        obj.StackingLipTopChamfer = obj.BaseProfileTopChamfer - obj.Tolerance - obj.StackingLipTopLedge
        obj.BinUnit = obj.GridSize - TOLERANCE*2*unitmm

        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight
        else:
            obj.TotalHeight = obj.HeightUnits*obj.HeightUnitValue

        ## Error Checking

        # Divider Minimum Height
        divmin = obj.HeightUnitValue + obj.InsideFilletRadius + 0.05*unitmm
        if obj.xDividerHeight < divmin and obj.xDividerHeight != 0:
            obj.xDividerHeight = divmin
            App.Console.PrintWarning("Divider Height must be equal to or greater than:  ")
            App.Console.PrintWarning(divmin)
            App.Console.PrintWarning("\n")

        if obj.yDividerHeight < divmin and obj.yDividerHeight != 0:
            obj.yDividerHeight = divmin
            App.Console.PrintWarning("Divider Height must be equal to or greater than:  ")
            App.Console.PrintWarning(divmin)
            App.Console.PrintWarning("\n")

        if obj.InsideFilletRadius > (1.6*unitmm):
            obj.InsideFilletRadius = 1.6*unitmm
            App.Console.PrintWarning("Inside Fillet Radius must be equal to or less than:  1.6 mm\n")

        ## Bin Construction

        fuse_total = MakeBinBase(self, obj)

        solid_center= RoundedRectangleExtrude(obj.xTotalWidth, obj.yTotalWidth, -obj.TotalHeight+obj.BaseProfileHeight, obj.TotalHeight-obj.BaseProfileHeight, obj.BinOuterRadius)
        solid_center.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))
        fuse_total = fuse_total.fuse(solid_center)

        compartements = MakeEcoBinCut(self, obj)

        fuse_total = fuse_total.cut(compartements)

        if obj.StackingLip:
            stacking_lip = MakeStackingLip(self, obj)
            fuse_total = Part.Shape.fuse(stacking_lip,fuse_total)

        if obj.MagnetHoles:
            holes = MakeBottomHoles(self, obj)
            fuse_total = Part.Shape.cut(fuse_total, holes)

        fuse_total = Part.Solid.removeSplitter(fuse_total)

        return fuse_total

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class PartsBin(FoundationGridfinity):

    def __init__(self, obj):
        super(PartsBin, self).__init__(obj)

        obj.addProperty("App::PropertyPythonObject",
                        "Bin", "base", "python gridfinity object")

        self.add_bin_properties(obj)
        self.add_custom_bin_properties(obj)
        self.add_reference_properties(obj)
        self.add_expert_properties(obj)

        obj.Proxy = self

    def add_bin_properties(self, obj):

        obj.addProperty("App::PropertyInteger","xGridUnits","Gridfinity","Length of the edges of the outline").xGridUnits=2
        obj.addProperty("App::PropertyInteger","yGridUnits","Gridfinity","Height of the extrusion").yGridUnits=2
        obj.addProperty("App::PropertyInteger","HeightUnits","Gridfinity","height of the bin in units, each unit is 7 mm").HeightUnits=6
        obj.addProperty("App::PropertyBool","StackingLip","Gridfinity","Toggle the stacking lip on or off").StackingLip=True
        obj.addProperty("App::PropertyBool","MagnetHoles","Gridfinity","Toggle the magnet holes on or off").MagnetHoles = True
        obj.addProperty("App::PropertyBool","ScrewHoles","Gridfinity","Toggle the screw holes on or off").ScrewHoles = True
        obj.addProperty("App::PropertyBool","Scoop","Gridfinity","Toggle the Scoop fillet on or off").Scoop = True
        obj.addProperty("App::PropertyInteger","xDividers","Gridfinity","Select the Number of Dividers in the x direction").xDividers = 0
        obj.addProperty("App::PropertyInteger","yDividers","Gridfinity","Select the number of Dividers in the y direction").yDividers = 1
        obj.addProperty("App::PropertyEnumeration", "LabelShelfPlacement", "Gridfinity", "Choose the style of the label shelf")
        obj.LabelShelfPlacement = ["Center", "Full Width", "Left", "Right"]
        obj.addProperty("App::PropertyEnumeration", "LabelShelfStyle", "Gridfinity", "Choose to turn the label shelf on or off")
        obj.LabelShelfStyle = ["Standard", "Off", "Overhang"]

    def add_custom_bin_properties(self, obj):
        obj.addProperty("App::PropertyLength","CustomHeight","GridfinityNonStandard","total height of the bin using the custom heignt instead of incraments of 7 mm").CustomHeight = 42
        obj.addProperty("App::PropertyLength","SequentialBridgingLayerHeight","GridfinityNonStandard","Layer Height that you print in for optimal print results").SequentialBridgingLayerHeight = 0.2
        obj.addProperty("App::PropertyBool","NonStandardHeight","GridfinityNonStandard","use a custom height if selected").NonStandardHeight=False
        obj.addProperty("App::PropertyLength","MagnetHoleDiameter", "GridfinityNonStandard", "Diameter of Magnet Holes <br> <br> default = 6.5 mm").MagnetHoleDiameter = MAGNET_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","MagnetHoleDepth", "GridfinityNonStandard", "Depth of Magnet Holes <br> <br> default = 2.4 mm").MagnetHoleDepth = MAGNET_HOLE_DEPTH
        obj.addProperty("App::PropertyLength","ScrewHoleDiameter", "GridfinityNonStandard", "Diameter of Screw Holes <br> <br> default = 3.0 mm").ScrewHoleDiameter = SCREW_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","ScrewHoleDepth", "GridfinityNonStandard", "Depth of Screw Holes <br> <br> default = 6.0 mm").ScrewHoleDepth = SCREW_HOLE_DEPTH
        obj.addProperty("App::PropertyLength","WallThickness", "GridfinityNonStandard", "Wall thickness of the bin <br> <br> default = 1.0 mm").WallThickness = 1.0
        obj.addProperty("App::PropertyLength","InsideFilletRadius", "GridfinityNonStandard", "inside fillet at the bottom of the bin <br> <br> default = 1.85 mm").InsideFilletRadius = 1.85
        obj.addProperty("App::PropertyLength","DividerThickness", "GridfinityNonStandard", "Thickness of the dividers, ideally an even multiple of layer width <br> <br> default = 1.2 mm").DividerThickness = 1.2
        obj.addProperty("App::PropertyLength","LabelShelfWidth", "GridfinityNonStandard", "Thickness of the Label Shelf <br> <br> default = 1.2 mm").LabelShelfWidth = LABEL_SHELF_WIDTH
        obj.addProperty("App::PropertyLength","LabelShelfLength", "GridfinityNonStandard", "Length of the Label Shelf <br> <br> default = 1.2 mm").LabelShelfLength = LABEL_SHELF_LENGTH
        obj.addProperty("App::PropertyAngle","LabelShelfAngle", "GridfinityNonStandard", "Angle of the bottom part of the Label <br> <br> default = 42º").LabelShelfAngle = LABEL_SHELF_ANGLE
        obj.addProperty("App::PropertyLength","ScoopRadius", "GridfinityNonStandard", "Radius of the Scoop <br> <br> default = 21 mm").ScoopRadius = SCOOP_RADIUS
        obj.addProperty("App::PropertyLength","xDividerHeight", "GridfinityNonStandard", "Custom Height of x dividers <br> <br> default = 0 mm = full height").xDividerHeight = 0
        obj.addProperty("App::PropertyLength","yDividerHeight", "GridfinityNonStandard", "Custom Height of y dividers <br> <br> default = 0 mm = full height").yDividerHeight = 0

    def add_reference_properties(self, obj):
        obj.addProperty("App::PropertyLength","xTotalWidth","ReferenceDimensions","total width of bin in x direction", 1)
        obj.addProperty("App::PropertyLength","yTotalWidth","ReferenceDimensions","total width of bin in y direction", 1)
        obj.addProperty("App::PropertyLength","TotalHeight","ReferenceDimensions","total height of the bin", 1)
        obj.addProperty("App::PropertyLength","BaseProfileHeight","ReferenceDimensions","Height of the Gridfinity Base Profile", 1)
        obj.addProperty("App::PropertyLength","UsableHeight","ReferenceDimensions","Height of the bin minus the bottom unit, the amount of the bin that can be effectively used", 1)
        obj.addProperty("App::PropertyLength","BinUnit", "ReferenceDimensions", "Width of a single bin unit",1).BinUnit = BIN_UNIT

    def add_expert_properties(self, obj):
        obj.addProperty("App::PropertyLength","BaseProfileBottomChamfer", "zzExpertOnly", "height of chamfer in bottom of bin                                                                                                         base profile <br> <br> default = 0.8 mm",1).BaseProfileBottomChamfer=BIN_BASE_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","BaseProfileVerticalSection", "zzExpertOnly", "Height of the vertical section in bin base profile",1).BaseProfileVerticalSection=BIN_BASE_VERTICAL_SECTION
        obj.addProperty("App::PropertyLength","BaseProfileTopChamfer", "zzExpertOnly", "Height of the top chamfer in the bin base profile",1).BaseProfileTopChamfer=BIN_BASE_TOP_CHAMFER
        obj.addProperty("App::PropertyLength","GridSize", "zzExpertOnly", "Size of the Grid").GridSize = GRID_SIZE
        obj.addProperty("App::PropertyLength","HeightUnitValue", "zzExpertOnly", "height per unit, default is 7mm",1).HeightUnitValue = HEIGHT_UNIT
        obj.addProperty("App::PropertyLength","BinOuterRadius", "zzExpertOnly", "Outer radius of the bin",1).BinOuterRadius = BIN_OUTER_RADIUS
        obj.addProperty("App::PropertyLength","BinVerticalRadius", "zzExpertOnly", "Radius of the base profile Vertical section",1).BinVerticalRadius = BIN_BASE_VERTICAL_RADIUS
        obj.addProperty("App::PropertyLength","BinBottomRadius", "zzExpertOnly", "bottom of bin corner radius",1).BinBottomRadius = BIN_BASE_BOTTOM_RADIUS

        obj.addProperty("App::PropertyLength","Tolerance", "zzExpertOnly", "The tolerance on each side of a bin between before the edge of the grid <br> <br> default = 0.25 mm",1).Tolerance = TOLERANCE
        obj.addProperty("App::PropertyLength","MagnetHoleDistanceFromEdge", "zzExpertOnly", "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",1).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE
        obj.addProperty("App::PropertyLength","StackingLipTopLedge", "zzExpertOnly", "Top Ledge of the stacking lip <br> <br> default = 0.4 mm",1).StackingLipTopLedge = STACKING_LIP_TOP_LEDGE
        obj.addProperty("App::PropertyLength","StackingLipTopChamfer", "zzExpertOnly", "Top Chamfer of the Stacking lip",1)
        obj.addProperty("App::PropertyLength","StackingLipBottomChamfer", "zzExpertOnly", "Bottom Chamfer of the Stacking lip<br> <br> default = 0.7 mm",1).StackingLipBottomChamfer = STACKING_LIP_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","StackingLipVerticalSection", "zzExpertOnly", "vertical section of the Stacking lip<br> <br> default = 1.8 mm",1).StackingLipVerticalSection = STACKING_LIP_VERTICAL_SECTION
        obj.addProperty("App::PropertyLength","LabelShelfVerticalThickness", "zzExpertOnly", "Vertical Thickness of the Label Shelf <br> <br> default = 2 mm").LabelShelfVerticalThickness = LABEL_SHELF_VERTICAL_THICKNESS



    def generate_gridfinity_shape(self, obj):

        ## Calculated Properties

        obj.xTotalWidth = obj.xGridUnits*obj.GridSize-obj.Tolerance*2
        obj.yTotalWidth = obj.yGridUnits*obj.GridSize-obj.Tolerance*2
        obj.BaseProfileHeight = obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection+obj.BaseProfileTopChamfer
        obj.StackingLipTopChamfer = obj.BaseProfileTopChamfer - obj.Tolerance - obj.StackingLipTopLedge
        obj.BinUnit = obj.GridSize - TOLERANCE*2*unitmm

        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight
        else:
            obj.TotalHeight = obj.HeightUnits*obj.HeightUnitValue
        obj.UsableHeight = obj.TotalHeight - obj.HeightUnitValue

        ## Error Checking

        # Divider Minimum Height
        divmin = obj.HeightUnitValue + obj.InsideFilletRadius + 0.05*unitmm
        if obj.xDividerHeight < divmin and obj.xDividerHeight != 0:
            obj.xDividerHeight = divmin
            App.Console.PrintWarning("Divider Height must be equal to or greater than:  ")
            App.Console.PrintWarning(divmin)
            App.Console.PrintWarning("\n")

        if obj.yDividerHeight < divmin and obj.yDividerHeight != 0:
            obj.yDividerHeight = divmin
            App.Console.PrintWarning("Divider Height must be equal to or greater than:  ")
            App.Console.PrintWarning(divmin)
            App.Console.PrintWarning("\n")

        if obj.xDividerHeight < obj.TotalHeight and obj.LabelShelfStyle != "Off" and obj.xDividerHeight != 0 and obj.xDividers != 0:
            obj.LabelShelfStyle = "Off"
            App.Console.PrintWarning("Label Shelf turned off for less than full height x dividers")

        ## Bin Construction

        fuse_total = MakeBinBase(self, obj)

        solid_center= RoundedRectangleExtrude(obj.xTotalWidth, obj.yTotalWidth, -obj.TotalHeight+obj.BaseProfileHeight, obj.TotalHeight-obj.BaseProfileHeight, obj.BinOuterRadius)
        solid_center.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))
        fuse_total = fuse_total.fuse(solid_center)

        compartements = MakeCompartements(self, obj)

        fuse_total = fuse_total.cut(compartements)

        if obj.StackingLip:
            stacking_lip = MakeStackingLip(self, obj)
            fuse_total = Part.Shape.fuse(stacking_lip,fuse_total)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = MakeBottomHoles(self, obj)
            fuse_total = Part.Shape.cut(fuse_total, holes)

        if obj.LabelShelfStyle != "Off":
            label_shelf = MakeLabelShelf(self, obj)
            fuse_total = fuse_total.fuse(label_shelf)

        if obj.Scoop:
            scoop = MakeScoop(self, obj)
            fuse_total = fuse_total.fuse(scoop)

        fuse_total = Part.Solid.removeSplitter(fuse_total)

        return fuse_total


    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

class Baseplate(FoundationGridfinity):


    def __init__(self, obj):
        super(Baseplate, self).__init__(obj)

        obj.addProperty("App::PropertyPythonObject",
                        "Bin", "base", "python gridfinity object")

        self.add_bin_properties(obj)
        self.add_reference_properties(obj)
        self.add_expert_properties(obj)


        obj.Proxy = self

    def add_bin_properties(self, obj):

        obj.addProperty("App::PropertyInteger","xGridUnits","Gridfinity","Length of the edges of the outline").xGridUnits=2
        obj.addProperty("App::PropertyInteger","yGridUnits","Gridfinity","Height of the extrusion").yGridUnits=2

    def add_reference_properties(self, obj):
        obj.addProperty("App::PropertyLength","xTotalWidth","ReferenceDimensions","total width of bin in x direction", 1)
        obj.addProperty("App::PropertyLength","yTotalWidth","ReferenceDimensions","total width of bin in y direction", 1)
        obj.addProperty("App::PropertyLength","TotalHeight","ReferenceDimensions","total height of the bin", 1)
        obj.addProperty("App::PropertyLength","BaseProfileHeight","ReferenceDimensions","Height of the Gridfinity Base Profile", 1)

    def add_expert_properties(self, obj):
        obj.addProperty("App::PropertyLength","BaseProfileBottomChamfer", "zzExpertOnly", "height of chamfer in bottom of bin                                                                                                         base profile <br> <br> default = 0.8 mm",1).BaseProfileBottomChamfer=BASEPLATE_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","BaseProfileVerticalSection", "zzExpertOnly", "Height of the vertical section in bin base profile",1).BaseProfileVerticalSection=BASEPLATE_VERTICAL_SECTION
        obj.addProperty("App::PropertyLength","BaseProfileTopChamfer", "zzExpertOnly", "Height of the top chamfer in the bin base profile",1).BaseProfileTopChamfer=BASEPLATE_TOP_CHAMFER
        obj.addProperty("App::PropertyLength","BaseplateProfileTotalHeight", "zzExpertOnly", "Height of the bin base profile",1)
        obj.addProperty("App::PropertyLength","GridSize", "zzExpertOnly", "Size of the Grid").GridSize = GRID_SIZE
        obj.addProperty("App::PropertyLength","HeightUnitValue", "zzExpertOnly", "height per unit, default is 7mm",1).HeightUnitValue = 7
        obj.addProperty("App::PropertyLength","BinOuterRadius", "zzExpertOnly", "Outer radius of the baseplate",1).BinOuterRadius = BASEPLATE_OUTER_RADIUS
        obj.addProperty("App::PropertyLength","BinVerticalRadius", "zzExpertOnly", "Radius of the baseplate profile Vertical section",1).BinVerticalRadius = BASEPLATE_VERTICAL_RADIUS
        obj.addProperty("App::PropertyLength","BinBottomRadius", "zzExpertOnly", "bottom of baseplate corner radius",1).BinBottomRadius = BASEPLATE_BOTTOM_RADIUS
        obj.addProperty("App::PropertyLength","BaseplateTopLedgeWidth", "zzExpertOnly", "Top ledge of baseplate",1).BaseplateTopLedgeWidth = BASEPLATE_TOP_LEDGE_WIDTH
        obj.addProperty("App::PropertyLength","BinUnit", "zzExpertOnly", "Width of a single bin unit",2).BinUnit = BIN_UNIT
        obj.addProperty("App::PropertyLength","Tolerance", "zzExpertOnly", "The tolerance on each side of a bin between before the edge of the grid <br> <br> default = 0.25 mm",1).Tolerance = TOLERANCE
        obj.addProperty("App::PropertyLength","MagnetHoleDistanceFromEdge", "zzExpertOnly", "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",1).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE

    def generate_gridfinity_shape(self, obj):

        obj.xTotalWidth = obj.xGridUnits*obj.GridSize
        obj.yTotalWidth = obj.yGridUnits*obj.GridSize
        obj.BaseProfileHeight = obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection+obj.BaseProfileTopChamfer
        obj.TotalHeight = obj.BaseProfileHeight
        obj.BinUnit = obj.GridSize - obj.BaseplateTopLedgeWidth *2

        fuse_total = MakeBinBase(self, obj)
        solid_center= RoundedRectangleExtrude(obj.xTotalWidth, obj.yTotalWidth, -obj.TotalHeight, obj.TotalHeight, obj.BinOuterRadius)
        solid_center.translate(App.Vector(obj.xTotalWidth/2-obj.GridSize/2,obj.yTotalWidth/2-obj.GridSize/2,0))
        fuse_total = Part.Shape.cut(solid_center, fuse_total)

        return fuse_total

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

class MagnetBaseplate(FoundationGridfinity):

    def __init__(self, obj):
        super(MagnetBaseplate, self).__init__(obj)

        obj.addProperty("App::PropertyPythonObject",
                        "Bin", "base", "python gridfinity object")

        self.add_bin_properties(obj)
        self.add_reference_properties(obj)
        self.add_expert_properties(obj)
        self.add_custom_baseplate_properties(obj)
        self.add_hidded_properties(obj)


        obj.Proxy = self

    def add_bin_properties(self, obj):

        obj.addProperty("App::PropertyInteger","xGridUnits","Gridfinity","Length of the edges of the outline").xGridUnits=2
        obj.addProperty("App::PropertyInteger","yGridUnits","Gridfinity","Height of the extrusion").yGridUnits=2
        obj.addProperty("App::PropertyBool","MagnetHoles","Gridfinity","MagnetHoles").MagnetHoles = True


    def add_reference_properties(self, obj):
        obj.addProperty("App::PropertyLength","xTotalWidth","ReferenceDimensions","total width of bin in x direction", 1)
        obj.addProperty("App::PropertyLength","yTotalWidth","ReferenceDimensions","total width of bin in y direction", 1)
        obj.addProperty("App::PropertyLength","TotalHeight","ReferenceDimensions","total height of the baseplate", 1)
        obj.addProperty("App::PropertyLength","BaseProfileHeight","ReferenceDimensions","Height of the Gridfinity Base Profile", 1)


    def add_custom_baseplate_properties(self, obj):
        obj.addProperty("App::PropertyLength","SmallFillet","NonStandard","Small fillet on iside of baseplate <br> <br> default = 1 mm").SmallFillet = BASEPLATE_SMALL_FILLET
        obj.addProperty("App::PropertyLength","MagnetHoleDiameter", "NonStandard", "Diameter of Magnet Holes <br> <br> default = 6.5 mm").MagnetHoleDiameter = MAGNET_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","MagnetHoleDepth", "NonStandard", "Depth of Magnet Holes <br> <br> default = 2.4 mm").MagnetHoleDepth = MAGNET_HOLE_DEPTH
        obj.addProperty("App::PropertyLength","MagnetEdgeThickness", "NonStandard", "Thickness of edge holding magnets in place <br> <br> default = 1.2 mm").MagnetEdgeThickness = MAGNET_EDGE_THICKNESS
        obj.addProperty("App::PropertyLength","MagnetBase", "NonStandard", "Thickness of base under the magnets <br> <br> default = 0.4 mm").MagnetBase = MAGNET_BASE
        obj.addProperty("App::PropertyLength","MagnetBaseHole", "NonStandard", "Diameter of the hole at the bottom of the magnet cutout <br> <br> default = 3 mm").MagnetBaseHole = MAGNET_BASE_HOLE
        obj.addProperty("App::PropertyLength","MagnetChamfer", "NonStandard", "Chamfer at top of magnet hole <br> <br> default = 0.4 mm").MagnetChamfer = MAGNET_CHAMFER

    def add_expert_properties(self, obj):
        obj.addProperty("App::PropertyLength","BaseProfileBottomChamfer", "zzExpertOnly", "height of chamfer in bottom of bin                                                                                                         base profile <br> <br> default = 0.8 mm",1).BaseProfileBottomChamfer=BASEPLATE_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","BaseProfileVerticalSection", "zzExpertOnly", "Height of the vertical section in bin base profile",1).BaseProfileVerticalSection=BASEPLATE_VERTICAL_SECTION
        obj.addProperty("App::PropertyLength","BaseProfileTopChamfer", "zzExpertOnly", "Height of the top chamfer in the bin base profile",1).BaseProfileTopChamfer=BASEPLATE_TOP_CHAMFER
        obj.addProperty("App::PropertyLength","BaseplateProfileTotalHeight", "zzExpertOnly", "Height of the bin base profile",1)
        obj.addProperty("App::PropertyLength","GridSize", "zzExpertOnly", "Size of the Grid").GridSize = GRID_SIZE
        obj.addProperty("App::PropertyLength","HeightUnitValue", "zzExpertOnly", "height per unit, default is 7mm",1).HeightUnitValue = 7
        obj.addProperty("App::PropertyLength","BinOuterRadius", "zzExpertOnly", "Outer radius of the baseplate",1).BinOuterRadius = BASEPLATE_OUTER_RADIUS
        obj.addProperty("App::PropertyLength","BinVerticalRadius", "zzExpertOnly", "Radius of the baseplate profile Vertical section",1).BinVerticalRadius = BASEPLATE_VERTICAL_RADIUS
        obj.addProperty("App::PropertyLength","BinBottomRadius", "zzExpertOnly", "bottom of baseplate corner radius",1).BinBottomRadius = BASEPLATE_BOTTOM_RADIUS
        obj.addProperty("App::PropertyLength","BaseplateTopLedgeWidth", "zzExpertOnly", "Top ledge of baseplate",1).BaseplateTopLedgeWidth = BASEPLATE_TOP_LEDGE_WIDTH
        obj.addProperty("App::PropertyLength","BinUnit", "zzExpertOnly", "Width of a single bin unit",2).BinUnit = BIN_UNIT
        obj.addProperty("App::PropertyLength","Tolerance", "zzExpertOnly", "The tolerance on each side of a bin between before the edge of the grid <br> <br> default = 0.25 mm",1).Tolerance = TOLERANCE
        obj.addProperty("App::PropertyLength","MagnetHoleDistanceFromEdge", "zzExpertOnly", "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",1).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE

    def add_hidded_properties(self,obj):
        obj.addProperty("App::PropertyLength","BaseThickness", "NonStandard", "Thickness of base under the normal baseplate  profile <br> <br> default = 6.4 mm").BaseThickness = BASE_THICKNESS
        obj.setEditorMode("BaseThickness",2)

    def generate_gridfinity_shape(self, obj):

        obj.xTotalWidth = obj.xGridUnits*obj.GridSize
        obj.yTotalWidth = obj.yGridUnits*obj.GridSize


        #Bottom of Bin placement, used for ability to reuse previous features.
        obj.BaseProfileHeight = obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection+obj.BaseProfileTopChamfer

        #actaully the total height of the baseplate
        obj.TotalHeight = obj.BaseProfileHeight + obj.MagnetHoleDepth + obj.MagnetBase

        obj.BinUnit = obj.GridSize - obj.BaseplateTopLedgeWidth *2

        fuse_total = MakeBinBase(self, obj)
        fuse_total.translate(App.Vector(0,0,obj.TotalHeight - obj.BaseProfileHeight))

        solid_center= RoundedRectangleExtrude(obj.xTotalWidth, obj.yTotalWidth, -obj.TotalHeight, obj.TotalHeight, obj.BinOuterRadius)
        solid_center.translate(App.Vector(obj.xTotalWidth/2-obj.GridSize/2,obj.yTotalWidth/2-obj.GridSize/2,0))
        fuse_total = Part.Shape.cut(solid_center, fuse_total)

        cutout = MakeBaseplateCenterCut(self, obj)
        fuse_total = Part.Shape.cut(fuse_total, cutout)

        magholes = MakeBaseplateMagnetHoles(self, obj)
        fuse_total = Part.Shape.cut(fuse_total, magholes)

        return fuse_total

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

class ScrewTogetherBaseplate(FoundationGridfinity):

    def __init__(self, obj):
        super(ScrewTogetherBaseplate, self).__init__(obj)

        obj.addProperty("App::PropertyPythonObject",
                        "Bin", "base", "python gridfinity object")

        self.add_bin_properties(obj)
        self.add_reference_properties(obj)
        self.add_expert_properties(obj)
        self.add_custom_baseplate_properties(obj)


        obj.Proxy = self

    def add_bin_properties(self, obj):

        obj.addProperty("App::PropertyInteger","xGridUnits","Gridfinity","Length of the edges of the outline").xGridUnits=2
        obj.addProperty("App::PropertyInteger","yGridUnits","Gridfinity","Height of the extrusion").yGridUnits=2


    def add_reference_properties(self, obj):
        obj.addProperty("App::PropertyLength","xTotalWidth","ReferenceDimensions","total width of bin in x direction", 1)
        obj.addProperty("App::PropertyLength","yTotalWidth","ReferenceDimensions","total width of bin in y direction", 1)
        obj.addProperty("App::PropertyLength","TotalHeight","ReferenceDimensions","total height of the baseplate", 1)
        obj.addProperty("App::PropertyLength","BaseProfileHeight","ReferenceDimensions","Height of the Gridfinity Base Profile", 1)


    def add_custom_baseplate_properties(self, obj):
        obj.addProperty("App::PropertyLength","SmallFillet","NonStandard","Small fillet on iside of baseplate <br> <br> default = 1 mm").SmallFillet = BASEPLATE_SMALL_FILLET
        obj.addProperty("App::PropertyLength","MagnetHoleDiameter", "NonStandard", "Diameter of Magnet Holes <br> <br> default = 6.5 mm").MagnetHoleDiameter = MAGNET_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","MagnetHoleDepth", "NonStandard", "Depth of Magnet Holes <br> <br> default = 2.4 mm").MagnetHoleDepth = MAGNET_HOLE_DEPTH
        obj.addProperty("App::PropertyLength","MagnetEdgeThickness", "NonStandard", "Thickness of edge holding magnets in place <br> <br> default = 1.2 mm").MagnetEdgeThickness = MAGNET_EDGE_THICKNESS
        obj.addProperty("App::PropertyLength","BaseThickness", "NonStandard", "Thickness of base under the normal baseplate  profile <br> <br> default = 6.4 mm").BaseThickness = BASE_THICKNESS
        obj.addProperty("App::PropertyLength","MagnetBaseHole", "NonStandard", "Diameter of the hole at the bottom of the magnet cutout <br> <br> default = 3 mm").MagnetBaseHole = MAGNET_BASE_HOLE
        obj.addProperty("App::PropertyLength","MagnetChamfer", "NonStandard", "Chamfer at top of magnet hole <br> <br> default = 0.4 mm").MagnetChamfer = MAGNET_CHAMFER
        obj.addProperty("App::PropertyLength","MagnetBottomChamfer", "NonStandard", "Chamfer at bottom of magnet hole <br> <br> default = 2 mm").MagnetBottomChamfer = MAGNET_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","ScrewHoleDiameter", "NonStandard", "Diameter of screw holes inside magnet holes <br> <br> default = 3 mm").ScrewHoleDiameter =  SCREW_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","ConnectionHoleDiameter", "NonStandard", "Holes on the sides to connect multiple baseplates together <br> <br> default = 3.2 mm").ConnectionHoleDiameter = CONNECTION_HOLE_DIAMETER

    def add_expert_properties(self, obj):
        obj.addProperty("App::PropertyLength","BaseProfileBottomChamfer", "zzExpertOnly", "height of chamfer in bottom of bin                                                                                                         base profile <br> <br> default = 0.8 mm",1).BaseProfileBottomChamfer=BASEPLATE_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","BaseProfileVerticalSection", "zzExpertOnly", "Height of the vertical section in bin base profile",1).BaseProfileVerticalSection=BASEPLATE_VERTICAL_SECTION
        obj.addProperty("App::PropertyLength","BaseProfileTopChamfer", "zzExpertOnly", "Height of the top chamfer in the bin base profile",1).BaseProfileTopChamfer=BASEPLATE_TOP_CHAMFER
        obj.addProperty("App::PropertyLength","BaseplateProfileTotalHeight", "zzExpertOnly", "Height of the bin base profile",1)
        obj.addProperty("App::PropertyLength","GridSize", "zzExpertOnly", "Size of the Grid").GridSize = GRID_SIZE
        obj.addProperty("App::PropertyLength","HeightUnitValue", "zzExpertOnly", "height per unit, default is 7mm",1).HeightUnitValue = 7
        obj.addProperty("App::PropertyLength","BinOuterRadius", "zzExpertOnly", "Outer radius of the baseplate",1).BinOuterRadius = BASEPLATE_OUTER_RADIUS
        obj.addProperty("App::PropertyLength","BinVerticalRadius", "zzExpertOnly", "Radius of the baseplate profile Vertical section",1).BinVerticalRadius = BASEPLATE_VERTICAL_RADIUS
        obj.addProperty("App::PropertyLength","BinBottomRadius", "zzExpertOnly", "bottom of baseplate corner radius",1).BinBottomRadius = BASEPLATE_BOTTOM_RADIUS
        obj.addProperty("App::PropertyLength","BaseplateTopLedgeWidth", "zzExpertOnly", "Top ledge of baseplate",1).BaseplateTopLedgeWidth = BASEPLATE_TOP_LEDGE_WIDTH
        obj.addProperty("App::PropertyLength","BinUnit", "zzExpertOnly", "Width of a single bin unit",2).BinUnit = BIN_UNIT
        obj.addProperty("App::PropertyLength","Tolerance", "zzExpertOnly", "The tolerance on each side of a bin between before the edge of the grid <br> <br> default = 0.25 mm").Tolerance = TOLERANCE
        obj.addProperty("App::PropertyLength","MagnetHoleDistanceFromEdge", "zzExpertOnly", "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm").MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE


    def generate_gridfinity_shape(self, obj):

        obj.xTotalWidth = obj.xGridUnits*obj.GridSize
        obj.yTotalWidth = obj.yGridUnits*obj.GridSize

        #Bottom of Bin placement, used for ability to reuse previous features.
        obj.BaseProfileHeight = obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection+obj.BaseProfileTopChamfer

        #actaully the total height of the baseplate
        obj.TotalHeight = obj.BaseProfileHeight + obj.BaseThickness

        obj.BinUnit = obj.GridSize - obj.BaseplateTopLedgeWidth *2

        fuse_total = MakeBinBase(self, obj)
        fuse_total.translate(App.Vector(0,0,obj.TotalHeight - obj.BaseProfileHeight))

        solid_center= RoundedRectangleExtrude(obj.xTotalWidth, obj.yTotalWidth, -obj.TotalHeight, obj.TotalHeight, obj.BinOuterRadius)
        solid_center.translate(App.Vector(obj.xTotalWidth/2-obj.GridSize/2,obj.yTotalWidth/2-obj.GridSize/2,0))
        fuse_total = Part.Shape.cut(solid_center, fuse_total)

        cutout = MakeBaseplateCenterCut(self, obj)
        fuse_total = Part.Shape.cut(fuse_total, cutout)

        magholes = MakeBaseplateMagnetHoles(self, obj)
        fuse_total = Part.Shape.cut(fuse_total, magholes)

        magchamfer = MakeBPScrewBottomCham(self, obj)
        fuse_total = Part.Shape.cut(fuse_total, magchamfer)

        conholes = MakeBPConnectionHoles(self, obj)
        fuse_total = Part.Shape.cut(fuse_total, conholes)

        return fuse_total

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

