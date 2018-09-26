# BakeMyScan

![fossils](https://user-images.githubusercontent.com/37718992/46110731-e6948f00-c1e4-11e8-9e2a-ffcacb201f69.jpg)

This github repository contains:

* A blender add-on I wrote to process 3D scans (from my own scans or from Sketchfab) into lowpoly assets with blender.
* Python scripts, based on the add-on, to batch-process local or remote (from Sketchfab) 3D models.

## 1 - Features

The add-on allows to:

* import and clean 3D scans
* create orthographic projections of a given model
* smartly remesh the imported models to a given number of faces
* import and configure Cycles materials based on PBR texture sets from your computer
* bake texture sets between high and low resolution models
* export a .fbx model and its associated textures with PBR-friendly names

Although I mainly use it to reprocess scans with an associated albedo texture (as on the collection of 1500 triangles fossils above and [visible here](https://sketchfab.com/models/3d1161a5db4244e486de6de0c66f759c)), the add-on is also very useful to create and bake complex Cycles node setups - based on mixes of PBR texture sets for instance - as on the following model:

![oldman](https://user-images.githubusercontent.com/37718992/46110740-e7c5bc00-c1e4-11e8-9dbe-096f42d8875a.jpeg)

On the left is the original model, made of 313k triangles with an associated albedo texture. On the right is the reprocessed version, made of 3.6k triangles, with a PBR material baked from a mix of metal PBR texture sets (brass, damaged bronze and bronze patina). This model is visible on [Sketchfab](https://sketchfab.com/models/0f7535dc9dd1492e842cd6b2d23f4885).

## 2 - Installation

To install the add-on in blender, simply [download the BakeMyScan.zip archive contained in the latest release](https://github.com/norgeotloic/BakeMyScan/releases/latest) and install it in blender with the menu *File* -> *User Preferences* -> *Add-ons* -> *Install Add-on from File* (do not forget to save your settings!).

Note that if you wish to interface blender with [**mmgs**](http://www.mmgtools.org) (a powerful OpenSource remeshing tool for linux and MacOS), you must install mmgs following the instructions on the [mmgtools github repository](https://github.com/MmgTools/mmg)

## 3 - Usage

Instructions about the add-on usage can be found on the [usage page](docs/ADDON_USAGE.md).

You'll also find [instructions to process models from the command line](docs/SCRIPTS_BATCH.md), as well as [instructions to automatically download and process Sketchfab models and collections based on their URLs](docs/SCRIPTS_SKETCHFAB.md).

## 4 - Contributing and License

Do not hesitate to [open an issue](https://github.com/norgeotloic/BakeMyScan/issues) if you find a bug, or to [create a pull request](https://github.com/norgeotloic/BakeMyScan/pulls) if you've modified the code and would like to submit your changes.

This code is licensed under [GNU GPL v3](LICENSE.md).

And if you found this add-on useful and would like to say thanks, you could even consider [buying me a coffee](https://www.buymeacoffee.com/JrxfoZRVy)!
