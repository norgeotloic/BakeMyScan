# Batch process models from Sketchfab

*NOTE: This script is still VERY unstable, and might not work in many cases...*

The following instructions explain how to automatically download and process either one Sketchfab model or all models from a collection, taking the model's or collection's url as input.

Automation is badass, but as sometimes things don't go as planned (which can happen as those scripts are "wrappers wrapping wrappers" actually wrapping the [bakeAll.py](/scripts/bakeAll.py) file with Sketchfab API calls and browser automation techniques), I also kept an option to only download models without actually reprocessing them.

**IMPORTANT**: as you can check in the source files, the python scripts only use your Sketchfab email adress and password in the *login_to_sketchfab* function (found in [bakeSketchfab.py](/scripts/bakeSketchfab.py)) in order to automatically login to your Sketchfab account as selenium, the tool used to automate web browsing tasks, does not reuse your current Firefox preferences and saved accounts.

## Prerequisites

After having installed the add-on, extracted the scripts and checked that you have a correct version of python3 on your system - as explained on [this page](SCRIPTS_BATCH.md), you'll also need to make sure to:

* Install **Firefox**.
* Install a version of [**selenium**](https://www.seleniumhq.org/) matching your python version ([instructions here](https://selenium-python.readthedocs.io/installation.html)).
* Install the python library **urllib** (```pip install urllib``` or ```conda install urllib```).

## Usage

The script is used as follows:

```
python3.5 bakeSketchfab.py -u URL -o OUTDIR [-m MAIL] [-p PWD] [-t TARGET] [-r RESOLUTION] [-s SUFFIX] [-d]
```
with:

* **URL**: Sketchfab model's url
* **OUTDIR**: Directory for the lowpoly model(s) (must be empty!!)
* **MAIL**: Sketchfab account e-mail
* **PWD**: Sketchfab account password
* **TARGET**: target number of triangles
* **RESOLUTION**: baked textures resolution
* **SUFFIX**: name to prepend to the output model(s)
* **-d**: use this flag to only download the models and not process them

To reprocess [this stick](https://skfb.ly/6AQxO) to a 500 tris mesh associated with 512px textures stored in */home/loic/tmp*:
```
python3.5 bakeSketchfab.py -u https://skfb.ly/6AQxO -o /home/loic/tmp -m loic@mail.com -p mypassword -t 500 -r 512
```

To reprocess all models from [this collection](https://sketchfab.com/norgeotloic/collections/lowpoly-assets) to 250 tris models associated with 1024px textures and stored in */home/loic/tmp*:

```
python3.5 bakeSketchfab.py -u https://sketchfab.com/norgeotloic/collections/lowpoly-assets -o /home/loic/tmp -m loic@mail.com -p mypassword -t 250 -r 1024
```

To only download the models from the same collection, one would use the command:

```
python3.5 bakeSketchfab.py -u https://sketchfab.com/norgeotloic/collections/lowpoly-assets -o /home/loic/tmp -m loic@mail.com -p mypassword -d
```

Note that the models name, url and license as well as the author name and profile url are dumped to a *credits.md* file in the output directory, to keep track of the objects you downloaded and allow you to give appropriate credit.
