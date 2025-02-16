# This import needs to be first as it set some library paths to use the Freecad python API
import freecad  # noqa: I001,F401

import unittest
from unittest import mock

import FreeCAD as fc  # noqa:N813
import Part

from freecad.gridfinity_workbench import utils


class UtilsTest(unittest.TestCase):
    def test_copy_and_translate_empty_list(self) -> None:
        shape = mock.MagicMock(spec=Part.Shape)

        self.assertRaises(ValueError, utils.copy_and_translate, shape, [])

    def test_copy_and_translate_vector_list(self) -> None:
        shape = mock.MagicMock(spec=Part.Shape)
        vec_list = [fc.Vector(1, 2, 3), fc.Vector(4, 5, 6)]

        utils.copy_and_translate(shape, vec_list)

        self.assertEqual(2, shape.translated.call_count)

    def test_curve_to_wire_empty_list(self) -> None:
        self.assertRaises(ValueError, utils.curve_to_wire, [])

    def test_curve_to_wire_one_line(self) -> None:
        vertexes = [fc.Vector(0, 0, 0), fc.Vector(10, 0, 0)]
        line = Part.LineSegment(vertexes[0], vertexes[1])

        wire = utils.curve_to_wire([line])

        self.assertEqual(wire.Length, 10)
        self.assertListEqual(vertexes, [vertex.Point for vertex in wire.Vertexes])

    def test_cuve_to_wire_rectangle(self) -> None:
        line_1 = Part.LineSegment(fc.Vector(0, 0, 0), fc.Vector(10, 0, 0))
        line_2 = Part.LineSegment(fc.Vector(10, 0, 0), fc.Vector(10, 10, 0))
        line_3 = Part.LineSegment(fc.Vector(10, 10, 0), fc.Vector(10, 0, 0))
        line_4 = Part.LineSegment(fc.Vector(10, 0, 0), fc.Vector(0, 0, 0))

        wire = utils.curve_to_wire([line_1, line_2, line_3, line_4])

        self.assertTrue(wire.isClosed)
        self.assertEqual(wire.Length, 10 * 4)
        self.assertEqual(len(wire.Edges), 4)

    def test_create_rounded_rectangle_radius_1(self) -> None:
        length, width, radius = 5, 6, 1
        rect = utils.create_rounded_rectangle(length, width, 0, radius)
        self.assertEqual(rect.BoundBox.XLength, length)
        self.assertEqual(rect.BoundBox.YLength, width)
        self.assertAlmostEqual(Part.Face(rect).Area, 29.14159265)

    def test_create_rounded_rectangle_radius_2_5(self) -> None:
        length, width, radius = 7, 8, 2.5
        rect = utils.create_rounded_rectangle(length, width, 0, radius)
        self.assertEqual(rect.BoundBox.XLength, length)
        self.assertEqual(rect.BoundBox.YLength, width)
        self.assertAlmostEqual(Part.Face(rect).Area, 50.63495408)

    def test_create_rounded_rectangle_radius_0(self) -> None:
        length, width, radius = 5, 6, 0
        self.assertRaises(ValueError, utils.create_rounded_rectangle, length, width, 0, radius)

    def test_create_rounded_rectangle_radius_equal_to_half_widhtx(self) -> None:
        length, width, radius = 4, 6, 2
        self.assertRaises(ValueError, utils.create_rounded_rectangle, length, width, 0, radius)

    def test_create_rounded_rectangle_radius_equal_to_half_widhty(self) -> None:
        length, width, radius = 6, 4, 2
        self.assertRaises(ValueError, utils.create_rounded_rectangle, length, width, 0, radius)
