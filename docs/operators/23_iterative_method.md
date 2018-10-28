# Iterative method
This operator provides an efficient way to decimate a model while keeping good details, making the compromise of creating elongated triangles.

![hand](https://user-images.githubusercontent.com/37718992/46110734-e6948f00-c1e4-11e8-8f38-5e03497d2ad9.gif)

It first performs a coarse decimation on the mesh depending on the target number of faces you specified. This step is done in order to speed-up the iterative remeshing process, and is equivalent to using a relatively "medium-poly" version of your object.

Reasonable values for the number of triangles are between 100k to 500k triangles, be ready to wait a little bit if you exceed such thresholds... I usually perform one iteration of mmgs, instantmeshes or meshlab to get such a number of faces.

The operator then iteratively performs a sequence of *Planar decimation*, *Triangulate*, *Smooth*, *Ratio decimation* and *Shrinkwrap* modifiers as well as a cleaning step, usually keeping more details in the high-curvature regions of the object than on the flat zones, until the target number of faces is reached.

The last iteration is then cancelled, and a last decimation step is finally applied to stick to the exact number of faces you aimed for, before unwrapping the object.
