"""Type declarations for casting"""

# ruff: noqa: D101, D102, D107, N815

import typing
from typing import Final, TypeVar

import FreeCAD as fc  # noqa: N813

from . import const

CALCULATED_VALUE = 0

Length = float
Angle = float


class LayoutMixin(fc.DocumentObject):
    GenerationLocation: str = ""
    xLocationOffset: Length = 0.0
    yLocationOffset: Length = 0.0
    xTotalWidth: Length = 0.0
    yTotalWidth: Length = 0.0
    xGridSize: Length = const.X_GRID_SIZE
    yGridSize: Length = const.Y_GRID_SIZE
    Baseplate: bool = False


class RectangleLayoutMixin(LayoutMixin):
    xGridUnits: int = const.X_GRID_UNITS
    yGridUnits: int = const.Y_GRID_UNITS


class SolidShapeMixin(LayoutMixin):
    TotalHeight: Length = CALCULATED_VALUE


class BaseMixin(SolidShapeMixin):
    BaseProfileBottomChamfer: Length = const.BIN_BASE_BOTTOM_CHAMFER
    BaseProfileVerticalSection: Length = const.BIN_BASE_VERTICAL_SECTION
    BaseProfileTopChamfer: Length = const.BIN_BASE_TOP_CHAMFER
    BinOuterRadius: Length = const.BIN_OUTER_RADIUS
    BinVerticalRadius: Length = const.BIN_BASE_VERTICAL_RADIUS
    BinBottomRadius: Length = const.BIN_BASE_BOTTOM_RADIUS
    Clearance: Length = const.CLEARANCE
    BaseProfileHeight: Final[Length] = CALCULATED_VALUE


class BaseplateMixin(BaseMixin):
    BaseplateTopLedgeWidth: Length = const.BASEPLATE_TOP_LEDGE_WIDTH


class HoleMixin(SolidShapeMixin):
    MagnetHoles: bool = const.MAGNET_HOLES
    ScrewHoles: bool = const.SCREW_HOLES
    SequentialBridgingLayerHeight: Length = const.SEQUENTIAL_BRIDGING_LAYER_HEIGHT
    MagnetHolesShape: str = const.HOLE_SHAPES[0]
    MagnetHoleDiameter: Length = const.MAGNET_HOLE_DIAMETER
    MagnetHoleDepth: Length = const.MAGNET_HOLE_DEPTH
    ScrewHoleDiameter: Length = const.SCREW_HOLE_DIAMETER
    ScrewHoleDepth: Length = const.SCREW_HOLE_DEPTH
    MagnetHoleDistanceFromEdge: Length = const.MAGNET_HOLE_DISTANCE_FROM_EDGE


class SolidMidSectionMixin(BaseMixin):
    HeightUnits: int = 1
    ## Gridfinity Non Standard Parameters
    CustomHeight: Length = 42
    NonStandardHeight: bool = False
    WallThickness: Length = 2
    HeightUnitValue: Length = const.HEIGHT_UNIT_VALUE


class StackingLipMixin(SolidMidSectionMixin):
    StackingLip: bool = False
    StackingLipNotches: bool = False
    StackingLipTopLedge: Length = const.STACKING_LIP_TOP_LEDGE
    StackingLipTopChamfer: Length = 0.0
    StackingLipBottomChamfer: Length = const.STACKING_LIP_BOTTOM_CHAMFER
    StackingLipVerticalSection: Length = const.STACKING_LIP_VERTICAL_SECTION
    StackingLipNotchesChamfer: Length = const.STACKING_LIP_NOTCHES_CHAMFER
    StackingLipNotchesRecess: Length = const.STACKING_LIP_NOTCHES_RECESS


class SimpleBinMixin(StackingLipMixin, HoleMixin):
    pass


class LabelShelfMixin:
    LabelShelfStyle: str = ""
    LabelShelfPlacement: str = ""
    LabelShelfWidth: Length = const.LABEL_SHELF_WIDTH
    LabelShelfLength: float = const.LABEL_SHELF_LENGTH
    LabelShelfAngle: Angle = const.LABEL_SHELF_ANGLE
    LabelShelfStackingOffset: Length = const.LABEL_SHELF_STACKING_OFFSET
    LabelShelfVerticalThickness: Length = const.LABEL_SHELF_VERTICAL_THICKNESS


class CompartmentsMixin(SimpleBinMixin, LabelShelfMixin):
    xDividers: int = const.X_DIVIDERS
    yDividers: int = const.Y_DIVIDERS
    InsideFilletRadius: Length = const.INSIDE_FILLET_RADIUS
    DividerThickness: Length = const.DIVIDER_THICKNESS
    xDividerHeight: Length = const.CUSTOM_X_DIVIDER_HEIGHT
    yDividerHeight: Length = const.CUSTOM_Y_DIVIDER_HEIGHT
    UsableHeight: Length = CALCULATED_VALUE


class EcoCompartmentsMixin(CompartmentsMixin):
    BaseWallThickness: Length = const.BASE_WALL_THICKNESS


class ScoopMixin(CompartmentsMixin):
    ScoopRadius: Length = const.SCOOP_RADIUS
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
    RecessedTopDepth: Length = const.RECESSED_TOP_DEPTH


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
