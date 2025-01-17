"""Gridfinity workbench commands module.

Contains command objects representing what should happen on a button press.
"""

from pathlib import Path

import FreeCAD
import FreeCADGui

from .features import (
    Baseplate,
    BinBase,
    BinBlank,
    EcoBin,
    MagnetBaseplate,
    PartsBin,
    ScrewTogetherBaseplate,
    SimpleStorageBin,
)

ICONDIR = Path(__file__).parent / "icons"


class ViewProviderGridfinity:
    """Gridfinity workbench viewprovider."""

    def __init__(self, obj: FreeCAD.DocumentObject, icon_path: Path) -> None:
        """Create a gridfinity viewprovider.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            icon_path (Path): Path to icon file.

        """
        # Set this object to the proxy object of the actual view provider
        obj.Proxy = self
        self.icon_path = (
            icon_path or Path(__file__).parent / "icons" / "gridfinity_workbench_icon.svg"
        )

    def attach(self, vobj: FreeCADGui.ViewProviderDocumentObject) -> None:
        """Attach viewproviderdocument object to self.

        Args:
            vobj (FreeCADGui.ViewProviderDocumentObject): view provider document object.

        """
        self.vobj = vobj

    def getIcon(self) -> str:  # noqa: N802
        """Get icons path.

        Returns:
            str: path of the icon.

        """
        return self.icon_path


class BaseCommand:
    """Base for gridfinity workbench command.

    A command should derive from this BaseCommand class.

    """

    NAME = ""
    GRIDFINITY_FUNCTION = None

    def IsActive(self) -> bool:  # noqa: N802
        """Check if command should be active.

        Gridfinity workbench command should only be active when there is an active document.

        Returns:
            bool: True when command is active, otherwise False.

        """
        return FreeCAD.ActiveDocument is not None

    def Activated(self) -> None:  # noqa: N802
        """Execute when command is activated."""
        FreeCADGui.doCommand("import freecad.gridfinity_workbench.commands")
        FreeCADGui.doCommandGui(
            f"freecad.gridfinity_workbench.commands.{self.__class__.__name__}.create()",
        )
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.SendMsgToActiveView("ViewFit")

    @classmethod
    def create(cls) -> FreeCAD.DocumentObject:
        """Create the gridfinity workbench object.

        Returns:
            FreeCAD.DocumentObject: FreeCAD object containing gridfinity model and properties.

        """
        if FreeCAD.GuiUp:
            # borrowed from threaded profiles
            body = FreeCADGui.ActiveDocument.ActiveView.getActiveObject("pdbody")
            part = FreeCADGui.ActiveDocument.ActiveView.getActiveObject("part")

            if body:
                obj = FreeCAD.ActiveDocument.addObject(
                    "PartDesign::FeaturePython",
                    cls.NAME,
                )
            else:
                obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", cls.NAME)
            ViewProviderGridfinity(obj.ViewObject, str(cls.Pixmap))
            cls.GRIDFINITY_FUNCTION(obj)

            if body:
                body.addObject(obj)
            elif part:
                part.Group += [obj]
        else:
            obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", cls.NAME)
            cls.GRIDFINITY_FUNCTION(obj)
        return obj

    def GetResources(self) -> dict[str, str]:  # noqa: N802
        """Get command resources.

        Returns:
            dict[str, str]: dictionary witht the resources.

        """
        return {
            "Pixmap": str(self.Pixmap),
            "MenuText": self.MenuText,
            "ToolTip": self.ToolTip,
        }


class CreateBinBlank(BaseCommand):
    """Create Bin Blank command."""

    NAME = "BinBlank"
    GRIDFINITY_FUNCTION = BinBlank
    Pixmap = ICONDIR / "BinBlank.svg"
    MenuText = "Gridfinity Blank Bin"
    ToolTip = "Create a Gridfinity Blank Bin"


class CreateBinBase(BaseCommand):
    """Create Bin Base command."""

    NAME = "BinBase"
    GRIDFINITY_FUNCTION = BinBase
    Pixmap = ICONDIR / "BinBase.svg"
    MenuText = "Gridfinity Bin Base"
    ToolTip = "Create a Gridfinity Bin Base"


class CreateSimpleStorageBin(BaseCommand):
    """Create Simple Storage Bin command."""

    NAME = "SimpleStorageBin"
    GRIDFINITY_FUNCTION = SimpleStorageBin
    Pixmap = ICONDIR / "SimpleStorageBin.svg"
    MenuText = "Gridfinity Simple Storage Bin"
    ToolTip = "Create a Gridfinity Simple Storage Bin"


class CreateEcoBin(BaseCommand):
    """Create Eco Bin command."""

    NAME = "EcoBin"
    GRIDFINITY_FUNCTION = EcoBin
    Pixmap = ICONDIR / "eco_bin.svg"
    MenuText = "Gridfinity Eco Bin"
    ToolTip = "Create a Gridfinity Eco Bin"


class CreatePartsBin(BaseCommand):
    """Create Parts Bin Command."""

    NAME = "PartsBin"
    GRIDFINITY_FUNCTION = PartsBin
    Pixmap = ICONDIR / "parts_bin.svg"
    MenuText = "Gridfinity Parts Bin"
    ToolTip = "Create a Gridfinity Parts Bin"


class CreateBaseplate(BaseCommand):
    """Create Baseplate command."""

    NAME = "Baseplate"
    GRIDFINITY_FUNCTION = Baseplate
    Pixmap = ICONDIR / "Baseplate.svg"
    MenuText = "Gridfinity simple baseplate"
    ToolTip = "Create a Gridfinity Baseplate"


class CreateMagnetBaseplate(BaseCommand):
    """Create Magnet Baseplate command."""

    NAME = "MagnetBaseplate"
    GRIDFINITY_FUNCTION = MagnetBaseplate
    Pixmap = ICONDIR / "magnet_baseplate.svg"
    MenuText = "Gridfinity magnet baseplate"
    ToolTip = "Create a Gridfinity Baseplate"


class CreateScrewTogetherBaseplate(BaseCommand):
    """Create Screw together baseplate command."""

    NAME = "ScrewTogetherBaseplate"
    GRIDFINITY_FUNCTION = ScrewTogetherBaseplate
    Pixmap = ICONDIR / "screw_together_baseplate.svg"
    MenuText = "Gridfinity Screw together baseplate"
    ToolTip = "Create a Gridfinity Screw Together Baseplate"
