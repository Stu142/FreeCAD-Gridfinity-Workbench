"""Feature modules contain bins an baseplate objects."""

from abc import abstractmethod

import FreeCAD
import Part
from FreeCAD import Units

from .baseplate_feature_construction import (
    BaseplateConnectionHoles,
    BaseplateScrewBottomChamfer,
    BaseplateCenterCut,
    BaseplateBaseValues,
    BaseplateSolidShape,
    BaseplateMagnetHoles,
)
from .const import (
    BASE_THICKNESS,
    BASEPLATE_BOTTOM_CHAMFER,
    BASEPLATE_BOTTOM_RADIUS,
    BASEPLATE_OUTER_RADIUS,
    BASEPLATE_SMALL_FILLET,
    BASEPLATE_TOP_CHAMFER,
    BASEPLATE_TOP_LEDGE_WIDTH,
    BASEPLATE_VERTICAL_RADIUS,
    BASEPLATE_VERTICAL_SECTION,
    BIN_BASE_BOTTOM_CHAMFER,
    BIN_BASE_BOTTOM_RADIUS,
    BIN_BASE_TOP_CHAMFER,
    BIN_BASE_VERTICAL_RADIUS,
    BIN_BASE_VERTICAL_SECTION,
    BIN_OUTER_RADIUS,
    CLEARANCE,
    CONNECTION_HOLE_DIAMETER,
    GRID_SIZE,
    HEIGHT_UNIT,
    LABEL_SHELF_ANGLE,
    LABEL_SHELF_LENGTH,
    LABEL_SHELF_STACKING_OFFSET,
    LABEL_SHELF_VERTICAL_THICKNESS,
    LABEL_SHELF_WIDTH,
    MAGNET_BASE,
    MAGNET_BASE_HOLE,
    MAGNET_BOTTOM_CHAMFER,
    MAGNET_CHAMFER,
    MAGNET_EDGE_THICKNESS,
    MAGNET_HOLE_DEPTH,
    MAGNET_HOLE_DIAMETER,
    MAGNET_HOLE_DISTANCE_FROM_EDGE,
    SCOOP_RADIUS,
    SCREW_HOLE_DEPTH,
    SCREW_HOLE_DIAMETER,
    STACKING_LIP_BOTTOM_CHAMFER,
    STACKING_LIP_TOP_LEDGE,
    STACKING_LIP_VERTICAL_SECTION,
    ECO_WALL_THICKNESS,
)

from .grid_initial_layout import (
    RectangleLayout,
)

from .feature_construction import (
    make_bin_base,
    make_bottom_holes,
    EcoBinCut,
    Scoop,
    make_stacking_lip,
    Compartments,
    LabelShelf,
)
from .feature_construction_complex_bin import (
    make_complex_bin_base,
    make_l_mid_section,
    BinSolidMidSection,
    BlankBinRecessedTop,
    StackingLip,
    BinBottomHoles,
    BinBaseValues,
)
from .utils import Utils
from .version import __version__

unitmm = Units.Quantity("1 mm")


__all__ = [
    "Baseplate",
    "BinBlank",
    "EcoBin",
    "EcoBin",
    "LBinBlank",
    "MagnetBaseplate",
    "PartsBin",
    "ScrewTogetherBaseplate",
]


HOLE_SHAPES = ["Round", "Hex"]


