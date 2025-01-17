"""Module containig various utility functions.

The utility functions can be used throughout the Gridfinity
workbench code.
"""

import FreeCAD
import Part


class Utils:
    """Class containing utility functions."""

    @staticmethod
    def copy_and_translate(shape: Part.Shape, vec_list: list[FreeCAD.Vector]) -> Part.Shape:
        """Copy a shape and translates.

        This function copies and translate a shape by a vector for as many times as there are
        vectors in the list.

        Args:
            shape (Part.Shape): Shape to copy.
            vec_list (list[FreeCAD.Vector]): List of vectors wher the copies should be translated
                to.

        Raises:
            ValueError: List is empty
            RuntimeError: Nothing copied.

        Returns:
            Part.Shape: Shape consting of the copies in the locations specified by vec_list.

        """
        if not vec_list:
            msg = "Vector list is empty"
            raise ValueError(msg)

        final_shape: Part.Shape | None = None
        for vec in vec_list:
            tmp = shape.copy()
            tmp = tmp.translate(vec)
            final_shape = tmp if final_shape is None else final_shape.fuse(tmp)

        if final_shape is None:
            msg = "Nothing has been copied"
            raise RuntimeError(msg)

        return final_shape

    @staticmethod
    def curve_to_wire(list_of_items: list[Part.LineSegment]) -> Part.Wire:
        """Make a wire from cuvers (line,linesegment,arc,ect).

        This function accepts all curves and makes it into a wire. Note that the wire should be
        closed.

        Args:
            list_of_items (list[Part.LineSegment]): List of items to convert in a wire.

        Returns:
            Part.Wire: The created wire

        """
        return Part.Wire([item.toShape() for item in list_of_items])
