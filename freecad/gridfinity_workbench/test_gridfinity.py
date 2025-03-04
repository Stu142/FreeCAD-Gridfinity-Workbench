import unittest
from pathlib import Path
from tempfile import gettempdir

import FreeCAD as fc  # noqa: N813
import FreeCADGui as fcg  # noqa: N813

tempdir = Path(gettempdir())
doc_name = "GridfinityDocument"


class TestCommands(unittest.TestCase):
    def test_commands_active(self) -> None:
        fc.newDocument(doc_name)
        commands = [
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
        for command_name in commands:
            command = fcg.Command.get(command_name)
            self.assertTrue(command.isActive())
        fc.closeDocument(doc_name)


class TestSave(unittest.TestCase):
    def setUp(self) -> None:
        self.filepath = str(tempdir / self.__class__.__name__) + ".FCStd"

    def test_serialization(self) -> None:
        doc = fc.newDocument(doc_name)
        commands = [
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

        for command_name in commands:
            fcg.Command.get(command_name).run()
        self.assertEqual(len(doc.Objects), len(commands))

        doc.saveAs(str(self.filepath))
        fc.closeDocument(doc_name)

    def test_reopen(self) -> None:
        doc = fc.newDocument(doc_name)

        fcg.Command.get("CreateBinBlank").run()

        doc.saveAs(str(self.filepath))
        fc.closeDocument(doc_name)
        doc = fc.openDocument(self.filepath)

        self.assertEqual(len(doc.Objects), 1)
        obj = doc.Objects[0]

        # change something, so `recompute` is not optimized out
        # (even force=True doesn't guarantee this)
        obj.xGridUnits = 3
        recomputed_count = doc.recompute((obj,), True)  # noqa: FBT003
        self.assertEqual(recomputed_count, 1)
