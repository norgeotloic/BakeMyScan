# Basic usage

Once the add-on is installed, you'll have a new tab available in your **Tool shelf** (the panel on the left of the 3D view, which you can open with **T**), called "InterfaceMmgs" and containing 3 buttons:

![lion](https://user-images.githubusercontent.com/37718992/44309665-62bbdb80-a3ca-11e8-909e-c98561aacffe.jpg)

### 1 - Export a .mesh

The name is quite explicit, you'll be able to export the selected object from blender into a [.mesh file](https://www.ljll.math.upmc.fr/frey/logiciels/Docmedit.dir/Docmedit.html#SECTION00031000000000000000).

You'll want to do so if you wish to use one of the following software (mostly command line tools):

* [tetgen](http://wias-berlin.de/software/index.jsp?id=TetGen&lang=1): volume mesher
* [metis](http://glaros.dtc.umn.edu/gkhome/metis/metis/overview): graph partitioning
* [gmsh](http://gmsh.info/): a FEM (Finite Element Method) mesh generator
* [medit](https://github.com/ISCDtoolbox/Medit): a .mesh file viewer
* [solvers developed at ISCD (Sorbonne Université, Paris)](https://github.com/ISCDtoolbox)
* advanced options from **mmg** (more on this in the "Advanced usage")

Also available from the main menu: **File** -> **Export** -> **MESH (.mesh)**

### 2 - Import a .mesh

Quite explicit also, allows you to import a surface model stored in a .mesh file (for instance an output of one of the previous software) into blender.

Also available from the main menu: **File** -> **Export** -> **MESH (.mesh)**

### 3 - Remesh with mmgs

The core functionnality of this addon!

What it does is simply export the currently selected model to a .mesh file, run mmgs with the created .mesh file as an input, and import the output from mmgs.

When running this operator, you'll be presented with two options:

![options](https://user-images.githubusercontent.com/37718992/44310249-57b97900-a3d3-11e8-814e-5a40712e39f0.png)
