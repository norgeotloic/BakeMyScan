# Save PBR library as JSON

This operator will save the library created thanks to the ["Create PBR library"](41_PBR_library.md) operator to a user-specified .json file.

This is recommended especially for directories containing lots of textures.

For instance, I have got on my hard drive a directory with a few gigabytes of textures. The simple step of reading the library from this directory can take up to a full minute, while reading a .json file is nearly instantaneous.

In the future, I'd possibly try to incorporate this step as an automatic process: automatically creating such a .json file whenever a directory is searched. That could allow to open this file on blender initialization. Maybe using a system through User Preferences could also be a good idea...
