# Add-on operators

Once the add-on is installed, you'll have a new tab available in your **Tool shelf** (the panel on the left of the 3D view, which you can open with **T**), called "BakeMyScan" and containing a bunch of operators grouped under collapsible panels:

![operators](https://user-images.githubusercontent.com/37718992/47621094-e264d580-daf2-11e8-9aa3-4242a029b74a.jpg)

### Import operators

Used to import and preprocess models.

* [Import](operators/11_import.md): Import a scan
* [Pre-process](operators/12_preprocess.md): Apply pre-processing / cleaning steps on the imported model

### Remeshing operators

##### Internal methods

These operators do not depend on external software. The iterative method is probably the most useful of them.

* [Simple decimate](operators/21_simple_decimate.md): Remesh with blender "Decimate" modifier
* [Naive quads](operators/22_naive_quads.md): Remesh to quads inside blender
* [Iterative method](operators/23_iterative_method.md): Remesh to a desired number of faces through an iterative method

##### Interface to external software

These operators work by invoking the command-line interfaces of external software.

* [MMGS](operators/31_mmgs.md): Remesh with mmgs
* [Meshlab](operators/32_meshlab.md): Remesh with Meshlab
* [Instant Meshes](operators/33_instant.md): Remesh with Instant Meshes
* [Quadriflow](operators/34_quadriflow.md): Remesh with Quadriflow

### Materials and textures operators

##### PBR library

Operators used to import Cycles materials from a local library of PBR textures.

* [Create PBR library](operators/41_PBR_library.md): Create a PBR textures library from textures inside a directory
* [Save library to JSON](operators/42_save_JSON.md): Save the textures library to a .json file
* [Load library from JSON](operators/43_load_JSON.md): Reload the library from a .json file
* [Load material from library](operators/44_load_material_from_library.md): Import and assign a material from the PBR library

##### Other material operators

Operators used to create PBR materials. They must be used in order to use the baking operators hereafter.

* [UV unwrapping](operators/51_unwrap.md): Unwraps the model, with a user-selected method
* [New empty material](operators/52_empty_material.md): Creates an empty PBR material (needed for later steps)
* [Assign PBR textures](operators/53_assign_texture.md): Assign a texture to a slot (albedo, roughness, normal) of a PBR material
* [Load material from texture](operators/54_material_from_texture.md): Loads a material from one PBR texture (by looking for similary-named textures)

### Baking operators

Operators simplifying baking operations between two models (usually a high resolution and a lowpoly one). They must be used in conjunction with the material operators.

* [Bake textures to images](operators/61_bake_textures.md): Bake textures from a PBR material to images
* [Bake textures to vertex colors](operators/62_bake_to_vertex_colors.md): Bake textures to vertex colors

### Export operators

Various operators used to export the results of the baking or remeshing operations to external software or for online viewing.

* [Ortho view](operators/71_orthoview.md): Export an orthographic projection of the selected object
* [Export to fbx](operators/72_export_fbx.md): Export the selected object and its associated textures to fbx and matching images

### Hidden operators
Some operators are not available in the UI, but are available through menus or the search function. Below are their documentation for reference and hypothetic script usages:
* [Export .mesh](operators/81_export_mesh.md): available under *File* -> *Export* -> *MESH (.mesh)*
* [Import .mesh](operators/82_import_mesh.md): available under *File* -> *Import* -> *MESH (.mesh)*
