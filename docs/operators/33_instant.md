# Instant Meshes

This operator provides an interface to [Instant Meshes](https://github.com/wjakob/instant-meshes), another powerful remeshing software.

Although many other add-ons exist providing interfaces to this software, I had to include it for the "sake of completness".

## Command-line interface

If you leave the "Open the GUI" checkbox unchecked, Instant Meshes will be run through the command-line.

You'll have to select a method the software will use to remesh your model (number of faces, number of vertices or edge length), as well as the threshold for the chosen method. As only one of those methods can be used at once, the three thresholds are available in the Basic options panel, although only the one corresponding to the chosen algorithm will effectively be used.

It is advised to let the "advanced" options at their default values, unless you know what you are doing.

## GUI interface

If, however, you check the "Open the GUI" checkbox, the selected options will be ignored, and Instant Meshes will be launched in its own window.

The model which will be imported back in blender is the last one which will be saved, as a .obj, through Instant Meshes.

The add-on actually parses the text output of Instant Meshes, and reads in the last .obj file it finds.
