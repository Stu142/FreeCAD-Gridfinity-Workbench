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
    "CreateLBinBlank",
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
        self.commands.remove("CreateLBinBlank")

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

    def test_custom_bin_l(self) -> None:
        custom_shape.custom_bin_dialog = lambda _1, _2: GridDialogData(
            layout=[
                [True, True, True],
                [True, False, False],
            ],
            bin_type="Blank Bin",
        )
        fcg.Command.get("CreateLBinBlank").run()
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
        self.assertAlmostEqual(obj.Shape.Volume, 12606.095388468213)

    def test_screw_together_baseplate(self) -> None:
        fcg.Command.get("CreateScrewTogetherBaseplate").run()
        obj = fcg.ActiveDocument.ActiveObject.Object
        self.assertAlmostEqual(obj.Shape.Volume, 22897.352081257995)
