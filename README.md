*As of today (17th of october), the release is broken for the scripts part (so no automatic pipeline for a few days...) as I am currently modifying nearly everything to make them robust!*

*I'd advice you to "watch" this repository, as I'll make some changes soon. Sorry for the "Alpha" troubles...*

*Concerning the add-on, all of the remeshing methods should work correctly - provided the external software are correctly installed - and you should also be able to export an orthographic view of your model, as well as use a texture directory to import PBR materials ("Texture panel")*

# BakeMyScan

A blender add-on I wrote to process 3D scans (from my own scans or from Sketchfab) into lowpoly assets, along with Python scripts to automate the process on local or remote (from Sketchfab) 3D models.

## 1 - What do I use this add-on for?

* Generate collections of lowpoly assets from high resolution scans
* Interface with advanced remeshing techniques (a.k.a never use the "Decimate modifier" again!)
* One click texture baking (supporting Cycles nodes)
* Download all models from a Sketchfab collection

I mainly use this add-on to reprocess 3D photogrammetry scans with an associated albedo texture (as on the [collection of lowpoly fossils](https://sketchfab.com/models/3d1161a5db4244e486de6de0c66f759c) shown below (remeshed to 1.5k triangles, when the original models were between 100k and 5M polygons):

![fossils](https://user-images.githubusercontent.com/37718992/46110731-e6948f00-c1e4-11e8-9e2a-ffcacb201f69.jpg)

But this add-on is also very useful to create and bake complex Cycles node setups - based on mixes of PBR texture sets for instance - as on the following model:

![oldman](https://user-images.githubusercontent.com/37718992/46110740-e7c5bc00-c1e4-11e8-9dbe-096f42d8875a.jpeg)

On the left is the original object, made of 313k triangles with an associated albedo texture. On the right is the reprocessed version (visible on [Sketchfab](https://sketchfab.com/models/0f7535dc9dd1492e842cd6b2d23f4885)), made of 3.6k triangles, with a PBR material baked from a mix of metal PBR texture sets (brass, damaged bronze and bronze patina).

And as a bonus, you'll get an easy interface to powerful remeshing solutions!

## 2 - Installation

To install the add-on in blender, simply [download the BakeMyScan.zip archive contained in the latest release](https://github.com/norgeotloic/BakeMyScan/releases/latest) and install it in blender with the menu *File* -> *User Preferences* -> *Add-ons* -> *Install Add-on from File* (do not forget to save your settings!).

A few external remeshing software can be used through this addon:

* **[MMGtools](https://www.mmgtools.org/)**: A very powerful surface remesher, try it!
* [Meshlab](http://www.meshlab.net/): I guess you know that one already.
* [InstantMeshes](http://igl.ethz.ch/projects/instant-meshes/): very nice to work with quadrilaterals.
* [Quadriflow](https://github.com/hjwdzh/QuadriFlow): supposedly fixes some Instant Meshes inconsistencies. No GUI though...

To interface them, you'll first have to install them (Duh!). You can download binaries for Instant Meshes [here](https://github.com/wjakob/instant-meshes#pre-compiled-binaries), Meshlab [there](http://www.meshlab.net/#download) (we'll actually need meshlabserver, the command-line interface to Meshlab, which comes with the download) and MMGtools [over here](http://www.mmgtools.org/mmg-remesher-downloads), but you will have to compile Quadriflow yourself... I managed to do so on a linux computer, but not yet on Windows. So good luck with that one ;) !

Once the software you wish to use is installed, you'll have to open the add-on preferences, and fill in the paths to the executable (either the "path" as on the first three examples below, or the command used to run the software, as for meshlabserver which i have to run with an additional variable on my system. On Windows, those paths will end up with .exe):

![preferences](https://user-images.githubusercontent.com/37718992/47116936-538aca00-d263-11e8-8d7a-e428bc8b9c2d.png)

## 3 - Usage

Instructions about the add-on usage can be found on the [usage page](docs/ADDON_USAGE.md).

You'll also find [instructions to process models from the command line](docs/SCRIPTS_BATCH.md), as well as [instructions to automatically download Sketchfab models and collections based on their URLs](docs/SCRIPTS_SKETCHFAB.md).

## 4 - Contributing and License

Do not hesitate to [open an issue](https://github.com/norgeotloic/BakeMyScan/issues) if you find a bug, or to [create a pull request](https://github.com/norgeotloic/BakeMyScan/pulls) if you've modified the code and would like to submit your changes.

This code is licensed under [GNU GPL v3](LICENSE.md).

And if you found this add-on useful and would like to say thanks, you could even consider [buying me a coffee](https://www.buymeacoffee.com/JrxfoZRVy)!
