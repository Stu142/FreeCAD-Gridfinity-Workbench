"""Custom shape features for bin and baplate generation."""

import FreeCAD as fc  # noqa: N813
import Part

from . import utils
from .feature_construction import _stacking_lip_profile
from .utils import GridfinityLayout


def custom_shape_solid(
    obj: fc.DocumentObject,
    layout: GridfinityLayout,
    height: float,
) -> Part.Shape:
    """Make solid cubes of the gridsize per the layout."""
    grid_box = Part.makeBox(obj.xGridSize, obj.yGridSize, height, fc.Vector(0, 0, -height))
    return utils.copy_in_layout(grid_box, layout, obj.xGridSize, obj.yGridSize)


def custom_shape_trim(
    obj: fc.DocumentObject,
    layout: GridfinityLayout,
    xtrim: fc.Units.Quantity,
    ytrim: fc.Units.Quantity,
) -> Part.Shape:
    """Make outer edge solid to trim edges from custom shape solid."""

    def is_set(x: int, y: int) -> bool:
        return x >= 0 and x < len(layout) and y >= 0 and y < len(layout[x]) and layout[x][y]

    x_trim_box = Part.makeBox(
        xtrim.Value,
        obj.yGridSize + ytrim,
        obj.TotalHeight,
        fc.Vector(0, -ytrim, -obj.TotalHeight),
    )
    y_trim_box = Part.makeBox(
        obj.xGridSize + 2 * xtrim,
        ytrim.Value,
        obj.TotalHeight,
        fc.Vector(-xtrim, 0, -obj.TotalHeight),
    )

    x_vec_list = []
    y_vec_list = []
    for x, col in enumerate(layout):
        for y, cell in enumerate(col):
            if cell:
                if not is_set(x - 1, y):
                    x_vec_list.append(fc.Vector(x * obj.xGridSize, y * obj.yGridSize))
                if not is_set(x + 1, y):
                    x_vec_list.append(
                        fc.Vector((x + 1) * obj.xGridSize - xtrim, y * obj.yGridSize),
                    )
                if not is_set(x, y - 1):
                    y_vec_list.append(fc.Vector(x * obj.xGridSize, y * obj.yGridSize))
                if not is_set(x, y + 1):
                    y_vec_list.append(
                        fc.Vector(x * obj.xGridSize, (y + 1) * obj.yGridSize - ytrim),
                    )

    fuse_total = utils.copy_and_translate(x_trim_box, x_vec_list)

    fuse_total = fuse_total.fuse(utils.copy_and_translate(y_trim_box, y_vec_list))

    return fuse_total


def vertical_edge_fillet(
    solid_shape: Part.Shape,
    radius: float,
) -> Part.Shape:
    """Fillet vertical Edges of input shape."""
    edges = [edge for edge in solid_shape.Edges if edge.Vertexes[0].Z != edge.Vertexes[1].Z]
    return solid_shape.makeFillet(radius, edges)


def _is_concave_edge(edge: Part.Edge, solid: Part.Shape) -> bool:
    """Return true if edge is a concave edge."""
    delta, tolerance = 1, 0.1
    v0, v1 = edge.Vertexes[0], edge.Vertexes[1]
    x, y, z = v0.X, v0.Y, min(v0.Z, v1.Z) + delta  # A point just above the bottom edge.
    steps = [-delta, +delta]  # Size of steps to check around the edge.
    # Test four points around the edge to see how many are inside the solid.
    inside_count = sum(
        solid.isInside(fc.Vector(x + xdelta, y + ydelta, z), tolerance, True)  # noqa: FBT003
        for xdelta in steps
        for ydelta in steps
    )
    # The edge is concave if exactly 3 of the 4 points around (x, y) are inside the solid.
    return inside_count == 3  # noqa: PLR2004


def vertical_edge_fillet_with_concave_edges(
    solid_shape: Part.Shape,
    convex_radius: float,
    concave_radius: float,
) -> Part.Shape:
    """Fillet vertical Edges of input shape."""
    edges = [edge for edge in solid_shape.Edges if edge.Vertexes[0].Z != edge.Vertexes[1].Z]
    concave_edges, convex_edges = [], []
    for edge in edges:
        if _is_concave_edge(edge, solid_shape):
            concave_edges.append(edge)
        else:
            convex_edges.append(edge)
    solid_shape = solid_shape.makeFillet(convex_radius, convex_edges)
    solid_shape = solid_shape.makeFillet(concave_radius, concave_edges)
    return solid_shape


def get_largest_top_wire(solid_shape: Part.Shape, zheight: float) -> Part.Wire:
    """Return the largest wire of the top face of a solid shape."""
    solid_shape = solid_shape.translate(fc.Vector(0, 0, zheight))
    wires = [
        wire
        for wire in solid_shape.Wires
        if wire.Vertexes[0].Point.z == zheight
        and wire.Vertexes[1].Point.z == zheight
        and wire.Vertexes[2].Point.z == zheight
    ]
    return max(wires, key=lambda wire: len(wire.Vertexes))


def custom_shape_stacking_lip(
    obj: fc.DocumentObject,
    solid_shape: Part.Shape,
    layout: GridfinityLayout,
) -> Part.Shape:
    """Create Custom Stacking Lip."""
    bin_outside_shape = get_object_shape(
        obj,
        solid_shape,
        layout,
        obj.Clearance,
        obj.Clearance,
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
    xoffset: fc.Units.Quantity,
    yoffset: fc.Units.Quantity,
) -> Part.Wire:
    """Return wire of object shape."""
    trim = custom_shape_trim(obj, layout, xoffset, yoffset)
    solid_cut = solid_shape.cut(trim)
    solid_cut = solid_cut.removeSplitter()
    solid_rounded = vertical_edge_fillet(solid_cut, obj.BinOuterRadius.Value)
    object_shape_wire = get_largest_top_wire(solid_rounded, 0)

    return object_shape_wire


def clean_up_layout(layout: GridfinityLayout) -> list[list[bool]]:
    """Remove empty rows and colums from the layout."""
    for _ in range(2):
        layout = [row for row in layout if any(row)]
        layout = [list(i) for i in zip(*layout)]

    return layout


def cut_outside_shape(
    obj: fc.DocumentObject,
    bin_outside_solid: Part.Shape,
) -> Part.Shape:
    """Return solid outer boundry of shape to cut away objects protruding from bin."""
    overall_rectangle = utils.rounded_rectangle_extrude(
        obj.xTotalWidth.Value + obj.Clearance.Value * 2,
        obj.yTotalWidth.Value + obj.Clearance.Value * 2,
        -obj.TotalHeight,
        obj.TotalHeight,
        0.01,
    ).translate(
        fc.Vector(obj.xTotalWidth / 2 + obj.Clearance, obj.yTotalWidth / 2 + obj.Clearance),
    )
    perimeter_negative = overall_rectangle.cut(bin_outside_solid)

    return perimeter_negative
