*As of today (17th of october), the release is broken for the scripts part (so no automatic pipeline for a few days...) as I am currently modifying nearly everything to make them robust!*

*I'd advice you to "watch" this repository, as I'll make some changes soon. Sorry for the "Alpha" troubles...*

*Concerning the add-on, all of the remeshing methods should work correctly - provided the external software are correctly installed - and you should also be able to export an orthographic view of your model, as well as use a texture directory to import PBR materials ("Texture panel")*

# BakeMyScan

[![fossils](https://user-images.githubusercontent.com/37718992/46110731-e6948f00-c1e4-11e8-9e2a-ffcacb201f69.jpg)](https://skfb.ly/6yUtB)

A blender add-on I use to transform high resolution 3D scans into lowpoly assets, manually or through python scripts.

1. [Installation](#installation)
2. [Features & usage](#features-and-usage)
3. [Contributing](#contributing)
4. [License](#license)

## Installation

To setup the add-on, first [download this .zip](https://github.com/norgeotloic/BakeMyScan/archive/dev.zip) and select it in blender with the menu *File* -> *User Preferences* -> *Add-ons* -> *Install Add-on from File*.

Although a few remeshing options are available "out of the box", BakeMyScan provides interfaces to various opensource remeshing software. To use them, you'll first have to install them on your system:
* **[MMGtools](https://www.mmgtools.org/)**: A powerful surface remesher, available as [binaries](http://www.mmgtools.org/mmg-remesher-downloads) or from [sources](https://github.com/MmgTools/mmg).
* **[Meshlab](http://www.meshlab.net/)**: An all-around 3D toolbox, which you can [download here]([there](http://www.meshlab.net/#download)) or [compile from sources](https://github.com/cnr-isti-vclab/meshlab).
* **[InstantMeshes](http://igl.ethz.ch/projects/instant-meshes/)**, very useful to get quads topology. Binaries and sources are [available on github](https://github.com/wjakob/instant-meshes).
* **[Quadriflow](http://stanford.edu/~jingweih/papers/quadriflow/)**: A recent quadrilateral meshes generator, similar to Instant Meshes in its results, but without any GUI. You'll need to compile it yourself from [the project's github repository](https://github.com/hjwdzh/QuadriFlow) as no binaries are available. [Yet...](https://github.com/hjwdzh/QuadriFlow/issues/22)

To interface the software in blender, open the add-on preferences, and fill in the paths to the executables. On windows, you'll need to select the *.exe* executable files, while you can simply specify the command used to run the programs on MacOS and linux systems.

For instance, to setup "meshlabserver" (the command line version of Meshlab), I could type "meshlabserver" on Linux or MacOS (as the executables should be available in the PATH), while on Windows I would have to select the file "C://Program Files/VCG/Meshlab/meshlabserver.exe".

![preferences](https://user-images.githubusercontent.com/37718992/47116936-538aca00-d263-11e8-8d7a-e428bc8b9c2d.png)

## Features and usage

#### blender add-on

This add-on allows to easily:

* Remesh a high resolution object into a lowpoly model.
* Bake texure and normal maps between the original and remeshed models
* Bake complex Cycles node setups (procedural textures, color ramps, mixing nodes...) to images
* Load PBR materials from an offline texture "library"
* Create orthographic projection images of a model

Typical BakeMyScan usages are demonstrated [on this page](docs/workflows.md), and you'll find a description of every available operator [here](docs/operators.md).

#### python scripts

BakeMyScan also comes bundled with useful python scripts allowing to:
* Automatically download all objects from a Sketchfab collection
* Batch process models from the command-line
* Import multiple models in a grid layout in blender

You'll find instructions on batch-processing through python scripts [on this page](docs/batch.md).

## Contributing

Do not hesitate to [open an issue](https://github.com/norgeotloic/BakeMyScan/issues) if you find a bug or feel that an important feature is missing.

You could also [create a pull request](https://github.com/norgeotloic/BakeMyScan/pulls) if you've modified and improved the code and would like to submit your changes.

And as another way to contribute, feel free to [buy me a coffee](https://www.buymeacoffee.com/JrxfoZRVy) if you found this add-on useful and would like to say thanks!

## License

This code is licensed under [GNU GPL v3](LICENSE.md), which is quite permissive, but I would still be glad if you could drop a link to this github repository alongside content created with this add-on!
