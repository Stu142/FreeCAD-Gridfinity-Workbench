"""Gridfinity workbench commands module.

Contains command objects representing what should happen on a button press.
"""

from pathlib import Path

import FreeCAD as fc  # noqa: N813
import FreeCADGui as fcg  # noqa: N813

from .features import (
    Baseplate,
    BinBase,
    BinBlank,
    EcoBin,
    LBinBlank,
    MagnetBaseplate,
    PartsBin,
    ScrewTogetherBaseplate,
    SimpleStorageBin,
    CustomBin,
)

ICONDIR = Path(__file__).parent / "icons"


class ViewProviderGridfinity:
    """Gridfinity workbench viewprovider."""

    def __init__(self, obj: fc.DocumentObject, icon_path: Path) -> None:
        """Create a gridfinity viewprovider.

        Args:
            obj (FreeCAD.DocumentObject): Document object.
            icon_path (Path): Path to icon file.

        """
        # Set this object to the proxy object of the actual view provider
        obj.Proxy = self
        self._check_attr()  # required to set icon_path when reopening a bin after saving
        self.icon_path = (
            icon_path or Path(__file__).parent / "icons" / "gridfinity_workbench_icon.svg"
        )

    def _check_attr(self) -> None:  # required to set icon_path when reopening after saving
        """Check for missing attributes."""
        if not hasattr(self, "icon_path"):
            self.icon_path = Path(__file__).parent / "icons" / "gridfinity_workbench_icon.svg"

    def attach(self, vobj: fcg.ViewProviderDocumentObject) -> None:
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
        # required to set icon_path when reopening a gridfinity object after saving
        self._check_attr()
        return self.icon_path

    def dumps(
        self,
    ) -> None:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        self._check_attr()  # set icon_path when reopening a gridfinity object after saving
        return {"icon_path": self.icon_path}  # ^^

    def loads(
        self,
        state: tuple,
    ) -> None:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        if (
            state and "icon_path" in state
        ):  # set icon_path when reopening a gridfinity object after savin
            self.icon_path = state["icon_path"]  # ^^


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
        return fc.ActiveDocument is not None

    def Activated(self) -> None:  # noqa: N802
        """Execute when command is activated."""
        fcg.doCommand("import freecad.gridfinity_workbench.commands")
        fcg.doCommandGui(
            f"freecad.gridfinity_workbench.commands.{self.__class__.__name__}.create()",
        )
        fc.ActiveDocument.recompute()
        fcg.SendMsgToActiveView("ViewFit")

    @classmethod
    def create(cls) -> fc.DocumentObject:
        """Create the gridfinity workbench object.

        Returns:
            FreeCAD.DocumentObject: FreeCAD object containing gridfinity model and properties.

        """
        if fc.GuiUp:
            # borrowed from threaded profiles
            body = fcg.ActiveDocument.ActiveView.getActiveObject("pdbody")
            part = fcg.ActiveDocument.ActiveView.getActiveObject("part")

            if body:
                obj = fc.ActiveDocument.addObject(
                    "PartDesign::FeaturePython",
                    cls.NAME,
                )
            else:
                obj = fc.ActiveDocument.addObject("Part::FeaturePython", cls.NAME)
            ViewProviderGridfinity(obj.ViewObject, str(cls.Pixmap))
            cls.GRIDFINITY_FUNCTION(obj)

            if body:
                body.addObject(obj)
            elif part:
                part.Group += [obj]
        else:
            obj = fc.ActiveDocument.addObject("Part::FeaturePython", cls.NAME)
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


class CreateLBinBlank(BaseCommand):
    """Create Blank L shaped bin command."""

    NAME = "LBinBlank"
    GRIDFINITY_FUNCTION = LBinBlank
    Pixmap = ICONDIR / "BetaLBinBlank.svg"
    MenuText = "Gridfinity L Shaped Blank Bin"
    ToolTip = "Create a Gridfinity L Shaped Blank Bin"


class CreateCustomBin(BaseCommand):
    """Create a custom bin."""
    NAME = "CustomBin"
    GRIDFINITY_FUNCTION = CustomBin
    Pixmap = ICONDIR / "BetaLBinBlank.svg"
    MenuText = "Gridfinity Custom Bin"
    ToolTip = "Draw a custom shaped bin"
