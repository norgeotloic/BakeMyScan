# Add-on usage

*Some of the add-on functions are quite unstable, and might only work in specific contexts and circumstances. Reading the information on this page is therefore highly recommended*

Once the add-on is installed, you'll have a new tab available in your **Tool shelf** (the panel on the left of the 3D view, which you can open with **T**), called "BakeMyScan" and containing a few operators:

![gui](https://user-images.githubusercontent.com/37718992/46110732-e6948f00-c1e4-11e8-8112-1b571120d0bb.jpg)

## 1 - Workflow

#### 1.1 - Transform a high resolution mesh to a lowpoly asset

![ramses](https://user-images.githubusercontent.com/37718992/46110741-e7c5bc00-c1e4-11e8-966e-fa9a9761f01b.jpeg)

During the photogrammetry process, I often end up with .obj or .ply files made of hundreds of thousands of triangles (often between 200k and 5M depending on the software and quality settings used), which are way too heavy to use in game engines or for web visualization.

I therefore wrote the BakeMyScan add-on to be able to reprocess such models to a few thousands triangles, while still keeping a fine control on the process as well as the global appearance satisfying thanks to albedo and normal maps usage. The add-on allows me to easily:

1. Import the high resolution model and its associated albedo and normal maps if they are found.
2. Create a nicely decimated copy of the initial object, with a targeted number of faces (1500 triangles for instance) and UV unwrap it.
3. Bake the albedo and normal map textures between the high and low resolution objects.
4. Export the lowpoly mesh to a .fbx file and the baked textures to associated image files on my drive.

#### 1.2 - Mix PBR textures in a new Cycles material and bake the result

![death](https://user-images.githubusercontent.com/37718992/46110730-e5fbf880-c1e4-11e8-8a62-de2ca2f96445.jpeg)

I also use this add-on to bake complex mixes of PBR textures between objects.

For instance, if I wanted to create a PBR material for a high resolution photogrammetry scan of a statue, I can adjust the previous workflow and use the add-on to:

1. Import the high resolution model and discard its associated texture maps.
2. Create a new Cycles node setup and mix different Principled shaders (blender PBR material): a mix of damaged brass and rusted iron textures for the body of the statue, some bronze patina where the normals are pointing up, dirt or rust in the creases, smoother metal on the "pointy" parts of the object...
3. Create a decimated copy of the initial object, with a user-specified number of faces, and UV unwrap it.
4. Bake the final albedo, roughness, metalness and normal textures between the high and low resolution objects.
5. Export the lowpoly mesh and its associated textures to a .fbx file along with smartly named image files.

## 2 - Operators

### 2.1 - Import

Currently supports .obj, .ply, .stl, .fbx, .dae, .x3d and .wrl files.

This button does not only import a file, but also does a bunch of preprocessing operations on the object (you can check the code in [op_import_scan.py](https://github.com/norgeotloic/BakeMyScan/blob/master/src/op_import_scan.py)):

1. Remove everything which is not a mesh
2. Remove the material if one was assigned on import
3. Clear the custom split normals, sharp edges, doubles and loose
4. Clean hypothetic problematic normals non manifolds and smooth (if the "manifold" checkbox was checked)
5. Center the object in the 3D view and scale it to one blender unit
6. Rename the object according to the file name and assign a Cycles material to it, trying to match the associated textures

Please note that to be matched automatically, the texture files associated with your model must be located close to the model file and have a *meaningful name*:

**The lowercase name of a texture file must end with a specific pattern corresponding to its role, in order to be associated with the appropriate slot of a Principled shader node**

The functions used to find corresponding textures are available in the file [fn_match.py](https://github.com/norgeotloic/BakeMyScan/blob/master/scripts/src/fn_match.py), and here is the python dictionnary corresponding to the patterns used:

```
patterns = {
      "albedo"      : ["albedo", "diffuse", "dif", "alb", "basecolor", "color", "_d", "_col","tex"],
      "ao"          : ["ao", "occlusion", "occ"],
      "metallic"    : ["metallic", "metal", "metalness"],
      "roughness"   : ["roughness", "rou", "rough", "_r"],
      "glossiness"  : ["specular", "ref", "spec", "glossiness", "reflect", "refl", "gloss"],
      "normal"      : ["normal", "normals", "nor", "_n", "norm", "nrm"],
      "height"      : ["height", "dis", "disp", "displacement"],
      "emission"    : ["emission", "emit", "emissive"],
      "opacity"     : ["alpha", "transparent", "opacity", "transp", "mask"],
  }
```

For instance, consider the following directory structure:

```
model1/
  model1.fbx
  textures/
    makesomelight.png
    normals.png
    albedo.png
    metal.jpeg
elephant/
  thatstheelephant.obj
  theelephant_NORMALS.png
  elephant_glossiness.jpeg
  eleph_alpha.jpg
  someCOlOr.png
model-123456789ABCDEF/
  source/
    strangeName17-FTW.ply
  textures/
    NORMALS.png
    model_dif.png
    model_emissive.jpeg
    model_ao.png
```

* Importing **model1/model1.fbx** will create a material using *albedo.png* as an albedo map, *normals.png* as normal map and *metal.jpeg* for the metalness. Note that *makesomelight.png* won't be used as an emission factor, as "light" is not in the patterns for the emission slot.
* Importing **elephant/thatstheelephant.obj** will create a material using *someCOlOr.png* as an albedo map, *theelephant_NORMALS.png* as normal map, *eleph_alpha.jpg* as an opacity factor and *elephant_glossiness.jpeg* as a gloss map (inverted to be used as roughness).
* Importing **model-123456789ABCDEF/source/strangeName17-FTW.ply** will also map the 4 textures present in the *textures* directory, as the operator first try to match textures in the model's directory, then in its subdirectories, then in a "textures" directory located in its parent directory.

**AS A CONCLUSION**: if your textures are named in a sensible manner, your material should be correctly imported in blender and be ready for render or for baking. However, if you encounter a problem or some textures are not found, you can still jump into the Node editor mode and manually assign the image files to the texture nodes.

### 2.2 - Ortho view

This operator exports an orthographic projection of the selected object, as on the following image:

![lion_ortho](https://user-images.githubusercontent.com/37718992/46110736-e72d2580-c1e4-11e8-95cd-af5fba1ef1f0.jpg)

On completion, the active 3D view window will be split in two horizontal parts. You'll have to collapse the top part in order to retrieve your initial settings (I can't figure how to do this using python API from an add-on, blender tells me that the two areas "do not share an edge"...).

### 2.3 - Decimate

![hand](https://user-images.githubusercontent.com/37718992/46110734-e6948f00-c1e4-11e8-8f38-5e03497d2ad9.gif)

This operator first performs a coarse decimation on the mesh depending on the target number of faces you specified. This step is done in order to speed-up the iterative remeshing process, and is equivalent to using a relatively "medium-poly" version of your object.

Reasonable values for the number of triangles are between 100k to 500k triangles, be ready to wait a little bit if you exceed such thresholds... I usually perform one iteration of mmgs, instantmeshes or meshlab to get such a number of faces.

The operator then iteratively performs a sequence of *Planar decimation*, *Triangulate*, *Smooth*, *Ratio decimation* and *Shrinkwrap* modifiers as well as a cleaning step, usually keeping more details in the high-curvature regions of the object than on the flat zones, until the target number of faces is reached.

The last iteration is then cancelled, and a last decimation step is finally applied to stick to the exact number of faces you aimed for, before unwrapping the object.

### 2.4 - MMGS

![napo](https://user-images.githubusercontent.com/37718992/46110737-e72d2580-c1e4-11e8-8814-2bcb6cc57bb5.png)

*This section presents the basic usage of mmgs in blender. "Advanced" usages include remeshing separate parts of a model with different precisions (as explained [here](MISC_MMGS_SEPARATED_PARTS.md)), or interfacing with tetgen and paraview to create volumetric meshes (shown [here](MISC_MMGS_TETGEN_PARAVIEW.md))*

[mmgs](http://mmgtools.org) is a powerful command-line remeshing tool for linux and MacOS only, which can for be used as an alternative to Instant Meshes, Meshlab remeshing filters or the "Decimate" modifier in blender.

It uses a specific file format for input and output, the MEDIT .mesh format. As this specific format is not supported by blender, I had to create 3 operators to interface with mmgs:

1. **Export to .mesh**: this operator is not present in the 3D view panel, but is available under the menu *File* -> *Export* -> *MESH (.mesh)*. As its name suggests, it will export the selected object to a .mesh file on your hard drive.
2. **Import a .mesh**: this operator is not present in the 3D view panel either, but under *File* -> *Import* -> *MESH (.mesh)*, and will ... import a .mesh file.
3. **Remesh with mmgs**: this operator is the only one visible as **MMGS** in the BakeMyScan panel. It actually uses the previous operators to export the selected object to a .mesh file, run mmgs as a command-line process on the exported file, and re-import the output of mmgs as a .mesh file into blender.

The **MMGS** button (*only active on linux and MacOS if mmgs is installed*) will reveal two options on click (although mmgs used as a command-line program has much more): the Hausdorff ratio and a "Smooth" checkbox.

#### 2.4.1 - Hausdorff ratio

In a few words, mmgs processes an object by constraining the maximal distance between the resulting surface and the original one. This maximal distance is called the Hausdorff distance:

* A high Hausdorff distance will yield a final mesh more distant from the original model, but containing far less polygons.
* A lower Hausdorff distance however will give you a better approximation of the surface, but the polycount will be higher.

To ignore the impact of the size of the model, I have set the Hausdorff parameter as a **ratio of the longest model’s dimension** in the add-on.

Therefore, a 3 meters object with a Hausdorff Ratio set to 0.002 will return a surface approximation constrained to a 0.6cm distance from the original mesh. Here is an example using Suzanne as the original model:

![suzanne](https://user-images.githubusercontent.com/37718992/46110743-e7c5bc00-c1e4-11e8-8057-a783c55e3f0e.jpg)

More precise info about the Hausdorff parameter is available on [MMGPlatform website](https://www.mmgtools.org/mmg-remesher-try-mmg/mmg-remesher-options/mmg-remesher-option-hausd)

#### 2.4.2 - Smooth surface

Keep that checked if your model is "organic", without sharp edges, for instance for the result from a 3D scan.

If your model contains sharp angles, you'll want to uncheck that button.

Below is the effect of this parameter on a model containing sharp edges, with a hausdorff ratio set to 0.001. Note that it went way better for the non-smooth model:

![smoothcube](https://user-images.githubusercontent.com/37718992/46110742-e7c5bc00-c1e4-11e8-8bba-66277341da9a.jpg)

### 2.5 - Set textures path

This operator creates a library of PBR texture sets from a directory on your computer.

The directory you specify will be **RECURSIVELY** searched for texture files, so **DO NOT USE "C://Users/you" OR "/home/you/"** as those would be very long to search! In my case, all the PBR textures I have downloaded from internet are stored in a directory of my hard drive: */media/loic/Data/textures/*, under different directories depending on their origin (*/media/loic/Data/textures/Texturescom/*, */media/loic/Data/textures/FreePBR* ...).

This function uses the **same function and patterns as described in the "Import" operator (2.1)**, and creates a texture set by identifying patterns having a common suffix. For instance, *wood1_albedo.png* and *wood1_normals.jpeg* will be matched and grouped in a common material named "wood1".

A bunch of cleanup is also done on the file names and to ignore material variations (*wood_007_NORMALS_var1.png* will be kept over *wood_007_NORMALS_var2.png* for instance).

What this operator does is actually creating a global dictionary, *bpy.types.Scene.pbrtextures*, which will be referenced to later. The keys are the material base names, and each element is a new directory which keys are the "channel names", and contain the paths to the associated texture images.

I personally use (mostly) free PBR textures from the following resources:

* [3d-wolf.com](https://www.3d-wolf.com/products/textures.html)
* [textures.com](http://textures.com)
* [freepbr.com](https://freepbr.com/)
* [Renderosity](https://www.renderosity.com/mod/freestuff/?item_id=76206)
* [Milos Belanec's gumroad](https://gumroad.com/milosbelanec)
* [Artem Lebedev's gumroad](https://gumroad.com/l/ekRhc)
* [Sungwoo Lee's gumroad](https://gumroad.com/l/HEZvu)
* [3dtextures.me](https://3dtextures.me/tag/pbr/)

### 2.6 - Import PBR material

Once having selected a directory to look for textures, you will be prompted to select the material base name that you wish to import. A new PBR material (based on a "Principled" shader node) will then be created and assigned to the active object, and the associated textures will be linked to the node's correct inputs.

**You can also use this operator from the Node editor**, by hitting the spacebar and looking for "PBR". In this case, instead of creating a new material, the operator will create a node group which output is the output of the correctly linked principled shader node. This allows to easily use "Mix Shader" nodes to easily mix two texture sets.

For instance, here is a dummy example of the search pop-up in the node editor, of a simple mix of texture sets based on Cycles nodes, as well as a render of the corresponding material:

![nodesetup](https://user-images.githubusercontent.com/37718992/46110739-e72d2580-c1e4-11e8-8375-e9a095be04b2.jpg)

### 2.7 - Bake Textures

If executed correctly, this operator allows to bake the result of complex Cycles node setups, for instance multiple PBR texture sets mixed according to noise textures.

Its mechanism is a bit complicated, but has to be understood in order to be able to use it. The process is roughly the following and works for either one or two objects:

```
For each baking type the user selected (albedo, metal, roughness...):
  1. Identify the source and target objects (if two objects are selected, this works like "selected to active", else the source is also the target object).
  2. Make a copy of the source object's material
  3. Look for all Principled nodes present in this newly created material (and recursively look into node groups for such shader nodes too).
  4. For each Principled node found that way:
    1. Remove the input links to the node not associated to the current baking type
    2. Remove the nodes left unconnected
    3. Transform the Principled nodes to Emission nodes
    4. Bake the resulting Emission channel to a new image, and save it according to the selected object name and the current baking type.
  5. Remove the copy of the initial material
```

The baking of the normals is treated differently, as the geometric normals are baked using Blender Render, and combined to the "material-induced" normals linked to the Principled shader nodes with quite complex node setups (implemented in the file [fn_nodes.py](https://github.com/norgeotloic/BakeMyScan/blob/master/src/fn_nodes.py)).

On success, the operator will load the resulting material and assign it to the active object for you to preview the baking results.

**NOTE:** The behavior of this operator is not 100% stable yet, and I should improve on the mixing of geometric and surface normals, as well as on the roughness and metallic maps which do not always seem to bake correctly. However, the baking of geometry and albedo textures works fine, and is usually sufficient for most conversion to lowpoly assets.

### 2.8 - Export to fbx

More information on this later...