class FoundationGridfinity:
    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        obj.addProperty(
            "App::PropertyString",
            "version",
            "version",
            "Gridfinity Workbench Version",
            1,
        )

        obj.version = __version__

    def execute(self, fp: Part.Feature) -> None:
        gridfinity_shape = self.generate_gridfinity_shape(fp)

        if hasattr(fp, "BaseFeature") and fp.BaseFeature is not None:
            # we're inside a PartDesign Body, thus need to fuse with the base feature

            gridfinity_shape.Placement = (
                fp.Placement
            )  # ensure the bin is placed correctly before fusing

            result_shape = fp.BaseFeature.Shape.fuse(gridfinity_shape)

            result_shape.transformShape(fp.Placement.inverse().toMatrix(), copy=True)

            fp.Shape = result_shape

        else:
            fp.Shape = gridfinity_shape

    @abstractmethod
    def generate_gridfinity_shape(self, fp: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate the TopoShape of the object."""


class BinBlank(FoundationGridfinity):
    """Gridfinity BinBlank object."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Create BinBlank object.

        Args:
            obj (FreeCAD.DocumentObject): Document object


        """
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )


        self.features = [RectangleLayout(obj),
            BinSolidMidSection(obj),
            BlankBinRecessedTop(obj),
            StackingLip(obj),
            BinBottomHoles(obj),
            BinBaseValues(obj),
        ]

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate BinBlanek Shape.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Bin Blank shape

        """

        BinBaseValues.Make(self, obj)

        layout = RectangleLayout.Make(self, obj)

        bin_outside_shape = Utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        bin_outside_shape.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        bin_inside_shape = Utils.create_rounded_rectangle(
            obj.xTotalWidth - obj.WallThickness * 2,
            obj.yTotalWidth - obj.WallThickness * 2,
            0,
            obj.BinOuterRadius - obj.WallThickness,
        )
        bin_inside_shape.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        fuse_total = BinSolidMidSection.Make(self, obj, bin_outside_shape)

        bin_base = make_complex_bin_base(obj,layout)

        fuse_total = fuse_total.fuse(bin_base)

        if obj.RecessedTopDepth > 0:
            recessed_cut = BlankBinRecessedTop.Make(self, obj, bin_inside_shape)

            fuse_total = fuse_total.cut(recessed_cut)

        if obj.StackingLip:
            stacking_lip = StackingLip.Make(obj, bin_outside_shape)

            fuse_total = fuse_total.fuse(stacking_lip)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = BinBottomHoles.Make(obj, layout)

            fuse_total = Part.Shape.cut(fuse_total, holes)

        return fuse_total


class BinBase(FoundationGridfinity):
    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        self.features = [RectangleLayout(obj),
            BinSolidMidSection(obj, default_height_units = 1),
            BlankBinRecessedTop(obj),
            StackingLip(obj, stacking_lip_default = False),
            BinBottomHoles(obj),
            BinBaseValues(obj),
        ]

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        BinBaseValues.Make(self, obj)

        layout = RectangleLayout.Make(self, obj)

        bin_outside_shape = Utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        bin_outside_shape.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        bin_inside_shape = Utils.create_rounded_rectangle(
            obj.xTotalWidth - obj.WallThickness * 2,
            obj.yTotalWidth - obj.WallThickness * 2,
            0,
            obj.BinOuterRadius - obj.WallThickness,
        )
        bin_inside_shape.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        fuse_total = BinSolidMidSection.Make(self, obj, bin_outside_shape)

        bin_base = make_complex_bin_base(obj,layout)

        fuse_total = fuse_total.fuse(bin_base)

        if obj.RecessedTopDepth > 0:
            recessed_cut = BlankBinRecessedTop.Make(self, obj, bin_inside_shape)

            fuse_total = fuse_total.cut(recessed_cut)

        if obj.StackingLip:
            stacking_lip = StackingLip.Make(obj, bin_outside_shape)

            fuse_total = fuse_total.fuse(stacking_lip)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = BinBottomHoles.Make(obj, layout)

            fuse_total = Part.Shape.cut(fuse_total, holes)

        return fuse_total

class SimpleStorageBin(FoundationGridfinity):
    """Simple Storage Bin."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize Simple storage bin properties.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        self.features = [RectangleLayout(obj),
            BinSolidMidSection(obj),
            StackingLip(obj),
            BinBottomHoles(obj),
            BinBaseValues(obj),
            Compartments(obj, x_div_default = 0, y_div_default = 0),
            LabelShelf(obj, label_style_default = "Off"),
            Scoop(obj, scoop_default = False),
        ]
        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate simple storage bin.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Storage bin shape.

        """

        BinBaseValues.Make(self, obj)

        layout = RectangleLayout.Make(self, obj)

        bin_outside_shape = Utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        bin_outside_shape.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        bin_inside_shape = Utils.create_rounded_rectangle(
            obj.xTotalWidth - obj.WallThickness * 2,
            obj.yTotalWidth - obj.WallThickness * 2,
            0,
            obj.BinOuterRadius - obj.WallThickness,
        )
        bin_inside_shape.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        fuse_total = BinSolidMidSection.Make(self, obj, bin_outside_shape)

        bin_base = make_complex_bin_base(obj,layout)

        fuse_total = fuse_total.fuse(bin_base)

        compartements = Compartments.Make(obj, bin_inside_shape)

        fuse_total = fuse_total.cut(compartements)

        if obj.StackingLip:
            stacking_lip = StackingLip.Make(obj, bin_outside_shape)

            fuse_total = fuse_total.fuse(stacking_lip)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = BinBottomHoles.Make(obj, layout)

            fuse_total = Part.Shape.cut(fuse_total, holes)

        if obj.LabelShelfStyle != "Off":
            label_shelf = LabelShelf.Make(obj)

            fuse_total = fuse_total.fuse(label_shelf)

        if obj.Scoop:
            scoop = Scoop.Make(obj)

            fuse_total = fuse_total.fuse(scoop)

        return Part.Solid.removeSplitter(fuse_total)

class EcoBin(FoundationGridfinity):
    """Eco Bin."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize Eco bin properties."""
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        self.features = [RectangleLayout(obj),
            BinSolidMidSection(obj, default_wall_thickness = 0.8),
            StackingLip(obj),
            BinBottomHoles(obj),
            BinBaseValues(obj),
            LabelShelf(obj),
            EcoBinCut(obj),

        ]

        obj.Proxy = self

        """
        self._add_bin_properties(obj)

        self._add_custom_bin_properties(obj)

        self._add_reference_properties(obj)

        self._add_expert_properties(obj)



    def _add_bin_properties(self, obj: FreeCAD.DocumentObject) -> None:
        obj.addProperty(
            "App::PropertyInteger",
            "xGridUnits",
            "Gridfinity",
            "Length of the edges of the outline",
        ).xGridUnits = 2

        obj.addProperty(
            "App::PropertyInteger",
            "yGridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).yGridUnits = 2

        obj.addProperty(
            "App::PropertyInteger",
            "HeightUnits",
            "Gridfinity",
            "height of the bin in units, each unit is 7 mm",
        ).HeightUnits = 6

        obj.addProperty(
            "App::PropertyBool",
            "StackingLip",
            "Gridfinity",
            "Toggle the stacking lip on or off",
        ).StackingLip = True

        obj.addProperty(
            "App::PropertyBool",
            "MagnetHoles",
            "Gridfinity",
            "Toggle the magnet holes on or off",
        ).MagnetHoles = False





    def _add_custom_bin_properties(self, obj: FreeCAD.DocumentObject) -> None:
        obj.addProperty(
            "App::PropertyLength",
            "CustomHeight",
            "GridfinityNonStandard",
            "total height of the bin using the custom heignt instead of increments of 7 mm",
        ).CustomHeight = 42

        obj.addProperty(
            "App::PropertyLength",
            "SequentialBridgingLayerHeight",
            "GridfinityNonStandard",
            "Layer Height that you print in for optimal print results",
        ).SequentialBridgingLayerHeight = 0.2

        obj.addProperty(
            "App::PropertyBool",
            "NonStandardHeight",
            "GridfinityNonStandard",
            "use a custom height if selected",
        ).NonStandardHeight = False

        obj.addProperty(
            "App::PropertyEnumeration",
            "MagnetHolesShape",
            "GridfinityNonStandard",
            (
                "Shape of magnet holes. <br> <br> Hex meant to be press fit. <br> "
                "Round meant to be glued"
            ),
        )

        obj.MagnetHolesShape = HOLE_SHAPES

        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDiameter",
            "GridfinityNonStandard",
            (
                "Diameter of Magnet Holes <br>For Hex holes, inscribed diameter<br> <br> "
                "default = 6.5 mm"
            ),
        ).MagnetHoleDiameter = MAGNET_HOLE_DIAMETER

        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDepth",
            "GridfinityNonStandard",
            "Depth of Magnet Holes <br> <br> default = 2.4 mm",
        ).MagnetHoleDepth = MAGNET_HOLE_DEPTH

        obj.addProperty(
            "App::PropertyLength",
            "WallThickness",
            "GridfinityNonStandard",
            "Wall thickness of the bin <br> <br> default = 0.8 mm",
        ).WallThickness = 0.8


    def _add_reference_properties(self, obj: FreeCAD.DocumentObject) -> None:
        obj.addProperty(
            "App::PropertyLength",
            "xTotalWidth",
            "ReferenceDimensions",
            "total width of bin in x direction",
            1,
        )

        obj.addProperty(
            "App::PropertyLength",
            "yTotalWidth",
            "ReferenceDimensions",
            "total width of bin in y direction",
            1,
        )

        obj.addProperty(
            "App::PropertyLength",
            "TotalHeight",
            "ReferenceDimensions",
            "total height of the bin",
            1,
        )

        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileHeight",
            "ReferenceDimensions",
            "Height of the Gridfinity Base Profile",
            1,
        )

        obj.addProperty(
            "App::PropertyLength",
            "BinUnit",
            "ReferenceDimensions",
            "Width of a single bin unit",
            1,
        ).BinUnit = BIN_UNIT

    def _add_expert_properties(self, obj: FreeCAD.DocumentObject) -> None:
        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileBottomChamfer",
            "zzExpertOnly",
            "height of chamfer in bottom of bin base profile <br> <br> default = 0.8 mm",
            1,
        ).BaseProfileBottomChamfer = BIN_BASE_BOTTOM_CHAMFER

        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileVerticalSection",
            "zzExpertOnly",
            "Height of the vertical section in bin base profile",
            1,
        ).BaseProfileVerticalSection = BIN_BASE_VERTICAL_SECTION

        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileTopChamfer",
            "zzExpertOnly",
            "Height of the top chamfer in the bin base profile",
            1,
        ).BaseProfileTopChamfer = BIN_BASE_TOP_CHAMFER

        obj.addProperty(
            "App::PropertyLength",
            "GridSize",
            "zzExpertOnly",
            "Size of the Grid",
        ).GridSize = GRID_SIZE

        obj.addProperty(
            "App::PropertyLength",
            "HeightUnitValue",
            "zzExpertOnly",
            "height per unit, default is 7mm",
            1,
        ).HeightUnitValue = HEIGHT_UNIT

        obj.addProperty(
            "App::PropertyLength",
            "BinOuterRadius",
            "zzExpertOnly",
            "Outer radius of the bin",
            1,
        ).BinOuterRadius = BIN_OUTER_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "BinVerticalRadius",
            "zzExpertOnly",
            "Radius of the base profile Vertical section",
            1,
        ).BinVerticalRadius = BIN_BASE_VERTICAL_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "BinBottomRadius",
            "zzExpertOnly",
            "bottom of bin corner radius",
            1,
        ).BinBottomRadius = BIN_BASE_BOTTOM_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "Clearance",
            "zzExpertOnly",
            (
                "The tolerance on each side of a bin between before the edge of the grid <br> <br> "
                "default = 0.25 mm"
            ),
            1,
        ).Clearance = CLEARANCE

        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDistanceFromEdge",
            "zzExpertOnly",
            "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",
            1,
        ).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE

        obj.addProperty(
            "App::PropertyLength",
            "StackingLipTopLedge",
            "zzExpertOnly",
            "Top Ledge of the stacking lip <br> <br> default = 0.4 mm",
            1,
        ).StackingLipTopLedge = STACKING_LIP_TOP_LEDGE

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
        ).StackingLipBottomChamfer = STACKING_LIP_BOTTOM_CHAMFER

        obj.addProperty(
            "App::PropertyLength",
            "StackingLipVerticalSection",
            "zzExpertOnly",
            "vertical section of the Stacking lip<br> <br> default = 1.8 mm",
            1,
        ).StackingLipVerticalSection = STACKING_LIP_VERTICAL_SECTION

        obj.addProperty(
            "App::PropertyBool",
            "ScrewHoles",
            "Gridfinity",
            "Toggle the screw holes on or off",
        ).ScrewHoles = False

        obj.setEditorMode("ScrewHoles", 2)

        obj.addProperty(
            "App::PropertyLength",
            "ScrewHoleDiameter",
            "GridfinityNonStandard",
            "Diameter of Screw Holes <br> <br> default = 3.0 mm",
        ).ScrewHoleDiameter = SCREW_HOLE_DIAMETER

        obj.setEditorMode("ScrewHoleDiameter", 2)

        obj.addProperty(
            "App::PropertyLength",
            "ScrewHoleDepth",
            "GridfinityNonStandard",
            "Depth of Screw Holes <br> <br> default = 6.0 mm",
        ).ScrewHoleDepth = SCREW_HOLE_DEPTH

        obj.setEditorMode("ScrewHoleDepth", 2)

        """
    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Create gridfinity EcoBin shape.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject.

        Returns:
            Part.Shape: EcoBin shape.

        """

        """
        ## Parameter Calculation

        obj.xTotalWidth = obj.xGridUnits * obj.GridSize - obj.Clearance * 2

        obj.yTotalWidth = obj.yGridUnits * obj.GridSize - obj.Clearance * 2

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )

        obj.StackingLipTopChamfer = (
            obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
        )

        obj.BinUnit = obj.GridSize - CLEARANCE * 2 * unitmm

        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight

        else:
            obj.TotalHeight = obj.HeightUnits * obj.HeightUnitValue
        """
        """
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
            """
        ## Bin Construction

        BinBaseValues.Make(self, obj)

        layout = RectangleLayout.Make(self, obj)

        bin_outside_shape = Utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        bin_outside_shape.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        bin_inside_shape = Utils.create_rounded_rectangle(
            obj.xTotalWidth - obj.WallThickness * 2,
            obj.yTotalWidth - obj.WallThickness * 2,
            0,
            obj.BinOuterRadius - obj.WallThickness,
        )
        bin_inside_shape.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        fuse_total = BinSolidMidSection.Make(self, obj, bin_outside_shape)

        bin_base = make_complex_bin_base(obj,layout)

        fuse_total = fuse_total.fuse(bin_base)

        compartements = EcoBinCut.Make(obj, bin_inside_shape)

        fuse_total = fuse_total.cut(compartements)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = BinBottomHoles.Make(obj, layout)

            fuse_total = Part.Shape.cut(fuse_total, holes)

        if obj.StackingLip:
            stacking_lip = StackingLip.Make(obj, bin_outside_shape)

            fuse_total = fuse_total.fuse(stacking_lip)

        """
        fuse_total = make_bin_base(obj)

        solid_center = Utils.rounded_rectangle_extrude(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.TotalHeight + obj.BaseProfileHeight,
            obj.TotalHeight - obj.BaseProfileHeight,
            obj.BinOuterRadius,
        )

        solid_center.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 - obj.BinUnit / 2,
                obj.yTotalWidth / 2 - obj.BinUnit / 2,
                0,
            ),
        )

        fuse_total = fuse_total.fuse(solid_center)

        compartements = EcoBinCut.Make(obj)

        fuse_total = fuse_total.cut(compartements)

        if obj.StackingLip:
            stacking_lip = make_stacking_lip(obj)

            fuse_total = Part.Shape.fuse(stacking_lip, fuse_total)

        if obj.MagnetHoles:
            holes = make_bottom_holes(obj)

            fuse_total = Part.Shape.cut(fuse_total, holes)
        """
        return Part.Solid.removeSplitter(fuse_total)



class PartsBin(FoundationGridfinity):
    """PartsBin object."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize Partsbin properties.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        self.features = [RectangleLayout(obj),
            BinSolidMidSection(obj),
            StackingLip(obj),
            BinBottomHoles(obj),
            BinBaseValues(obj),
            Compartments(obj),
            LabelShelf(obj),
            Scoop(obj),
        ]
        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate Parts bin.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Parts bin shape.

        """

        BinBaseValues.Make(self, obj)

        layout = RectangleLayout.Make(self, obj)

        bin_outside_shape = Utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        bin_outside_shape.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        bin_inside_shape = Utils.create_rounded_rectangle(
            obj.xTotalWidth - obj.WallThickness * 2,
            obj.yTotalWidth - obj.WallThickness * 2,
            0,
            obj.BinOuterRadius - obj.WallThickness,
        )
        bin_inside_shape.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        fuse_total = BinSolidMidSection.Make(self, obj, bin_outside_shape)

        bin_base = make_complex_bin_base(obj,layout)

        fuse_total = fuse_total.fuse(bin_base)

        compartements = Compartments.Make(obj, bin_inside_shape)

        fuse_total = fuse_total.cut(compartements)

        if obj.StackingLip:
            stacking_lip = StackingLip.Make(obj, bin_outside_shape)

            fuse_total = fuse_total.fuse(stacking_lip)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = BinBottomHoles.Make(obj, layout)

            fuse_total = Part.Shape.cut(fuse_total, holes)

        if obj.LabelShelfStyle != "Off":
            label_shelf = LabelShelf.Make(obj)

            fuse_total = fuse_total.fuse(label_shelf)

        if obj.Scoop:
            scoop = Scoop.Make(obj)

            fuse_total = fuse_total.fuse(scoop)

        return Part.Solid.removeSplitter(fuse_total)


class Baseplate(FoundationGridfinity):
    """BasePlate object."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize Baseplate properties.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        """
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        self.features = [RectangleLayout(obj, baseplate_default = True),
            BaseplateSolidShape(obj),
            BaseplateBaseValues(obj),

        ]

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:

        BaseplateBaseValues.Make(self, obj)

        layout = RectangleLayout.Make(self, obj)

        baseplate_outside_shape = Utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        baseplate_outside_shape.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2,
                obj.yTotalWidth / 2,
                0,
            ),
        )

        solid_shape = BaseplateSolidShape.Make(self, obj, baseplate_outside_shape)

        fuse_total = make_complex_bin_base(obj,layout)
        fuse_total.translate(
            FreeCAD.Vector(
                0,
                0,
                obj.TotalHeight,
            ),
        )

        return Part.Shape.cut(solid_shape, fuse_total)


