"""Initialize workbench gui.

The file name is given by FreeCAD. FreeCAD uses this file to initialize GUI components.
"""

from pathlib import Path
from typing import ClassVar

import FreeCADGui
import FreeCAD


try:
    from FreeCADGui import Workbench

except ImportError:
    FreeCAD.Console.PrintWarning(
        "you are using the GridfinityWorkbench with an old version of FreeCAD (<0.16)",
    )

    FreeCAD.Console.PrintWarning(
        "the class Workbench is loaded, although not imported: magic",
    )


ICONPATH = Path(__file__).parent / "icons"


class GridfinityWorkbench(Workbench):
    """class which gets initiated at startup of the FreeCAD GUI."""

    MenuText = "Gridfinity"

    ToolTip = "FreeCAD Gridfinity Workbench"

    Icon = str(ICONPATH / "gridfinity_workbench_icon.svg")

    toolbox: ClassVar[list[str]] = [
        "CreateBinBlank",
        "CreateBinBase",
        "CreateSimpleStorageBin",
        "CreateEcoBin",
        "CreatePartsBin",
        "CreateBaseplate",
        "CreateMagnetBaseplate",
        "CreateScrewTogetherBaseplate",
        "CreateLBinBlank",
    ]

    def GetClassName(self) -> str:  # noqa: N802
        """Get freecad internal class name.

        Returns:
            str: c++ style class name

        """
        return "Gui::PythonWorkbench"

    def Initialize(self) -> None:  # noqa: N802
        """Initialize workbench.

        This function is called at the first activation of the workbench.
        here is the place to import all the commands.
        """
        from .commands import (
            CreateBaseplate,
            CreateBinBase,
            CreateBinBlank,
            CreateEcoBin,
            CreateLBinBlank,
            CreateMagnetBaseplate,
            CreatePartsBin,
            CreateScrewTogetherBaseplate,
            CreateSimpleStorageBin,
        )

        FreeCAD.Console.PrintMessage("switching to Gridfinity Workbench\n")

        self.appendToolbar("Gridfinity", self.toolbox)

        self.appendMenu("Gridfinity", self.toolbox)

        FreeCADGui.addCommand("CreateBinBlank", CreateBinBlank())
        FreeCADGui.addCommand("CreateBinBase", CreateBinBase())
        FreeCADGui.addCommand("CreateSimpleStorageBin", CreateSimpleStorageBin())
        FreeCADGui.addCommand("CreateEcoBin", CreateEcoBin())
        FreeCADGui.addCommand("CreatePartsBin", CreatePartsBin())
        FreeCADGui.addCommand("CreateBaseplate", CreateBaseplate())
        FreeCADGui.addCommand("CreateMagnetBaseplate", CreateMagnetBaseplate())
        FreeCADGui.addCommand("CreateScrewTogetherBaseplate", CreateScrewTogetherBaseplate())
        FreeCADGui.addCommand("CreateLBinBlank", CreateLBinBlank())


FreeCADGui.addWorkbench(GridfinityWorkbench())
