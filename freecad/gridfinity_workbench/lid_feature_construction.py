"""Module containing Gridfinity lid feature construction helpers."""

from __future__ import annotations

import FreeCAD as fc  # noqa: N813
import Part

from . import const, custom_shape_features, utils

unitmm = fc.Units.Quantity("1 mm")
smallmm = fc.Units.Quantity("0.01 mm")


def lid_properties(obj: fc.DocumentObject) -> None:
    """Add lid-specific properties to an object."""
    obj.addProperty(
        "App::PropertyLength",
        "LidThickness",
        "GridfinityNonStandard",
        "Thickness of the lid top plate <br> <br> default = 2 mm",
    ).LidThickness = const.LID_THICKNESS

    obj.addProperty(
        "App::PropertyLength",
        "LidInsetClearance",
        "GridfinityNonStandard",
        "Clearance between lid edge and bin inner wall <br> <br> default = 0.25 mm",
    ).LidInsetClearance = const.LID_INSET_CLEARANCE

    obj.addProperty(
        "App::PropertyLength",
        "LidChamfer",
        "GridfinityNonStandard",
        "Chamfer on the lower lid edge for stacking lip fit <br> <br> default = 0.6 mm",
    ).LidChamfer = const.LID_CHAMFER

    obj.addProperty(
        "App::PropertyBool",
        "HandleEnabled",
        "GridfinityLid",
        "Enable the handle ridge on top of the lid",
    ).HandleEnabled = const.LID_HANDLE_ENABLED

    obj.addProperty(
        "App::PropertyLength",
        "HandleLength",
        "GridfinityLid",
        "Handle length along X <br> <br> default = 30 mm",
    ).HandleLength = const.LID_HANDLE_LENGTH

    obj.addProperty(
        "App::PropertyLength",
        "HandleWidth",
        "GridfinityLid",
        "Handle width along Y <br> <br> default = 10 mm",
    ).HandleWidth = const.LID_HANDLE_WIDTH

    obj.addProperty(
        "App::PropertyLength",
        "HandleHeight",
        "GridfinityLid",
        "Handle height along Z <br> <br> default = 10 mm",
    ).HandleHeight = const.LID_HANDLE_HEIGHT

    obj.addProperty(
        "App::PropertyLength",
        "HandleOffsetX",
        "GridfinityLid",
        "Handle center offset along X <br> <br> default = 0 mm",
    ).HandleOffsetX = const.LID_HANDLE_OFFSET_X

    obj.addProperty(
        "App::PropertyLength",
        "HandleOffsetY",
        "GridfinityLid",
        "Handle center offset along Y <br> <br> default = 0 mm",
    ).HandleOffsetY = const.LID_HANDLE_OFFSET_Y

    obj.addProperty(
        "App::PropertyAngle",
        "HandleRotation",
        "GridfinityLid",
        "Handle rotation angle <br> <br> default = 0 deg",
    ).HandleRotation = const.LID_HANDLE_ROTATION

    obj.addProperty(
        "App::PropertyLength",
        "HandleCornerRadius",
        "GridfinityLid",
        "Handle corner radius <br> <br> default = 5 mm",
    ).HandleCornerRadius = const.LID_HANDLE_CORNER_RADIUS

    obj.addProperty(
        "App::PropertyLength",
        "HandleBaseRadius",
        "GridfinityLid",
        "Blend radius between lid and handle <br> <br> default = 1.5 mm",
    ).HandleBaseRadius = const.LID_HANDLE_BASE_RADIUS

    obj.addProperty(
        "App::PropertyLength",
        "HandleTopRadius",
        "GridfinityLid",
        "Top edge radius of the handle <br> <br> default = 1.5 mm",
    ).HandleTopRadius = const.LID_HANDLE_TOP_RADIUS



def lid_base_properties(obj: fc.DocumentObject) -> None:
    """Add base bin parameters needed for standalone lids."""
    obj.addProperty(
        "App::PropertyLength",
        "WallThickness",
        "zzExpertOnly",
        "Wall thickness used to size the lid",
    ).WallThickness = const.WALL_THICKNESS

    obj.addProperty(
        "App::PropertyLength",
        "BinOuterRadius",
        "zzExpertOnly",
        "Outer radius used to size the lid corners",
    ).BinOuterRadius = const.BIN_OUTER_RADIUS

    obj.addProperty(
        "App::PropertyLength",
        "BaseProfileTopChamfer",
        "zzExpertOnly",
        "Height of the top chamfer in the bin base profile",
    ).BaseProfileTopChamfer = const.BIN_BASE_TOP_CHAMFER

    obj.addProperty(
        "App::PropertyLength",
        "StackingLipTopLedge",
        "zzExpertOnly",
        "Top ledge of the stacking lip",
    ).StackingLipTopLedge = const.STACKING_LIP_TOP_LEDGE

    obj.addProperty(
        "App::PropertyLength",
        "StackingLipBottomChamfer",
        "zzExpertOnly",
        "Bottom chamfer of the stacking lip",
    ).StackingLipBottomChamfer = const.STACKING_LIP_BOTTOM_CHAMFER

    obj.addProperty(
        "App::PropertyLength",
        "Clearance",
        "zzExpertOnly",
        "Clearance between bins <br> <br> default = 0.25 mm",
    ).Clearance = const.CLEARANCE

    obj.addProperty(
        "App::PropertyBool",
        "StackingLip",
        "zzExpertOnly",
        "Stacking lip enabled flag",
    ).StackingLip = const.STACKING_LIP


