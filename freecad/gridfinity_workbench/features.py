from __future__ import division
import os
import numpy as np
import math
import FreeCAD as App
import Part
from .feature_construction import MakeStackingLip, MakeBinBase, RoundedRectangleExtrude, MakeBottomHoles
from Part import Shape, Wire, Face, makeLoft, BSplineSurface, \
    makePolygon, makeHelix, makeShell, makeSolid, LineSegment
from .const import BIN_BASE_TOP_CHAMFER, BIN_BASE_BOTTOM_CHAMFER, BIN_BASE_VERTICAL_SECTION, GRID_SIZE, BIN_OUTER_RADIUS, BIN_UNIT, BIN_BASE_VERTICAL_RADIUS, BIN_BASE_BOTTOM_RADIUS, TOLERANCE, MAGNET_HOLE_DIAMETER, MAGNET_HOLE_DEPTH, MAGNET_HOLE_DISTANCE_FROM_EDGE, SCREW_HOLE_DIAMETER, SCREW_HOLE_DEPTH, BASEPLATE_BOTTOM_CHAMFER, BASEPLATE_VERTICAL_SECTION, BASEPLATE_TOP_CHAMFER, BASEPLATE_TOP_LEDGE_WIDTH, BASEPLATE_OUTER_RADIUS, BASEPLATE_VERTICAL_RADIUS, BASEPLATE_BOTTOM_RADIUS


__version__ = "0.0.1"

