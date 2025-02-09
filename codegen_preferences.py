import xml.etree.ElementTree as ET
import re
from pathlib import Path
import sys

pattern = re.compile(r"(?<!^)(?=[A-Z])")
def to_snake_case(name: str) -> str:
    return pattern.sub("_", name).lower()

expected_path = "Mod/Gridfinity"

classes = {
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

getter_code = """
def {snake_case}() -> {type}:
    return _get_{type}("{pascal_case}")
"""

workbench_dir = Path(__file__).parent / "freecad" / "gridfinity_workbench"
ui_dir = workbench_dir / "ui"
output_file = workbench_dir / "preferences" / "auto.py"

def codegen(widget) -> str:
    clazz = widget.attrib["class"]
    if not clazz.startswith("Gui::Pref"):
        return ''
    for t, clazzes in classes.items():
        if clazz in clazzes:
            break
    else:
        print(f"Unrecognized class {clazz}")
        sys.exit(1)

    path = widget.find("./property[@name='prefPath']/cstring").text
    name = widget.find("./property[@name='prefEntry']/cstring").text
    if path != expected_path:
        print(f"Warning: preferences for {name} have path {path!r} instead of {expected_path!r}")
        sys.exit(1)

    return getter_code.format(type=t, pascal_case=name, snake_case=to_snake_case(name))

getters = [
    codegen(widget)
    for file in ui_dir.glob("*.ui")
    for widget in ET.parse(file).getroot().findall(".//widget")
]
getters.sort()

file_prefix = R'''"""This file was auto generated, do not edit it!

If you want to change any function, override it in `__init__.py` in this directory.
If you make changes to the `.ui` files, run `codegen_preferences.py` again to update this file.
"""
# fmt: off

import FreeCAD

# Helpers

_PARAMS = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Gridfinity")
_MAGIC = -987

def _get_float(param: str) -> float:
    res = _PARAMS.GetFloat(param, _MAGIC)
    assert res != _MAGIC
    return res

def _get_int(param: str) -> int:
    res = _PARAMS.GetInt(param, _MAGIC)
    assert res != _MAGIC
    return res

def _get_bool(param: str) -> bool:
    return _PARAMS.GetBool(param, False)

# Preference getters
'''

file_suffix = R'''
# fmt: on
'''

with open(output_file, "w") as f:
    f.write(file_prefix)
    f.write(''.join(getters))
    f.write(file_suffix)