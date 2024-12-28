import os
import FreeCADGui as Gui
import FreeCAD as App
from freecad.gridfinity_workbench import ICONPATH

try:
    from FreeCADGui import Workbench
except ImportError:
    App.Console.PrintWarning(
        "you are using the GridfinityWorkbench with an old version of FreeCAD (<0.16)")
    App.Console.PrintWarning(
        "the class Workbench is loaded, although not imported: magic")

class GridfinityWorkbench(Workbench):
    """
    class which gets initiated at starup of the gui
    """
    MenuText = "Gridfinity"
    ToolTip = "FreeCAD Gridfinity Workbench"
    Icon = os.path.join(ICONPATH, "gridfinity_workbench_icon.svg")
    toolbox = [
        "CreateBinBlank",
        "CreateBinBase",
        "CreateSimpleStorageBin",
        "CreateEcoBin",
        "CreatePartsBin",
        "CreateBaseplate",
        "CreateMagnetBaseplate",
        "CreateScrewTogetherBaseplate"]

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        here is the place to import all the commands
        """
        from .commands import CreateBinBlank
        from .commands import CreateBinBase
        from .commands import CreateSimpleStorageBin
        from .commands import CreateEcoBin
        from .commands import CreatePartsBin
        from .commands import CreateBaseplate
        from .commands import CreateMagnetBaseplate
        from .commands import CreateScrewTogetherBaseplate

        App.Console.PrintMessage("switching to Gridfinity Workbench\n")

        self.appendToolbar("Gridfinity", self.toolbox)
        self.appendMenu("Gridfinity", self.toolbox)

        Gui.addCommand('CreateBinBlank', CreateBinBlank())
        Gui.addCommand('CreateBinBase', CreateBinBase())
        Gui.addCommand('CreateSimpleStorageBin', CreateSimpleStorageBin())
        Gui.addCommand('CreateEcoBin', CreateEcoBin())
        Gui.addCommand('CreatePartsBin', CreatePartsBin())
        Gui.addCommand('CreateBaseplate', CreateBaseplate())
        Gui.addCommand('CreateMagnetBaseplate', CreateMagnetBaseplate())
        Gui.addCommand('CreateScrewTogetherBaseplate', CreateScrewTogetherBaseplate())


    def Activated(self):
        pass

    def Deactivated(self):
        pass


Gui.addWorkbench(GridfinityWorkbench())

