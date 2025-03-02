"""Gridfinity workbench commands module.

Contains command objects representing what should happen on a button press.
"""

# ruff: noqa: D101, D107

import re
from pathlib import Path

import FreeCAD as fc  # noqa: N813
import FreeCADGui as fcg  # noqa: N813

from . import custom_shape, utils
from .features import (
    Baseplate,
    BinBase,
    BinBlank,
    CustomBin,
    EcoBin,
    FoundationGridfinity,
    LBinBlank,
    MagnetBaseplate,
    PartsBin,
    ScrewTogetherBaseplate,
    SimpleStorageBin,
)

ICONDIR = Path(__file__).parent / "icons"

PASCAL_CASE_REGEX = re.compile(r"(?<!^)(?=[A-Z])")


class ViewProviderGridfinity:
    """Gridfinity workbench viewprovider."""

    def __init__(self, obj: fc.DocumentObject, icon_path: Path) -> None:
        # Set this object to the proxy object of the actual view provider
        obj.Proxy = self
        self._check_attr()
        self.icon_path = icon_path or ICONDIR / "gridfinity_workbench_icon.svg"

    def _check_attr(self) -> None:
        """Check for missing attributes.

        Required to set icon_path when reopening after saving.
        """
        if not hasattr(self, "icon_path"):
            self.icon_path = ICONDIR / "gridfinity_workbench_icon.svg"

    def attach(self, vobj: fcg.ViewProviderDocumentObject) -> None:
        """Attach viewproviderdocument object to self."""
        self.vobj = vobj

    def getIcon(self) -> str:  # noqa: N802
        """Get icons path."""
        self._check_attr()
        return self.icon_path

    def dumps(self) -> dict:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        self._check_attr()
        return {"icon_path": self.icon_path}

    def loads(self, state: dict) -> None:
        """Needed for JSON Serialization when saving a file containing gridfinity object."""
        if state and "icon_path" in state:
            self.icon_path = state["icon_path"]


class BaseCommand:
    """Base for gridfinity workbench command.

    A command should derive from this BaseCommand class.

    """

    def __init__(
        self,
        *,
        name: str,
        pixmap: Path,
        menu_text: str,
        tooltip: str,
    ) -> None:
        self.name = name
        self.pixmap = pixmap
        self.menu_text = menu_text
        self.tooltip = tooltip

    def IsActive(self) -> bool:  # noqa: N802
        """Check if command should be active.

        Gridfinity workbench command should only be active when there is an active document.

        Returns:
            bool: True when command is active, otherwise False.

        """
        return fc.ActiveDocument is not None

    def Activated(self) -> None:  # noqa: N802
        """Execute when command is activated."""
        raise NotImplementedError

    def GetResources(self) -> dict[str, str]:  # noqa: N802
        """Get command resources."""
        return {
            "Pixmap": str(self.pixmap),
            "MenuText": self.menu_text,
            "ToolTip": self.tooltip,
        }


class CreateCommand(BaseCommand):
    """Base for gridfinity workbench command.

    Used for commands that always create an object.

    """

    def __init__(
        self,
        *,
        name: str,
        gridfinity_function: type[FoundationGridfinity],
        pixmap: Path,
    ) -> None:
        super().__init__(
            name=name,
            pixmap=pixmap,
            menu_text=f"Gridfinity {PASCAL_CASE_REGEX.sub(' ', name)}",
            tooltip=f"Create a Gridfinty {PASCAL_CASE_REGEX.sub(' ', name)}.",
        )
        self.gridfinity_function = gridfinity_function

    def Activated(self) -> None:  # noqa: N802
        """Execute when command is activated."""
        obj = utils.new_object(self.name)
        if fc.GuiUp:
            ViewProviderGridfinity(obj.ViewObject, str(self.pixmap))

        self.gridfinity_function(obj)

        fc.ActiveDocument.recompute()
        fcg.SendMsgToActiveView("ViewFit")


class CreateBinBlank(CreateCommand):
    def __init__(self) -> None:
        super().__init__(
            name="BinBlank",
            gridfinity_function=BinBlank,
            pixmap=ICONDIR / "BinBlank.svg",
        )


class CreateBinBase(CreateCommand):
    def __init__(self) -> None:
        super().__init__(
            name="BinBase",
            gridfinity_function=BinBase,
            pixmap=ICONDIR / "BinBase.svg",
        )


class CreateSimpleStorageBin(CreateCommand):
    def __init__(self) -> None:
        super().__init__(
            name="SimpleStorageBin",
            gridfinity_function=SimpleStorageBin,
            pixmap=ICONDIR / "SimpleStorageBin.svg",
        )


class CreateEcoBin(CreateCommand):
    def __init__(self) -> None:
        super().__init__(
            name="EcoBin",
            gridfinity_function=EcoBin,
            pixmap=ICONDIR / "eco_bin.svg",
        )


class CreatePartsBin(CreateCommand):
    def __init__(self) -> None:
        super().__init__(
            name="PartsBin",
            gridfinity_function=PartsBin,
            pixmap=ICONDIR / "parts_bin.svg",
        )


class CreateBaseplate(CreateCommand):
    def __init__(self) -> None:
        super().__init__(
            name="Baseplate",
            gridfinity_function=Baseplate,
            pixmap=ICONDIR / "Baseplate.svg",
        )


class CreateMagnetBaseplate(CreateCommand):
    def __init__(self) -> None:
        super().__init__(
            name="MagnetBaseplate",
            gridfinity_function=MagnetBaseplate,
            pixmap=ICONDIR / "magnet_baseplate.svg",
        )


class CreateScrewTogetherBaseplate(CreateCommand):
    def __init__(self) -> None:
        super().__init__(
            name="ScrewTogetherBaseplate",
            gridfinity_function=ScrewTogetherBaseplate,
            pixmap=ICONDIR / "screw_together_baseplate.svg",
        )


class CreateLBinBlank(CreateCommand):
    def __init__(self) -> None:
        super().__init__(
            name="LShapedBlankBin",
            gridfinity_function=LBinBlank,
            pixmap=ICONDIR / "BetaLBinBlank.svg",
        )


class CreateCustomBin(BaseCommand):
    def __init__(self) -> None:
        super().__init__(
            name="CustomBin",
            pixmap=ICONDIR / "CustomBlankBinBeta.svg",
            menu_text="Gridfinity Custom Bin",
            tooltip="Draw a custom shaped bin.",
        )

    def Activated(self) -> None:  # noqa: N802, D102
        layout = custom_shape.get_layout()
        if layout is None:
            return

        obj = utils.new_object(self.name)
        if fc.GuiUp:
            ViewProviderGridfinity(obj.ViewObject, str(self.pixmap))

        CustomBin(obj, layout)

        fc.ActiveDocument.recompute()
        fcg.SendMsgToActiveView("ViewFit")
