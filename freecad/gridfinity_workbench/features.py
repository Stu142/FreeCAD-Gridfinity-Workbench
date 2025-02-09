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
    ) -> None:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        return


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
        self.bintype = "standard"
        self.features = [
            RectangleLayout(obj, baseplate_default=False),
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
        BinBaseValues.make(self, obj)

        layout = RectangleLayout.make(self, obj)

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

        fuse_total = BinSolidMidSection.make(self, obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(make_complex_bin_base(obj, layout))

        if obj.RecessedTopDepth > 0:
            fuse_total = fuse_total.cut(BlankBinRecessedTop.make(self, obj, bin_inside_shape))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(StackingLip.make(self, obj, bin_outside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(BinBottomHoles.make(self, obj, layout))

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

        self.bintype = "standard"
        self.features = [
            RectangleLayout(obj, baseplate_default=False),
            BinSolidMidSection(
                obj,
                default_height_units=1,
                default_wall_thickness=const.WALL_THICKNESS,
            ),
            BlankBinRecessedTop(obj),
            StackingLip(obj, stacking_lip_default=False),
            BinBottomHoles(obj, magnet_holes_default=const.MAGNET_HOLES),
            BinBaseValues(obj),
        ]

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        BinBaseValues.make(self, obj)

        layout = RectangleLayout.make(self, obj)

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

        fuse_total = BinSolidMidSection.make(self, obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(make_complex_bin_base(obj, layout))

        if obj.RecessedTopDepth > 0:
            fuse_total = fuse_total.cut(BlankBinRecessedTop.make(self, obj, bin_inside_shape))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(StackingLip.make(self, obj, bin_outside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(BinBottomHoles.make(self, obj, layout))

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
        self.bintype = "standard"
        self.features = [
            RectangleLayout(obj, baseplate_default=False),
            BinSolidMidSection(
                obj,
                default_height_units=const.HEIGHT_UNITS,
                default_wall_thickness=const.WALL_THICKNESS,
            ),
            StackingLip(obj, stacking_lip_default=const.STACKING_LIP),
            BinBottomHoles(obj, magnet_holes_default=const.MAGNET_HOLES),
            BinBaseValues(obj),
            Compartments(obj, x_div_default=0, y_div_default=0),
            LabelShelf(obj, label_style_default="Off"),
            Scoop(obj, scoop_default=False),
        ]
        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate simple storage bin.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Storage bin shape.

        """
        BinBaseValues.make(self, obj)

        layout = RectangleLayout.make(self, obj)

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

        fuse_total = BinSolidMidSection.make(self, obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(make_complex_bin_base(obj, layout))
        fuse_total = fuse_total.cut(Compartments.make(self, obj, bin_inside_shape))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(StackingLip.make(self, obj, bin_outside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(BinBottomHoles.make(self, obj, layout))

        if obj.LabelShelfStyle != "Off":
            fuse_total = fuse_total.fuse(LabelShelf.make(self, obj))

        if obj.Scoop:
            fuse_total = fuse_total.fuse(Scoop.make(self, obj))

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

        self.bintype = "eco"
        self.features = [
            RectangleLayout(obj, baseplate_default=False),
            BinSolidMidSection(
                obj,
                default_height_units=const.HEIGHT_UNITS,
                default_wall_thickness=const.ECO_WALL_THICKNESS,
            ),
            StackingLip(obj, stacking_lip_default=const.STACKING_LIP),
            BinBottomHoles(obj, magnet_holes_default=False),
            BinBaseValues(obj),
            LabelShelf(obj, label_style_default="Standard"),
            EcoCompartments(obj),
        ]

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Create gridfinity EcoBin shape.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject.

        Returns:
            Part.Shape: EcoBin shape.

        """
        ## Bin Construction

        BinBaseValues.make(self, obj)

        layout = RectangleLayout.make(self, obj)

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

        fuse_total = BinSolidMidSection.make(self, obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(make_complex_bin_base(obj, layout))
        fuse_total = fuse_total.cut(EcoCompartments.make(self, obj, layout, bin_inside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(BinBottomHoles.make(self, obj, layout))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(StackingLip.make(self, obj, bin_outside_shape))

        if obj.LabelShelfStyle != "Off":
            fuse_total = fuse_total.fuse(LabelShelf.make(self, obj))

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

        self.bintype = "standard"
        self.features = [
            RectangleLayout(obj, baseplate_default=False),
            BinSolidMidSection(
                obj,
                default_height_units=const.HEIGHT_UNITS,
                default_wall_thickness=const.WALL_THICKNESS,
            ),
            StackingLip(obj, stacking_lip_default=const.STACKING_LIP),
            BinBottomHoles(obj, magnet_holes_default=const.MAGNET_HOLES),
            BinBaseValues(obj),
            Compartments(obj, x_div_default=const.X_DIVIDERS, y_div_default=const.Y_DIVIDERS),
            LabelShelf(obj, label_style_default="Standard"),
            Scoop(obj, scoop_default=const.SCOOP),
        ]
        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate Parts bin.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Parts bin shape.

        """
        BinBaseValues.make(self, obj)

        layout = RectangleLayout.make(self, obj)

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

        fuse_total = BinSolidMidSection.make(self, obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(make_complex_bin_base(obj, layout))
        fuse_total = fuse_total.cut(Compartments.make(self, obj, bin_inside_shape))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(StackingLip.make(self, obj, bin_outside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(BinBottomHoles.make(self, obj, layout))

        if obj.LabelShelfStyle != "Off":
            fuse_total = fuse_total.fuse(LabelShelf.make(self, obj))

        if obj.Scoop:
            fuse_total = fuse_total.fuse(Scoop.make(self, obj))

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

        self.features = [
            RectangleLayout(obj, baseplate_default=True),
            BaseplateSolidShape(obj),
            BaseplateBaseValues(obj),
        ]

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate Baseplate.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Baseplate shape.

        """
        BaseplateBaseValues.make(self, obj)

        layout = RectangleLayout.make(self, obj)

        baseplate_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        baseplate_outside_shape.translate(fc.Vector(obj.xTotalWidth / 2, obj.yTotalWidth / 2, 0))

        solid_shape = BaseplateSolidShape.make(
            self,
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

        self.features = [
            RectangleLayout(obj, baseplate_default=True),
            BaseplateSolidShape(obj),
            BaseplateBaseValues(obj),
            BaseplateMagnetHoles(obj),
            BaseplateCenterCut(obj),
        ]

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate partsbin shape.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        Returns:
            Part.Shape: PartsBin Shape.

        """
        BaseplateBaseValues.make(self, obj)

        layout = RectangleLayout.make(self, obj)

        baseplate_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.MagnetHoleDepth - obj.MagnetBase,
            obj.BinOuterRadius,
        )
        baseplate_outside_shape.translate(fc.Vector(obj.xTotalWidth / 2, obj.yTotalWidth / 2, 0))

        solid_shape = BaseplateSolidShape.make(
            self,
            obj,
            baseplate_outside_shape,
            baseplate_type="magnet",
        )

        fuse_total = make_complex_bin_base(obj, layout)
        fuse_total.translate(fc.Vector(0, 0, obj.TotalHeight))
        fuse_total = solid_shape.cut(fuse_total)
        fuse_total = fuse_total.cut(BaseplateMagnetHoles.make(self, obj, layout))
        fuse_total = fuse_total.cut(BaseplateCenterCut.make(self, obj, layout))

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

        self.features = [
            RectangleLayout(obj, baseplate_default=True),
            BaseplateSolidShape(obj),
            BaseplateBaseValues(obj),
            BaseplateMagnetHoles(obj),
            BaseplateCenterCut(obj),
            BaseplateScrewBottomChamfer(obj),
            BaseplateConnectionHoles(obj),
        ]

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate Parts Bin shape.

        Args:
            obj (FreeCAD.DocumentObject): Document Object.

        Returns:
            Part.Shape: ParstBin Shape.

        """
        BaseplateBaseValues.make(self, obj)

        layout = RectangleLayout.make(self, obj)

        baseplate_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.BaseThickness,
            obj.BinOuterRadius,
        )
        baseplate_outside_shape.translate(fc.Vector(obj.xTotalWidth / 2, obj.yTotalWidth / 2, 0))

        solid_shape = BaseplateSolidShape.make(
            self,
            obj,
            baseplate_outside_shape,
            baseplate_type="screw_together",
        )

        fuse_total = make_complex_bin_base(obj, layout)
        fuse_total.translate(fc.Vector(0, 0, obj.TotalHeight))
        fuse_total = solid_shape.cut(fuse_total)
        fuse_total = fuse_total.cut(BaseplateMagnetHoles.make(self, obj, layout))
        fuse_total = fuse_total.cut(BaseplateCenterCut.make(self, obj, layout))
        fuse_total = fuse_total.cut(BaseplateScrewBottomChamfer.make(self, obj, layout))
        fuse_total = fuse_total.cut(BaseplateConnectionHoles.make(self, obj))

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

        self.bintype = "standard"

        self.features = [
            LShapedLayout(obj, baseplate_default=False),
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
        """Generate gridfinity L shaped bin.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject

        Returns:
            Part.Shape: L shaped bin shape.

        """
        BinBaseValues.make(self, obj)

        layout = LShapedLayout.make(self, obj)

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

        fuse_total = BinSolidMidSection.make(self, obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(make_complex_bin_base(obj, layout))

        if obj.RecessedTopDepth > 0:
            fuse_total = fuse_total.cut(BlankBinRecessedTop.make(self, obj, bin_inside_shape))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(StackingLip.make(self, obj, bin_outside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(BinBottomHoles.make(self, obj, layout))

        return fuse_total
