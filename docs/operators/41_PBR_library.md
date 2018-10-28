# Create a PBR library

This operator creates a library of PBR texture sets from a directory on your computer.

The directory you specify will be **RECURSIVELY** searched for texture files, so **DO NOT USE "C://Users/you" OR "/home/you/"** as those would be very long to search! In my case, all the PBR textures I have downloaded from internet are stored in a directory of my hard drive: */media/loic/Data/textures/*, under different directories depending on their origin (*/media/loic/Data/textures/Texturescom/*, */media/loic/Data/textures/FreePBR* ...).

This function uses the **same function and patterns as described in the "Import" operator (2.1)**, and creates a texture set by identifying patterns having a common suffix. For instance, *wood1_albedo.png* and *wood1_normals.jpeg* will be matched and grouped in a common material named "wood1".

A bunch of cleanup is also done on the file names and to ignore material variations (*wood_007_NORMALS_var1.png* will be kept over *wood_007_NORMALS_var2.png* for instance).

What this operator does is actually creating a global dictionary, *bpy.types.Scene.pbrtextures*, which will be referenced to later. The keys are the material base names, and each element is a new directory which keys are the "channel names", and contain the paths to the associated texture images.

The loaded texture sets will then be available through the ["Load material from library" operator](44_load_material_from_library.md).

## (Most often) free PBR textures

I personally use (mostly) free PBR textures from the following resources:

* [3d-wolf.com](https://www.3d-wolf.com/products/textures.html)
* [textures.com](http://textures.com)
* [freepbr.com](https://freepbr.com/)
* [Renderosity](https://www.renderosity.com/mod/freestuff/?item_id=76206)
* [Milos Belanec's gumroad](https://gumroad.com/milosbelanec)
* [Artem Lebedev's gumroad](https://gumroad.com/l/ekRhc)
* [Sungwoo Lee's gumroad](https://gumroad.com/l/HEZvu)
* [3dtextures.me](https://3dtextures.me/tag/pbr/)
