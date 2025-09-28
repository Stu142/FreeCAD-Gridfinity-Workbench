"""Feature modules contain bins an baseplate objects."""

# ruff: noqa: D101, D102, D107

from abc import abstractmethod

import FreeCAD as fc  # noqa: N813
import Part

from . import baseplate_feature_construction as baseplate_feat
from . import const, grid_initial_layout, label_shelf, utils
from . import feature_construction as feat
from .custom_shape_features import (
    clean_up_layout,
    custom_shape_solid,
    custom_shape_stacking_lip,
    custom_shape_trim,
    cut_outside_shape,
    vertical_edge_fillet,
)
from .version import __version__

unitmm = fc.Units.Quantity("1 mm")


class FoundationGridfinity:
    def __init__(self, obj: fc.DocumentObject) -> None:
        obj.addProperty(
            "App::PropertyString",
            "version",
            "version",
            "Gridfinity Workbench Version",
            read_only=True,
        ).version = __version__

        obj.Proxy = self

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
        obj.setEditorMode("StackingLip", 2)
        obj.setEditorMode("RecessedTopDepth", 2)
        obj.setEditorMode("WallThickness", 2)


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

        obj.setExpression("UsableHeight", "TotalHeight - HeightUnitValue")

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
            max(obj.BinOuterRadius - obj.WallThickness, 0.5 * unitmm),
        )
        bin_inside_shape.translate(
            fc.Vector(obj.xTotalWidth / 2 + obj.Clearance, obj.yTotalWidth / 2 + obj.Clearance),
        )

        fuse_total = feat.make_bin_solid_mid_section(obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(feat.make_complex_bin_base(obj, layout))
        face = Part.Face(bin_inside_shape).translate(fc.Vector(0, 0, -obj.UsableHeight))
        compartments = face.extrude(fc.Vector(0, 0, obj.UsableHeight))

        fuse_total = fuse_total.cut(feat.make_compartments(obj, compartments))

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
        feat.scoop_properties(obj, scoop_default=False)

        obj.setExpression("UsableHeight", "TotalHeight - HeightUnitValue")

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        layout = grid_initial_layout.make_rectangle_layout(obj)

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

        fuse_total = feat.make_bin_solid_mid_section(obj, bin_outside_shape)
        fuse_total = fuse_total.fuse(feat.make_complex_bin_base(obj, layout))
        face = Part.Face(bin_inside_shape).translate(
            fc.Vector(
                0,
                0,
                -obj.TotalHeight + obj.BaseProfileHeight + obj.BaseWallThickness,
            ),
        )

        compartment_solid = face.extrude(
            fc.Vector(0, 0, obj.TotalHeight - obj.BaseProfileHeight - obj.BaseWallThickness),
        )

        # First cut eco compartments to create the interior spaces
        eco_compartments = feat.make_eco_compartments(obj, layout, compartment_solid)
        fuse_total = fuse_total.cut(eco_compartments)

        # Now add scoop, but only where eco compartments exist (reversed logic)
        if obj.Scoop:
            scoop = feat.make_scoop(obj, usable_height=obj.TotalHeight - obj.BaseWallThickness)
            # Only add scoop where compartments exist - use intersection to constrain
            scoop_constrained = scoop.common(eco_compartments)
            fuse_total = fuse_total.fuse(scoop_constrained)

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

        grid_initial_layout.rectangle_layout_properties(obj, baseplate_default=True)
        baseplate_feat.solid_shape_properties(obj)
        baseplate_feat.base_values_properties(obj)

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
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

        grid_initial_layout.rectangle_layout_properties(obj, baseplate_default=True)
        baseplate_feat.solid_shape_properties(obj)
        baseplate_feat.base_values_properties(obj)
        baseplate_feat.magnet_holes_properties(obj)
        baseplate_feat.center_cut_properties(obj)

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
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

        grid_initial_layout.rectangle_layout_properties(obj, baseplate_default=True)
        baseplate_feat.solid_shape_properties(obj)
        baseplate_feat.base_values_properties(obj)
        baseplate_feat.magnet_holes_properties(obj)
        baseplate_feat.center_cut_properties(obj)
        baseplate_feat.screw_bottom_chamfer_properties(obj)
        baseplate_feat.connection_holes_properties(obj)

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
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
        fuse_total = fuse_total.cut(baseplate_feat.make_connection_holes(obj, layout))

        return fuse_total


class CustomBlankBin(FoundationGridfinity):
    """Gridfinity CustomBlankBin object."""

    def __init__(self, obj: fc.DocumentObject, layout: list[list[bool]]) -> None:
        super().__init__(obj)
        self.layout = layout

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
        """Generate BinBlank Shape."""
        ## calculated here

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )

        obj.StackingLipTopChamfer = (
            obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
        )
        ## calculated values over
        layout = clean_up_layout(self.layout)
        grid_initial_layout.make_custom_shape_layout(obj, layout)
        solid_shape = custom_shape_solid(obj, layout, obj.TotalHeight - obj.BaseProfileHeight)
        outside_trim = custom_shape_trim(obj, layout, obj.Clearance, obj.Clearance)
        fuse_total = solid_shape.cut(outside_trim)
        fuse_total = fuse_total.removeSplitter()
        fuse_total = vertical_edge_fillet(fuse_total, obj.BinOuterRadius)
        fuse_total = fuse_total.fuse(feat.make_complex_bin_base(obj, layout))

        if obj.RecessedTopDepth > 0:
            recessed_solid = custom_shape_solid(obj, layout, obj.RecessedTopDepth)
            recessed_outside_trim = custom_shape_trim(
                obj,
                layout,
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
            holes = feat.make_bin_bottom_holes(obj, layout)
            fuse_total = Part.Shape.cut(fuse_total, holes)
        if obj.StackingLip:
            fuse_total = fuse_total.fuse(
                custom_shape_stacking_lip(obj, solid_shape, layout),
            )

        return fuse_total

    def dumps(self) -> dict:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        return {"layout": self.layout}

    def loads(self, state: dict) -> None:
        """Needed for JSON Serialization when opening a file containing gridfinity object."""
        self.layout = state["layout"]


class CustomBinBase(FoundationGridfinity):
    """Gridfinity CustomBinBase object."""

    def __init__(self, obj: fc.DocumentObject, layout: list[list[bool]]) -> None:
        super().__init__(obj)
        self.layout = layout

        grid_initial_layout.custom_shape_layout_properties(obj, baseplate_default=False)
        feat.bin_solid_mid_section_properties(
            obj,
            default_height_units=1,
            default_wall_thickness=const.WALL_THICKNESS,
        )
        feat.blank_bin_recessed_top_properties(obj)
        feat.stacking_lip_properties(obj, stacking_lip_default=False)
        feat.bin_bottom_holes_properties(obj, magnet_holes_default=const.MAGNET_HOLES)
        feat.bin_base_values_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate BinBase Shape."""
        ## calculated here
        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )

        obj.StackingLipTopChamfer = (
            obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
        )
        ## calculated values over
        layout = clean_up_layout(self.layout)
        grid_initial_layout.make_custom_shape_layout(obj, layout)
        solid_shape = custom_shape_solid(obj, layout, obj.TotalHeight - obj.BaseProfileHeight)
        outside_trim = custom_shape_trim(obj, layout, obj.Clearance, obj.Clearance)
        fuse_total = solid_shape.cut(outside_trim)
        fuse_total = fuse_total.removeSplitter()
        fuse_total = vertical_edge_fillet(fuse_total, obj.BinOuterRadius)
        fuse_total = fuse_total.fuse(feat.make_complex_bin_base(obj, layout))

        if obj.RecessedTopDepth > 0:
            recessed_solid = custom_shape_solid(obj, layout, obj.RecessedTopDepth)
            recessed_outside_trim = custom_shape_trim(
                obj,
                layout,
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
            holes = feat.make_bin_bottom_holes(obj, layout)
            fuse_total = Part.Shape.cut(fuse_total, holes)
        if obj.StackingLip:
            fuse_total = fuse_total.fuse(
                custom_shape_stacking_lip(obj, solid_shape, layout),
            )

        return fuse_total

    def dumps(self) -> dict:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        return {"layout": self.layout}

    def loads(self, state: dict) -> None:
        """Needed for JSON Serialization when opening a file containing gridfinity object."""
        self.layout = state["layout"]


class CustomEcoBin(FoundationGridfinity):
    """Gridfinity CustomEcoBin object."""

    def __init__(self, obj: fc.DocumentObject, layout: list[list[bool]]) -> None:
        super().__init__(obj)
        self.layout = layout

        grid_initial_layout.custom_shape_layout_properties(obj, baseplate_default=False)
        feat.bin_solid_mid_section_properties(
            obj,
            default_height_units=const.HEIGHT_UNITS,
            default_wall_thickness=const.WALL_THICKNESS,
        )
        feat.stacking_lip_properties(obj, stacking_lip_default=const.STACKING_LIP)
        feat.bin_bottom_holes_properties(obj, magnet_holes_default=False)
        feat.bin_base_values_properties(obj)
        feat.label_shelf_properties(obj, label_style_default="Off")
        feat.eco_compartments_properties(obj)
        feat.scoop_properties(obj, scoop_default=False)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate EcoBin Shape."""
        ## calculated here

        obj.BaseProfileHeight = (
            obj.BaseProfileBottomChamfer
            + obj.BaseProfileVerticalSection
            + obj.BaseProfileTopChamfer
        )

        obj.StackingLipTopChamfer = (
            obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
        )
        ## calculated values over
        layout = clean_up_layout(self.layout)
        grid_initial_layout.make_custom_shape_layout(obj, layout)
        solid_shape = custom_shape_solid(obj, layout, obj.TotalHeight - obj.BaseProfileHeight)
        outside_trim = custom_shape_trim(obj, layout, obj.Clearance, obj.Clearance)
        fuse_total = solid_shape.cut(outside_trim)
        fuse_total = fuse_total.removeSplitter()
        fuse_total = vertical_edge_fillet(fuse_total, obj.BinOuterRadius)
        fuse_total = fuse_total.fuse(feat.make_complex_bin_base(obj, layout))

        feat.eco_error_check(obj)
        compartments_solid = custom_shape_solid(
            obj,
            layout,
            obj.TotalHeight - obj.BaseProfileHeight - obj.BaseWallThickness,
        )
        compartment_trim = custom_shape_trim(
            obj,
            layout,
            obj.Clearance + obj.WallThickness,
            obj.Clearance + obj.WallThickness,
        )
        compartments_solid = compartments_solid.cut(compartment_trim)
        compartments_solid = compartments_solid.removeSplitter()
        compartments_solid = vertical_edge_fillet(
            compartments_solid,
            obj.BinOuterRadius - obj.WallThickness,
        )
        inside_wall_solid_full_height = custom_shape_solid(
            obj,
            layout,
            obj.TotalHeight,
        )
        inside_wall_solid_full_height = inside_wall_solid_full_height.cut(compartment_trim)
        inside_wall_solid_full_height = inside_wall_solid_full_height.removeSplitter()
        inside_wall_solid_full_height = vertical_edge_fillet(
            inside_wall_solid_full_height,
            obj.BinOuterRadius - obj.WallThickness,
        )
        # First cut eco compartments to create the interior spaces
        compartments = feat.make_eco_compartments(obj, layout, compartments_solid)
        inside_wall_negative = cut_outside_shape(obj, inside_wall_solid_full_height)
        compartments = compartments.cut(inside_wall_negative)
        fuse_total = fuse_total.cut(compartments)

        # Now add scoop, but only where eco compartments exist (reversed logic)
        if obj.Scoop:
            scoop = feat.make_scoop(obj, usable_height=obj.TotalHeight - obj.BaseWallThickness)
            # Only add scoop where compartments exist - use intersection to constrain
            scoop_constrained = scoop.common(compartments)
            fuse_total = fuse_total.fuse(scoop_constrained)

        if obj.LabelShelfStyle != "Off":
            label_shelf = feat.make_label_shelf(obj, "eco")
            label_shelf = label_shelf.cut(inside_wall_negative)
            fuse_total = fuse_total.fuse(label_shelf)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = self.bin_bottom_holes.make(obj, layout)
            fuse_total = Part.Shape.cut(fuse_total, holes)
        if obj.StackingLip:
            fuse_total = fuse_total.fuse(
                custom_shape_stacking_lip(obj, solid_shape, layout),
            )

        return fuse_total.removeSplitter()

    def dumps(self) -> dict:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        return {"layout": self.layout}

    def loads(self, state: dict) -> None:
        """Needed for JSON Serialization when opening a file containing gridfinity object."""
        self.layout = state["layout"]


class CustomStorageBin(FoundationGridfinity):
    """Gridfinity CustomStorageBin object."""

    def __init__(self, obj: fc.DocumentObject, layout: list[list[bool]]) -> None:
        super().__init__(obj)
        self.layout = layout

        grid_initial_layout.custom_shape_layout_properties(obj, baseplate_default=False)
        feat.bin_solid_mid_section_properties(
            obj,
            default_height_units=const.HEIGHT_UNITS,
            default_wall_thickness=const.WALL_THICKNESS,
        )
        feat.stacking_lip_properties(obj, stacking_lip_default=const.STACKING_LIP)
        feat.bin_bottom_holes_properties(obj, magnet_holes_default=const.MAGNET_HOLES)
        feat.bin_base_values_properties(obj)
        feat.compartments_properties(obj, x_div_default=0, y_div_default=0)
        feat.label_shelf_properties(obj, label_style_default="Off")
        feat.scoop_properties(obj, scoop_default=False)

        obj.setExpression("UsableHeight", "TotalHeight - HeightUnitValue")

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate StorageBin Shape."""
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
        layout = clean_up_layout(self.layout)
        grid_initial_layout.make_custom_shape_layout(obj, layout)
        solid_shape = custom_shape_solid(obj, layout, obj.TotalHeight - obj.BaseProfileHeight)
        outside_trim = custom_shape_trim(obj, layout, obj.Clearance, obj.Clearance)
        fuse_total = solid_shape.cut(outside_trim)
        fuse_total = fuse_total.removeSplitter()
        fuse_total = vertical_edge_fillet(fuse_total, obj.BinOuterRadius)
        fuse_total = fuse_total.fuse(feat.make_complex_bin_base(obj, layout))

        compartments_solid = custom_shape_solid(obj, layout, obj.UsableHeight)
        compartment_trim = custom_shape_trim(
            obj,
            layout,
            obj.Clearance + obj.WallThickness,
            obj.Clearance + obj.WallThickness,
        )
        compartments_solid = compartments_solid.cut(compartment_trim)
        compartments_solid = compartments_solid.removeSplitter()
        compartments_solid = vertical_edge_fillet(
            compartments_solid,
            obj.BinOuterRadius - obj.WallThickness,
        )
        compartments = feat.make_compartments(obj, compartments_solid)

        fuse_total = fuse_total.cut(compartments)

        if obj.ScrewHoles or obj.MagnetHoles:
            holes = feat.make_bin_bottom_holes(obj, layout)
            fuse_total = Part.Shape.cut(fuse_total, holes)
        if obj.StackingLip:
            fuse_total = fuse_total.fuse(
                custom_shape_stacking_lip(obj, solid_shape, layout),
            )
        outside_bin_solid = cut_outside_shape(obj, compartments_solid)

        if obj.LabelShelfStyle != "Off":
            label_shelf = feat.make_label_shelf(obj, "standard")
            label_shelf = label_shelf.cut(outside_bin_solid)
            fuse_total = fuse_total.fuse(label_shelf)

        if obj.Scoop:
            scoop = feat.make_scoop(obj)
            scoop = scoop.cut(outside_bin_solid)
            fuse_total = fuse_total.fuse(scoop)

        return fuse_total.removeSplitter()

    def dumps(self) -> dict:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        return {"layout": self.layout}

    def loads(self, state: dict) -> None:
        """Needed for JSON Serialization when opening a file containing gridfinity object."""
        self.layout = state["layout"]


class CustomBaseplate(FoundationGridfinity):
    """Gridfinity CustomBaseplate object."""

    def __init__(self, obj: fc.DocumentObject, layout: list[list[bool]]) -> None:
        super().__init__(obj)
        self.layout = layout

        grid_initial_layout.custom_shape_layout_properties(obj, baseplate_default=True)
        baseplate_feat.solid_shape_properties(obj)
        baseplate_feat.base_values_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate Baseplate Shape."""
        ## calculated here
        obj.TotalHeight = obj.BaseProfileHeight

        ## calculated values over
        layout = clean_up_layout(self.layout)
        grid_initial_layout.make_custom_shape_layout(obj, layout)
        solid_shape = custom_shape_solid(
            obj,
            layout,
            obj.TotalHeight,
        ).translate(fc.Vector(0, 0, obj.TotalHeight))
        solid_shape = solid_shape.removeSplitter()
        solid_shape = vertical_edge_fillet(solid_shape, obj.BinOuterRadius)

        fuse_total = feat.make_complex_bin_base(obj, layout)
        fuse_total.translate(fc.Vector(0, 0, obj.TotalHeight))
        fuse_total = solid_shape.cut(fuse_total)

        return fuse_total

    def dumps(self) -> dict:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        return {"layout": self.layout}

    def loads(self, state: dict) -> None:
        """Needed for JSON Serialization when opening a file containing gridfinity object."""
        self.layout = state["layout"]


class CustomMagnetBaseplate(FoundationGridfinity):
    """Gridfinity CustomMagnetBaseplate object."""

    def __init__(self, obj: fc.DocumentObject, layout: list[list[bool]]) -> None:
        super().__init__(obj)
        self.layout = layout

        grid_initial_layout.custom_shape_layout_properties(obj, baseplate_default=True)
        baseplate_feat.solid_shape_properties(obj)
        baseplate_feat.base_values_properties(obj)
        baseplate_feat.magnet_holes_properties(obj)
        baseplate_feat.center_cut_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate MagnetBaseplate Shape."""
        ## calculated here
        obj.TotalHeight = obj.BaseProfileHeight + obj.MagnetHoleDepth + obj.MagnetBase

        ## calculated values over
        layout = clean_up_layout(self.layout)
        grid_initial_layout.make_custom_shape_layout(obj, layout)
        solid_shape = custom_shape_solid(
            obj,
            layout,
            obj.TotalHeight,
        ).translate(fc.Vector(0, 0, obj.BaseProfileHeight))
        solid_shape = solid_shape.removeSplitter()
        solid_shape = vertical_edge_fillet(solid_shape, obj.BinOuterRadius)

        fuse_total = feat.make_complex_bin_base(obj, layout)
        fuse_total.translate(fc.Vector(0, 0, obj.TotalHeight))
        fuse_total = solid_shape.cut(fuse_total)
        fuse_total = fuse_total.cut(baseplate_feat.make_magnet_holes(obj, layout))
        fuse_total = fuse_total.cut(baseplate_feat.make_center_cut(obj, layout))

        return fuse_total

    def dumps(self) -> dict:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        return {"layout": self.layout}

    def loads(self, state: dict) -> None:
        """Needed for JSON Serialization when opening a file containing gridfinity object."""
        self.layout = state["layout"]


class CustomScrewTogetherBaseplate(FoundationGridfinity):
    """Gridfinity CustomScrewTogetherBaseplate object."""

    def __init__(self, obj: fc.DocumentObject, layout: list[list[bool]]) -> None:
        super().__init__(obj)
        self.layout = layout

        grid_initial_layout.custom_shape_layout_properties(obj, baseplate_default=True)
        baseplate_feat.solid_shape_properties(obj)
        baseplate_feat.base_values_properties(obj)
        baseplate_feat.magnet_holes_properties(obj)
        baseplate_feat.center_cut_properties(obj)
        baseplate_feat.screw_bottom_chamfer_properties(obj)
        baseplate_feat.connection_holes_properties(obj)

        obj.Proxy = self

    def generate_gridfinity_shape(self, obj: fc.DocumentObject) -> Part.Shape:
        """Generate Screw Together Baseplate Shape."""
        ## calculated here
        obj.TotalHeight = obj.BaseProfileHeight + obj.BaseThickness

        ## calculated values over
        layout = clean_up_layout(self.layout)
        grid_initial_layout.make_custom_shape_layout(obj, layout)
        solid_shape = custom_shape_solid(
            obj,
            layout,
            obj.TotalHeight,
        ).translate(fc.Vector(0, 0, obj.BaseProfileHeight))
        solid_shape = solid_shape.removeSplitter()
        solid_shape = vertical_edge_fillet(solid_shape, obj.BinOuterRadius)

        fuse_total = feat.make_complex_bin_base(obj, layout)
        fuse_total.translate(fc.Vector(0, 0, obj.TotalHeight))
        fuse_total = solid_shape.cut(fuse_total)
        fuse_total = fuse_total.cut(baseplate_feat.make_magnet_holes(obj, layout))
        fuse_total = fuse_total.cut(baseplate_feat.make_center_cut(obj, layout))
        fuse_total = fuse_total.cut(baseplate_feat.make_screw_bottom_chamfer(obj, layout))
        fuse_total = fuse_total.cut(baseplate_feat.make_connection_holes(obj, layout))

        return fuse_total

    def dumps(self) -> dict:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        return {"layout": self.layout}

    def loads(self, state: dict) -> None:
        """Needed for JSON Serialization when opening a file containing gridfinity object."""
        self.layout = state["layout"]


class StandaloneLabelShelf:
    def __init__(
        self,
        obj: fc.DocumentObject,
        target_obj: fc.DocumentObject,
        face: Part.Face,
    ) -> None:
        obj.addProperty(
            "App::PropertyString",
            "version",
            "version",
            "Gridfinity Workbench Version",
            read_only=True,
        ).version = __version__

        obj.addProperty(
            "App::PropertyLength",
            "Width",
            "GridfinityNonStandard",
            "Width of the Label Shelf, how far it sticks out from the wall"
            " <br> <br> default = 12 mm",
        ).Width = const.LABEL_SHELF_WIDTH
        obj.addProperty(
            "App::PropertyLength",
            "Length",
            "GridfinityNonStandard",
            "Length of the Label Shelf, how long it is <br> <br> default = 42 mm",
        ).Length = const.LABEL_SHELF_LENGTH
        obj.addProperty(
            "App::PropertyAngle",
            "Angle",
            "GridfinityNonStandard",
            "Angle of the bottom part of the Label Shelf <br> <br> default = 45",
        ).Angle = const.LABEL_SHELF_ANGLE
        obj.addProperty(
            "App::PropertyLength",
            "LabelShelfVerticalThickness",
            "zzExpertOnly",
            "Vertical Thickness of the Label Shelf <br> <br> default = 2 mm",
        ).LabelShelfVerticalThickness = const.LABEL_SHELF_VERTICAL_THICKNESS

        obj.addProperty(
            "App::PropertyLink",
            "Attachment",
            "Base",
            "Object this label shelf is attached to.",
            read_only=True,
        ).Attachment = target_obj

        normal = face.normalAt(*face.Surface.parameter(face.CenterOfMass))
        rotation = fc.Rotation(fc.Vector(1, 0, 0), normal)

        points = [v.Point for v in face.Vertexes]
        height = max([p.z for p in points])
        [p1, p2] = [p for p in points if p.z > height - 1e-4]
        translation = (p1 + p2) / 2  # type: ignore[operator]

        placement = fc.Placement(translation, rotation)

        obj.Proxy = self

        obj.Placement = placement
        obj.setExpression(
            "Placement.Base.z",
            "Attachment.StackingLip == 1 ? -Attachment.LabelShelfStackingOffset : 0mm",
        )

    def execute(self, obj: Part.Feature) -> None:
        width = obj.Width
        stacking_lip_offset = feat.calc_stacking_lip_offset(obj.Attachment)
        # Check if the shelf is covered by a stacking lip
        check_point = obj.Placement.Base + obj.Placement.Rotation.multVec(
            fc.Vector(stacking_lip_offset / 2),
        )
        if obj.Attachment.StackingLip and obj.Attachment.Shape.isInside(check_point, 1e-6, False):  # noqa: FBT003
            width += stacking_lip_offset

        shape = label_shelf.from_angle(
            length=obj.Length,
            width=width,
            thickness=obj.LabelShelfVerticalThickness,
            angle=obj.Angle,
            center=True,
        )

        obj.Shape = shape

    def dumps(self) -> None:
        return

    def loads(self, state: tuple) -> None:  # noqa: ARG002
        return
