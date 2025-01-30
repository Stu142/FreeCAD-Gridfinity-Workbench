import FreeCAD

from .const import (
    X_GRID_UNITS,
    Y_GRID_UNITS,
    GRID_SIZE,
    X_GRID_SIZE,
    Y_GRID_SIZE,
)

from abc import abstractmethod
from enum import Enum


class Feature:
    @abstractmethod
    def Make(obj):
        raise NotImplementedError()


class RectangleLayout(Feature):
    """Creat layout for rectanlge shaped Gridfinity object and add relevant properties"""

    def __init__(self, obj: FreeCAD.DocumentObject, baseplate_default=False):
        """Create Rectangle Layout.

        Args:
            obj (FreeCAD.DocumentObject): Document object

        """
        ## Standard Gridfinity Parameters
        obj.addProperty(
            "App::PropertyInteger",
            "xGridUnits",
            "Gridfinity",
            "Length of the edges of the outline <br> <br> default = 2",
        ).xGridUnits = X_GRID_UNITS

        obj.addProperty(
            "App::PropertyInteger",
            "yGridUnits",
            "Gridfinity",
            "Length of the edges of the outline <br> <br> default = 2",
        ).yGridUnits = Y_GRID_UNITS

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
        ).xGridSize = X_GRID_SIZE

        obj.addProperty(
            "App::PropertyLength",
            "yGridSize",
            "zzExpertOnly",
            "Size of the grid in y direction <br> <br> default = 42 mm",
        ).yGridSize = Y_GRID_SIZE

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

        rectangle_layout = [[True for y in range(obj.yGridUnits)] for x in range(obj.xGridUnits)]

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

        return rectangle_layout


class l_Layout(Feature):
    def __init__(self, obj: FreeCAD.DocumentObject):
        """makes L layout

        Args:
            obj (FreeCAD.DocumentObject): Document object.
        """

    def Make(self, obj: FreeCAD.DocumentObject):
        """makes L layout

        Args:
            obj (FreeCAD.DocumentObject): Document object.

        Returns:
            Part.Shape: Extruded part to cut out inside of bin.

        """
        # obj.xMaxGrids = len(layout)
        # obj.yMaxGrids = len(layout[0])

        return rectangle_layout