class MagnetBaseplate(FoundationGridfinity):
    """Magnet baseplate object."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize magnet baseplate properties.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject.

        """
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        self.features = [RectangleLayout(obj, baseplate_default = True),
            BaseplateSolidShape(obj, magnet_baseplate_default = True),
            BaseplateBaseValues(obj),
            BaseplateMagnetHoles(obj),
            BaseplateCenterCut(obj),
        ]

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate partsbin shape.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        Returns:
            Part.Shape: PartsBin Shape.

        """

        BaseplateBaseValues.Make(self, obj)

        layout = RectangleLayout.Make(self, obj)

        baseplate_outside_shape = Utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.MagnetHoleDepth - obj.MagnetBase,
            obj.BinOuterRadius,
        )
        baseplate_outside_shape.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2,
                obj.yTotalWidth / 2,
                0,
            ),
        )

        solid_shape = BaseplateSolidShape.Make(self, obj, baseplate_outside_shape)

        fuse_total = make_complex_bin_base(obj,layout)
        fuse_total.translate(
            FreeCAD.Vector(
                0,
                0,
                obj.TotalHeight,
            ),
        )

        fuse_total = Part.Shape.cut(solid_shape, fuse_total)



        magholes = BaseplateMagnetHoles.Make(obj)

        fuse_total = Part.Shape.cut(fuse_total, magholes)

        cutout = BaseplateCenterCut.Make(obj)

        return Part.Shape.cut(fuse_total, cutout)

class ScrewTogetherBaseplate(FoundationGridfinity):
    """Screw together baseplate object."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize screw together baseplate properties.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        """
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )
        obj.Proxy = self

        self.features = [RectangleLayout(obj, baseplate_default = True),
            BaseplateSolidShape(obj, screw_together_baseplate_default = True),
            BaseplateBaseValues(obj),
            BaseplateMagnetHoles(obj),
            BaseplateCenterCut(obj),
            BaseplateScrewBottomChamfer(obj),
            BaseplateConnectionHoles(obj),
        ]

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate Parts Bin shape.

        Args:
            obj (FreeCAD.DocumentObject): Document Object.

        Returns:
            Part.Shape: ParstBin Shape.

        """
        BaseplateBaseValues.Make(self, obj)

        layout = RectangleLayout.Make(self, obj)

        baseplate_outside_shape = Utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.BaseThickness,
            obj.BinOuterRadius,
        )
        baseplate_outside_shape.translate(
            FreeCAD.Vector(
                obj.xTotalWidth / 2,
                obj.yTotalWidth / 2,
                0,
            ),
        )

        solid_shape = BaseplateSolidShape.Make(self, obj, baseplate_outside_shape)

        fuse_total = make_complex_bin_base(obj,layout)
        fuse_total.translate(
            FreeCAD.Vector(
                0,
                0,
                obj.TotalHeight,
            ),
        )

        fuse_total = Part.Shape.cut(solid_shape, fuse_total)



        magholes = BaseplateMagnetHoles.Make(obj)

        fuse_total = Part.Shape.cut(fuse_total, magholes)

        cutout = BaseplateCenterCut.Make(obj)

        fuse_total = fuse_total.cut(cutout)

        magchamfer = BaseplateScrewBottomChamfer.Make(obj)

        fuse_total = Part.Shape.cut(fuse_total, magchamfer)

        conholes = BaseplateConnectionHoles.Make(obj)

        return Part.Shape.cut(fuse_total, conholes)

class LBinBlank(FoundationGridfinity):
    """L shaped blank bin object."""

    def __init__(self, obj: FreeCAD.DocumentObject) -> None:
        """Initialize L shaped blank bin properties.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject

        """
        super().__init__(obj)

        obj.addProperty("App::PropertyPythonObject", "Bin", "base", "python gridfinity object")

        self._add_bin_properties(obj)
        self._add_custom_bin_properties(obj)
        self._add_reference_properties(obj)
        self._add_expert_properties(obj)
        self._add_hidden_properties(obj)

        obj.Proxy = self

    def _add_bin_properties(self, obj: FreeCAD.DocumentObject) -> None:
        obj.addProperty(
            "App::PropertyInteger",
            "aGridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).aGridUnits = 3
        obj.addProperty(
            "App::PropertyInteger",
            "bGridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).bGridUnits = 1
        obj.addProperty(
            "App::PropertyInteger",
            "cGridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).cGridUnits = 1
        obj.addProperty(
            "App::PropertyInteger",
            "dGridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).dGridUnits = 1
        obj.addProperty(
            "App::PropertyInteger",
            "HeightUnits",
            "Gridfinity",
            "height of the bin in units, each is 7 mm",
        ).HeightUnits = 6
        obj.addProperty(
            "App::PropertyBool",
            "StackingLip",
            "Gridfinity",
            "Toggle the stacking lip on or off",
        ).StackingLip = True
        obj.addProperty(
            "App::PropertyBool",
            "MagnetHoles",
            "Gridfinity",
            "Toggle the magnet holes on or off",
        ).MagnetHoles = True
        obj.addProperty(
            "App::PropertyBool",
            "ScrewHoles",
            "Gridfinity",
            "Toggle the screw holes on or off",
        ).ScrewHoles = True

    def _add_custom_bin_properties(self, obj: FreeCAD.DocumentObject) -> None:
        obj.addProperty(
            "App::PropertyLength",
            "CustomHeight",
            "GridfinityNonStandard",
            "total height of the bin using the custom heignt instead of incraments of 7 mm",
        ).CustomHeight = 42
        obj.addProperty(
            "App::PropertyLength",
            "SequentialBridgingLayerHeight",
            "GridfinityNonStandard",
            "Layer Height that you print in for optimal print results",
        ).SequentialBridgingLayerHeight = 0.2
        obj.addProperty(
            "App::PropertyBool",
            "NonStandardHeight",
            "GridfinityNonStandard",
            "use a custom height if selected",
        ).NonStandardHeight = False
        obj.addProperty(
            "App::PropertyEnumeration",
            "MagnetHolesShape",
            "GridfinityNonStandard",
            (
                "Shape of magnet holes. <br> <br> Hex meant to be press fit. <br> "
                "Round meant to be glued"
            ),
        )
        obj.MagnetHolesShape = HOLE_SHAPES
        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDiameter",
            "GridfinityNonStandard",
            "Diameter of Magnet Holes <br> <br> default = 6.5 mm",
        ).MagnetHoleDiameter = MAGNET_HOLE_DIAMETER
        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDepth",
            "GridfinityNonStandard",
            "Depth of Magnet Holes <br> <br> default = 2.4 mm",
        ).MagnetHoleDepth = MAGNET_HOLE_DEPTH
        obj.addProperty(
            "App::PropertyLength",
            "ScrewHoleDiameter",
            "GridfinityNonStandard",
            "Diameter of Screw Holes <br> <br> default = 3.0 mm",
        ).ScrewHoleDiameter = SCREW_HOLE_DIAMETER
        obj.addProperty(
            "App::PropertyLength",
            "ScrewHoleDepth",
            "GridfinityNonStandard",
            "Depth of Screw Holes <br> <br> default = 6.0 mm",
        ).ScrewHoleDepth = SCREW_HOLE_DEPTH

    def _add_reference_properties(self, obj: FreeCAD.DocumentObject) -> None:
        obj.addProperty(
            "App::PropertyLength",
            "xTotalWidth",
            "ReferenceDimensions",
            "total width of bin in x direction",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "yTotalWidth",
            "ReferenceDimensions",
            "total width of bin in y direction",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "TotalHeight",
            "ReferenceDimensions",
            "total height of the bin",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileHeight",
            "ReferenceDimensions",
            "Height of the Gridfinity Base Profile",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "xBinUnit",
            "ReferenceDimensions",
            "Width of a single bin unit",
            1,
        ).xBinUnit = BIN_UNIT
        obj.addProperty(
            "App::PropertyLength",
            "yBinUnit",
            "ReferenceDimensions",
            "Width of a single bin unit",
            1,
        ).yBinUnit = BIN_UNIT

        obj.addProperty(
            "App::PropertyLength",
            "aTotalDimension",
            "ReferenceDimensions",
            "total width of a dimension",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "bTotalDimension",
            "ReferenceDimensions",
            "total width of b dimension",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "cTotalDimension",
            "ReferenceDimensions",
            "total width of c dimension",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "dTotalDimension",
            "ReferenceDimensions",
            "total width of d dimension",
            1,
        )

    def _add_expert_properties(self, obj: FreeCAD.DocumentObject) -> None:
        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileBottomChamfer",
            "zzExpertOnly",
            "height of chamfer in bottom of bin base profile <br> <br> default = 0.8 mm",
            1,
        ).BaseProfileBottomChamfer = BIN_BASE_BOTTOM_CHAMFER
        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileVerticalSection",
            "zzExpertOnly",
            "Height of the vertical section in bin base profile",
            1,
        ).BaseProfileVerticalSection = BIN_BASE_VERTICAL_SECTION
        obj.addProperty(
            "App::PropertyLength",
            "BaseProfileTopChamfer",
            "zzExpertOnly",
            "Height of the top chamfer in the bin base profile",
            1,
        ).BaseProfileTopChamfer = BIN_BASE_TOP_CHAMFER
        obj.addProperty(
            "App::PropertyLength",
            "GridSize",
            "zzExpertOnly",
            "Size of the Grid",
        ).GridSize = GRID_SIZE
        obj.addProperty(
            "App::PropertyLength",
            "HeightUnitValue",
            "zzExpertOnly",
            "height per unit, default is 7mm",
            1,
        ).HeightUnitValue = 7
        obj.addProperty(
            "App::PropertyLength",
            "BinOuterRadius",
            "zzExpertOnly",
            "Outer radius of the bin",
            1,
        ).BinOuterRadius = BIN_OUTER_RADIUS
        obj.addProperty(
            "App::PropertyLength",
            "BinVerticalRadius",
            "zzExpertOnly",
            "Radius of the base profile Vertical section",
            1,
        ).BinVerticalRadius = BIN_BASE_VERTICAL_RADIUS
        obj.addProperty(
            "App::PropertyLength",
            "BinBottomRadius",
            "zzExpertOnly",
            "bottom of bin corner radius",
            1,
        ).BinBottomRadius = BIN_BASE_BOTTOM_RADIUS

        obj.addProperty(
            "App::PropertyLength",
            "Clearance",
            "zzExpertOnly",
            (
                "The Clearance on each side of a bin between before the edge of the grid <br> <br> "
                "default = 0.25 mm"
            ),
            1,
        ).Clearance = CLEARANCE
        obj.addProperty(
            "App::PropertyLength",
            "MagnetHoleDistanceFromEdge",
            "zzExpertOnly",
            "Distance of the magnet holes from bin edge <br> <br> default = 8.0 mm",
            1,
        ).MagnetHoleDistanceFromEdge = MAGNET_HOLE_DISTANCE_FROM_EDGE
        obj.addProperty(
            "App::PropertyLength",
            "StackingLipTopLedge",
            "zzExpertOnly",
            "Top Ledge of the stacking lip <br> <br> default = 0.4 mm",
            1,
        ).StackingLipTopLedge = STACKING_LIP_TOP_LEDGE
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
        ).StackingLipBottomChamfer = STACKING_LIP_BOTTOM_CHAMFER
        obj.addProperty(
            "App::PropertyLength",
            "StackingLipVerticalSection",
            "zzExpertOnly",
            "vertical section of the Stacking lip<br> <br> default = 1.8 mm",
            1,
        ).StackingLipVerticalSection = STACKING_LIP_VERTICAL_SECTION

    def _add_hidden_properties(self, obj: FreeCAD.DocumentObject) -> None:
        obj.addProperty(
            "App::PropertyLength",
            "WallThickness",
            "GridfinityNonStandard",
            "for stacking lip",
        ).WallThickness = 1
        obj.setEditorMode("WallThickness", 2)

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate gridfinity L shaped bin.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject

        Returns:
            Part.Shape: L shaped bin shape.

        """
        if obj.NonStandardHeight:
            obj.TotalHeight = obj.CustomHeight
        else:
            obj.TotalHeight = obj.HeightUnits * obj.HeightUnitValue

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )
        obj.StackingLipTopChamfer = (
            obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
        )
        obj.xBinUnit = obj.GridSize - CLEARANCE * 2 * unitmm
        obj.yBinUnit = obj.GridSize - CLEARANCE * 2 * unitmm

        obj.aTotalDimension = obj.aGridUnits * obj.GridSize - obj.Clearance * 2
        obj.bTotalDimension = obj.bGridUnits * obj.GridSize - obj.Clearance * 2
        obj.cTotalDimension = obj.cGridUnits * obj.GridSize - obj.Clearance * 2
        obj.dTotalDimension = obj.dGridUnits * obj.GridSize

        binlayout = [
            [False for x in range(obj.bGridUnits + obj.dGridUnits)] for y in range(obj.aGridUnits)
        ]

        for x in range(obj.aGridUnits):
            for y in range(obj.bGridUnits + obj.dGridUnits):
                if x < obj.cGridUnits:
                    binlayout[x][y] = True
                if y < obj.bGridUnits:
                    binlayout[x][y] = True

        fusetotal = make_complex_bin_base(obj, binlayout)

        midsection = make_l_mid_section(obj)

        fusetotal = fusetotal.fuse(midsection)

        """stacking_lip_path = create_rounded_l(
            LShapeData(
                obj.aTotalDimension,
                obj.bTotalDimension,
                obj.cTotalDimension,
                obj.dTotalDimension,
            ),
            obj.Clearance,
            obj.Clearance,
            obj.BinOuterRadius,
        )"""

        if obj.StackingLip:
            stacking_lip = make_complex_stacking_lip(obj)
            fusetotal = Part.Shape.fuse(stacking_lip, fusetotal)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = make_complex_bottom_holes(obj, binlayout)
            fusetotal = Part.Shape.cut(fusetotal, holes)

        return fusetotal
