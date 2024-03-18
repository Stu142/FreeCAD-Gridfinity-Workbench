# FreeCAD Workbench-Starterkit

This is a template for a FreeCAD workbench / module. As python-packaging and packaging for FreeCAD is not an easy task, this repository should give a overview of the things learned so far. If all you want is to create an extension for FreeCAD (module, additional gui-stuff, workbench), simple copy this repo and start replacing things.

To try the latest release of this template:
```bash
# Install this template
pip install freecad.workbench_starterkit

# Uninstall (to remove this template)
pip uninstall freecad.workbench_starterkit 
```

## Structure of a workbench:

### Initialization Files

- `init_gui.py`: mandatory for modules adding new functionality to the GUI.
- `__init__.py`: entry function for non-gui FreeCAD and python. Called when you import your package: `from freecad import my_package`

Both of these initialization files are called when the FreeCAD-gui is launched. Launching `freecadcmd` or importing FreeCAD (`import freead`) will call the `__init__.py` file. (*The python import will not yet work on every system, but we are working towards a standartization*).

### Structure
This is the minimal structure of a namespace-package to add a workbench to FreeCAD.

```
freecad/
└── workbench_starterkit/
    ├── __init__.py
    └── init_gui.py
```

**Note:** `init_gui.py` are called at startup of FreeCAD.  
:exclamation: **Do not put very time-intensive code in these files to reduce the start-up time.**


## Naming of FreeCAD modules

Several names are needed:
- **repository-name**  
  The name of the repository AKA `freecad.repository_name`  
  eg.: `freecad.workbench_starterkit`

- **distribution-name**  
  This name is set in the [setup.py](setup.py)  
  eg.: `name='freecad.workbench_starterkit'`

- **package-name**  
  The name of the package which can be imported from python.  
  **Notes:** it's possible that there are several packages in one repository with only one `setup.py`. You **simply specify all packages and modules** in the `packages` section of the `setup.py`.  
  This name **must not contain** any python operator symbols like "-".  
  If the repository contains only one pthon-package it makes sense to choose the same names for the repository-name, python-package and the pypi-package.  
  eg.: `freecad.workbench_starterkit`


## Rules

**The "freecad" namespace is not allowed to be used directly.**  
This means it is not allowed to set any variables in the `__init__.py` of freecad. (But as with python3 this `__init__.py` should not exist anyway, this isn't a problem.) Further it's not allowed to add variables to the freecad-namespace directly. This can introduce name-clashes.  

Examples:  
:x: `freecad.myVariable = 10`  
:+1: `freecad.app.myVariable = 10`


## Testing your module/workbench

If you want to work on your extension you have the following options:

- Start FreeCAD from the root-directory you are working in (eg. workbench_starterkit)
- Simply link the extension to a location where python can find it.
- `pip install -e .` adds the root-directory to easy_install.path.

## Using pip (setuptool or distutlis)

Currently FreeCAD has several ways to install packages: 
1. [Freecad Addon Manager][AddonManager] 
2. [freecad-pluginloader][pluginloader]  

With `pip` and `pypi` a third option is introduced. In addition, utilizing `pip` also provides powerful possibilities to install third party dependencies.

### setup file

The `setup.py` file located in the main directory is a minimal example to get an extension installed. There we are using `setuptools`. If you need advanced options to install your package, please have a look at the [setuptools docs][setuptools].

### versions

It's common practice to include a version-string in the python-package. The version should then be imported to the root-`__init__.py` to use it like this:

```python
import freecad.workbench_starterkit
freecad.workbench_starterkit.__version__
```

In the setup.py we do not have access to the library itself, so the `__version__` must be imported without the assumption that the package is installed. This can be done by running the file directly with `exec`.  

:exclamation:**TODO**: Is there any better way to do this?

### resources

In addition to the `setup.py` there is often the need for a [`MANIFEST.in`][MANIFEST] With this file it's possible to install data like icons, documentation files, ... (everything not directly connected to python).  
To tell `setuptools` to use the `MANIFEST.in` add this line to the setup function in the setup.py:

```python
setup(..., include_package_data=True)
```

### dependencies

you can specify required packages by setting the `install_requires` in the setup-function of the `setup.py`

```python
setup(..., install_requires=['required_package'], ...)
```

### install local

To install your extension locally with pip, do the following from a cmd (windows) or terminal (unix):

```bash
cd <path_to_your_package>
pip install .
```

### uploading your package to pypi

Please have a look at this [pypi twine tutorial][twine].

Be careful with version-numbering. It seems pypi doesn't allow to upload a package with a version smaller then the biggest version of the package uploaded. This seems to be true also for deleted packages and deleted versions.

Once uploaded, the package can be installed with:

```bash
pip install <package-name>
```

## Additional Information

### Projects using this structure

- [pyrate][pyrate] - Optical raytracing based on Python  
- [OpenGlider][OpenGlider] - Python library to build paragliders
- [FCGear][FCGear] - a gear module for FreeCAD
- [freecad_pipintegration][FC_pipintegration] - support pip installable freecad-packages

### Glossary

- **_module_** : a Python source file, which can expose classes, functions and global variables
- **_package_** : a directory containing Python modules.
- **_distribution_** : the artifacts which are created by running the setup.py. Can contain multiple packages.
- **_workbench_** : a _graphical space_ inside the FreeCAD-Gui which adds functionality related to a specific task
- **_namespace-package_** : a package which adds functionality to a specific namespace. For FreeCAD we are talking about packages which are importable with `from freecad import my_package`. (Sometimes it's also called new-style-module)
- **_extension-module_**: a library (`.so` or `.dll`) written in C/C++ which adds the possibility to import this library with python.

### Glossary terms used in this discussion (that may lead to confusion)

- **_freecad-module_**: It's anything available through FreeCAD's python interpreter and placed in FreeCADs directory structure.  
This can be a **module, package, workbench, namespace-package, extension-module**.
- **_new_style_module_**: This refers to **packages** which are added to FreeCAD as **namespace-packages**
- **_old_style_module_**: A **package** which is plugged into FreeCAD by adding it's base-directory to `sys.path` and uses `Init.py` and `InitGui.py` to get initialized by FreeCAD.

### Tip

Due to the fact we are now using the `pktutil-module` to find extensions of FreeCAD, it's possible to use standard-python-paths to place the extension. This is any location which is included in the `sys.path`.  

To get a list of all the locations simple run this code in the FreeCAD-console:

```python
import sys
sys.path
```

--------------------------------------------------------------------------------

[AddonManager]: https://github.com/FreeCAD/FreeCAD-addons
[pluginloader]: https://github.com/microelly2/freecad-pluginloader
[setuptools]: https://setuptools.readthedocs.io/en/latest/
[MANIFEST]: https://docs.python.org/2/distutils/sourcedist.html#commands
[twine]: https://pypi.python.org/pypi/twine
[pyrate]: https://github.com/mess42/pyrate
[OpenGlider]: https://github.com/booya-at/OpenGlider
[FCGear]: https://github.com/looooo/FCGear
[FC_pipintegration]: https://github.com/looooo/freecad_pipintegration
