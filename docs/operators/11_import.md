# Import a model

This operator acts as a simple wrapper around different importing operators, and simply allows to import a model.

It currently supports .obj, .ply, .stl, .fbx, .dae, .x3d and .wrl format.

Note that the model will be imported with its material(s), which are not compatible with the other operators provided in this add-on.

In order to pre-process the imported model, you'll have to use the ["Pre-process" operator](12_preprocess.md).
