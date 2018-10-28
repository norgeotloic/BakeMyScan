# Meshlab

This operator creates an interface to meshlabserver (the command-line version of Meshlab).

It applies a ["Quadric Edge Collapse Decimation"](https://help.sketchfab.com/hc/en-us/articles/205852789-MeshLab-Decimating-a-model) on the model.

The main parameter is the target number of triangles, but I plan on interfacing the other parameters for the filter.

In the long term and if other Meshlab filters prove interesting for remeshing operations, I'd also like to include different scripts, and maybe let the user specify its .mlx script to be interfaced in blender.
