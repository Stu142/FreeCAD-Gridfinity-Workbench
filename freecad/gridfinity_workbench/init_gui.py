"""Initialize workbench gui.

The file name is given by FreeCAD. FreeCAD uses this file to initialize GUI components.
"""

from pathlib import Path

import FreeCAD as fc  # noqa: N813
import FreeCADGui as fcg  # noqa: N813

try:
    from FreeCADGui import Workbench
except ImportError:
    fc.Console.PrintWarning(
        "you are using the GridfinityWorkbench with an old version of FreeCAD (<0.16)\n"
        "the class Workbench is loaded, although not imported: magic\n",
    )


ICONPATH = Path(__file__).parent / "icons"


class GridfinityWorkbench(Workbench):
    """class which gets initiated at startup of the FreeCAD GUI."""

    MenuText = "Gridfinity"

    ToolTip = "FreeCAD Gridfinity Workbench"

    Icon = str(ICONPATH / "gridfinity_workbench_icon.svg")

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
        from . import commands

        fc.Console.PrintMessage("switching to Gridfinity Workbench\n")

        workbench_commands = {
            "CreateBinBlank": commands.CreateBinBlank(),
            "CreateBinBase": commands.CreateBinBase(),
            "CreateSimpleStorageBin": commands.CreateSimpleStorageBin(),
            "CreateEcoBin": commands.CreateEcoBin(),
            "CreatePartsBin": commands.CreatePartsBin(),
            "CreateBaseplate": commands.CreateBaseplate(),
            "CreateMagnetBaseplate": commands.CreateMagnetBaseplate(),
            "CreateScrewTogetherBaseplate": commands.CreateScrewTogetherBaseplate(),
            "CreateLBinBlank": commands.CreateLBinBlank(),
            "CreateCustomBin": commands.DrawBin(),
            "CreateCustomBaseplate": commands.DrawBaseplate(),
            "StandaloneLabelShelf": commands.StandaloneLabelShelf(),
        }

        for command_name, command in workbench_commands.items():
            fcg.addCommand(command_name, command)

        self.appendToolbar("Gridfinity", list(workbench_commands.keys()))
        self.appendMenu("Gridfinity", list(workbench_commands.keys()))


fcg.addWorkbench(GridfinityWorkbench())

fc.__unit_test__ += ["freecad.gridfinity_workbench.test_gridfinity"]
