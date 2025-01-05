# FreeCAD Gridfinity Workbench
This Workbench will generate several variations of parametric Gridfinity bins and baseplates that can be easily customized. Gridfinity was created by Zack Freedman; if you are new, watch the intro video [Zack's intro video](https://www.youtube.com/watch?v=ra_9zU-mnl8).

If you get value from my work on this project, which took a lot of time, consider supporting me at [stu142.com/supportme](https://stu142.com/supportme)

If you want more information about the Gridfinity Spec, check out the documentation I have made at [https://github.com/Stu142/Gridfinity-Documentation](https://github.com/Stu142/Gridfinity-Documentation)

# Customizable Parameters
| Bin Parameters | Baseplate Parameters|
|:-----:|:-------:|
|![bin parameters](/Assets/Images/property_view/bin_properties.png)|![bin parameters](/Assets/Images/property_view/baseplate_properties.png)|

# How to Use
Select the bin or baseplate you wish to edit in the feature tree.
Select the Property view tab on the bottom right and change the values. Hit enter or click on the model viewing area to update the model. 
![tree_view](/Assets/Videos/blank_bin_demo.gif)
![tree_view](/Assets/Videos/storage_bin_demo.gif)

# Bin Generation
|Bin Blank | Simple Storage Bin|Eco Bin|
|:-------:|:-------:|:-------:|
| ![](/Assets/Images/Bins/bin_blank.png)|![](/Assets/Images/Bins/simple_storage_bin.png)|![](/Assets/Images/Bins/eco_bin.png)|
|**Parts Bin**|**Bin Base**|
|![](/Assets/Images/Bins/parts_bin.png)|![](/Assets/Images/Bins/bin_base.png)|

## Bin Bottoms
|Screw and Magnet Bottom|Magnet Bottom|
|:-------:|:-------:|
| ![](/Assets/Images/bin_bottoms/screw_magnet_bottom.png)|![](/Assets/Images/bin_bottoms/magnet_bottom.png)|
|**Screw Bottom**|**Plain**|
|![](/Assets/Images/bin_bottoms/screw_bottom.png)|![](/Assets/Images/bin_bottoms/nothing_bottom.png)|

## Bin Label Shelf
|Center|Full Width|
|:-------:|:-------:|
| ![](/Assets/Images/label/center_label.png)|![](/Assets/Images/label/full_width_label.png)|
|**Left**|**Right**|
|![](/Assets/Images/label/left_label.png)|![](/Assets/Images/label/right_label.png)|

## Bin Other features
| Custom Divider Height|Scoop|
|:-------:|:-------:|
| ![](/Assets/Images/divider_height.png)|![](/Assets/Images/scoop.png)|
# Baseplate Generation
|Baseplate | Magnet Baseplate|Screw Together Baseplate|
|:-------:|:-------:|:-------:|
| ![](/Assets/Images/baseplates/baseplate.png)|![](/Assets/Images/baseplates/magnet_baseplate.png)|![](/Assets/Images/baseplates/screw_baseplate.png)|

# Installation
- Install using the built-in FreeCAD addon manager 
- Alternatively, download and place the files in the FreeCAD/Mod File. 

# Dependencies
- This Workbench has been verified as working on FreeCAD 0.21.1, 0.21.2 and 1.0.0

# Contributions
- Clone this repository
- Create a Pull Request
  - Keep in mind that this repository enforces some coding standards/rules
    - formatting: ruff formatting is used in this repository. Configure ruff as auto formatter in your IDE or run `ruff format`

# Changlog
**2025/01/05 Version 0.7.0**
- Added Hex holes for magnets
- Added Angle Control for stacking Lip

**2024/09/10 Version 0.6.0**
- Added Bin Base generation
- Added custom independent x and y divider height parameter
- Move generation location to 0,0

**2024/04/28 Version 0.5.0**
- Added label shelf generation for parts bin: Center, Full Width, Left, Right 
- Added scoop option for parts bin 
- Added Eco Bin 




