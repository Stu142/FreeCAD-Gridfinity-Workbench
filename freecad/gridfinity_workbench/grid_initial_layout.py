"""Makes grid layouts, calculates total width properties."""

import FreeCAD as fc

from . import const
from .gridfinity_types import *


def _location_properties(obj: fc.DocumentObject) -> None:
    """Properties used by all gridfinity objects."""
    obj.addProperty(
        "App::PropertyEnumeration",
        "GenerationLocation",
        "Gridfinity",
        "Location of the bin. Change depending on how you want to customize",
    ).GenerationLocation = ["Positive from Origin", "Centered at Origin"]

    obj.addProperty(
        "App::PropertyLength",
        "xLocationOffset",
        "ShouldBeHidden",
        "changing bin location in the x direction",
        hidden=True,
    )

    obj.addProperty(
        "App::PropertyLength",
        "yLocationOffset",
        "ShouldBeHidden",
        "changing bin location in the y direction",
        hidden=True,
    )


def _total_width_properties(obj: fc.DocumentObject) -> None:
    """Total Width Properties."""
    obj.addProperty(
        "App::PropertyLength",
        "xTotalWidth",
        "ReferenceParameters",
        "total width of Gridfinity object in x direction",
        read_only=True,
    )

    obj.addProperty(
        "App::PropertyLength",
        "yTotalWidth",
        "ReferenceParameters",
        "total width of Gridfinity object in y direction",
        read_only=True,
    )


def _grid_size_properties(obj: fc.DocumentObject) -> None:
    """Grid Size Properties."""
    obj.addProperty(
        "App::PropertyLength",
        "xGridSize",
        "zzExpertOnly",
        "Size of each grid in x direction <br> <br> default = 42 mm",
    ).xGridSize = const.X_GRID_SIZE

    obj.addProperty(
        "App::PropertyLength",
        "yGridSize",
        "zzExpertOnly",
        "Size of each grid in y direction <br> <br> default = 42 mm",
    ).yGridSize = const.Y_GRID_SIZE


def rectangle_layout_properties(obj: fc.DocumentObject, *, baseplate_default: bool) -> None:
    """Create Rectangle Layout.

    Args:
        obj (FreeCAD.DocumentObject): Document object
        baseplate_default (Bool): is Gridfinity Object baseplate

    """
    _location_properties(obj)
    _total_width_properties(obj)
    _grid_size_properties(obj)

    ## Standard Gridfinity Parameters
    obj.addProperty(
        "App::PropertyInteger",
        "xGridUnits",
        "Gridfinity",
        "Number of grid units in the x direction <br> <br> default = 2",
    ).xGridUnits = const.X_GRID_UNITS

    obj.addProperty(
        "App::PropertyInteger",
        "yGridUnits",
        "Gridfinity",
        "Number of grid units in the y direction <br> <br> default = 2",
    ).yGridUnits = const.Y_GRID_UNITS

    ## Hidden Properties
    obj.addProperty(
        "App::PropertyBool",
        "Baseplate",
        "ShouldBeHidden",
        "Is the Gridfinity Object a baseplate",
        hidden=True,
    ).Baseplate = baseplate_default

    ## Expressions
    obj.setExpression(
        "xTotalWidth",
        "xGridUnits * xGridSize - (Baseplate == 1 ? 0mm : 2 * Clearance)",
    )
    obj.setExpression(
        "yTotalWidth",
        "yGridUnits * yGridSize - (Baseplate == 1 ? 0mm : 2 * Clearance)",
    )


def make_rectangle_layout(obj: RectangleLayoutMixin) -> list[list[bool]]:
    """Generate Rectanble layout and calculate relevant parameters."""
    if obj.GenerationLocation == "Centered at Origin":
        if obj.Baseplate:
            obj.xLocationOffset = obj.xTotalWidth / 2
            obj.yLocationOffset = obj.yTotalWidth / 2
        else:
            obj.xLocationOffset = obj.xTotalWidth / 2 + obj.Clearance
            obj.yLocationOffset = obj.yTotalWidth / 2 + obj.Clearance
    else:
        obj.xLocationOffset = 0
        obj.yLocationOffset = 0

    return [[True] * obj.yGridUnits for x in range(obj.xGridUnits)]


def custom_shape_layout_properties(obj: fc.DocumentObject, *, baseplate_default: bool) -> None:
    """Add relevant properties for a custom shape gridfinity object.

    Args:
        obj (FreeCAD.DocumentObject): Document object
        baseplate_default (Bool): is Gridfinity Object baseplate

    """
    _total_width_properties(obj)
    _grid_size_properties(obj)

    _location_properties(obj)
    obj.setEditorMode("GenerationLocation", 2)

    ## Standard Gridfinity Parameters

    ## Hidden Properties
    obj.addProperty(
        "App::PropertyBool",
        "Baseplate",
        "ShouldBeHidden",
        "Is the Gridfinity Object a baseplate",
        hidden=True,
    ).Baseplate = baseplate_default


def make_custom_shape_layout(obj: LayoutMixin, layout: list[list[bool]]) -> None:
    """Calculate values for custom shape.

    Args:
        obj (FreeCAD.DocumentObject): Document object
        layout (list[list[bool]]): Layout of the gridfinity grid.

    """
    x_grid_pos = []
    y_max_pos = []
    y_min_pos = []

    for i, col in enumerate(layout):
        y_grid_pos = [i for i, y in enumerate(col) if y]
        if y_grid_pos:
            y_min_pos.append(min(y_grid_pos))
            y_max_pos.append(max(y_grid_pos))
            x_grid_pos.append(i)

    x_min_grid = min(x_grid_pos) + 1
    x_max_grid = max(x_grid_pos) + 1
    y_min_grid = min(y_min_pos) + 1
    y_max_grid = max(y_max_pos) + 1

    if obj.Baseplate:
        obj.xTotalWidth = (x_max_grid + 1 - x_min_grid) * obj.xGridSize
        obj.yTotalWidth = (y_max_grid + 1 - y_min_grid) * obj.yGridSize
    else:
        obj.xTotalWidth = (x_max_grid + 1 - x_min_grid) * obj.xGridSize - obj.Clearance * 2
        obj.yTotalWidth = (y_max_grid + 1 - y_min_grid) * obj.yGridSize - obj.Clearance * 2
