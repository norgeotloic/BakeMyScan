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
