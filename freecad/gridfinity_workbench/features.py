"""Feature modules contain bins an baseplate objects."""

# ruff: noqa: D101, D107

from abc import abstractmethod

import FreeCAD as fc  # noqa: N813
import Part

from . import baseplate_feature_construction as baseplate_feat
from . import const, grid_initial_layout, utils
from . import feature_construction as feat
from .custom_shape_features import (
    custom_shape_solid,
    custom_shape_stacking_lip,
    custom_shape_trim,
    vertical_edge_fillet,
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

    def dumps(self) -> dict:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        return {}

    def loads(self, state: dict) -> None:
        """Needed for JSON Serialization when opening a file containing gridfinity object.

        State argument required, otherwise expecting argument error message.
        """


class CustomBin(FoundationGridfinity):
    def __init__(self, obj: fc.DocumentObject, layout: list[list[bool]]) -> None:
        super().__init__(obj)
        self.layout = layout

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )
        grid_initial_layout.custom_shape_layout_properties(obj, baseplate_default=False)
        feat.bin_solid_mid_section_properties(
            obj,
            default_height_units=const.HEIGHT_UNITS,
            default_wall_thickness=const.WALL_THICKNESS,
        )
        feat.blank_bin_recessed_top_properties(obj)
        feat.stacking_lip_properties(obj, stacking_lip_default=const.STACKING_LIP)
        feat.bin_bottom_holes_properties(obj, magnet_holes_default=const.MAGNET_HOLES)
        feat.bin_base_values_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
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
        grid_initial_layout.make_custom_shape_layout(obj, self.layout)
        solid_shape = custom_shape_solid(obj, self.layout, obj.TotalHeight - obj.BaseProfileHeight)
        outside_trim = custom_shape_trim(obj, self.layout, obj.Clearance.Value, obj.Clearance.Value)
        fuse_total = solid_shape.cut(outside_trim)
        fuse_total = fuse_total.removeSplitter()
        fuse_total = vertical_edge_fillet(fuse_total, obj.BinOuterRadius)
        fuse_total = fuse_total.fuse(feat.make_complex_bin_base(obj, self.layout))

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
            holes = feat.make_bin_bottom_holes(obj, self.layout)
            fuse_total = Part.Shape.cut(fuse_total, holes)
        if obj.StackingLip:
            fuse_total = fuse_total.fuse(custom_shape_stacking_lip(obj, solid_shape, self.layout))

        return fuse_total

    def dumps(self) -> dict:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        return {"layout": self.layout}

    def loads(self, state: dict) -> None:
        """Needed for JSON Serialization when opening a file containing gridfinity object."""
        self.layout = state["layout"]


