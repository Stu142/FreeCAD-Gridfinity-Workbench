"""Custom shape features for bin and baplate generation."""

import FreeCAD as fc  # noqa: N813
import Part

from . import utils
from .feature_construction import _stacking_lip_profile

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
    for col in layout:
        ytranslate = 0
        for cell in col:
            if cell:
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

    def is_set(x: int, y: int) -> bool:
        return x >= 0 and x < len(layout) and y >= 0 and y < len(layout[x]) and layout[x][y]

    x_trim_box = Part.makeBox(
        xtrim,
        obj.yGridSize.Value + ytrim,
        obj.TotalHeight,
        fc.Vector(0, -ytrim, -obj.TotalHeight),
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
    for x in range(len(layout)):
        ytranslate = 0
        for y in range(len(layout[x])):
            if layout[x][y]:
                if not is_set(x - 1, y):
                    x_vec_list.append(fc.Vector(xtranslate, ytranslate, 0))
                if not is_set(x + 1, y):
                    x_vec_list.append(
                        fc.Vector(xtranslate + obj.xGridSize.Value - xtrim, ytranslate, 0),
                    )
                if not is_set(x, y - 1):
                    y_vec_list.append(fc.Vector(xtranslate, ytranslate, 0))
                if not is_set(x, y + 1):
                    y_vec_list.append(
                        fc.Vector(xtranslate, ytranslate + obj.yGridSize.Value - ytrim, 0),
                    )
            ytranslate += obj.yGridSize.Value
        xtranslate += obj.xGridSize.Value

    fuse_total = utils.copy_and_translate(x_trim_box, x_vec_list)

    fuse_total = fuse_total.fuse(utils.copy_and_translate(y_trim_box, y_vec_list))

    return fuse_total


def vertical_edge_fillet(
    solid_shape: Part.Shape,
    radius: float,
) -> Part.Shape:
    """Fillet vertical Edges of input shape."""
    b_edges = []

    for edge in solid_shape.Edges:
        z0 = edge.Vertexes[0].Point.z
        z1 = edge.Vertexes[1].Point.z

        if z0 != z1:
            b_edges.append(edge)

    return solid_shape.makeFillet(radius, b_edges)


def get_largest_top_wire(solid_shape: Part.Shape, zheight: float) -> Part.Wire:
    """Return the largest wire of the top face of a solid shape."""
    solid_shape = solid_shape.translate(fc.Vector(0, 0, zheight))
    b_wires = []
    b_wire_size = []

    for wire in solid_shape.Wires:
        z0 = wire.Vertexes[0].Point.z
        z1 = wire.Vertexes[1].Point.z
        z2 = wire.Vertexes[2].Point.z

        if z0 == zheight and z1 == zheight and z2 == zheight:
            b_wire_size.append(len(wire.Vertexes))
            b_wires.append(wire)
    i = b_wire_size.index(max(b_wire_size))

    return b_wires[i]


def custom_shape_stacking_lip(
    obj: fc.DocumentObject,
    solid_shape: Part.Shape,
    layout: GridfinityLayout,
) -> Part.Wire:
    """Create Custom Stacking Lip."""
    bin_outside_shape = get_object_shape(
        obj,
        solid_shape,
        layout,
        obj.Clearance.Value,
        obj.Clearance.Value,
        )

    for x in range(len(layout)):
        for y in range(len(layout[x])):
            if layout[x][y]:
                break

        else:
            continue
        break

    wire = _stacking_lip_profile(obj).translate(
        fc.Vector(
            x * obj.xGridSize.Value,
            y * obj.yGridSize.Value,
        ),
    )
    stacking_lip = Part.Wire(bin_outside_shape).makePipe(wire)
    stacking_lip = Part.makeSolid(stacking_lip)

    return stacking_lip

def get_object_shape(
    obj: fc.DocumentObject,
    solid_shape: Part.Shape,
    layout: GridfinityLayout,
    xoffset: float,
    yoffset: float,
    ) -> Part.Wire:
    """Return wire of object shape."""
    trim = custom_shape_trim(obj, layout, xoffset, yoffset)
    solid_cut = solid_shape.cut(trim)
    solid_cut = solid_cut.removeSplitter()
    solid_rounded = vertical_edge_fillet(solid_cut, obj.BinOuterRadius.Value)
    object_shape_wire = get_largest_top_wire(solid_rounded, 0)

    return object_shape_wire

def clean_up_layout(layout: GridfinityLayout)-> None:
    """Remove empty rows and colums from the layout."""
    layout = [row for row in layout if not all(not a for a in row)]
    layout = [list(i) for i in zip(*layout)]
    layout = [row for row in layout if not all(not a for a in row)]
    layout = [list(i) for i in zip(*layout)]

    return layout

def cut_outside_shape(
    obj: fc.DocumentObject,
    bin_outside_shape: Part.Wire,
    )-> Part.Solid:
    """Return solid outer boundry of shape to cut away objects protruding from bin."""
    overall_rectangle = utils.rounded_rectangle_extrude(
        obj.xTotalWidth.Value + obj.Clearance.Value *2,
        obj.yTotalWidth.Value + obj.Clearance.Value *2,
        -obj.TotalHeight,
        obj.TotalHeight,
        0.01).translate(fc.Vector(
            obj.xTotalWidth / 2 + obj.Clearance,
            obj.yTotalWidth / 2 + obj.Clearance,
            ))
    face = Part.Face(bin_outside_shape)
    object_shape_extrude = face.extrude(fc.Vector(0, 0, -obj.TotalHeight))
    perimeter_negative = overall_rectangle.cut(object_shape_extrude)

    return perimeter_negative