def add_attachment_reference_properties(obj: fc.DocumentObject) -> None:
    """Add read-only properties that mirror attachment values."""
    obj.addProperty(
        "App::PropertyLength",
        "xTotalWidth",
        "ReferenceParameters",
        "Total width in X from attachment",
        read_only=True,
    )
    obj.addProperty(
        "App::PropertyLength",
        "yTotalWidth",
        "ReferenceParameters",
        "Total width in Y from attachment",
        read_only=True,
    )
    obj.addProperty(
        "App::PropertyLength",
        "xGridSize",
        "ReferenceParameters",
        "Grid size in X from attachment",
        read_only=True,
    )
    obj.addProperty(
        "App::PropertyLength",
        "yGridSize",
        "ReferenceParameters",
        "Grid size in Y from attachment",
        read_only=True,
    )
    obj.addProperty(
        "App::PropertyLength",
        "xLocationOffset",
        "ShouldBeHidden",
        "X location offset from attachment",
        hidden=True,
        read_only=True,
    )
    obj.addProperty(
        "App::PropertyLength",
        "yLocationOffset",
        "ShouldBeHidden",
        "Y location offset from attachment",
        hidden=True,
        read_only=True,
    )
    obj.addProperty(
        "App::PropertyLength",
        "WallThickness",
        "ReferenceParameters",
        "Wall thickness from attachment",
        read_only=True,
    )
    obj.addProperty(
        "App::PropertyLength",
        "BinOuterRadius",
        "ReferenceParameters",
        "Outer radius from attachment",
        read_only=True,
    )
    obj.addProperty(
        "App::PropertyLength",
        "BaseProfileTopChamfer",
        "ReferenceParameters",
        "Top chamfer height from attachment",
        read_only=True,
    )
    obj.addProperty(
        "App::PropertyLength",
        "StackingLipTopLedge",
        "ReferenceParameters",
        "Stacking lip top ledge from attachment",
        read_only=True,
    )
    obj.addProperty(
        "App::PropertyLength",
        "StackingLipBottomChamfer",
        "ReferenceParameters",
        "Stacking lip bottom chamfer from attachment",
        read_only=True,
    )
    obj.addProperty(
        "App::PropertyLength",
        "Clearance",
        "ReferenceParameters",
        "Clearance from attachment",
        read_only=True,
    )
    obj.addProperty(
        "App::PropertyBool",
        "StackingLip",
        "ReferenceParameters",
        "Stacking lip enabled flag from attachment",
        read_only=True,
    )


def bind_attachment_expressions(obj: fc.DocumentObject) -> None:
    """Bind attachment expressions to reference properties."""
    obj.setExpression("xTotalWidth", "Attachment.xTotalWidth")
    obj.setExpression("yTotalWidth", "Attachment.yTotalWidth")
    obj.setExpression("xGridSize", "Attachment.xGridSize")
    obj.setExpression("yGridSize", "Attachment.yGridSize")
    obj.setExpression("xLocationOffset", "Attachment.xLocationOffset")
    obj.setExpression("yLocationOffset", "Attachment.yLocationOffset")
    obj.setExpression("WallThickness", "Attachment.WallThickness")
    obj.setExpression("BinOuterRadius", "Attachment.BinOuterRadius")
    obj.setExpression("BaseProfileTopChamfer", "Attachment.BaseProfileTopChamfer")
    obj.setExpression("StackingLipTopLedge", "Attachment.StackingLipTopLedge")
    obj.setExpression("StackingLipBottomChamfer", "Attachment.StackingLipBottomChamfer")
    obj.setExpression("Clearance", "Attachment.Clearance")
    obj.setExpression("StackingLip", "Attachment.StackingLip")


