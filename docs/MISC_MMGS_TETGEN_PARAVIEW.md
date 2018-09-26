### tetgen and paraview to create a slice of a volume mesh

*Warning: you'll have to be familiar with the terminal to reproduce the following example!*

![lionmmgs](https://user-images.githubusercontent.com/37718992/46110735-e72d2580-c1e4-11e8-9938-846fa8f6af8f.jpg)

Here is a way to use other tools to recreate a model similar to the one above, which will require:

* **Optional**: [3D print toolbox add-on](https://daler.github.io/blender-for-3d-printing/printing/3d-print-toolbox.html)
* [tetgen](http://wias-berlin.de/software/index.jsp?id=TetGen&lang=1)
* [paraview](https://www.paraview.org/)
* python

##### 1 - blender: create a 3D printing compatible object
In order to use tetgen and create a volume mesh of your object, you'll have to make sure that it is watertight, and that no faces are intersecting.

If your model is quite simple and you don't want to check it before trying tetgen, please do so.

But if it is a complex model with lots of potentially intersecting parts, you'll want to fix that, as well as making your model watertight ("closed").

To do so, I often use one of :

* The **check all** functionality of the D print toolbox add-on, to make sure that no faces are intersecting. If the check returns some positive results, I then manually fix the mesh. That's a longer, but cleaner approach
* The **Remesh** modifier with smoothing enabled, which will guarantee that my mesh is conform

Once your model is ready, export it to a .mesh file, and open a terminal!

###### 2 - tetgen and mmg3d to fill the mesh with tetrahedra
In order to create tetrahedra (the volume equivalent of triangles for surfaces) inside a surface, I'll use the software tetgen with the following command line:

```
tetgen -pgaA /path/to/myModel.mesh
```

This will create a coarse volumetric mesh inside my surface, which I'll then refine by using **mmg3d** - the volumetric equivalent of **mmgs** - which comes with the installation of mmgs (note the *.1* in the file name):

```
mmg3d /path/to/myModel.1.mesh
```

The file ```/path/to/myModel.1.o.mesh``` is then ready to be fed to paraview, after having been converted to a .vtk file by using the [convertToVTK.py](/scripts/convertToVTK.py) python script present in the **scripts/** directory of this add-on (which you'll have to uncompress if it is still in a .zip format):

```
python /path/to/addon/scripts/convertToVTK.py /path/to/myModel.1.o.mesh
```

On success, a file called ```/path/to/myModel.1.o.vtk``` should have been created, which we'll be ready to slice through!

###### 3 - paraview to slice through the model
I won't enter into the details of paraview, but in order to cut your model you'll have to:

1. Open the .vtk file in paraview
2. Display it with the "Apply button"
3. Add a "Clip" filter, and hit "Apply" to see the effect
4. Check the "Crinkle clip" option in the filter's parameters to display the tetrahedra inside
5. Adjust the clipping plane position, hitting the "Apply" button everytime you do so

Once your object looks as you wish, you can finally export the scene to a .x3d file, import the file in blender, and remove all the necessary stuff from your workspace.

Et voilà! A nice cut-through version of your inital model!
