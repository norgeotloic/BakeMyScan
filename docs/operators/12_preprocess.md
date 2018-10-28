# Pre-process a model

This operator gives multiple preprocessing options, allowing to clean a model previously imported with the ["Import" operator](11_import.md) for instance.

The different options available are:

* Clean materials: remove all materials and material slots from the object
* Remove duplicated vertices: explicit
* Delete loose geometry: remove unconnected edges and vertices
* Remove sharp marks: clean all edges marked as "sharp"
* Clean normals: make normals consistent and clear the custom normals
* Center the object: translate the model so that its center is in [0,0,0]
* Scale to unit box: scale the object so that its largest is equal to one
* Smoothing iterations: apply some smoothing on the model
* Make manifold: make the object manifold thanks to the 3D printing add-on

Using this operator is especially recommended when you wish to use the rest of BakeMyScan operators, as it will maximize the chances of having consistent objects.



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
