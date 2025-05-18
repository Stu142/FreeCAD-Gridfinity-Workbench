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

    def test_copy_in_grid_x_count_0(self) -> None:
        shape = mock.MagicMock(spec=Part.Shape)
        self.assertRaises(
            ValueError,
            utils.copy_in_grid,
            shape,
            x_count=0,
            y_count=1,
            x_offset=0,
            y_offset=0,
        )

    def test_copy_in_grid_y_count_0(self) -> None:
        shape = mock.MagicMock(spec=Part.Shape)
        self.assertRaises(
            ValueError,
            utils.copy_in_grid,
            shape,
            x_count=1,
            y_count=0,
            x_offset=0,
            y_offset=0,
        )

    def test_copy_in_grid(self) -> None:
        shape = mock.MagicMock(spec=Part.Shape)
        shapes = utils.copy_in_grid(shape, x_count=2, y_count=3, x_offset=10, y_offset=5)
        shape.translated.assert_has_calls(
            [
                mock.call(fc.Vector(0, 0, 0)),
                mock.call(fc.Vector(0, 5, 0)),
                mock.call(fc.Vector(0, 10, 0)),
                mock.call(fc.Vector(10, 0, 0)),
                mock.call(fc.Vector(10, 5, 0)),
                mock.call(fc.Vector(10, 10, 0)),
            ],
        )
        self.assertEqual(shapes, shape.translated().multiFuse())

    def test_copy_in_corners(self) -> None:
        shape = mock.MagicMock(spec=Part.Shape)
        x, y, z = 3, 4, 5
        utils.copy_in_corners(shape, x, y, z)
        shape.translated.assert_has_calls(
            [
                mock.call(fc.Vector(-x, -y, z)),
                mock.call(fc.Vector(x, -y, z)),
                mock.call(fc.Vector(-x, y, z)),
                mock.call(fc.Vector(x, y, z)),
            ],
        )

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

    def test_rounded_rectangle_chamfer(self) -> None:
        x_width, y_width, height, radius = 5, 10, 4, 2
        shape = utils.rounded_rectangle_chamfer(x_width, y_width, 0, height, radius)
        self.assertAlmostEqual(shape.BoundBox.XLength, x_width + 2 * height)
        self.assertAlmostEqual(shape.BoundBox.YLength, y_width + 2 * height)
        self.assertAlmostEqual(shape.BoundBox.ZLength, height)
        self.assertAlmostEqual(shape.Volume, 465.8170906488923)

    def test_rounded_rectangle_extrude(self) -> None:
        x_width, y_width, height, radius = 5, 10, 4, 2
        shape = utils.rounded_rectangle_extrude(x_width, y_width, 0, height, radius)
        self.assertAlmostEqual(shape.BoundBox.XLength, x_width)
        self.assertAlmostEqual(shape.BoundBox.YLength, y_width)
        self.assertAlmostEqual(shape.BoundBox.ZLength, height)
        self.assertAlmostEqual(shape.Volume, 186.2654824574367)

    def test_multi_fuse_empty_list(self) -> None:
        self.assertRaises(ValueError, utils.multi_fuse, [])

    def test_multi_fuse_list_of_1(self) -> None:
        lst = [mock.MagicMock(spec=Part.Shape)]
        fuse = utils.multi_fuse(lst)
        lst[0].multiFuse.assert_not_called()
        self.assertEqual(fuse, lst[0])

    def test_multi_fuse_list_of_3(self) -> None:
        lst = [
            mock.MagicMock(spec=Part.Shape),
            mock.MagicMock(spec=Part.Shape),
            mock.MagicMock(spec=Part.Shape),
        ]
        fuse = utils.multi_fuse(lst)
        lst[0].multiFuse.assert_called_once_with(lst[1:])
        self.assertEqual(fuse, lst[0].multiFuse())

    def test_loop_short_list(self) -> None:
        self.assertRaises(ValueError, utils.loop, [])

    def test_loop_3_points(self) -> None:
        vecs = [fc.Vector(0, 0), fc.Vector(0, 2), fc.Vector(2, 1)]
        loop = utils.loop(vecs)

        self.assertEqual(len(loop), len(vecs))

        self.assertEqual(loop[0].StartPoint, vecs[0])
        self.assertEqual(loop[0].EndPoint, vecs[1])

        self.assertEqual(loop[1].StartPoint, vecs[1])
        self.assertEqual(loop[1].EndPoint, vecs[2])

        self.assertEqual(loop[2].StartPoint, vecs[2])
        self.assertEqual(loop[2].EndPoint, vecs[0])

    def test_corners(self) -> None:
        x, y = 3, 4
        points = utils.corners(x, y)
        self.assertEqual(len(points), 4)
        self.assertCountEqual(
            points,
            [fc.Vector(x, y), fc.Vector(-x, y), fc.Vector(-x, -y), fc.Vector(x, -y)],
        )
