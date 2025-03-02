"""A script to generate python bindings for FreeCAD preferences.

This script parses `.ui` files (which are just XML), and generates a typed python functions for
getting them.

It also runs some checks for the preferences:
- Check if they belong to 'Mod/Gridfinity' group
- Check if there is only a single setter widget for each preference variable
- They have a default value set. This is more needed for code generation itself, as it isn't
  incorrect for the XML to ommit them - default ones are used then.
"""

# ruff: noqa: D103, T201, S314

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

_CLASSES = {
    "float": {
        "Gui::PrefDoubleSpinBox",
    },
    "int": {
        "Gui::PrefSpinBox",
    },
    "bool": {
        "Gui::PrefCheckBox",
    },
}

_WORKBENCH_DIR = Path(__file__).parent / "freecad" / "gridfinity_workbench"
_UI_DIR = _WORKBENCH_DIR / "ui"
_OUTPUT_FILE = _WORKBENCH_DIR / "preferences" / "auto.py"

_EXPECTED_PATH = "Mod/Gridfinity"


def get_value(widget: ET.Element, t: str) -> str | None:
    if t == "float":
        prop = widget.find("./property[@name='value']/double")
    elif t == "int":
        prop = widget.find("./property[@name='value']/number")
    elif t == "bool":
        prop = widget.find("./property[@name='checked']/bool")
        return None if prop is None else prop.text.capitalize()
    else:
        raise AssertionError(f"Unrecognized type {t!r}")
    return None if prop is None else prop.text


preferences = {}

for file in _UI_DIR.glob("*.ui"):
    for widget in ET.parse(file).getroot().findall(".//widget"):
        clazz = widget.attrib["class"]
        if not clazz.startswith("Gui::Pref"):
            continue

        for t, clazzes in _CLASSES.items():  # noqa: B007
            if clazz in clazzes:
                break
        else:
            print(f"Unrecognized class {clazz}")
            sys.exit(1)

        name = widget.find("./property[@name='prefEntry']/cstring").text
        path = widget.find("./property[@name='prefPath']/cstring").text

        if path != _EXPECTED_PATH:
            print(f"Preferences for {name} have path {path!r} instead of {_EXPECTED_PATH!r}")
            sys.exit(1)

        if name in preferences:
            print(f"Multiple preference widgets for entry {name}")
            other_file = preferences[name][0]
            if file == other_file:
                print(f"Both defined in {file.relative_to(_WORKBENCH_DIR)}")
            else:
                print(
                    f"Defined in {other_file.relative_to(_WORKBENCH_DIR)} and"
                    f"{file.relative_to(_WORKBENCH_DIR)}.",
                )
            sys.exit(1)

        value = get_value(widget, t)
        if value is None:
            print(
                f"No default value for property {name!r} of type {t!r} in file "
                f"{file.relative_to(_WORKBENCH_DIR)}",
            )
            print(
                "Try changing it to something different, saving the file, changing it back to"
                "desired value and saving again.",
            )
            sys.exit(1)

        preferences[name] = (file, t, value)


_TO_SNAKE_CASE_PATERN = re.compile(r"(?<!^)(?=[A-Z])")


def to_snake_case(name: str) -> str:
    return _TO_SNAKE_CASE_PATERN.sub("_", name).lower()


_GETTER_CODE = """
def {snake_case}() -> {type}:
    # from {file}
    return _PARAMS.Get{Type}("{pascal_case}", {default})
"""


def codegen(name: str, file: Path, t: str, default: str) -> str:
    return _GETTER_CODE.format(
        type=t,
        Type=t.capitalize(),
        pascal_case=name,
        snake_case=to_snake_case(name),
        default=default,
        file=file.relative_to(_UI_DIR),
    )


getters = [codegen(name, *args) for name, args in preferences.items()]
getters.sort()

_FILE_PREFIX = R'''"""This file was auto generated, do not edit it directly!

If you want to:
- change a default value: do it in a `.ui` file.
- change a paramter name: do it in a `.ui` file.
- customize a function behaviour: override it in `__init__.py` in this directory

If you make changes to the `.ui` files, run `codegen_preferences.py` again to update this file.
"""
# fmt: off

import FreeCAD

_PARAMS = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Gridfinity")
'''

_FILE_SUFFIX = R"""
# fmt: on
"""

with Path.open(_OUTPUT_FILE, "w") as f:
    f.write(_FILE_PREFIX)
    for getter in getters:
        f.write(getter)
    f.write(_FILE_SUFFIX)
