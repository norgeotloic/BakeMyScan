# BakeMyScan

A blender add-on I wrote to process 3D scans (from my own scans or from Sketchfab) into lowpoly assets with blender:

![grid](https://user-images.githubusercontent.com/37718992/44431859-fabeee00-a59f-11e8-80da-6705b218db81.jpg)

## Download

If you only wish to use the blender add-on, simply [download the .zip archive of the latest release](https://github.com/norgeotloic/BakeMyScan/releases) and install it in blender with the menu *File* -> *User Preferences* -> *Add-ons* -> *Install Add-on from File* (do not forget to save your settings!).

However, if you wish to use the command line to batch-process scans, you'll need to [download the .zip archive of the full repository](https://github.com/norgeotloic/BakeMyScan/archive/master.zip), which contains python files not included in the add-on release.

## Prerequisites

The main features of the add-on should work "out of the box", on any linux, MacOS and Windows system.

Some further configuration is however needed if you wish to have access to more advanced functionalities:

* To interface blender with [**mmgs**](http://www.mmgtools.org) (a powerful OpenSource remeshing tool for linux and MacOS), you must install mmgs following the instructions on the [mmgtools github repository](https://github.com/MmgTools/mmg)
* To batch-process models from the command line, you'll need a working installation of **python3** installed on your system. Although you could try using the version of python bundled with blender (untested), the easiest way is to install python3.5 from [**Anaconda**](https://conda.io/docs/user-guide/install/download.html).
* If you wish to process Sketchfab models and full collections from their url, you'll also need to have **Firefox** installed, as well as a version of [**selenium**](https://www.seleniumhq.org/) matching your python version (see [those instructions](https://selenium-python.readthedocs.io/installation.html))

## Usage

To start using this add-on and manually process a 3D scan in blender, please consult the [basic instructions](docs/ADDON_USAGE.md).

You'll also find instructions to batch-process local 3D models from the command-line on [this page](docs/SCRIPTS_BATCH.md), and to automatically download and process models from Sketchfab [here](docs/SCRIPTS_SKETCHFAB.md).

## Contributing

Do not hesitate to [open an issue](https://github.com/norgeotloic/BakeMyScan/issues) if you find a bug, or to [create a pull request](https://github.com/norgeotloic/BakeMyScan/pulls) if you've modified the code and would like to submit your changes.

And if you found this add-on useful and would like to say thanks, you could even consider [buying me a coffee](https://www.buymeacoffee.com/JrxfoZRVy)!

## License

This code is licensed under [GNU GPL v3](LICENSE.md).
