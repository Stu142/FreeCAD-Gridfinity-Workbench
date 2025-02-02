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
            "aGridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).aGridUnits = 3
        obj.addProperty(
            "App::PropertyInteger",
            "bGridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).bGridUnits = 1
        obj.addProperty(
            "App::PropertyInteger",
            "cGridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).cGridUnits = 1
        obj.addProperty(
            "App::PropertyInteger",
            "dGridUnits",
            "Gridfinity",
            "Height of the extrusion",
        ).dGridUnits = 1

        ## Reference Parameters
        obj.addProperty(
            "App::PropertyLength",
            "aTotalDimension",
            "ReferenceDimensions",
            "total width of a dimension",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "bTotalDimension",
            "ReferenceDimensions",
            "total width of b dimension",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "cTotalDimension",
            "ReferenceDimensions",
            "total width of c dimension",
            1,
        )
        obj.addProperty(
            "App::PropertyLength",
            "dTotalDimension",
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
            obj.aTotalDimension = obj.aGridUnits * obj.xGridSize
            obj.bTotalDimension = obj.bGridUnits * obj.yGridSize
            obj.cTotalDimension = obj.cGridUnits * obj.xGridSize
            obj.dTotalDimension = obj.dGridUnits * obj.yGridSize

            obj.xTotalWidth = obj.aGridUnits * obj.xGridSize
            obj.yTotalWidth = (obj.bGridUnits + obj.dGridUnits) * obj.yGridSize

        else:
            obj.aTotalDimension = obj.aGridUnits * obj.xGridSize - obj.Clearance * 2
            obj.bTotalDimension = obj.bGridUnits * obj.yGridSize - obj.Clearance * 2
            obj.cTotalDimension = obj.cGridUnits * obj.xGridSize - obj.Clearance * 2
            obj.dTotalDimension = obj.dGridUnits * obj.yGridSize

            obj.xTotalWidth = obj.aGridUnits * obj.xGridSize - obj.Clearance * 2
            obj.yTotalWidth = (obj.bGridUnits + obj.dGridUnits) * obj.yGridSize - obj.Clearance * 2

        obj.xMaxGrids = obj.aGridUnits

        obj.yMaxGrids = obj.bGridUnits + obj.dGridUnits

        if obj.GenerationLocation == "Centered at Origin":
            obj.xLocationOffset = obj.xTotalWidth / 2
            obj.yLocationOffset = obj.yTotalWidth / 2
        else:
            obj.xLocationOffset = 0
            obj.yLocationOffset = 0

        ## L layout matrix creation
        layout = [
            [False for y in range(obj.bGridUnits + obj.dGridUnits)] for x in range(obj.aGridUnits)
        ]

        for x in range(obj.aGridUnits):
            for y in range(obj.bGridUnits + obj.dGridUnits):
                if x < obj.cGridUnits:
                    layout[x][y] = True
                if y < obj.bGridUnits:
                    layout[x][y] = True

        return layout
