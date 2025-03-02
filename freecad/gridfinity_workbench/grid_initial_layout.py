"""Makes grid layouts, calculates total width properties."""

import FreeCAD as fc  # noqa: N813

from . import const


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
    )
    obj.setEditorMode("xLocationOffset", 2)

    obj.addProperty(
        "App::PropertyLength",
        "yLocationOffset",
        "ShouldBeHidden",
        "changing bin location in the y direction",
    )
    obj.setEditorMode("yLocationOffset", 2)


def _total_width_properties(obj: fc.DocumentObject) -> None:
    """Total Width Properties."""
    obj.addProperty(
        "App::PropertyLength",
        "xTotalWidth",
        "ReferenceParameters",
        "total width of Gridfinity object in x direction",
        1,
    )

    obj.addProperty(
        "App::PropertyLength",
        "yTotalWidth",
        "ReferenceParameters",
        "total width of Gridfinity object in y direction",
        1,
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


class RectangleLayout:
    """Create layout for rectanlge shaped Gridfinity object and add relevant properties."""

    def __init__(self, obj: fc.DocumentObject, *, baseplate_default: bool) -> None:
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
        ).Baseplate = baseplate_default

        obj.setEditorMode("Baseplate", 2)

    def make(self, obj: fc.DocumentObject) -> list[list[bool]]:
        """Generate Rectanble layout and calculate relevant parameters.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            rectangle_layout: 2 dimentional list of feature locations

        """
        if obj.Baseplate:
            obj.xTotalWidth = obj.xGridUnits * obj.xGridSize
            obj.yTotalWidth = obj.yGridUnits * obj.yGridSize
        else:
            obj.xTotalWidth = obj.xGridUnits * obj.xGridSize - obj.Clearance * 2
            obj.yTotalWidth = obj.yGridUnits * obj.yGridSize - obj.Clearance * 2

        if obj.GenerationLocation == "Centered at Origin":
            obj.xLocationOffset = obj.xTotalWidth / 2
            obj.yLocationOffset = obj.yTotalWidth / 2
        else:
            obj.xLocationOffset = 0
            obj.yLocationOffset = 0

        return [[True for y in range(obj.yGridUnits)] for x in range(obj.xGridUnits)]


class LShapedLayout:
    """Creat layout matrix for L shaped Gridfinity object and add relevant properties."""

    def __init__(self, obj: fc.DocumentObject, *, baseplate_default: bool) -> None:
        """Make L layout.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            baseplate_default (bool): Whether the object is a baseplate or not.

        """
        _location_properties(obj)
        _total_width_properties(obj)
        _grid_size_properties(obj)
        ## Gridfinity Parameters

        obj.addProperty(
            "App::PropertyInteger",
            "x1GridUnits",
            "Gridfinity",
            "Overall grid units in the x direction",
        ).x1GridUnits = 3
        obj.addProperty(
            "App::PropertyInteger",
            "y1GridUnits",
            "Gridfinity",
            "Overall grid units in the y direction",
        ).y1GridUnits = 2
        obj.addProperty(
            "App::PropertyInteger",
            "x2GridUnits",
            "Gridfinity",
            "Grid units of L part in the x direction",
        ).x2GridUnits = 1
        obj.addProperty(
            "App::PropertyInteger",
            "y2GridUnits",
            "Gridfinity",
            "Grid units of L part in the y direction",
        ).y2GridUnits = 1

        ## Reference Parameters
        obj.addProperty(
            "App::PropertyLength",
            "x1TotalDimension",
            "ReferenceDimensions",
            "total dimension of the gridfintiy object in the x direction",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "y1TotalDimension",
            "ReferenceDimensions",
            "total dimension of the gridfintiy object in the y direction",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "x2TotalDimension",
            "ReferenceDimensions",
            "total width of the L part in the x direction",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "y2TotalDimension",
            "ReferenceDimensions",
            "total width of the L part in the y direction",
            1,
        )
        ## Hidden Properties
        obj.addProperty(
            "App::PropertyBool",
            "Baseplate",
            "Flags",
            "Is the Gridfinity Object a baseplate",
        ).Baseplate = baseplate_default
        obj.setEditorMode("Baseplate", 2)

    def make(self, obj: fc.DocumentObject) -> list[list[bool]]:
        """Make L layout.

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Extruded part to cut out inside of bin.

        """
        ## Error Checking

        if obj.x2GridUnits >= obj.x1GridUnits:
            obj.x2GridUnits = obj.x1GridUnits - 1
            fc.Console.PrintWarning("x2 Grid Units must be less than x1")
        if obj.y2GridUnits >= obj.y1GridUnits:
            obj.y2GridUnits = obj.y1GridUnits - 1
            fc.Console.PrintWarning("y2 Grid Units must be less than y1")

        ## Calculated Parameters

        if obj.Baseplate:
            obj.x1TotalDimension = obj.x1GridUnits * obj.xGridSize
            obj.y1TotalDimension = obj.y1GridUnits * obj.yGridSize
            obj.x2TotalDimension = obj.x2GridUnits * obj.xGridSize
            obj.y2TotalDimension = obj.y2GridUnits * obj.yGridSize

            obj.xTotalWidth = obj.x1GridUnits * obj.xGridSize
            obj.yTotalWidth = obj.y1GridUnits * obj.yGridSize
        else:
            obj.x1TotalDimension = obj.x1GridUnits * obj.xGridSize - obj.Clearance * 2
            obj.y1TotalDimension = obj.y1GridUnits * obj.yGridSize - obj.Clearance * 2
            obj.x2TotalDimension = obj.x2GridUnits * obj.xGridSize - obj.Clearance * 2
            obj.y2TotalDimension = obj.y2GridUnits * obj.yGridSize - obj.Clearance * 2

            obj.xTotalWidth = obj.x1GridUnits * obj.xGridSize - obj.Clearance * 2
            obj.yTotalWidth = obj.y1GridUnits * obj.yGridSize - obj.Clearance * 2

        if obj.GenerationLocation == "Centered at Origin":
            obj.xLocationOffset = obj.xTotalWidth / 2
            obj.yLocationOffset = obj.yTotalWidth / 2
        else:
            obj.xLocationOffset = 0
            obj.yLocationOffset = 0

        return [
            [True] * (obj.y1GridUnits if x < obj.x2GridUnits else obj.y2GridUnits)
            for x in range(obj.x1GridUnits)
        ]


class CustomShapeLayout:
    """Add relevant properties for a custom shape gridfinity object."""

    def __init__(self, obj: fc.DocumentObject, *, baseplate_default: bool) -> None:
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
        ).Baseplate = baseplate_default
        obj.setEditorMode("Baseplate", 2)

    def calc(self, obj: fc.DocumentObject) -> None:
        """Calculate values for custom shape.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        """
        x_grid_pos = []
        y_max_pos = []
        y_min_pos = []

        for i, col in enumerate(self.layout):
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
