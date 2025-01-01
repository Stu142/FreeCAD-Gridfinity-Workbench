import os
import FreeCAD
import FreeCADGui as Gui
from .features import (
    BinBlank,
    BinBase,
    Baseplate,
    SimpleStorageBin,
    MagnetBaseplate,
    ScrewTogetherBaseplate,
    EcoBin,
    PartsBin,
)


class ViewProviderGridfinity(object):
    def __init__(self, obj, icon_fn=None):
        # Set this object to the proxy object of the actual view provider
        obj.Proxy = self
        self._check_attr()
        dirname = os.path.dirname(__file__)
        self.icon_fn = icon_fn or os.path.join(
            dirname, "icons", "gridfinity_workbench_icon.svg"
        )

    def _check_attr(self):
        """Check for missing attributes."""
        if not hasattr(self, "icon_fn"):
            setattr(
                self,
                "icon_fn",
                os.path.join(
                    os.path.dirname(__file__), "icons", "gridfinity_workbench_icon.svg"
                ),
            )

    def attach(self, vobj):
        self.vobj = vobj

    def getIcon(self):
        self._check_attr()
        return self.icon_fn

    def __getstate__(self):
        self._check_attr()
        return {"icon_fn": self.icon_fn}

    def __setstate__(self, state):
        if state and "icon_fn" in state:
            self.icon_fn = state["icon_fn"]


class BaseCommand(object):
    NAME = ""
    GRIDFINITY_FUNCTION = None
    ICONDIR = os.path.join(os.path.dirname(__file__), "icons")

    def __init__(self):
        pass

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        else:
            return True

    def Activated(self):
        Gui.doCommand("import freecad.gridfinity_workbench.commands")
        Gui.doCommandGui(
            "freecad.gridfinity_workbench.commands.{}.create()".format(
                self.__class__.__name__
            )
        )
        FreeCAD.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")

    @classmethod
    def create(cls):
        if FreeCAD.GuiUp:
            # borrowed from threaded profiles
            body = Gui.ActiveDocument.ActiveView.getActiveObject("pdbody")
            part = Gui.ActiveDocument.ActiveView.getActiveObject("part")

            if body:
                obj = FreeCAD.ActiveDocument.addObject(
                    "PartDesign::FeaturePython", cls.NAME
                )
            else:
                obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", cls.NAME)
            ViewProviderGridfinity(obj.ViewObject, cls.Pixmap)
            cls.GRIDFINITY_FUNCTION(obj)

            if body:
                body.addObject(obj)
            elif part:
                part.Group += [obj]
        else:
            obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", cls.NAME)
            cls.GRIDFINITY_FUNCTION(obj)
        return obj

    def GetResources(self):
        return {
            "Pixmap": self.Pixmap,
            "MenuText": self.MenuText,
            "ToolTip": self.ToolTip,
        }


class CreateBinBlank(BaseCommand):
    NAME = "BinBlank"
    GRIDFINITY_FUNCTION = BinBlank
    Pixmap = os.path.join(BaseCommand.ICONDIR, "BinBlank.svg")
    MenuText = "Gridfinity Blank Bin"
    ToolTip = "Create a Gridfinity Blank Bin"


class CreateBinBase(BaseCommand):
    NAME = "BinBase"
    GRIDFINITY_FUNCTION = BinBase
    Pixmap = os.path.join(BaseCommand.ICONDIR, "BinBase.svg")
    MenuText = "Gridfinity Bin Base"
    ToolTip = "Create a Gridfinity Bin Base"


class CreateSimpleStorageBin(BaseCommand):
    NAME = "SimpleStorageBin"
    GRIDFINITY_FUNCTION = SimpleStorageBin
    Pixmap = os.path.join(BaseCommand.ICONDIR, "SimpleStorageBin.svg")
    MenuText = "Gridfinity Simple Storage Bin"
    ToolTip = "Create a Gridfinity Simple Storage Bin"


class CreateEcoBin(BaseCommand):
    NAME = "EcoBin"
    GRIDFINITY_FUNCTION = EcoBin
    Pixmap = os.path.join(BaseCommand.ICONDIR, "eco_bin.svg")
    MenuText = "Gridfinity Eco Bin"
    ToolTip = "Create a Gridfinity Eco Bin"


class CreatePartsBin(BaseCommand):
    NAME = "PartsBin"
    GRIDFINITY_FUNCTION = PartsBin
    Pixmap = os.path.join(BaseCommand.ICONDIR, "parts_bin.svg")
    MenuText = "Gridfinity Parts Bin"
    ToolTip = "Create a Gridfinity Parts Bin"


class CreateBaseplate(BaseCommand):
    NAME = "Baseplate"
    GRIDFINITY_FUNCTION = Baseplate
    Pixmap = os.path.join(BaseCommand.ICONDIR, "Baseplate.svg")
    MenuText = "Gridfinity simple baseplate"
    ToolTip = "Create a Gridfinity Baseplate"


class CreateMagnetBaseplate(BaseCommand):
    NAME = "MagnetBaseplate"
    GRIDFINITY_FUNCTION = MagnetBaseplate
    Pixmap = os.path.join(BaseCommand.ICONDIR, "magnet_baseplate.svg")
    MenuText = "Gridfinity magnet baseplate"
    ToolTip = "Create a Gridfinity Baseplate"


class CreateScrewTogetherBaseplate(BaseCommand):
    NAME = "ScrewTogetherBaseplate"
    GRIDFINITY_FUNCTION = ScrewTogetherBaseplate
    Pixmap = os.path.join(BaseCommand.ICONDIR, "screw_together_baseplate.svg")
    MenuText = "Gridfinity Screw together baseplate"
    ToolTip = "Create a Gridfinity Screw Together Baseplate"