class FullBin(FoundationGridfinity):
    """Gridfinity abstract FullBin object.

    This is not a standalone command, but is used as a base for for BinBlank and BinBase.
    """

    def __init__(
        self,
        obj: fc.DocumentObject,
        *,
        height_units_default: int,
        stacking_lip_default: bool,
    ) -> None:
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        grid_initial_layout.rectangle_layout_properties(obj, baseplate_default=False)
        feat.bin_solid_mid_section_properties(
            obj,
            default_height_units=height_units_default,
            default_wall_thickness=const.WALL_THICKNESS,
        )
        feat.blank_bin_recessed_top_properties(obj)
        feat.stacking_lip_properties(obj, stacking_lip_default=stacking_lip_default)
        feat.bin_bottom_holes_properties(obj, magnet_holes_default=const.MAGNET_HOLES)
        feat.bin_base_values_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        layout = grid_initial_layout.make_rectangle_layout(obj)

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

        fuse_total = feat.make_bin_solid_mid_section(obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(feat.make_complex_bin_base(obj, layout))

        if obj.RecessedTopDepth > 0:
            fuse_total = fuse_total.cut(feat.make_blank_bin_recessed_top(obj, bin_inside_shape))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(feat.make_stacking_lip(obj, bin_outside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(feat.make_bin_bottom_holes(obj, layout))

        return fuse_total


class BinBlank(FullBin):
    def __init__(self, obj: fc.DocumentObject) -> None:
        super().__init__(
            obj,
            height_units_default=const.HEIGHT_UNITS,
            stacking_lip_default=const.STACKING_LIP,
        )


class BinBase(FullBin):
    def __init__(self, obj: fc.DocumentObject) -> None:
        super().__init__(
            obj,
            height_units_default=1,
            stacking_lip_default=False,
        )


class StorageBin(FoundationGridfinity):
    """Gridfinity abstract StorageBin object.

    This is not a standalone command, but is used as a base for for SimpleStorageBin and PartsBin.
    """

    def __init__(
        self,
        obj: fc.DocumentObject,
        *,
        x_div_default: int,
        y_div_default: int,
        label_style_default: str,
        scoop_default: bool,
    ) -> None:
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        grid_initial_layout.rectangle_layout_properties(obj, baseplate_default=False)
        feat.bin_solid_mid_section_properties(
            obj,
            default_height_units=const.HEIGHT_UNITS,
            default_wall_thickness=const.WALL_THICKNESS,
        )
        feat.stacking_lip_properties(obj, stacking_lip_default=const.STACKING_LIP)
        feat.bin_bottom_holes_properties(obj, magnet_holes_default=const.MAGNET_HOLES)
        feat.bin_base_values_properties(obj)
        feat.compartments_properties(obj, x_div_default=x_div_default, y_div_default=y_div_default)
        feat.label_shelf_properties(obj, label_style_default=label_style_default)
        feat.scoop_properties(obj, scoop_default=scoop_default)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        layout = grid_initial_layout.make_rectangle_layout(obj)

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

        fuse_total = feat.make_bin_solid_mid_section(obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(feat.make_complex_bin_base(obj, layout))
        fuse_total = fuse_total.cut(feat.make_compartments(obj, bin_inside_shape))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(feat.make_stacking_lip(obj, bin_outside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(feat.make_bin_bottom_holes(obj, layout))

        if obj.LabelShelfStyle != "Off":
            fuse_total = fuse_total.fuse(feat.make_label_shelf(obj, "standard"))

        if obj.Scoop:
            fuse_total = fuse_total.fuse(feat.make_scoop(obj))

        return fuse_total.removeSplitter()


class SimpleStorageBin(StorageBin):
    def __init__(self, obj: fc.DocumentObject) -> None:
        super().__init__(
            obj,
            x_div_default=0,
            y_div_default=0,
            label_style_default="Off",
            scoop_default=False,
        )


class PartsBin(StorageBin):
    def __init__(self, obj: fc.DocumentObject) -> None:
        super().__init__(
            obj,
            x_div_default=const.X_DIVIDERS,
            y_div_default=const.Y_DIVIDERS,
            label_style_default="Standard",
            scoop_default=const.SCOOP,
        )


class EcoBin(FoundationGridfinity):
    def __init__(self, obj: fc.DocumentObject) -> None:
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        grid_initial_layout.rectangle_layout_properties(obj, baseplate_default=False)
        feat.bin_solid_mid_section_properties(
            obj,
            default_height_units=const.HEIGHT_UNITS,
            default_wall_thickness=const.ECO_WALL_THICKNESS,
        )
        feat.stacking_lip_properties(obj, stacking_lip_default=const.STACKING_LIP)
        feat.bin_bottom_holes_properties(obj, magnet_holes_default=False)
        feat.bin_base_values_properties(obj)
        feat.label_shelf_properties(obj, label_style_default="Standard")
        feat.eco_compartments_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        layout = grid_initial_layout.make_rectangle_layout(obj)

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

        fuse_total = feat.make_bin_solid_mid_section(obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(feat.make_complex_bin_base(obj, layout))
        fuse_total = fuse_total.cut(feat.make_eco_compartments(obj, layout, bin_inside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(feat.make_bin_bottom_holes(obj, layout))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(feat.make_stacking_lip(obj, bin_outside_shape))

        if obj.LabelShelfStyle != "Off":
            fuse_total = fuse_total.fuse(feat.make_label_shelf(obj, "eco"))

        return fuse_total.removeSplitter()


class Baseplate(FoundationGridfinity):
    def __init__(self, obj: fc.DocumentObject) -> None:
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        grid_initial_layout.rectangle_layout_properties(obj, baseplate_default=True)
        baseplate_feat.solid_shape_properties(obj)
        baseplate_feat.base_values_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        baseplate_feat.make_base_values(obj)

        layout = grid_initial_layout.make_rectangle_layout(obj)

        baseplate_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            0,
            obj.BinOuterRadius,
        )
        baseplate_outside_shape.translate(fc.Vector(obj.xTotalWidth / 2, obj.yTotalWidth / 2, 0))

        solid_shape = baseplate_feat.make_solid_shape(
            obj,
            baseplate_outside_shape,
            baseplate_type="standard",
        )

        fuse_total = feat.make_complex_bin_base(obj, layout)
        fuse_total.translate(fc.Vector(0, 0, obj.TotalHeight))
        fuse_total = solid_shape.cut(fuse_total)

        return fuse_total


class MagnetBaseplate(FoundationGridfinity):
    def __init__(self, obj: fc.DocumentObject) -> None:
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )

        grid_initial_layout.rectangle_layout_properties(obj, baseplate_default=True)
        baseplate_feat.solid_shape_properties(obj)
        baseplate_feat.base_values_properties(obj)
        baseplate_feat.magnet_holes_properties(obj)
        baseplate_feat.center_cut_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        baseplate_feat.make_base_values(obj)

        layout = grid_initial_layout.make_rectangle_layout(obj)

        baseplate_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.MagnetHoleDepth - obj.MagnetBase,
            obj.BinOuterRadius,
        )
        baseplate_outside_shape.translate(fc.Vector(obj.xTotalWidth / 2, obj.yTotalWidth / 2, 0))

        solid_shape = baseplate_feat.make_solid_shape(
            obj,
            baseplate_outside_shape,
            baseplate_type="magnet",
        )

        fuse_total = feat.make_complex_bin_base(obj, layout)
        fuse_total.translate(fc.Vector(0, 0, obj.TotalHeight))
        fuse_total = solid_shape.cut(fuse_total)
        fuse_total = fuse_total.cut(baseplate_feat.make_magnet_holes(obj, layout))
        fuse_total = fuse_total.cut(baseplate_feat.make_center_cut(obj, layout))

        return fuse_total


class ScrewTogetherBaseplate(FoundationGridfinity):
    def __init__(self, obj: fc.DocumentObject) -> None:
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyPythonObject",
            "Bin",
            "base",
            "python gridfinity object",
        )
        obj.Proxy = self

        grid_initial_layout.rectangle_layout_properties(obj, baseplate_default=True)
        baseplate_feat.solid_shape_properties(obj)
        baseplate_feat.base_values_properties(obj)
        baseplate_feat.magnet_holes_properties(obj)
        baseplate_feat.center_cut_properties(obj)
        baseplate_feat.screw_bottom_chamfer_properties(obj)
        baseplate_feat.connection_holes_properties(obj)

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        baseplate_feat.make_base_values(obj)

        layout = grid_initial_layout.make_rectangle_layout(obj)

        baseplate_outside_shape = utils.create_rounded_rectangle(
            obj.xTotalWidth,
            obj.yTotalWidth,
            -obj.BaseThickness,
            obj.BinOuterRadius,
        )
        baseplate_outside_shape.translate(fc.Vector(obj.xTotalWidth / 2, obj.yTotalWidth / 2, 0))

        solid_shape = baseplate_feat.make_solid_shape(
            obj,
            baseplate_outside_shape,
            baseplate_type="screw_together",
        )

        fuse_total = feat.make_complex_bin_base(obj, layout)
        fuse_total.translate(fc.Vector(0, 0, obj.TotalHeight))
        fuse_total = solid_shape.cut(fuse_total)
        fuse_total = fuse_total.cut(baseplate_feat.make_magnet_holes(obj, layout))
        fuse_total = fuse_total.cut(baseplate_feat.make_center_cut(obj, layout))
        fuse_total = fuse_total.cut(baseplate_feat.make_screw_bottom_chamfer(obj, layout))
        fuse_total = fuse_total.cut(baseplate_feat.make_connection_holes(obj))

        return fuse_total


class LBinBlank(FoundationGridfinity):
    def __init__(self, obj: fc.DocumentObject) -> None:
        super().__init__(obj)

        obj.addProperty("App::PropertyPythonObject", "Bin", "base", "python gridfinity object")

        grid_initial_layout.l_shaped_layout_properties(obj, baseplate_default=False)
        feat.bin_solid_mid_section_properties(
            obj,
            default_height_units=const.HEIGHT_UNITS,
            default_wall_thickness=const.WALL_THICKNESS,
        )
        feat.blank_bin_recessed_top_properties(obj)
        feat.stacking_lip_properties(obj, stacking_lip_default=const.STACKING_LIP)
        feat.bin_bottom_holes_properties(obj, magnet_holes_default=const.MAGNET_HOLES)
        feat.bin_base_values_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        layout = grid_initial_layout.make_l_shaped_layout(obj)

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

        fuse_total = feat.make_bin_solid_mid_section(obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(feat.make_complex_bin_base(obj, layout))

        if obj.RecessedTopDepth > 0:
            fuse_total = fuse_total.cut(feat.make_blank_bin_recessed_top(obj, bin_inside_shape))

        if obj.StackingLip:
            fuse_total = fuse_total.fuse(feat.make_stacking_lip(obj, bin_outside_shape))

        if obj.ScrewHoles or obj.MagnetHoles:
            fuse_total = fuse_total.cut(feat.make_bin_bottom_holes(obj, layout))

        return fuse_total
