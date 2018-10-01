# Batch process models

*NOTE: These scripts are still VERY unstable, and might not work in many cases: python or patience required!*

In order to reprocess multiple scans in the blender GUI, you'd have to execute the relevant operators shown in the [add-on usage page](ADDON_USAGE.md) over and over again, which would (obviously) get tedious for a big number of models. Plus you would have to stay in front of your screen(s) during the whole process, spending more time waiting than actually clicking stuff.

On this page you'll therefore find details about scripts allowing you to:
1. Process one model from the command line
2. Process multiple models
3. Import the results in blender

## 0 - Prerequisites

To use the command line to batch-process scans, you'll need to have the add-on installed as explained in [README.md](/README.md) (and your User Preferences saved).

Then download and extract the [scripts.zip archive from the latest release](https://github.com/norgeotloic/BakeMyScan/releases/latest), which contains python files not included in the add-on release.

You'll also need a working installation of **python3** on your system. Although you could try using the version of python bundled with blender - which I have not tested and do not recommend - the easiest way is to install python3.5 from [**Anaconda**](https://conda.io/docs/user-guide/install/download.html) for instance.

## 1 - Process one model

The whole process is automated thanks to the [bakeOne.py](https://github.com/norgeotloic/BakeMyScan/blob/master/scripts/bakeOne.py) python script that blender can execute from the command line. To use it, open up your command line interface, navigate to the scripts directory and type in the following command (options between brackets are optional):

```
blender --background --python bakeOne.py -- -i INFILE -o OUTFILE [-t TARGETFACES] [-r RESOLUTION] [-a ALBEDO] [-n NORMAL]
```

with:

* **INFILE**: path to the 3D model
* **OUTFILE**: file to export to (currently .fbx only)
* **TARGETFACES**: target number of faces, default to 1500
* **RESOLUTION**: baked textures resolution, default to 1024
* **ALBEDO**: path to the model albedo texture, default to None
* **NORMAL**: path to the model normal map, default to None

For instance on a linux computer:

```
blender --background --python bakeOne.py -- -i /home/loic/statue.obj -o /home/loic/exports/statue_lowpoly.fbx -t 3000 -r 2048 -a /home/loic/statue_albedo.png -n /home/loic/statue_normal.png
```

If this command went according to the plan, you'll find a .fbx file made of 3000 triangles and called *statue_lowpoly.fbx* in the */home/loic/exports* directory, in which you'll also find 2048x2048 textures: *statue_lowpoly_ALBEDO.png* and *statue_lowpoly_NORMAL.png*.

If the command failed, you can try to:

1. check the terminal output to try and understand what happened
2. run the command without *--background*, which will open blender's GUI, and look at the blender file to understand what went wrong.

If this still does not work, have a look at my [TODO list](https://github.com/norgeotloic/BakeMyScan/issues/1) to see if you can relate to something I'm working on or planning to implement, and if you think you found a bug, do not hesitate to [open a new issue](https://github.com/norgeotloic/BakeMyScan/issues).

## 2 - Process multiple models

To process multiple models, you can use the [bakeAll.py](https://github.com/norgeotloic/BakeMyScan/blob/master/scripts/bakeAll.py) script, which is a wrapper around [bakeOne.py](https://github.com/norgeotloic/BakeMyScan/blob/master/scripts/bakeOne.py).

The command line syntax is as follows:

```
python3.5 bakeAll.py -i INDIR -o OUTDIR -p PREFIX [-t TARGETFACES] [-r RESOLUTION]
```

with:

* **INDIR**: "root" directory containing one directory for every 3d model (and associated textures)
* **OUTDIR**: existing directory to export the files into
* **PREFIX**: prefix to name the processed files
* **TARGETFACES**: target number of faces, default to 1500
* **RESOLUTION**: baked textures resolution, default to 1024

Please note that to be matched automatically, the albedo texture file associated with your model must contain "alb" or "col" (case-insensitive) in its name, while the normal texture must contain "nor". Files called *myObject_Albedo.png* or *COLOR_myObject.jpg* will therefore be identified as an albedo map (but not *myObject_image.jpg*) and *texture_norMalS.png* as a normal map.

The script will ask you to manually assign albedo and/or normal map textures if it does not find textures with such patterns.

For instance, the following directory structure can be automatically processed:

```
/home/loic/tmp/
  model1/
    model1.fbx
    textures/
      normals.png
      albedo.png
  elephant/
    thatstheelephant.obj
    theelephant_NORMALS.png
    someCOlOrs.png
  model-123456789ABCDEF/
    source/
      strangeName17-FTW.ply
    textures/
      theelephant_NORMALS.png
      someCOlOrs.png
```

The command used would be:

```
python3.5 bakeAll.py -i /home/loic/tmp -o /home/loic/lowpoly -p elephants -t 2500 -r 2048
```

![terminal](https://user-images.githubusercontent.com/37718992/46111093-ff517480-c1e5-11e8-9e58-e9e979c56415.jpg)

Upon completion (and after having received info similar to the screenshot above), the directory */home/loic/lowpoly* should look like so:

```
/home/loic/lowpoly/
  elephants_01.fbx
  elephants_01_ALBEDO.png
  elephants_01_NORMALS.png
  elephants_02.fbx
  elephants_02_ALBEDO.png
  elephants_02_NORMALS.png
  elephants_03.fbx
  elephants_03_ALBEDO.png
  elephants_03_NORMALS.png
  list.csv
  blender_log_001.txt
  blender_log_002.txt
  blender_log_003.txt
```

**IMPORTANT**: The last files are the logs from blender, which you can inspect if something went wrong during the transformation to lowpoly, and the **list.csv** file keeps track of the models previously processed, so that existing models are not overridden when running the script multiple times in a row (to modify problematic models or add new ones for instance).

## 3 - Import the results in blender

I also wrote a script ([importAll.py](https://github.com/norgeotloic/BakeMyScan/blob/master/scripts/importAll.py)) to import the baked models in blender on a grid layout, similar to the one below:

![fossils](https://user-images.githubusercontent.com/37718992/46110731-e6948f00-c1e4-11e8-9e2a-ffcacb201f69.jpg)

It is used like so:

```
blender --python importAll.py -- -i INDIR [-r NUMROWS]
```

with:

* **INDIR**: baked assets directory
* **NUMROWS**: number of rows for the grid layout

Note that as I did not specify the *--background* option, a new blender window will open, in which you'll be able to adjust the grid layout (using for instance *Individual origins as pivot point* to scale and rotate objects, or *Manipulate center points* to change the margin).

I would advice you to save the newly (and nicely!) created scene by packing the textures using *File* -> *External data* -> *Pack all in .blend*, which will then allow you to remove the temporary directories and models which were created in the process.
