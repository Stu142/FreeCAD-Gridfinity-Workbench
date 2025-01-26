"""Module containing gridfinity standard dimensions.

Gridfinity Standard Dimensions are placed here, changing theses values will alter the dimensions of
the bins and baseplates generated which may result in non compatable bins. Alternativly you can make
a custom grid size to your liking.
"""

# Global Parameters
GRID_SIZE = 42  # to remove once all bins have independant x and y grid size
X_GRID_SIZE = 42
Y_GRID_SIZE = 42
CLEARANCE = 0.25

MAGNET_HOLE_DIAMETER = 6.5
MAGNET_HOLE_DEPTH = 2.4

SCREW_HOLE_DIAMETER = 3
SCREW_HOLE_DEPTH = 6

MAGNET_HOLE_DISTANCE_FROM_EDGE = 8

# General Bin Parameters
HEIGHT_UNIT = 7 # leaving for teporary compatability. replacing due to naming confusion with other parameters
HEIGHT_UNITS = 6
HEIGHT_UNIT_VALUE = 7
WALL_THICKNESS = 1

MAGNET_HOLES = True
SCREW_HOLES = False

BIN_BASE_BOTTOM_CHAMFER = 0.8
BIN_BASE_VERTICAL_SECTION = 1.8
BIN_BASE_TOP_CHAMFER = 2.15

BIN_OUTER_RADIUS = 3.75
BIN_BASE_VERTICAL_RADIUS = 1.6
BIN_BASE_BOTTOM_RADIUS = 0.8

BIN_UNIT = GRID_SIZE - CLEARANCE * 2

STACKING_LIP = True
STACKING_LIP_TOP_LEDGE = 0.4
STACKING_LIP_BOTTOM_CHAMFER = 0.7
STACKING_LIP_VERTICAL_SECTION = 1.8

RECESSED_TOP_DEPTH = 0
SEQUENTIAL_BRIDGING_LAYER_HEIGHT = 0.2

# Rectangle Bin Defaults
X_GRID_UNITS = 2
Y_GRID_UNITS = 2

# General Baseplate Parameters

BASEPLATE_BOTTOM_CHAMFER = 0.7
BASEPLATE_VERTICAL_SECTION = 1.8
BASEPLATE_TOP_CHAMFER = 1.75
BASEPLATE_TOP_LEDGE_WIDTH = 0.4

BASEPLATE_OUTER_RADIUS = 4.0
BASEPLATE_VERTICAL_RADIUS = 1.85
BASEPLATE_BOTTOM_RADIUS = 1.15

# Magenet baseplate specific
BASEPLATE_SMALL_FILLET = 1
MAGNET_EDGE_THICKNESS = 1.2
MAGNET_BASE = 0.4
MAGNET_BASE_HOLE = 3
MAGNET_CHAMFER = 0.4

# Screw Together Baseplate Specific
CONNECTION_HOLE_DIAMETER = 3.2
MAGNET_BOTTOM_CHAMFER = 2
BASE_THICKNESS = 6.4

# Parts Bin Specific
LABEL_SHELF_WIDTH = 12
LABEL_SHELF_VERTICAL_THICKNESS = 1.2
LABEL_SHELF_LENGTH = 42
LABEL_SHELF_STACKING_OFFSET = 0.4
LABEL_SHELF_ANGLE = 45
SCOOP_RADIUS = 21
