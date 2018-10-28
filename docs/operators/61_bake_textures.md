# Bake Textures

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
