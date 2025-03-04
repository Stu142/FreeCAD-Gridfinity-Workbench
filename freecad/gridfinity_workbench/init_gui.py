"""Initialize workbench gui.

The file name is given by FreeCAD. FreeCAD uses this file to initialize GUI components.
"""

from pathlib import Path
from typing import ClassVar

import FreeCAD as fc  # noqa: N813
import FreeCADGui as fcg  # noqa: N813

try:
    from FreeCADGui import Workbench

except ImportError:
    fc.Console.PrintWarning(
        "you are using the GridfinityWorkbench with an old version of FreeCAD (<0.16)",
    )

    fc.Console.PrintWarning(
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
        "CreateCustomBin",
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
            CreateCustomBin,
            CreateEcoBin,
            CreateLBinBlank,
            CreateMagnetBaseplate,
            CreatePartsBin,
            CreateScrewTogetherBaseplate,
            CreateSimpleStorageBin,
        )

        fc.Console.PrintMessage("switching to Gridfinity Workbench\n")

        self.appendToolbar("Gridfinity", self.toolbox)

        self.appendMenu("Gridfinity", self.toolbox)

        fcg.addCommand("CreateBinBlank", CreateBinBlank())
        fcg.addCommand("CreateBinBase", CreateBinBase())
        fcg.addCommand("CreateSimpleStorageBin", CreateSimpleStorageBin())
        fcg.addCommand("CreateEcoBin", CreateEcoBin())
        fcg.addCommand("CreatePartsBin", CreatePartsBin())
        fcg.addCommand("CreateBaseplate", CreateBaseplate())
        fcg.addCommand("CreateMagnetBaseplate", CreateMagnetBaseplate())
        fcg.addCommand("CreateScrewTogetherBaseplate", CreateScrewTogetherBaseplate())
        fcg.addCommand("CreateLBinBlank", CreateLBinBlank())
        fcg.addCommand("CreateCustomBin", CreateCustomBin())


fcg.addWorkbench(GridfinityWorkbench())

fc.__unit_test__ += ["freecad.gridfinity_workbench.test_gridfinity"]
