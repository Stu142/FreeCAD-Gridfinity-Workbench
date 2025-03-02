"""Feature modules contain bins an baseplate objects."""

from abc import abstractmethod

import FreeCAD as fc  # noqa: N813
import Part

from . import const, utils
from .baseplate_feature_construction import (
    BaseplateBaseValues,
    BaseplateCenterCut,
    BaseplateConnectionHoles,
    BaseplateMagnetHoles,
    BaseplateScrewBottomChamfer,
    BaseplateSolidShape,
)
from .custom_shape_features import (
    custom_shape_solid,
    custom_shape_stacking_lip,
    custom_shape_trim,
    vertical_edge_fillet,
)
from .feature_construction import (
    BinBaseValues,
    BinBottomHoles,
    BinSolidMidSection,
    BlankBinRecessedTop,
    Compartments,
    EcoCompartments,
    LabelShelf,
    Scoop,
    StackingLip,
    make_complex_bin_base,
)
from .grid_initial_layout import (
    CustomShapeLayout,
    LShapedLayout,
    RectangleLayout,
)
from .version import __version__

unitmm = fc.Units.Quantity("1 mm")


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


class FoundationGridfinity:
    def __init__(self, obj: fc.DocumentObject) -> None:
        obj.addProperty(
            "App::PropertyString",
            "version",
            "version",
            "Gridfinity Workbench Version",
            1,
        ).version = __version__

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
    def generate_gridfinity_shape(self, fp: fc.DocumentObject) -> Part.Shape:
        """Generate the TopoShape of the object."""

    def dumps(
        self,
    ) -> None:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        return

    def loads(
        self,
        state: tuple,  # noqa: ARG002
    ) -> None:
        """Needed for JSON Serialization when saving a file containing gridfinity object.

        state argument required for opening saved gridfinity object,
        otherwise expecting argument error message
        """
        return


