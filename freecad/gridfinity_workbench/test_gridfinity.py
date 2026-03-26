import unittest
from pathlib import Path
from tempfile import gettempdir

import FreeCAD as fc  # noqa: N813
import FreeCADGui as fcg  # noqa: N813

from freecad.gridfinity_workbench.custom_shape import GridDialogData

from . import custom_shape

TEMPDIR = Path(gettempdir())
DOC_NAME = "GridfinityDocument"

SIMPLE_COMMANDS = [
    "CreateBinBlank",
    "CreateBinBase",
    "CreateSimpleStorageBin",
    "CreateEcoBin",
    "CreatePartsBin",
    "CreateBaseplate",
    "CreateMagnetBaseplate",
    "CreateScrewTogetherBaseplate",
]

CUSTOM_BIN_COMMANDS = [
    "CreateCustomBin",
    "CreateCustomBaseplate",
]


fcg.activateWorkbench("GridfinityWorkbench")


class TestWithDocument(unittest.TestCase):
    """Base class for test that do everything on an open document.

    If a test fails, the file can be found in temporary directory (/tmp on Linux).
    """

    def setUp(self) -> None:
        self.doc = fc.newDocument(DOC_NAME)
        self.filepath = f"{TEMPDIR / self.__class__.__name__!s}_{self._testMethodName}.FCStd"

    def tearDown(self) -> None:
        self.doc.saveAs(str(self.filepath))
        fc.closeDocument(DOC_NAME)


class TestCommands(unittest.TestCase):
    def test_commands_active(self) -> None:
        commands = SIMPLE_COMMANDS + CUSTOM_BIN_COMMANDS

        for command_name in commands:
            self.assertFalse(fcg.Command.get(command_name).isActive(), msg=command_name)

        fc.newDocument(DOC_NAME)

        for command_name in commands:
            self.assertTrue(fcg.Command.get(command_name).isActive(), msg=command_name)

        fc.closeDocument(DOC_NAME)


class TestSave(unittest.TestCase):
    def test_reopen(self) -> None:
        filepath = str(TEMPDIR / self.__class__.__name__) + ".FCStd"
        commands = SIMPLE_COMMANDS

        doc = fc.newDocument(DOC_NAME)

        for command_name in commands:
            fcg.Command.get(command_name).run()
        self.assertEqual(len(doc.Objects), len(commands))

        doc.saveAs(str(filepath))
        fc.closeDocument(doc.Name)

        doc = fc.openDocument(filepath)

        self.assertEqual(len(doc.Objects), len(commands))

        # change something, so `recompute` is not optimized out
        # (even force=True doesn't guarantee this)
        for obj in doc.Objects:
            obj.xGridSize = 30
        recomputed_count = doc.recompute(None, True)  # noqa: FBT003
        self.assertEqual(recomputed_count, len(commands))

        doc.save()
        fc.closeDocument(doc.Name)


class TestGenerationLocation(TestWithDocument):
    def setUp(self) -> None:
        super().setUp()
        self.commands = SIMPLE_COMMANDS.copy()

    def test_positive_from_origin(self) -> None:
        for command_name in self.commands:
            fcg.Command.get(command_name).run()
            obj = fcg.ActiveDocument.ActiveObject.Object
            if hasattr(obj, "LabelShelfStyle"):
                obj.LabelShelfStyle = "Off"
            if hasattr(obj, "Scoop"):
                obj.Scoop = False
            obj.recompute()
            center = obj.Shape.CenterOfGravity
            self.assertAlmostEqual(center.x, obj.xGridSize.Value, msg=command_name)
            self.assertAlmostEqual(center.y, obj.yGridSize.Value, msg=command_name)

    def test_centered_at_origin(self) -> None:
        for command_name in self.commands:
            fcg.Command.get(command_name).run()
            obj = fcg.ActiveDocument.ActiveObject.Object
            obj.GenerationLocation = "Centered at Origin"
            if hasattr(obj, "LabelShelfStyle"):
                obj.LabelShelfStyle = "Off"
            if hasattr(obj, "Scoop"):
                obj.Scoop = False
            obj.recompute()
            center = obj.Shape.CenterOfGravity
            self.assertAlmostEqual(center.x, 0, msg=command_name)
            self.assertAlmostEqual(center.y, 0, msg=command_name)


