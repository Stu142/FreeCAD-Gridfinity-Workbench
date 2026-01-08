"""Type declarations for casting"""

# ruff: noqa: D101, D102, D107, N815

import typing
from typing import Final, TypeVar

import FreeCAD as fc  # noqa: N813

from . import const

CALCULATED_VALUE = 0


class LayoutMixin(fc.DocumentObject):
    GenerationLocation: str = ""
    xLocationOffset: float = 0.0
    yLocationOffset: float = 0.0
    xTotalWidth: float = 0.0
    yTotalWidth: float = 0.0
    xGridSize: float = const.X_GRID_SIZE
    yGridSize: float = const.Y_GRID_SIZE
    Baseplate: bool = False


class RectangleLayoutMixin(LayoutMixin):
    xGridUnits: int = const.X_GRID_UNITS
    yGridUnits: int = const.Y_GRID_UNITS


class SolidShapeMixin(LayoutMixin):
    TotalHeight: float = CALCULATED_VALUE


class BaseMixin(SolidShapeMixin):
    BaseProfileBottomChamfer: float = const.BIN_BASE_BOTTOM_CHAMFER
    BaseProfileVerticalSection: float = const.BIN_BASE_VERTICAL_SECTION
    BaseProfileTopChamfer: float = const.BIN_BASE_TOP_CHAMFER
    BinOuterRadius: float = const.BIN_OUTER_RADIUS
    BinVerticalRadius: float = const.BIN_BASE_VERTICAL_RADIUS
    BinBottomRadius: float = const.BIN_BASE_BOTTOM_RADIUS
    Clearance: float = const.CLEARANCE
    BaseProfileHeight: Final[float] = CALCULATED_VALUE


class BaseplateMixin(BaseMixin):
    BaseplateTopLedgeWidth: float = const.BASEPLATE_TOP_LEDGE_WIDTH


class HoleMixin(SolidShapeMixin):
    MagnetHoles: bool = const.MAGNET_HOLES
    ScrewHoles: bool = const.SCREW_HOLES
    SequentialBridgingLayerHeight: float = const.SEQUENTIAL_BRIDGING_LAYER_HEIGHT
    MagnetHolesShape: str = const.HOLE_SHAPES[0]
    MagnetHoleDiameter: float = const.MAGNET_HOLE_DIAMETER
    MagnetHoleDepth: float = const.MAGNET_HOLE_DEPTH
    ScrewHoleDiameter: float = const.SCREW_HOLE_DIAMETER
    ScrewHoleDepth: float = const.SCREW_HOLE_DEPTH
    MagnetHoleDistanceFromEdge: float = const.MAGNET_HOLE_DISTANCE_FROM_EDGE


class SolidMidSectionMixin(BaseMixin):
    HeightUnits: int = 1
    ## Gridfinity Non Standard Parameters
    CustomHeight: float = 42
    NonStandardHeight: bool = False
    WallThickness: float = 2
    HeightUnitValue: float = const.HEIGHT_UNIT_VALUE


class StackingLipMixin(SolidMidSectionMixin):
    StackingLip: bool = False
    StackingLipNotches: bool = False
    StackingLipTopLedge: float = const.STACKING_LIP_TOP_LEDGE
    StackingLipTopChamfer: float = 0.0
    StackingLipBottomChamfer: float = const.STACKING_LIP_BOTTOM_CHAMFER
    StackingLipVerticalSection: float = const.STACKING_LIP_VERTICAL_SECTION
    StackingLipNotchesChamfer: float = const.STACKING_LIP_NOTCHES_CHAMFER
    StackingLipNotchesRecess: float = const.STACKING_LIP_NOTCHES_RECESS


class SimpleBinMixin(StackingLipMixin, HoleMixin):
    pass


class LabelShelfMixin:
    LabelShelfStyle: str = ""
    LabelShelfPlacement: str = ""
    LabelShelfWidth: float = const.LABEL_SHELF_WIDTH
    LabelShelffloat: float = const.LABEL_SHELF_LENGTH
    LabelShelfAngle: float = const.LABEL_SHELF_ANGLE
    LabelShelfStackingOffset: float = const.LABEL_SHELF_STACKING_OFFSET
    LabelShelfVerticalThickness: float = const.LABEL_SHELF_VERTICAL_THICKNESS


class CompartmentsMixin(SimpleBinMixin, LabelShelfMixin):
    xDividers: int = const.X_DIVIDERS
    yDividers: int = const.Y_DIVIDERS
    InsideFilletRadius: float = const.INSIDE_FILLET_RADIUS
    DividerThickness: float = const.DIVIDER_THICKNESS
    xDividerHeight: float = const.CUSTOM_X_DIVIDER_HEIGHT
    yDividerHeight: float = const.CUSTOM_Y_DIVIDER_HEIGHT
    UsableHeight: float = CALCULATED_VALUE


class EcoCompartmentsMixin(CompartmentsMixin):
    BaseWallThickness: float = const.BASE_WALL_THICKNESS


class ScoopMixin(CompartmentsMixin):
    ScoopRadius: float = const.SCOOP_RADIUS
    Scoop: bool = False


class BaseplateObject(
    RectangleLayoutMixin,
    BaseplateMixin,
):
    pass


class FullBinObject(
    RectangleLayoutMixin,
    StackingLipMixin,
    HoleMixin,
):
    ## Gridfinity Non Standard Parameters
    RecessedTopDepth: float = const.RECESSED_TOP_DEPTH


class StorageBinObject(
    RectangleLayoutMixin,
    ScoopMixin,
):
    pass


class EcoBinObject(
    RectangleLayoutMixin,
    EcoCompartmentsMixin,
):
    pass


GridfinityObject = TypeVar("GridfinityObject", bound=fc.DocumentObject)


def cast(type: type[GridfinityObject], obj: fc.DocumentObject) -> GridfinityObject:
    return typing.cast(GridfinityObject, typing.cast(object, obj))
