"""Module supporting version checks and migrations for Gridfinity Workbench objects."""

import FreeCAD as fc  # noqa: N813

from . import const
from .version import __version__


def check_object_version(obj: fc.DocumentObject) -> bool:
    """Check if the object's version matches the current version of the Gridfinity Workbench.

    Returns False if the object's version is different from the current version, indicating that
    the object needs to be updated.
    """
    return str(getattr(obj, "version", "")) == __version__


def migrate_object_version(obj: fc.DocumentObject) -> None:  # noqa: C901
    """Update an object from an older version to the current version.

    This function will check the version of the object against the current
    Gridfinity Workbench version. If they are different, it will update the
    object to the current version.
    """
    if check_object_version(obj):
        return

    ### v0.11.9 Changes ###

    if hasattr(obj, "MagnetHoles"):
        # Add properties for the crush ribs to hold magnets.
        if not hasattr(obj, "CrushRibsCount"):
            obj.addProperty(
                "App::PropertyInteger",
                "CrushRibsCount",
                "GridfinityNonStandard",
                "Number of crush ribs <br><br> default = 12",
            ).CrushRibsCount = const.CRUSH_RIB_N
        if not hasattr(obj, "CrushRibsWaviness"):
            obj.addProperty(
                "App::PropertyFloatConstraint",
                "CrushRibsWaviness",
                "GridfinityNonStandard",
                "Waviness of crush ribs, from range [0, 1]",
            ).CrushRibsWaviness = (const.CRUSH_RIB_WAVINESS, 0, 1, 0.05)

        # MagnetRelief property was renamed to MagnetRemoveChannel
        if not hasattr(obj, "MagnetRemoveChannel"):
            obj.addProperty(
                "App::PropertyBool",
                "MagnetRemoveChannel",
                "GridfinityNonStandard",
                "Toggle the magnet hole remove channel on or off, only used if magnet holes are on",
            ).MagnetRemoveChannel = getattr(obj, "MagnetRelief", False)
        if hasattr(obj, "MagnetRelief"):
            obj.removeProperty("MagnetRelief")

    ### v0.12.0 Changes ###

    # Calculation of UsableHeight was changed to use object Expressions.
    if hasattr(obj, "UsableHeight") and not obj.getExpression("UsableHeight"):
        obj.setExpression("UsableHeight", "TotalHeight - HeightUnitValue")

    # xGridUnits and yGridUnits were changed from int to float properties.
    if hasattr(obj, "xGridUnits") and isinstance(obj.xGridUnits, int):
        xgridunits = obj.xGridUnits
        obj.removeProperty("xGridUnits")
        obj.addProperty(
            "App::PropertyFloat",
            "xGridUnits",
            "Gridfinity",
            "Number of grid units in the x direction <br> <br> default = 2",
        ).xGridUnits = float(xgridunits)

    if hasattr(obj, "yGridUnits") and isinstance(obj.yGridUnits, int):
        ygridunits = obj.yGridUnits
        obj.removeProperty("yGridUnits")
        obj.addProperty(
            "App::PropertyFloat",
            "yGridUnits",
            "Gridfinity",
            "Number of grid units in the y direction <br> <br> default = 2",
        ).yGridUnits = float(ygridunits)

    fc.Console.PrintLog(
        f"Gridfinity Workbench v{__version__}: "
        f"updating '{obj.Name}' object properties from version v{obj.version}.\n"
        f"'{obj.Name}' will be saved with v{__version__} properties.\n",
    )

    # Update the version property to the current version after updating the object.
    obj.version = __version__
    obj.recompute()  # Force re-evaluation of expressions after updating properties.