class TestVolumes(TestWithDocument):
    def test_custom_bin_rectangle(self) -> None:
        custom_shape.custom_bin_dialog = lambda _1, _2: GridDialogData(
            layout=[[True, True], [True, True]],
            bin_type="Blank Bin",
        )
        fcg.Command.get("CreateBinBlank").run()
        obj1 = fcg.ActiveDocument.ActiveObject.Object
        fcg.Command.get("CreateCustomBin").run()
        obj2 = fcg.ActiveDocument.ActiveObject.Object
        self.assertAlmostEqual(obj1.Shape.Volume, obj2.Shape.Volume)

    def test_bin_blank(self) -> None:
        fcg.Command.get("CreateBinBlank").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        obj.MagnetHoles = False
        obj.recompute()
        self.assertAlmostEqual(obj.Shape.Volume, 288887.4126750665)
        obj.RecessedTopDepth = 3
        obj.recompute()
        self.assertAlmostEqual(obj.Shape.Volume, 270272.25637141115)
        obj.RecessedTopDepth = 0
        obj.StackingLip = False
        obj.recompute()
        self.assertAlmostEqual(obj.Shape.Volume, 286724.9489979051)

    def test_bin_base(self) -> None:
        fcg.Command.get("CreateBinBase").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        obj.MagnetHoles = False
        obj.recompute()
        self.assertAlmostEqual(obj.Shape.Volume, 43118.696363716575)

    def test_bin(self) -> None:
        fcg.Command.get("CreateSimpleStorageBin").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        obj.MagnetHoles = False
        obj.recompute()
        self.assertAlmostEqual(obj.Shape.Volume, 58187.690383500565)
        obj.StackingLip = False
        obj.recompute()
        self.assertAlmostEqual(obj.Shape.Volume, 54707.472846542325)

    def test_eco_bin(self) -> None:
        fcg.Command.get("CreateEcoBin").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        obj.MagnetHoles = False
        obj.recompute()
        self.assertAlmostEqual(obj.Shape.Volume, 24728.976287436377)

    def test_baseplate(self) -> None:
        fcg.Command.get("CreateBaseplate").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        self.assertAlmostEqual(obj.Shape.Volume, 5034.2316047825325)

    def test_magnet_baseplate(self) -> None:
        fcg.Command.get("CreateMagnetBaseplate").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        self.assertAlmostEqual(obj.Shape.Volume, 12622.098661445636)

    def test_magnet_baseplate_hex(self) -> None:
        fcg.Command.get("CreateMagnetBaseplate").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        obj.MagnetHolesShape = "Hex"
        obj.recompute()
        self.assertAlmostEqual(obj.Shape.Volume, 12502.10011889254)

    def test_screw_together_baseplate(self) -> None:
        fcg.Command.get("CreateScrewTogetherBaseplate").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        self.assertAlmostEqual(obj.Shape.Volume, 22913.35535423545)

    def test_bin_blank_integer_regression(self) -> None:
        """2x2 integer bin volume must be unchanged after fractional changes."""
        fcg.Command.get("CreateBinBlank").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        obj.MagnetHoles = False
        obj.recompute()
        self.assertAlmostEqual(obj.Shape.Volume, 288887.4126750665)


