# A note on texture names

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
