"""Custom shape features for bin and baplate generation."""

import FreeCAD as fc  # noqa: N813
import Part
from . import const, utils
GridfinityLayout = list[list[bool]]

unitmm = fc.Units.Quantity("1 mm")
zeromm = fc.Units.Quantity("0 mm")

def custom_shape_solid(obj: fc.DocumentObject, layout: GridfinityLayout) -> Part.Shape:

    parts = []
    xtranslate = zeromm
    ytranslate = zeromm

    grid_box = Part.makeBox( obj.xGridSize, obj.yGridSize, obj.TotalHeight, fc.Vector(0, 0, -obj.TotalHeight))

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

def custom_shape_trim(obj: fc.DocumentObject, layout: GridfinityLayout, xtrim: float, ytrim: float) -> Part.Shape:

    x_trim_box = Part.makeBox(xtrim, obj.yGridSize.Value + ytrim, obj.TotalHeight, fc.Vector(0, -ytrim, -obj.TotalHeight))
    y_trim_box = Part.makeBox(obj.xGridSize.Value + xtrim*2, ytrim, obj.TotalHeight, fc.Vector(-xtrim, 0, -obj.TotalHeight))

    x_vec_list = []
    y_vec_list = []
    xtranslate = 0
    for x in range(obj.xMaxGrids):
        ytranslate = 0
        for y in range(obj.yMaxGrids):
            if layout[x][y]:
                if not layout[x-1][y]:
                    x_vec_list.append(fc.Vector(xtranslate, ytranslate, 0))
                if not layout[x+1][y]:
                    x_vec_list.append(fc.Vector(xtranslate + obj.xGridSize.Value - xtrim, ytranslate, 0))
                if not layout[x][y-1]:
                    y_vec_list.append(fc.Vector(xtranslate, ytranslate, 0))
                if not layout[x][y+1]:
                    y_vec_list.append(fc.Vector(xtranslate, ytranslate + obj.yGridSize.Value - ytrim, 0))
            ytranslate += obj.yGridSize.Value
        xtranslate += obj.xGridSize.Value

    fuse_total = utils.copy_and_translate(x_trim_box, x_vec_list)

    fuse_total = fuse_total.fuse(utils.copy_and_translate(y_trim_box, y_vec_list))

    return fuse_total


def vertical_edge_fillet(obj: fc.DocumentObject, layout: GridfinityLayout, xtrim: float, ytrim: float) -> Part.Shape:

    return fuse_total