def _stacking_lip_inset(obj: fc.DocumentObject) -> fc.Units.Quantity:
    stacking_lip_top_chamfer = obj.BaseProfileTopChamfer - obj.Clearance - obj.StackingLipTopLedge
    lip_inset = (
        stacking_lip_top_chamfer
        + obj.StackingLipTopLedge
        + obj.StackingLipBottomChamfer
        - obj.WallThickness
    )
    return max(lip_inset, 0 * unitmm)


def _lid_outline_params(
    obj: fc.DocumentObject,
) -> tuple[fc.Units.Quantity, fc.Units.Quantity, fc.Units.Quantity, fc.Units.Quantity]:
    lip_inset = _stacking_lip_inset(obj)
    lid_width = obj.xTotalWidth - 2 * (obj.WallThickness + lip_inset + obj.LidInsetClearance)
    lid_height = obj.yTotalWidth - 2 * (obj.WallThickness + lip_inset + obj.LidInsetClearance)
    if lid_width <= 0 * unitmm or lid_height <= 0 * unitmm:
        raise RuntimeError("Lid size is not valid for the selected bin parameters.")

    radius = obj.BinOuterRadius - obj.WallThickness - lip_inset - obj.LidInsetClearance
    max_radius = min(lid_width, lid_height) / 2 - smallmm
    radius = min(radius, max_radius)
    if radius <= 0 * unitmm:
        raise RuntimeError("Lid radius is not valid for the selected bin parameters.")

    inset_offset = obj.Clearance + obj.WallThickness + lip_inset + obj.LidInsetClearance
    return lid_width, lid_height, radius, inset_offset


def _rect_wire(
    width: fc.Units.Quantity,
    height: fc.Units.Quantity,
    radius: fc.Units.Quantity,
    offset: fc.Units.Quantity,
) -> Part.Wire:
    wire = utils.create_rounded_rectangle(width, height, 0, radius)
    wire.translate(fc.Vector(width / 2 + offset, height / 2 + offset, 0))
    return wire


def make_lid_rect(obj: fc.DocumentObject) -> Part.Shape:
    """Create a rectangular lid shape that fits inside a bin."""
    lid_width, lid_height, radius, inset_offset = _lid_outline_params(obj)

    outer_wire = _rect_wire(lid_width, lid_height, radius, inset_offset)
    plate = Part.Face(outer_wire).extrude(fc.Vector(0, 0, -obj.LidThickness))
    plate = _apply_lid_chamfer(plate, obj.LidChamfer, -obj.LidThickness, radius)
    lid_shape = plate

    lid_shape = _add_handle(lid_shape, obj, inset_offset, lid_width, lid_height)
    lid_shape = _add_handle(lid_shape, obj, inset_offset, lid_width, lid_height)

    lid_shape.translate(fc.Vector(-obj.xLocationOffset, -obj.yLocationOffset, 0))
    return lid_shape.removeSplitter()


def make_lid_custom(obj: fc.DocumentObject, layout: list[list[bool]]) -> Part.Shape:
    """Create a custom-shape lid based on an attachment layout."""
    lid_width, lid_height, radius, inset_offset = _lid_outline_params(obj)
    obj.TotalHeight = obj.LidThickness

    plate_solid = custom_shape_features.custom_shape_solid(obj, layout, obj.LidThickness)
    plate_trim = custom_shape_features.custom_shape_trim(obj, layout, inset_offset, inset_offset)
    lid_shape = plate_solid.cut(plate_trim).removeSplitter()
    lid_shape = _apply_lid_chamfer(lid_shape, obj.LidChamfer, -obj.LidThickness, radius)
    lid_shape = custom_shape_features.vertical_edge_fillet(lid_shape, radius)

    lid_shape = _add_handle(lid_shape, obj, inset_offset, lid_width, lid_height)

    lid_shape.translate(fc.Vector(-obj.xLocationOffset, -obj.yLocationOffset, 0))
    return lid_shape.removeSplitter()


def _add_handle(
    lid_shape: Part.Shape,
    obj: fc.DocumentObject,
    inset_offset: fc.Units.Quantity,
    lid_width: fc.Units.Quantity,
    lid_height: fc.Units.Quantity,
) -> Part.Shape:
    """Fuse a handle into the lid and add base blending."""
    if not obj.HandleEnabled:
        return lid_shape
    if (
        obj.HandleLength <= 0 * unitmm
        or obj.HandleWidth <= 0 * unitmm
        or obj.HandleHeight <= 0 * unitmm
    ):
        return lid_shape

    center_x = inset_offset + lid_width / 2 + obj.HandleOffsetX
    center_y = inset_offset + lid_height / 2 + obj.HandleOffsetY
    base = fc.Vector(
        center_x - obj.HandleLength / 2,
        center_y - obj.HandleWidth / 2,
        0,
    )
    handle = _make_handle_shape(obj, center_x, center_y)
    if obj.HandleRotation != 0:
        handle.rotate(fc.Vector(center_x, center_y, 0), fc.Vector(0, 0, 1), obj.HandleRotation)
    handle = _apply_handle_top_fillet(handle, obj.HandleTopRadius)
    fused = lid_shape.fuse(handle)
    return _apply_handle_base_fillet(
        fused,
        base,
        obj.HandleLength,
        obj.HandleWidth,
        obj.HandleBaseRadius,
    )


