# New empty material

This operator creates a new Cycles material, based on a Principled Node, and ready to be used with image textures.

It is called in all operators creating materials in BakeMyScan, and creates a specific node setup that can be re-used for different applications.

In particular, in order to bake textures, it is especially recommended to use this operator in conjunction with the [Assign texture](53_assign_texture.md) operator in order to setup the source material.