class CustomBin(FoundationGridfinity):
    """Gridfinity CustomBin object."""

    def __init__(self, obj: fc.DocumentObject, layout: list[list[bool]]) -> None:
        super().__init__(obj)
        self.layout = layout

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )
        self.bintype = "standard"
        self.features = [
            CustomShapeLayout(obj, baseplate_default=False),
            BinSolidMidSection(
                obj,
                default_height_units=const.HEIGHT_UNITS,
                default_wall_thickness=const.WALL_THICKNESS,
            ),
            BlankBinRecessedTop(obj),
            StackingLip(obj, stacking_lip_default=const.STACKING_LIP),
            BinBottomHoles(obj, magnet_holes_default=const.MAGNET_HOLES),
            BinBaseValues(obj),
        ]

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate BinBlanek Shape.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Bin Blank shape

        """
        ## calculated here
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
        ## calculated values over
        CustomShapeLayout.calc(self, obj)
        solid_shape = custom_shape_solid(obj, self.layout, obj.TotalHeight - obj.BaseProfileHeight)
        outside_trim = custom_shape_trim(obj, self.layout, obj.Clearance.Value, obj.Clearance.Value)
        fuse_total = solid_shape.cut(outside_trim)
        fuse_total = fuse_total.removeSplitter()
        fuse_total = vertical_edge_fillet(fuse_total, obj.BinOuterRadius)
        fuse_total = fuse_total.fuse(make_complex_bin_base(obj, self.layout))

        if obj.RecessedTopDepth > 0:
            recessed_solid = custom_shape_solid(obj, self.layout, obj.RecessedTopDepth)
            recessed_outside_trim = custom_shape_trim(
                obj,
                self.layout,
                obj.Clearance.Value + obj.WallThickness.Value,
                obj.Clearance.Value + obj.WallThickness.Value,
            )
            recessed_solid = recessed_solid.cut(recessed_outside_trim)
            recessed_solid = recessed_solid.removeSplitter()
            recessed_solid = vertical_edge_fillet(
                recessed_solid,
                obj.BinOuterRadius - obj.WallThickness,
            )
            fuse_total = fuse_total.cut(recessed_solid)
        if obj.ScrewHoles or obj.MagnetHoles:
            holes = BinBottomHoles.make(self, obj, self.layout)
            fuse_total = Part.Shape.cut(fuse_total, holes)
        if obj.StackingLip:
            fuse_total = fuse_total.fuse(
                custom_shape_stacking_lip(obj, solid_shape, self.layout),
            )

        return fuse_total


class BinBlank(FoundationGridfinity):
    """Gridfinity BinBlank object."""

    def __init__(self, obj: fc.DocumentObject) -> None:
        """Create BinBlank object.

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

        self.rectangle_layout = RectangleLayout(obj, baseplate_default=False)
        self.bin_solid_mid_section = BinSolidMidSection(
            obj,
            default_height_units=const.HEIGHT_UNITS,
            default_wall_thickness=const.WALL_THICKNESS,
        )
        self.blank_bin_recessed_top = BlankBinRecessedTop(obj)
        self.stacking_lip = StackingLip(obj, stacking_lip_default=const.STACKING_LIP)
        self.bin_bottom_holes = BinBottomHoles(obj, magnet_holes_default=const.MAGNET_HOLES)
        self.bin_base_values = BinBaseValues(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate BinBlanek Shape.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Bin Blank shape

        """
        self.bin_base_values.make(obj)

        layout = self.rectangle_layout.make(obj)

        bin_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        bin_outside_shape.translate(
            fc.Vector(obj.xTotalWidth / 2 + obj.Clearance, obj.yTotalWidth / 2 + obj.Clearance),
        )

        bin_inside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth - obj.WallThickness * 2,
            obj.yTotalWidth - obj.WallThickness * 2,
            0,
            obj.BinOuterRadius - obj.WallThickness,
        )
        bin_inside_shape.translate(
            fc.Vector(obj.xTotalWidth / 2 + obj.Clearance, obj.yTotalWidth / 2 + obj.Clearance),
        )

        fuse_total = self.bin_solid_mid_section.make(obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(make_complex_bin_base(obj, layout))

        if obj.RecessedTopDepth > 0:
            fuse_total = fuse_total.cut(self.blank_bin_recessed_top.make(obj, bin_inside_shape))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(self.stacking_lip.make(obj, bin_outside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(self.bin_bottom_holes.make(obj, layout))

        return fuse_total


class BinBase(FoundationGridfinity):
    def __init__(self, obj: fc.DocumentObject) -> None:
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        self.rectangle_layout = RectangleLayout(obj, baseplate_default=False)
        self.bin_solid_mid_section = BinSolidMidSection(
            obj,
            default_height_units=1,
            default_wall_thickness=const.WALL_THICKNESS,
        )
        self.blank_bin_recessed_top = BlankBinRecessedTop(obj)
        self.stacking_lip = StackingLip(obj, stacking_lip_default=False)
        self.bin_bottom_holes = BinBottomHoles(obj, magnet_holes_default=const.MAGNET_HOLES)
        self.bin_base_values = BinBaseValues(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        self.bin_base_values.make(obj)

        layout = self.rectangle_layout.make(obj)

        bin_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        bin_outside_shape.translate(
            fc.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        bin_inside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth - obj.WallThickness * 2,
            obj.yTotalWidth - obj.WallThickness * 2,
            0,
            obj.BinOuterRadius - obj.WallThickness,
        )
        bin_inside_shape.translate(
            fc.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        fuse_total = self.bin_solid_mid_section.make(obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(make_complex_bin_base(obj, layout))

        if obj.RecessedTopDepth > 0:
            fuse_total = fuse_total.cut(self.blank_bin_recessed_top.make(obj, bin_inside_shape))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(self.stacking_lip.make(obj, bin_outside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(self.bin_bottom_holes.make(obj, layout))

        return fuse_total


class SimpleStorageBin(FoundationGridfinity):
    """Simple Storage Bin."""

    def __init__(self, obj: fc.DocumentObject) -> None:
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

        self.rectangle_layout = RectangleLayout(obj, baseplate_default=False)
        self.bin_solid_mid_section = BinSolidMidSection(
            obj,
            default_height_units=const.HEIGHT_UNITS,
            default_wall_thickness=const.WALL_THICKNESS,
        )
        self.stacking_lip = StackingLip(obj, stacking_lip_default=const.STACKING_LIP)
        self.bin_bottom_holes = BinBottomHoles(obj, magnet_holes_default=const.MAGNET_HOLES)
        self.bin_base_values = BinBaseValues(obj)
        self.compartments = Compartments(obj, x_div_default=0, y_div_default=0)
        self.label_shelf = LabelShelf(obj, label_style_default="Off")
        self.scoop = Scoop(obj, scoop_default=False)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate simple storage bin.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Storage bin shape.

        """
        self.bin_base_values.make(obj)

        layout = self.rectangle_layout.make(obj)

        bin_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        bin_outside_shape.translate(
            fc.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        bin_inside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth - obj.WallThickness * 2,
            obj.yTotalWidth - obj.WallThickness * 2,
            0,
            obj.BinOuterRadius - obj.WallThickness,
        )
        bin_inside_shape.translate(
            fc.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        fuse_total = self.bin_solid_mid_section.make(obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(make_complex_bin_base(obj, layout))
        fuse_total = fuse_total.cut(self.compartments.make(obj, bin_inside_shape))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(self.stacking_lip.make(obj, bin_outside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(self.bin_bottom_holes.make(obj, layout))

        if obj.LabelShelfStyle != "Off":
            fuse_total = fuse_total.fuse(self.label_shelf.make(obj, "standard"))

        if obj.Scoop:
            fuse_total = fuse_total.fuse(self.scoop.make(obj))

        return fuse_total.removeSplitter()


class EcoBin(FoundationGridfinity):
    """Eco Bin."""

    def __init__(self, obj: fc.DocumentObject) -> None:
        """Initialize Eco bin properties."""
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        self.rectangle_layout = RectangleLayout(obj, baseplate_default=False)
        self.bin_solid_mid_section = BinSolidMidSection(
            obj,
            default_height_units=const.HEIGHT_UNITS,
            default_wall_thickness=const.ECO_WALL_THICKNESS,
        )
        self.stacking_lip = StackingLip(obj, stacking_lip_default=const.STACKING_LIP)
        self.bin_bottom_holes = BinBottomHoles(obj, magnet_holes_default=False)
        self.bin_base_values = BinBaseValues(obj)
        self.label_shelf = LabelShelf(obj, label_style_default="Standard")
        self.eco_compartments = EcoCompartments(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Create gridfinity EcoBin shape.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject.

        Returns:
            Part.Shape: EcoBin shape.

        """
        ## Bin Construction

        self.bin_base_values.make(obj)

        layout = self.rectangle_layout.make(obj)

        bin_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        bin_outside_shape.translate(
            fc.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        bin_inside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth - obj.WallThickness * 2,
            obj.yTotalWidth - obj.WallThickness * 2,
            0,
            obj.BinOuterRadius - obj.WallThickness,
        )
        bin_inside_shape.translate(
            fc.Vector(
                obj.xTotalWidth / 2 + obj.Clearance,
                obj.yTotalWidth / 2 + obj.Clearance,
                0,
            ),
        )

        fuse_total = self.bin_solid_mid_section.make(obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(make_complex_bin_base(obj, layout))
        fuse_total = fuse_total.cut(self.eco_compartments.make(obj, layout, bin_inside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(self.bin_bottom_holes.make(obj, layout))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(self.stacking_lip.make(obj, bin_outside_shape))

        if obj.LabelShelfStyle != "Off":
            fuse_total = fuse_total.fuse(self.label_shelf.make(obj, "eco"))

        return fuse_total.removeSplitter()


class PartsBin(FoundationGridfinity):
    """PartsBin object."""

    def __init__(self, obj: fc.DocumentObject) -> None:
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

        self.rectangle_layout = RectangleLayout(obj, baseplate_default=False)
        self.bin_solid_mid_section = BinSolidMidSection(
            obj,
            default_height_units=const.HEIGHT_UNITS,
            default_wall_thickness=const.WALL_THICKNESS,
        )
        self.stacking_lip = StackingLip(obj, stacking_lip_default=const.STACKING_LIP)
        self.bin_bottom_holes = BinBottomHoles(obj, magnet_holes_default=const.MAGNET_HOLES)
        self.bin_base_values = BinBaseValues(obj)
        self.compartments = Compartments(
            obj,
            x_div_default=const.X_DIVIDERS,
            y_div_default=const.Y_DIVIDERS,
        )
        self.label_shelf = LabelShelf(obj, label_style_default="Standard")
        self.scoop = Scoop(obj, scoop_default=const.SCOOP)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate Parts bin.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Parts bin shape.

        """
        self.bin_base_values.make(obj)

        layout = self.rectangle_layout.make(obj)

        bin_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        bin_outside_shape.translate(
            fc.Vector(obj.xTotalWidth / 2 + obj.Clearance, obj.yTotalWidth / 2 + obj.Clearance, 0),
        )

        bin_inside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth - obj.WallThickness * 2,
            obj.yTotalWidth - obj.WallThickness * 2,
            0,
            obj.BinOuterRadius - obj.WallThickness,
        )
        bin_inside_shape.translate(
            fc.Vector(obj.xTotalWidth / 2 + obj.Clearance, obj.yTotalWidth / 2 + obj.Clearance, 0),
        )

        fuse_total = self.bin_solid_mid_section.make(obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(make_complex_bin_base(obj, layout))
        fuse_total = fuse_total.cut(self.compartments.make(obj, bin_inside_shape))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(self.stacking_lip.make(obj, bin_outside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(self.bin_bottom_holes.make(obj, layout))

        if obj.LabelShelfStyle != "Off":
            fuse_total = fuse_total.fuse(self.label_shelf.make(obj, "standard"))

        if obj.Scoop:
            fuse_total = fuse_total.fuse(self.scoop.make(obj))

        return fuse_total.removeSplitter()


class Baseplate(FoundationGridfinity):
    """BasePlate object."""

    def __init__(self, obj: fc.DocumentObject) -> None:
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

        self.rectangle_layout = RectangleLayout(obj, baseplate_default=True)
        self.baseplate_solid_shape = BaseplateSolidShape(obj)
        self.baseplate_base_values = BaseplateBaseValues(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate Baseplate.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Baseplate shape.

        """
        self.baseplate_base_values.make(obj)

        layout = self.rectangle_layout.make(obj)

        baseplate_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        baseplate_outside_shape.translate(fc.Vector(obj.xTotalWidth / 2, obj.yTotalWidth / 2, 0))

        solid_shape = self.baseplate_solid_shape.make(
            obj,
            baseplate_outside_shape,
            baseplate_type="standard",
        )

        fuse_total = make_complex_bin_base(obj, layout)
        fuse_total.translate(fc.Vector(0, 0, obj.TotalHeight))
        fuse_total = solid_shape.cut(fuse_total)

        return fuse_total


class MagnetBaseplate(FoundationGridfinity):
    """Magnet baseplate object."""

    def __init__(self, obj: fc.DocumentObject) -> None:
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

        self.rectangle_layout = RectangleLayout(obj, baseplate_default=True)
        self.baseplate_solid_shape = BaseplateSolidShape(obj)
        self.baseplate_base_values = BaseplateBaseValues(obj)
        self.baseplate_magnet_holes = BaseplateMagnetHoles(obj)
        self.baseplate_center_cut = BaseplateCenterCut(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate partsbin shape.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        Returns:
            Part.Shape: PartsBin Shape.

        """
        self.baseplate_base_values.make(obj)

        layout = self.rectangle_layout.make(obj)

        baseplate_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.MagnetHoleDepth - obj.MagnetBase,
            obj.BinOuterRadius,
        )
        baseplate_outside_shape.translate(fc.Vector(obj.xTotalWidth / 2, obj.yTotalWidth / 2, 0))

        solid_shape = self.baseplate_solid_shape.make(
            obj,
            baseplate_outside_shape,
            baseplate_type="magnet",
        )

        fuse_total = make_complex_bin_base(obj, layout)
        fuse_total.translate(fc.Vector(0, 0, obj.TotalHeight))
        fuse_total = solid_shape.cut(fuse_total)
        fuse_total = fuse_total.cut(self.baseplate_magnet_holes.make(obj, layout))
        fuse_total = fuse_total.cut(self.baseplate_center_cut.make(obj, layout))

        return fuse_total


class ScrewTogetherBaseplate(FoundationGridfinity):
    """Screw together baseplate object."""

    def __init__(self, obj: fc.DocumentObject) -> None:
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

        self.rectangle_layout = RectangleLayout(obj, baseplate_default=True)
        self.baseplate_solid_shape = BaseplateSolidShape(obj)
        self.baseplate_base_values = BaseplateBaseValues(obj)
        self.baseplate_magnet_holes = BaseplateMagnetHoles(obj)
        self.baseplate_center_cut = BaseplateCenterCut(obj)
        self.baseplate_screw_bottom_chamfer = BaseplateScrewBottomChamfer(obj)
        self.baseplate_connection_holes = BaseplateConnectionHoles(obj)

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate Parts Bin shape.

        Args:
            obj (FreeCAD.DocumentObject): Document Object.

        Returns:
            Part.Shape: ParstBin Shape.

        """
        self.baseplate_base_values.make(obj)

        layout = self.rectangle_layout.make(obj)

        baseplate_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.BaseThickness,
            obj.BinOuterRadius,
        )
        baseplate_outside_shape.translate(fc.Vector(obj.xTotalWidth / 2, obj.yTotalWidth / 2, 0))

        solid_shape = self.baseplate_solid_shape.make(
            obj,
            baseplate_outside_shape,
            baseplate_type="screw_together",
        )

        fuse_total = make_complex_bin_base(obj, layout)
        fuse_total.translate(fc.Vector(0, 0, obj.TotalHeight))
        fuse_total = solid_shape.cut(fuse_total)
        fuse_total = fuse_total.cut(self.baseplate_magnet_holes.make(obj, layout))
        fuse_total = fuse_total.cut(self.baseplate_center_cut.make(obj, layout))
        fuse_total = fuse_total.cut(self.baseplate_screw_bottom_chamfer.make(obj, layout))
        fuse_total = fuse_total.cut(self.baseplate_connection_holes.make(obj))

        return fuse_total


class LBinBlank(FoundationGridfinity):
    """L shaped blank bin object."""

    def __init__(self, obj: fc.DocumentObject) -> None:
        """Initialize L shaped blank bin properties.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject

        """
        super().__init__(obj)

        obj.addProperty("App::PropertyPythonObject", "Bin", "base", "python gridfinity object")

        self.l_shaped_layout = LShapedLayout(obj, baseplate_default=False)
        self.bin_solid_mid_section = BinSolidMidSection(
            obj,
            default_height_units=const.HEIGHT_UNITS,
            default_wall_thickness=const.WALL_THICKNESS,
        )
        self.blank_bin_recessed_top = BlankBinRecessedTop(obj)
        self.stacking_lip = StackingLip(obj, stacking_lip_default=const.STACKING_LIP)
        self.bin_bottom_holes = BinBottomHoles(obj, magnet_holes_default=const.MAGNET_HOLES)
        self.bin_base_values = BinBaseValues(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate gridfinity L shaped bin.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject

        Returns:
            Part.Shape: L shaped bin shape.

        """
        self.bin_base_values.make(obj)

        layout = self.l_shaped_layout.make(obj)

        bin_outside_shape = utils.create_rounded_l(
            utils.LShapeData(
                obj.x1TotalDimension,
                obj.y1TotalDimension,
                obj.x2TotalDimension,
                obj.y2TotalDimension,
            ),
            obj.Clearance,
            obj.Clearance,
            obj.BinOuterRadius,
        )

        bin_inside_shape = utils.create_rounded_l(
            utils.LShapeData(
                obj.x1TotalDimension - obj.WallThickness * 2,
                obj.y1TotalDimension - obj.WallThickness * 2,
                obj.x2TotalDimension - obj.WallThickness * 2,
                obj.y2TotalDimension,
            ),
            obj.Clearance + obj.WallThickness,
            obj.Clearance + obj.WallThickness,
            obj.BinOuterRadius - obj.WallThickness,
        )

        fuse_total = self.bin_solid_mid_section.make(obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(make_complex_bin_base(obj, layout))

        if obj.RecessedTopDepth > 0:
            fuse_total = fuse_total.cut(self.blank_bin_recessed_top.make(obj, bin_inside_shape))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(self.stacking_lip.make(obj, bin_outside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(self.bin_bottom_holes.make(obj, layout))

        return fuse_total
