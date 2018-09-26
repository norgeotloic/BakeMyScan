I also wrote a command-line script to automatically download and re-process Sketchfab models and collections based on their URLs. Note that this script is (and will probably stay) unstable and mostly untested, and could give you strange results depending on the original model(s).

In order to use it, you'll need to have **Firefox** installed, as well as a version of [**selenium**](https://www.seleniumhq.org/) matching your python version. Follow [those instructions](https://selenium-python.readthedocs.io/installation.html) to install selenium.

More information as well as usage instructions can be found [on this page](docs/SCRIPTS_SKETCHFAB.md).

# Batch process models from Sketchfab

This page instructions explain scripts to automatically download and process either one Sketchfab model ([wrapper_model.py](scripts/wrapper_model.py)) or all models from a collection ([wrapper_collection.py](scripts/wrapper_collection.py)), taking the model's or collection's url as input.

Automatization is badass, but as sometimes things don't go as planned (which can happen as those scripts are "wrappers wrapping wrappers" actually wrapping the [bakeAll.py](scripts/bakeAll.py) file with Sketchfab API calls and browser automation techniques), I also kept a script to "only" download all models from a Sketchfab collection, which you can then process using the [blender add-on](USAGE.md) or the [command line tools](LOCAL.md).

**IMPORTANT**: as you can check in the source files, the python scripts only use your Sketchfab email adress and password in the *login_to_sketchfab* function ([scripts/sktch.py](scripts/sktch.py)) in order to automatically login to your Sketchfab account as selenium, the tool used to automate web browsing tasks, does not reuse your current Firefox preferences and saved accounts.

## 1 - One Sketchfab model

The script I use to download and reprocess one model is [wrapper_model.py](scripts/wrapper_model.py), used as follows:

```
python3.5 scripts/wrapper_model.py -u URL -o OUTDIR [-m MAIL] [-p PWD] [-t TARGET] [-r RESOLUTION]
```
with:

* **URL**: Sketchfab model's url
* **OUTDIR**: Directory for the lowpoly model
* **MAIL**: Sketchfab account e-mail
* **PWD**: Sketchfab account password
* **TARGET**: target number of triangles
* **RESOLUTION**: baked textures resolution

for instance to reprocess [this stick](https://skfb.ly/6AQxO) to a 500 tris mesh associated with 512px textures stored in */home/loic/tmp*:
```
python3.5 scripts/wrapper_model.py -u https://skfb.ly/6AQxO -o /home/loic/tmp -m loic@mail.com -p mypassword -t 500 -r 512
```

## 2 - All models from a collection

In the same way, the script I use to download and reprocess all models from a collection is [wrapper_collection.py](scripts/wrapper_collection.py):

```
python3.5 scripts/wrapper_collection.py -u URL -o OUTDIR [-m MAIL] [-p PWD] [-t TARGET] [-r RESOLUTION]
```

with
* **URL**: Sketchfab collection's url
* **OUTDIR**: Directory to store the baked assets
* **MAIL**: Sketchfab account e-mail
* **PWD**: Sketchfab account password
* **TARGET**: target number of triangles
* **RESOLUTION**: baked textures resolution

for instance to reprocess all models from [this collection](https://sketchfab.com/norgeotloic/collections/lowpoly-assets) to 250 tris models associated with 1024px textures and stored in */home/loic/tmp*:

```
python3.5 scripts/wrapper_collection.py -u https://sketchfab.com/norgeotloic/collections/lowpoly-assets -o /home/loic/tmp -m loic@mail.com -p mypassword -t 250 -r 1024
```

Note that the models name, url and license as well as the author name and profile url are dumped to a *credits.md* file in the output directory, to keep track of the objects you downloaded and allow you to give appropriate credit.

## 3 - Only download models from a collection

The [downloadSkecthfabCollection.py](scripts/downloadSkecthfabCollection.py) only downloads and extracts all models from a Sketchfab collection (thus not reprocessing them).

It is used like so:
```
python3.5 scripts/downloadSkecthfabCollection.py -u URL -o OUTPUT [-m MAIL] [-p PWD] [-k]
```
with:

* **URL**: Sketchfab collection's url
* **OUTDIR**: Directory to download the models to
* **MAIL**: Sketchfab account e-mail
* **PWD**: Sketchfab account password
* **-k**: flag used to keep the .zip files after extraction (safer that way)