def _make_handle_shape(
    obj: fc.DocumentObject,
    center_x: fc.Units.Quantity,
    center_y: fc.Units.Quantity,
) -> Part.Shape:
    if obj.HandleCornerRadius > 0 * unitmm:
        max_radius = min(obj.HandleLength, obj.HandleWidth) / 2 - smallmm
        radius = min(obj.HandleCornerRadius, max_radius)
        if radius > 0 * unitmm:
            wire = utils.create_rounded_rectangle(
                obj.HandleLength,
                obj.HandleWidth,
                0,
                radius,
            )
            wire.translate(fc.Vector(center_x, center_y, 0))
            return Part.Face(wire).extrude(fc.Vector(0, 0, obj.HandleHeight))

    base = fc.Vector(
        center_x - obj.HandleLength / 2,
        center_y - obj.HandleWidth / 2,
        0,
    )
    return Part.makeBox(obj.HandleLength, obj.HandleWidth, obj.HandleHeight, base)


def _apply_lid_chamfer(
    lid_shape: Part.Shape,
    chamfer: fc.Units.Quantity,
    bottom_z: fc.Units.Quantity,
    corner_radius: fc.Units.Quantity,
) -> Part.Shape:
    if chamfer <= 0 * unitmm:
        return lid_shape

    max_chamfer = -bottom_z - smallmm
    if corner_radius > 0 * unitmm:
        max_chamfer = min(max_chamfer, corner_radius - smallmm)
    if max_chamfer <= 0 * unitmm:
        return lid_shape
    chamfer = min(chamfer, max_chamfer)

    edges = []
    z_ref = bottom_z.Value
    for edge in lid_shape.Edges:
        v1 = edge.Vertexes[0].Point.z
        v2 = edge.Vertexes[1].Point.z
        if abs(v1 - z_ref) < 1e-4 and abs(v2 - z_ref) < 1e-4:
            edges.append(edge)

    if not edges:
        return lid_shape

    try:
        return lid_shape.makeChamfer(chamfer.Value, edges)
    except Exception:  # noqa: BLE001
        return lid_shape


def _apply_handle_base_fillet(
    lid_shape: Part.Shape,
    base: fc.Vector,
    length: fc.Units.Quantity,
    width: fc.Units.Quantity,
    radius: fc.Units.Quantity,
) -> Part.Shape:
    if radius <= 0 * unitmm:
        return lid_shape

    bbox_min_x = base.x - 1e-4
    bbox_max_x = base.x + length.Value + 1e-4
    bbox_min_y = base.y - 1e-4
    bbox_max_y = base.y + width.Value + 1e-4
    z_ref = 0.0

    edges = []
    for edge in lid_shape.Edges:
        if len(edge.Vertexes) < 2:
            continue
        v1 = edge.Vertexes[0].Point
        v2 = edge.Vertexes[1].Point
        if abs(v1.z - z_ref) > 1e-4 or abs(v2.z - z_ref) > 1e-4:
            continue
        mid = edge.valueAt((edge.FirstParameter + edge.LastParameter) / 2)
        if bbox_min_x <= mid.x <= bbox_max_x and bbox_min_y <= mid.y <= bbox_max_y:
            edges.append(edge)

    if not edges:
        return lid_shape

    try:
        return lid_shape.makeFillet(radius, edges)
    except Exception:  # noqa: BLE001
        return lid_shape


def _apply_handle_top_fillet(handle: Part.Shape, radius: fc.Units.Quantity) -> Part.Shape:
    if radius <= 0 * unitmm:
        return handle

    z_ref = handle.BoundBox.ZMax
    edges = []
    for edge in handle.Edges:
        v1 = edge.Vertexes[0].Point.z
        v2 = edge.Vertexes[1].Point.z
        if abs(v1 - z_ref) < 1e-4 and abs(v2 - z_ref) < 1e-4:
            edges.append(edge)

    if not edges:
        return handle

    try:
        return handle.makeFillet(radius.Value, edges)
    except Exception:  # noqa: BLE001
        return handle
