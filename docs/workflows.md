# Workflows

Here are a few different typical usages of BakeMyScan:

1. [High resolution scan to lowpoly asset](#3d-scan-to-lowpoly)
2. [Bake a complex Cycles nodes material](#bake-a-complex-cycles-material)
3. [Non uniform remeshing with mmgs](#non-uniform-remeshing-with-mmgs)
4. [Volume slice through a model](#volume-slice-through-a-model)

## 3D scan to lowpoly

![ramses](https://user-images.githubusercontent.com/37718992/46110741-e7c5bc00-c1e4-11e8-966e-fa9a9761f01b.jpeg)

During the photogrammetry process, I often end up with .obj or .ply files made of hundreds of thousands of triangles (often between 200k and 5M depending on the software and quality settings used), which are way too heavy to use in game engines or for web visualization.

I therefore wrote the BakeMyScan add-on to be able to reprocess such models to a few thousands triangles, while still keeping a fine control on the process as well as the global appearance satisfying thanks to albedo and normal maps usage. The add-on allows me to easily:

1. Import the high resolution model and its associated albedo and normal maps if they are found.
2. Create a nicely decimated copy of the initial object, with a targeted number of faces (1500 triangles for instance) and UV unwrap it.
3. Bake the albedo and normal map textures between the high and low resolution objects.
4. Export the lowpoly mesh to a .fbx file and the baked textures to associated image files on my drive.

## Bake a complex Cycles material

![death](https://user-images.githubusercontent.com/37718992/46110730-e5fbf880-c1e4-11e8-8a62-de2ca2f96445.jpeg)

I also use this add-on to bake complex mixes of PBR textures between objects.

For instance, if I wanted to create a PBR material for a high resolution photogrammetry scan of a statue, I can adjust the previous workflow and use the add-on to:

1. Import the high resolution model and discard its associated texture maps.
2. Create a new Cycles node setup and mix different Principled shaders (blender PBR material): a mix of damaged brass and rusted iron textures for the body of the statue, some bronze patina where the normals are pointing up, dirt or rust in the creases, smoother metal on the "pointy" parts of the object...
3. Create a decimated copy of the initial object, with a user-specified number of faces, and UV unwrap it.
4. Bake the final albedo, roughness, metalness and normal textures between the high and low resolution objects.
5. Export the lowpoly mesh and its associated textures to a .fbx file along with smartly named image files.



## Non uniform remeshing with mmgs

The previous feature therefore allows you to remesh different parts of the model independantly, like I did with [this model of a Napoleon statue on Sketchfab](https://skfb.ly/6xHwD), remeshing details such as the sword separately from the horse's body:

![napo](https://user-images.githubusercontent.com/37718992/46110737-e72d2580-c1e4-11e8-8814-2bcb6cc57bb5.png)

To do so, you'll have to separate your model into different "submodels", while keeping the boundaries between them intact:

1. In Edit-mode, select all the edges separating the zones you wish to remesh independently (using **Edge loops**, **Select boundary loop**, or just the plain **Ctrl + right click** method for instance)
2. Use **Mark as sharp** to... mark them as sharp
3. Use the **Edge split** operator to split the regions you segmented
4. Select each region with **Select linked** or **Ctrl + L**, and separate them into a different object with **Separate (or p)** -> **Selection**. You could also just select everything and use **Separate** -> **Loose parts** if your model does not have loose parts you do not want to remesh separately.

You should now have as many objects as regions you created, which you can then remesh independently with the **MMGS** button, specifying a custom hausdorff ratio for each of them (keep in mind that the ratio is with the selected object's size, you'll therefore have to adjust!).

Once all your remeshed parts have been re-imported, you can then join them into an unique object by using **Join** or **Ctrl + J**, and jump to Edit-mode to **Remove doubles** vertices.



## Volume slice through a model

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

The file ```/path/to/myModel.1.o.mesh``` is then ready to be fed to paraview, after having been converted to a .vtk file by using the [convertToVTK.py](https://github.com/norgeotloic/BakeMyScan/blob/master/scripts/convertToVTK.py) python script present in the **scripts/** directory of this add-on (which you'll have to uncompress if it is still in a .zip format):

```
python convertToVTK.py /path/to/myModel.1.o.mesh
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
