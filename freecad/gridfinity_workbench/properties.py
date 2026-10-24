PROPERTY_TYPE_BOOLEAN = "App::PropertyBool"
PROPERTY_TYPE_DISTANCE = "App::PropertyDistance"

PROPERTY_SECTION_MAIN = "Gridfinity"
PROPERTY_SECTION_NON_STANDARD = "GridfinityNonStandard"
PROPERTY_SECTION_REFERENCE = "ReferenceParameters"

AUTO_ADDED_PROPERTY_DESCRIPTION = "Automatically added for compatibility."

import FreeCAD as fc
from typing import Any

property_defaults = {
    "MagnetHoleChamfer": (fc.Units.Quantity("0.25 mm"), PROPERTY_TYPE_DISTANCE, PROPERTY_SECTION_NON_STANDARD),
    "MagnetRemoveChannel": (False, PROPERTY_TYPE_BOOLEAN, PROPERTY_SECTION_NON_STANDARD),
    "StackingLipThinStyle": (False, PROPERTY_TYPE_BOOLEAN, PROPERTY_SECTION_MAIN),
}

def get(obj: fc.DocumentObject, property_name: str) -> Any:
    if hasattr(obj, property_name):
        return getattr(obj, property_name)
    elif property_name not in property_defaults:
        raise AttributeError(f"The object '{obj.Name}' is missing the required property '{property_name}' and there is no default value for this property.")
    else:
        property_default_value = property_defaults[property_name][0]
        property_type = property_defaults[property_name][1]
        property_section = property_defaults[property_name][2]
        obj.addProperty(property_type, property_name, property_section, AUTO_ADDED_PROPERTY_DESCRIPTION)
        setattr(obj, property_name, property_default_value)
        return property_default_value
