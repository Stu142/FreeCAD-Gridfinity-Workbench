# This import needs to be first as it set some library paths to use the Freecad python API
import freecad  # noqa: I001,F401

import unittest
from unittest import mock

import FreeCAD
import Part

from freecad.gridfinity_workbench.utils import Utils

Vector = FreeCAD.Vector


class UtilsTest(unittest.TestCase):
    def test_copy_and_translate_empty_list(self) -> None:
        shape = mock.MagicMock(spec=Part.Shape)

        self.assertRaises(ValueError, Utils.copy_and_translate, shape, [])

    def test_copy_and_translate_vector_list(self) -> None:
        shape = mock.MagicMock(spec=Part.Shape)
        vec_list = [FreeCAD.Vector(1, 2, 3), FreeCAD.Vector(4, 5, 6)]

        Utils.copy_and_translate(shape, vec_list)

        self.assertEqual(2, shape.copy.call_count)
        self.assertEqual(2, shape.copy.return_value.translate.call_count)
        for vec in vec_list:
            shape.copy.return_value.translate.assert_has_calls([mock.call(vec)])

    def test_curve_to_wire_empty_list(self) -> None:
        self.assertRaises(ValueError, Utils.curve_to_wire, [])

    def test_curve_to_wire_one_line(self) -> None:
        vertexes = [Vector(0, 0, 0), Vector(10, 0, 0)]
        line = Part.LineSegment(vertexes[0], vertexes[1])

        wire = Utils.curve_to_wire([line])

        self.assertEqual(wire.Length, 10)
        self.assertListEqual(vertexes, [vertex.Point for vertex in wire.Vertexes])

    def test_cuve_to_wire_rectangle(self) -> None:
        line_1 = Part.LineSegment(Vector(0, 0, 0), Vector(10, 0, 0))
        line_2 = Part.LineSegment(Vector(10, 0, 0), Vector(10, 10, 0))
        line_3 = Part.LineSegment(Vector(10, 10, 0), Vector(10, 0, 0))
        line_4 = Part.LineSegment(Vector(10, 0, 0), Vector(0, 0, 0))

        wire = Utils.curve_to_wire([line_1, line_2, line_3, line_4])

        self.assertTrue(wire.isClosed)
        self.assertEqual(wire.Length, 10 * 4)
        self.assertEqual(len(wire.Edges), 4)