class TestFractionalDimensions(TestWithDocument):
    def _make_bin_blank(self, x_units: float, y_units: float) -> fc.DocumentObject:
        fcg.Command.get("CreateBinBlank").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        obj.MagnetHoles = False
        obj.xGridUnits = x_units
        obj.yGridUnits = y_units
        obj.recompute()
        return obj

    def test_fractional_x_smoke(self) -> None:
        """xGridUnits=2.5 must not crash and produce geometry."""
        obj = self._make_bin_blank(2.5, 1.0)
        self.assertGreater(obj.Shape.Volume, 0)

    def test_fractional_x_volume_ordering(self) -> None:
        """vol(2,1) < vol(2.5,1) < vol(3,1)."""
        vol_2 = self._make_bin_blank(2.0, 1.0).Shape.Volume
        vol_25 = self._make_bin_blank(2.5, 1.0).Shape.Volume
        vol_3 = self._make_bin_blank(3.0, 1.0).Shape.Volume
        self.assertLess(vol_2, vol_25)
        self.assertLess(vol_25, vol_3)

    def test_fractional_y_volume_ordering(self) -> None:
        """vol(1,2) < vol(1,2.5) < vol(1,3)."""
        vol_2 = self._make_bin_blank(1.0, 2.0).Shape.Volume
        vol_25 = self._make_bin_blank(1.0, 2.5).Shape.Volume
        vol_3 = self._make_bin_blank(1.0, 3.0).Shape.Volume
        self.assertLess(vol_2, vol_25)
        self.assertLess(vol_25, vol_3)

    def test_both_fractional_volume_ordering(self) -> None:
        """vol(2,1) < vol(2.5,1.5) < vol(3,2)."""
        vol_lo = self._make_bin_blank(2.0, 1.0).Shape.Volume
        vol_mid = self._make_bin_blank(2.5, 1.5).Shape.Volume
        vol_hi = self._make_bin_blank(3.0, 2.0).Shape.Volume
        self.assertLess(vol_lo, vol_mid)
        self.assertLess(vol_mid, vol_hi)

    def test_fractional_centered_at_origin(self) -> None:
        """2.5x1 bin centered at origin should have CenterOfGravity.x ≈ 0."""
        fcg.Command.get("CreateBinBlank").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        obj.MagnetHoles = False
        obj.xGridUnits = 2.5
        obj.yGridUnits = 1.0
        obj.GenerationLocation = "Centered at Origin"
        obj.recompute()
        # Per-cell clearance causes ~0.085mm asymmetry for fractional cells (each fractional
        # cell requires full clearance on all sides to fit half-pitch grids); allow 0.1mm
        self.assertAlmostEqual(obj.Shape.CenterOfGravity.x, 0, delta=0.1)

    def test_fractional_x_magnet_holes_smoke(self) -> None:
        """xGridUnits=2.5 with magnet holes must not crash."""
        fcg.Command.get("CreateBinBlank").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        obj.MagnetHoles = True
        obj.xGridUnits = 2.5
        obj.yGridUnits = 1.0
        obj.recompute()
        self.assertGreater(obj.Shape.Volume, 0)

    def test_fractional_magnet_holes_volume_ordering(self) -> None:
        """Fractional strip wide enough for holes removes more volume than one that is not.

        xGridUnits=2.75 gives a fractional strip of 31.5mm > min_size (22.2mm),
        so holes are placed in the fractional strip.
        xGridUnits=2.5 gives a fractional strip of 21mm < min_size (22.2mm),
        so no holes are placed in the fractional strip.
        The 2.75x1 bin therefore has more hole volume removed than the 2.5x1 bin.
        """
        fcg.Command.get("CreateBinBlank").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        obj.yGridUnits = 1.0

        obj.xGridUnits = 2.75
        obj.MagnetHoles = True
        obj.recompute()
        vol_275_holes = obj.Shape.Volume
        obj.MagnetHoles = False
        obj.recompute()
        vol_275_no_holes = obj.Shape.Volume
        removed_275 = vol_275_no_holes - vol_275_holes

        obj.xGridUnits = 2.5
        obj.MagnetHoles = True
        obj.recompute()
        vol_25_holes = obj.Shape.Volume
        obj.MagnetHoles = False
        obj.recompute()
        vol_25_no_holes = obj.Shape.Volume
        removed_25 = vol_25_no_holes - vol_25_holes

        # 2.75x1 has fractional strip holes; 2.5x1 does not — more volume removed
        self.assertGreater(removed_275, removed_25)

    def test_fractional_magnet_remove_channel_smoke(self) -> None:
        """xGridUnits=2.75 with MagnetRemoveChannel must not crash."""
        fcg.Command.get("CreateBinBlank").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        obj.MagnetHoles = True
        obj.MagnetRemoveChannel = True
        obj.xGridUnits = 2.75
        obj.yGridUnits = 1.0
        obj.recompute()
        self.assertGreater(obj.Shape.Volume, 0)
