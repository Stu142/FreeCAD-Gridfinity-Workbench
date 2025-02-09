"""Custom shape features for bin and baplate generation."""

import Part
import Draft

import FreeCAD as fc  # noqa: N813

from . import utils

GridfinityLayout = list[list[bool]]

unitmm = fc.Units.Quantity("1 mm")
zeromm = fc.Units.Quantity("0 mm")


def custom_shape_solid(
    obj: fc.DocumentObject,
    layout: GridfinityLayout,
    height: float,
) -> Part.Shape:
    """Make solid cubes of the gridsize per the layout."""
    xtranslate = zeromm
    ytranslate = zeromm

    grid_box = Part.makeBox(obj.xGridSize, obj.yGridSize, height, fc.Vector(0, 0, -height))

    vec_list = []
    xtranslate = 0
    for x in range(obj.xMaxGrids):
        ytranslate = 0
        for y in range(obj.yMaxGrids):
            if layout[x][y]:
                vec_list.append(fc.Vector(xtranslate, ytranslate, 0))
            ytranslate += obj.yGridSize.Value
        xtranslate += obj.xGridSize.Value

    fuse_total = utils.copy_and_translate(grid_box, vec_list)

    return fuse_total


def custom_shape_trim(
    obj: fc.DocumentObject,
    layout: GridfinityLayout,
    xtrim: float,
    ytrim: float,
) -> Part.Shape:
    """Make outer edge solid to trim edges from custom shape solid."""
    x_trim_box = Part.makeBox(
        xtrim, obj.yGridSize.Value + ytrim, obj.TotalHeight, fc.Vector(0, -ytrim, -obj.TotalHeight),
    )
    y_trim_box = Part.makeBox(
        obj.xGridSize.Value + xtrim * 2,
        ytrim,
        obj.TotalHeight,
        fc.Vector(-xtrim, 0, -obj.TotalHeight),
    )

    x_vec_list = []
    y_vec_list = []
    xtranslate = 0
    for x in range(obj.xMaxGrids):
        ytranslate = 0
        for y in range(obj.yMaxGrids):
            if layout[x][y]:
                if not layout[x - 1][y]:
                    x_vec_list.append(fc.Vector(xtranslate, ytranslate, 0))
                if not layout[x + 1][y]:
                    x_vec_list.append(
                        fc.Vector(xtranslate + obj.xGridSize.Value - xtrim, ytranslate, 0),
                    )
                if not layout[x][y - 1]:
                    y_vec_list.append(fc.Vector(xtranslate, ytranslate, 0))
                if not layout[x][y + 1]:
                    y_vec_list.append(
                        fc.Vector(xtranslate, ytranslate + obj.yGridSize.Value - ytrim, 0),
                    )
            ytranslate += obj.yGridSize.Value
        xtranslate += obj.xGridSize.Value

    fuse_total = utils.copy_and_translate(x_trim_box, x_vec_list)

    fuse_total = fuse_total.fuse(utils.copy_and_translate(y_trim_box, y_vec_list))

    return fuse_total


def vertical_edge_fillet(
    solid_shape: Part.Shape, radius: float,
) -> Part.Shape:
    """Fillet vertical Edges of input shape."""
    b_edges = []

    for edge in solid_shape.Edges:
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z

        if z0 != z1:
            b_edges.append(edge)

    return solid_shape.makeFillet(radius, b_edges)


def get_wire_shape(solid_shape: Part.Shape, zheight: float) -> Part.Wire:
    """Fillet vertical Edges of input shape."""
    solid_shape = solid_shape.translate(fc.Vector(0, 0, zheight))
    b_wires = []

    for wire in solid_shape.Wires:
        z0 = wire.Vertexes[0].Point.z
        z1 = wire.Vertexes[1].Point.z
        z2 = wire.Vertexes[2].Point.z

        if z0 == zheight and z1 == zheight and z2 == zheight:
            b_wires.append(wire)

    return Part.Face(b_wires)


def custom_shape_stacking_lip(
    obj: fc.DocumentObject, solid_shape: Part.Shape, layout: GridfinityLayout
) -> Part.Wire:
    """Fillet vertical Edges of input shape."""
    wires = []
    offsets = [
        obj.Clearance.Value
        + obj.StackingLipTopLedge.Value
        + obj.StackingLipTopChamfer.Value
        + obj.StackingLipBottomChamfer.Value,
        obj.Clearance.Value + obj.StackingLipTopLedge.Value + obj.StackingLipTopChamfer.Value,
        obj.Clearance.Value + obj.StackingLipTopLedge.Value + obj.StackingLipTopChamfer.Value,
        obj.Clearance.Value + obj.StackingLipTopLedge.Value,
    ]
    z_offsets = [
        0,
        obj.StackingLipBottomChamfer.Value,
        obj.StackingLipBottomChamfer.Value + obj.StackingLipVerticalSection.Value,
        obj.StackingLipBottomChamfer.Value
        + obj.StackingLipVerticalSection.Value
        + obj.StackingLipTopChamfer.Value,
    ]
    fc.Console.PrintMessage(f"{offsets}\n")
    fc.Console.PrintMessage(f"{z_offsets}\n")
    for i in range(len(offsets)):
        trim = custom_shape_trim(obj, layout, offsets[i], offsets[i])
        solid_cut = solid_shape.cut(trim)
        solid_cut = solid_cut.removeSplitter()
        solid_rounded = vertical_edge_fillet(solid_cut, obj.BinOuterRadius.Value - offsets[i])
        wires.append(get_wire_shape(solid_rounded, z_offsets[i]))

    stacking_lip_negative = Part.makeLoft(wires, solid=True, ruled=True)

    stacking_lip_total_height = (
        obj.StackingLipBottomChamfer.Value
        + obj.StackingLipVerticalSection.Value
        + obj.StackingLipTopChamfer.Value
    )
    fuse_total = custom_shape_solid(obj, layout, stacking_lip_total_height)
    fuse_total = fuse_total.cut(
        custom_shape_trim(obj, layout, obj.Clearance.Value, obj.Clearance.Value)
    ).translate(fc.Vector(0, 0, stacking_lip_total_height))
    fuse_total = fuse_total.removeSplitter()
    fuse_total = vertical_edge_fillet(fuse_total, obj.BinOuterRadius.Value)
    fuse_total = fuse_total.cut(stacking_lip_negative)

    return fuse_total
