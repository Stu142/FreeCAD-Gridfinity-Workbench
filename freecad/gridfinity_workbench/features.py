"""Feature modules contain bins an baseplate objects."""

from abc import abstractmethod

import Part

import FreeCAD
from FreeCAD import Units

from . import utils
from .baseplate_feature_construction import (
    BaseplateBaseValues,
    BaseplateCenterCut,
    BaseplateConnectionHoles,
    BaseplateMagnetHoles,
    BaseplateScrewBottomChamfer,
    BaseplateSolidShape,
)
from .feature_construction import (
    Compartments,
    EcoCompartments,
    LabelShelf,
    Scoop,
)
from .feature_construction_complex_bin import (
    BinBaseValues,
    BinBottomHoles,
    BinSolidMidSection,
    BlankBinRecessedTop,
    LShapeData,
    StackingLip,
    create_rounded_l,
    make_complex_bin_base,
)
from .grid_initial_layout import (
    L_Layout,
    RectangleLayout,
)
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

    def dumps(
        self,
    ):  # Needed for JSON Serialization when saving a file containing gridfinity object
        return None

    def loads(
        self, state,
    ):  # Needed for JSON Serialization when saving a file containing gridfinity object
        return None


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
        self.bintype = "standard"
        self.features = [
            RectangleLayout(obj),
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

        bin_base = make_complex_bin_base(obj, layout)

        fuse_total = fuse_total.fuse(bin_base)

        if obj.RecessedTopDepth > 0:
            recessed_cut = BlankBinRecessedTop.Make(obj, bin_inside_shape)

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

        self.bintype = "standard"
        self.features = [
            RectangleLayout(obj),
            BinSolidMidSection(obj, default_height_units=1),
            BlankBinRecessedTop(obj),
            StackingLip(obj, stacking_lip_default=False),
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

        bin_base = make_complex_bin_base(obj, layout)

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
        self.bintype = "standard"
        self.features = [
            RectangleLayout(obj),
            BinSolidMidSection(obj),
            StackingLip(obj),
            BinBottomHoles(obj),
            BinBaseValues(obj),
            Compartments(obj, x_div_default=0, y_div_default=0),
            LabelShelf(obj, label_style_default="Off"),
            Scoop(obj, scoop_default=False),
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

        bin_outside_shape = utils.create_rounded_rectangle(

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

        bin_base = make_complex_bin_base(obj, layout)

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
            label_shelf = LabelShelf.Make(self, obj)

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

        self.bintype = "eco"
        self.features = [
            RectangleLayout(obj),
            BinSolidMidSection(obj, default_wall_thickness=0.8),
            StackingLip(obj),
            BinBottomHoles(obj, magnet_holes_default=False),
            BinBaseValues(obj),
            LabelShelf(obj),
            EcoCompartments(obj),
        ]

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Create gridfinity EcoBin shape.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject.

        Returns:
            Part.Shape: EcoBin shape.

        """
        ## Bin Construction

        BinBaseValues.Make(self, obj)

        layout = RectangleLayout.Make(self, obj)

        bin_outside_shape = utils.create_rounded_rectangle(
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

        bin_inside_shape = utils.create_rounded_rectangle(
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

        bin_base = make_complex_bin_base(obj, layout)

        fuse_total = fuse_total.fuse(bin_base)

        compartements = EcoCompartments.Make(obj, bin_inside_shape)

        fuse_total = fuse_total.cut(compartements)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = BinBottomHoles.Make(obj, layout)

            fuse_total = Part.Shape.cut(fuse_total, holes)

        if obj.StackingLip:
            stacking_lip = StackingLip.Make(obj, bin_outside_shape)

            fuse_total = fuse_total.fuse(stacking_lip)

        labelshelfheight = obj.LabelShelfVerticalThickness

        if obj.LabelShelfStyle != "Off":
            label_shelf = LabelShelf.Make(self, obj)
            # return label_shelf# temp
            fuse_total = fuse_total.fuse(label_shelf)

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

        self.bintype = "standard"
        self.features = [
            RectangleLayout(obj),
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


        bin_outside_shape = utils.create_rounded_rectangle(
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

        bin_inside_shape = utils.create_rounded_rectangle(
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

        bin_base = make_complex_bin_base(obj, layout)

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
            label_shelf = LabelShelf.Make(self, obj)

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

        self.features = [
            RectangleLayout(obj, baseplate_default=True),
            BaseplateSolidShape(obj),
            BaseplateBaseValues(obj),
        ]

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        BaseplateBaseValues.Make(self, obj)

        layout = RectangleLayout.Make(self, obj)


        baseplate_outside_shape = utils.create_rounded_rectangle(
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

        fuse_total = make_complex_bin_base(obj, layout)
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

        self.features = [
            RectangleLayout(obj, baseplate_default=True),
            BaseplateSolidShape(obj, magnet_baseplate_default=True),
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

        fuse_total = make_complex_bin_base(obj, layout)
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

        self.features = [
            RectangleLayout(obj, baseplate_default=True),
            BaseplateSolidShape(obj, screw_together_baseplate_default=True),
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


        baseplate_outside_shape = utils.create_rounded_rectangle(
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

        fuse_total = make_complex_bin_base(obj, layout)
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

        self.bintype = "standard"
        self.features = [
            L_Layout(obj),
            BinSolidMidSection(obj),
            BlankBinRecessedTop(obj),
            StackingLip(obj),
            BinBottomHoles(obj),
            BinBaseValues(obj),
        ]

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: FreeCAD.DocumentObject) -> Part.Shape:
        """Generate gridfinity L shaped bin.

        Args:
            obj (FreeCAD.DocumentObject): DocumentObject

        Returns:
            Part.Shape: L shaped bin shape.

        """
        BinBaseValues.Make(self, obj)

        layout = L_Layout.Make(self, obj)


        bin_outside_shape = create_rounded_l(
            LShapeData(
                obj.aTotalDimension,
                obj.bTotalDimension,
                obj.cTotalDimension,
                obj.dTotalDimension,
            ),
            obj.Clearance,
            obj.Clearance,
            obj.BinOuterRadius,
        )

        bin_inside_shape = create_rounded_l(
            LShapeData(
                obj.aTotalDimension - obj.WallThickness * 2,
                obj.bTotalDimension - obj.WallThickness * 2,
                obj.cTotalDimension - obj.WallThickness * 2,
                obj.dTotalDimension,
            ),
            obj.Clearance + obj.WallThickness,
            obj.Clearance + obj.WallThickness,
            obj.BinOuterRadius - obj.WallThickness,
        )

        fuse_total = BinSolidMidSection.Make(self, obj, bin_outside_shape)

        bin_base = make_complex_bin_base(obj, layout)

        fuse_total = fuse_total.fuse(bin_base)

        if obj.RecessedTopDepth > 0:
            recessed_cut = BlankBinRecessedTop.Make(obj, bin_inside_shape)

            fuse_total = fuse_total.cut(recessed_cut)

        if obj.StackingLip:
            stacking_lip = StackingLip.Make(obj, bin_outside_shape)

            fuse_total = fuse_total.fuse(stacking_lip)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = BinBottomHoles.Make(obj, layout)

            fuse_total = Part.Shape.cut(fuse_total, holes)
        return fuse_total

