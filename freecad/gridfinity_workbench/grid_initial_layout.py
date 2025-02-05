from abc import abstractmethod

import FreeCAD

from . import const


class Feature:
    @abstractmethod
    def Make(obj):
        raise NotImplementedError


def _universal_Properties(self, obj: FreeCAD.DocumentObject) -> None:
    """Properties used by all gridfinity objects."""
    ## Generation Location Property

    obj.addProperty(
        "App::PropertyEnumeration",
        "GenerationLocation",
        "Gridfinity",
        "Choose to turn the label shelf on or off",
    )

    obj.GenerationLocation = ["Positive from Origin", "Centered at Origin"]

    obj.addProperty(
        "App::PropertyLength",
        "xLocationOffset",
        "Hidden",
        "Length of the edges of the outline <br> <br> default = 2",
    )
    obj.setEditorMode("xLocationOffset", 2)

    obj.addProperty(
        "App::PropertyLength",
        "yLocationOffset",
        "Hidden",
        "Length of the edges of the outline <br> <br> default = 2",
    )
    obj.setEditorMode("yLocationOffset", 2)

    ## Reference Parameters
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

    obj.addProperty(
        "App::PropertyInteger",
        "xMaxGrids",
        "ReferenceParameters",
        "Overall largest number of grids in x direction",
        1,
    )

    obj.addProperty(
        "App::PropertyInteger",
        "yMaxGrids",
        "ReferenceParameters",
        "Overall largest number of grids in y direction",
        1,
    )
    ## Expert Parameters

    obj.addProperty(
        "App::PropertyLength",
        "xGridSize",
        "zzExpertOnly",
        "Size of the grid in x direction <br> <br> default = 42 mm",
    ).xGridSize = const.X_GRID_SIZE

    obj.addProperty(
        "App::PropertyLength",
        "yGridSize",
        "zzExpertOnly",
        "Size of the grid in y direction <br> <br> default = 42 mm",
    ).yGridSize = const.Y_GRID_SIZE


class RectangleLayout(Feature):
    """Creat layout for rectanlge shaped Gridfinity object and add relevant properties"""

    def __init__(self, obj: FreeCAD.DocumentObject, baseplate_default=False):
        """Create Rectangle Layout.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        """
        _universal_Properties(self, obj)

        ## Standard Gridfinity Parameters
        obj.addProperty(
            "App::PropertyInteger",
            "xGridUnits",
            "Gridfinity",
            "Length of the edges of the outline <br> <br> default = 2",
        ).xGridUnits = const.X_GRID_UNITS

        obj.addProperty(
            "App::PropertyInteger",
            "yGridUnits",
            "Gridfinity",
            "Length of the edges of the outline <br> <br> default = 2",
        ).yGridUnits = const.Y_GRID_UNITS

        ## Hidden Properties
        obj.addProperty(
            "App::PropertyBool",
            "Baseplate",
            "Flags",
            "Is the Gridfinity Object a baseplate",
        ).Baseplate = baseplate_default

        obj.setEditorMode("Baseplate", 2)

    def Make(self, obj: FreeCAD.DocumentObject):
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

        obj.xMaxGrids = obj.xGridUnits

        obj.yMaxGrids = obj.yGridUnits

        if obj.GenerationLocation == "Centered at Origin":
            obj.xLocationOffset = obj.xTotalWidth / 2
            obj.yLocationOffset = obj.yTotalWidth / 2
        else:
            obj.xLocationOffset = 0
            obj.yLocationOffset = 0

        rectangle_layout = [[True for y in range(obj.yGridUnits)] for x in range(obj.xGridUnits)]

        return rectangle_layout


class L_Layout(Feature):
    """Creat layout matrix for L shaped Gridfinity object and add relevant properties"""

    def __init__(self, obj: FreeCAD.DocumentObject, baseplate_default=False):
        """Makes L layout

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            baseplate_default: bool

        """
        _universal_Properties(self, obj)
        ## Gridfinity Parameters

        obj.addProperty(
            "App::PropertyInteger",
            "x1GridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).x1GridUnits = 3
        obj.addProperty(
            "App::PropertyInteger",
            "y1GridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).y1GridUnits = 2
        obj.addProperty(
            "App::PropertyInteger",
            "x2GridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).x2GridUnits = 1
        obj.addProperty(
            "App::PropertyInteger",
            "y2GridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).y2GridUnits = 1

        ## Reference Parameters
        obj.addProperty(
            "App::PropertyLength",
            "x1TotalDimension",
            "ReferenceDimensions",
            "total width of a dimension",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "y1TotalDimension",
            "ReferenceDimensions",
            "total width of b dimension",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "x2TotalDimension",
            "ReferenceDimensions",
            "total width of c dimension",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "y2TotalDimension",
            "ReferenceDimensions",
            "total width of d dimension",
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

    def Make(self, obj: FreeCAD.DocumentObject):
        """Makes L layout

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Extruded part to cut out inside of bin.

        """
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
            obj.y2TotalDimension = obj.y2GridUnits * obj.yGridSize

            obj.xTotalWidth = obj.x1GridUnits * obj.xGridSize - obj.Clearance * 2
            obj.yTotalWidth = obj.y1GridUnits * obj.yGridSize - obj.Clearance * 2

        obj.xMaxGrids = obj.x1GridUnits

        obj.yMaxGrids = obj.y1GridUnits

        if obj.GenerationLocation == "Centered at Origin":
            obj.xLocationOffset = obj.xTotalWidth / 2
            obj.yLocationOffset = obj.yTotalWidth / 2
        else:
            obj.xLocationOffset = 0
            obj.yLocationOffset = 0

        ## L layout matrix creation
        layout = [
            [False for y in range(obj.y1GridUnits)] for x in range(obj.x1GridUnits)
        ]

        for x in range(obj.x1GridUnits):
            for y in range(obj.y1GridUnits):
                if x < obj.x2GridUnits:
                    layout[x][y] = True
                if y < obj.y2GridUnits:
                    layout[x][y] = True

        return layout
