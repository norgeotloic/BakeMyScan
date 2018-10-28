# Import material from library

Once having selected a directory to look for textures, you will be prompted to select the material base name that you wish to import. A new PBR material (based on a "Principled" shader node) will then be created and assigned to the active object, and the associated textures will be linked to the node's correct inputs.

**You can also use this operator from the Node editor**, by hitting the spacebar and looking for "PBR". In this case, instead of creating a new material, the operator will create a node group which output is the output of the correctly linked principled shader node. This allows to easily use "Mix Shader" nodes to easily mix two texture sets.

For instance, here is a dummy example of the search pop-up in the node editor, of a simple mix of texture sets based on Cycles nodes, as well as a render of the corresponding material:

![nodesetup](https://user-images.githubusercontent.com/37718992/46110739-e72d2580-c1e4-11e8-8375-e9a095be04b2.jpg)