__all__ = ["BinBlank",
           "SimpleStorageBin",
           "Baseplate"]


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
        if hasattr(fp, "BaseFeature") and fp.BaseFeature != None:
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
        obj.addProperty("App::PropertyLength","MagnetHoleDiameter", "zzExpertOnly", "Diameter of Magnet Holes <br> <br> default = 6.5 mm").MagnetHoleDiameter = MAGNET_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","MagnetHoleDepth", "zzExpertOnly", "Depth of Magnet Holes <br> <br> default = 2.4 mm").MagnetHoleDepth = MAGNET_HOLE_DEPTH
        obj.addProperty("App::PropertyLength","ScrewHoleDiameter", "zzExpertOnly", "Diameter of Screw Holes <br> <br> default = 3.0 mm").ScrewHoleDiameter = SCREW_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","ScrewHoleDepth", "zzExpertOnly", "Depth of Screw Holes <br> <br> default = 6.0 mm").ScrewHoleDepth = SCREW_HOLE_DEPTH

    def add_reference_properties(self, obj):
        obj.addProperty("App::PropertyLength","xTotalWidth","ReferenceDimensions","total width of bin in x direction", 1)
        obj.addProperty("App::PropertyLength","yTotalWidth","ReferenceDimensions","total width of bin in y direction", 1)
        obj.addProperty("App::PropertyLength","TotalHeight","ReferenceDimensions","total height of the bin", 1)
        obj.addProperty("App::PropertyLength","BaseProfileHeight","ReferenceDimensions","Height of the Gridfinity Base Profile", 1)

    def add_expert_properties(self, obj):
        obj.addProperty("App::PropertyLength","BaseProfileBottomChamfer", "zzExpertOnly", "height of chamfer in bottom of bin                                                                                                         base profile <br> <br> default = 0.8 mm",1).BaseProfileBottomChamfer=BIN_BASE_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","BaseProfileVerticalSection", "zzExpertOnly", "Height of the vertical section in bin base profile",1).BaseProfileVerticalSection=BIN_BASE_VERTICAL_SECTION
        obj.addProperty("App::PropertyLength","BaseProfileTopChamfer", "zzExpertOnly", "Height of the top chamfer in the bin base profile",1).BaseProfileTopChamfer=BIN_BASE_TOP_CHAMFER
        obj.addProperty("App::PropertyLength","BaseProfileTotalHeight", "zzExpertOnly", "Height of the bin base profile",1)
        obj.addProperty("App::PropertyLength","GridSize", "zzExpertOnly", "Size of the Grid").GridSize = GRID_SIZE
        obj.addProperty("App::PropertyLength","HeightUnitValue", "zzExpertOnly", "height per unit, default is 7mm",1).HeightUnitValue = 7
        obj.addProperty("App::PropertyLength","BinOuterRadius", "zzExpertOnly", "Outer radius of the bin",1).BinOuterRadius = BIN_OUTER_RADIUS
        obj.addProperty("App::PropertyLength","BinVerticalRadius", "zzExpertOnly", "Radius of the base profile Vertical section",1).BinVerticalRadius = BIN_BASE_VERTICAL_RADIUS
        obj.addProperty("App::PropertyLength","BinBottomRadius", "zzExpertOnly", "bottom of bin corner radius",1).BinBottomRadius = BIN_BASE_BOTTOM_RADIUS
        obj.addProperty("App::PropertyLength","BinUnit", "zzExpertOnly", "Width of a single bin unit",1).BinUnit = BIN_UNIT
        obj.addProperty("App::PropertyLength","Tolerance", "zzExpertOnly", "The tolerance on each side of a bin between before the edge of the grid <br> <br> default = 0.25 mm",1).Tolerance = TOLERANCE
        obj.addProperty("App::PropertyLength","MagnetHoleDistanceFromEdge", "zzExpertOnly", "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",1).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE



    def generate_gridfinity_shape(self, obj):

        obj.xTotalWidth = obj.xGridUnits*obj.GridSize
        obj.yTotalWidth = obj.yGridUnits*obj.GridSize
        obj.BaseProfileHeight = obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection+obj.BaseProfileTopChamfer

        if obj.NonStandardHeight ==True:
            obj.TotalHeight = obj.CustomHeight
        else:
            obj.TotalHeight = obj.HeightUnits*obj.HeightUnitValue


        fuse_total = MakeBinBase(self, obj)
        solid_center= RoundedRectangleExtrude(obj.xTotalWidth, obj.yTotalWidth, -obj.TotalHeight+obj.BaseProfileHeight, obj.TotalHeight-obj.BaseProfileHeight, obj.BinOuterRadius)
        solid_center.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))

        fuse_total = Part.Shape.fuse(fuse_total, solid_center )

        if obj.StackingLip == True:
            stacking_lip = MakeStackingLip(self, obj)
            fuse_total = Part.Shape.fuse(stacking_lip,fuse_total)

        holes = MakeBottomHoles(self, obj)
        fuse_total = Part.Shape.cut(fuse_total, holes)

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
        obj.addProperty("App::PropertyInteger","HeightUnits","Gridfinity","height of the bin in units, each is 7 mm").HeightUnits=6
        obj.addProperty("App::PropertyBool","StackingLip","Gridfinity","Toggle the stacking lip on or off").StackingLip=True
        obj.addProperty("App::PropertyBool","MagnetHoles","Gridfinity","Toggle the magnet holes on or off").MagnetHoles = True
        obj.addProperty("App::PropertyBool","ScrewHoles","Gridfinity","Toggle the screw holes on or off").ScrewHoles = True


    def add_custom_bin_properties(self, obj):
        obj.addProperty("App::PropertyLength","CustomHeight","GridfinityNonStandard","total height of the bin using the custom heignt instead of incraments of 7 mm").CustomHeight = 42
        obj.addProperty("App::PropertyLength","SequentialBridgingLayerHeight","GridfinityNonStandard","Layer Height that you print in for optimal print results").SequentialBridgingLayerHeight = 0.2
        obj.addProperty("App::PropertyBool","NonStandardHeight","GridfinityNonStandard","use a custom height if selected").NonStandardHeight=False
        obj.addProperty("App::PropertyLength","MagnetHoleDiameter", "zzExpertOnly", "Diameter of Magnet Holes <br> <br> default = 6.5 mm").MagnetHoleDiameter = MAGNET_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","MagnetHoleDepth", "zzExpertOnly", "Depth of Magnet Holes <br> <br> default = 2.4 mm").MagnetHoleDepth = MAGNET_HOLE_DEPTH
        obj.addProperty("App::PropertyLength","ScrewHoleDiameter", "zzExpertOnly", "Diameter of Screw Holes <br> <br> default = 3.0 mm").ScrewHoleDiameter = SCREW_HOLE_DIAMETER
        obj.addProperty("App::PropertyLength","ScrewHoleDepth", "zzExpertOnly", "Depth of Screw Holes <br> <br> default = 6.0 mm").ScrewHoleDepth = SCREW_HOLE_DEPTH

    def add_reference_properties(self, obj):
        obj.addProperty("App::PropertyLength","xTotalWidth","ReferenceDimensions","total width of bin in x direction", 1)
        obj.addProperty("App::PropertyLength","yTotalWidth","ReferenceDimensions","total width of bin in y direction", 1)
        obj.addProperty("App::PropertyLength","TotalHeight","ReferenceDimensions","total height of the bin", 1)
        obj.addProperty("App::PropertyLength","BaseProfileHeight","ReferenceDimensions","Height of the Gridfinity Base Profile", 1)

    def add_expert_properties(self, obj):
        obj.addProperty("App::PropertyLength","BaseProfileBottomChamfer", "zzExpertOnly", "height of chamfer in bottom of bin                                                                                                         base profile <br> <br> default = 0.8 mm",1).BaseProfileBottomChamfer=BIN_BASE_BOTTOM_CHAMFER
        obj.addProperty("App::PropertyLength","BaseProfileVerticalSection", "zzExpertOnly", "Height of the vertical section in bin base profile",1).BaseProfileVerticalSection=BIN_BASE_VERTICAL_SECTION
        obj.addProperty("App::PropertyLength","BaseProfileTopChamfer", "zzExpertOnly", "Height of the top chamfer in the bin base profile",1).BaseProfileTopChamfer=BIN_BASE_TOP_CHAMFER
        obj.addProperty("App::PropertyLength","BaseProfileTotalHeight", "zzExpertOnly", "Height of the bin base profile",1)
        obj.addProperty("App::PropertyLength","GridSize", "zzExpertOnly", "Size of the Grid").GridSize = GRID_SIZE
        obj.addProperty("App::PropertyLength","HeightUnitValue", "zzExpertOnly", "height per unit, default is 7mm",1).HeightUnitValue = 7
        obj.addProperty("App::PropertyLength","BinOuterRadius", "zzExpertOnly", "Outer radius of the bin",1).BinOuterRadius = BIN_OUTER_RADIUS
        obj.addProperty("App::PropertyLength","BinVerticalRadius", "zzExpertOnly", "Radius of the base profile Vertical section",1).BinVerticalRadius = BIN_BASE_VERTICAL_RADIUS
        obj.addProperty("App::PropertyLength","BinBottomRadius", "zzExpertOnly", "bottom of bin corner radius",1).BinBottomRadius = BIN_BASE_BOTTOM_RADIUS
        obj.addProperty("App::PropertyLength","BinUnit", "zzExpertOnly", "Width of a single bin unit",1).BinUnit = BIN_UNIT
        obj.addProperty("App::PropertyLength","Tolerance", "zzExpertOnly", "The tolerance on each side of a bin between before the edge of the grid <br> <br> default = 0.25 mm",1).Tolerance = TOLERANCE
        obj.addProperty("App::PropertyLength","MagnetHoleDistanceFromEdge", "zzExpertOnly", "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",1).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE



    def generate_gridfinity_shape(self, obj):

        obj.xTotalWidth = obj.xGridUnits*obj.GridSize
        obj.yTotalWidth = obj.yGridUnits*obj.GridSize
        obj.BaseProfileHeight = obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection+obj.BaseProfileTopChamfer

        if obj.NonStandardHeight ==True:
            obj.TotalHeight = obj.CustomHeight
        else:
            obj.TotalHeight = obj.HeightUnits*obj.HeightUnitValue

        #gridfinity_part = FunctionBinBase(self, obj)

        fuse_total = MakeBinBase(self, obj)
        solid_center= RoundedRectangleExtrude(obj.xTotalWidth, obj.yTotalWidth, -obj.TotalHeight+obj.BaseProfileHeight, obj.TotalHeight-obj.BaseProfileHeight, obj.BinOuterRadius)
        solid_center.translate(App.Vector(obj.xTotalWidth/2-obj.BinUnit/2,obj.yTotalWidth/2-obj.BinUnit/2,0))

        fuse_total = Part.Shape.fuse(fuse_total, solid_center )

        if obj.StackingLip == True:
            stacking_lip = MakeStackingLip(self, obj)
            fuse_total = Part.Shape.fuse(stacking_lip,fuse_total)

        holes = MakeBottomHoles(self, obj)
        fuse_total = Part.Shape.cut(fuse_total, holes)
        #fuse_total = Part.Shape.fuse(fuse_total, holes)

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
        obj.addProperty("App::PropertyLength","BinUnit", "zzExpertOnly", "Width of a single bin unit",1).BinUnit = BIN_UNIT
        obj.addProperty("App::PropertyLength","Tolerance", "zzExpertOnly", "The tolerance on each side of a bin between before the edge of the grid <br> <br> default = 0.25 mm",1).Tolerance = TOLERANCE
        obj.addProperty("App::PropertyLength","MagnetHoleDistanceFromEdge", "zzExpertOnly", "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",1).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE

    def generate_gridfinity_shape(self, obj):

        obj.xTotalWidth = obj.xGridUnits*obj.GridSize
        obj.yTotalWidth = obj.yGridUnits*obj.GridSize
        obj.BaseProfileHeight = obj.BaseProfileBottomChamfer+obj.BaseProfileVerticalSection+obj.BaseProfileTopChamfer
        obj.TotalHeight = obj.BaseProfileHeight
        obj.BinUnit = obj.BinUnit - obj.BaseplateTopLedgeWidth *2 + obj.Tolerance*2

        fuse_total = MakeBinBase(self, obj)
        solid_center= RoundedRectangleExtrude(obj.xTotalWidth, obj.yTotalWidth, -obj.TotalHeight, obj.TotalHeight, obj.BinOuterRadius)
        solid_center.translate(App.Vector(obj.xTotalWidth/2-obj.GridSize/2,obj.yTotalWidth/2-obj.GridSize/2,0))
        fuse_total = Part.Shape.cut(solid_center, fuse_total)

        return fuse_total

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
