# Batch download models from Sketchfab

The following instructions explain how to automatically download either one Sketchfab model or all models from a collection, taking the model's or collection's url as input.

**IMPORTANT**: as you can check in the source files, the python scripts only use your Sketchfab email adress and password in the *login_to_sketchfab* function (found in [downloadSketchfab.py](https://github.com/norgeotloic/BakeMyScan/blob/master/scripts/downloadSketchfab.py)) in order to automatically login to your Sketchfab account as selenium, the tool used to automate web browsing tasks, does not reuse your current Firefox preferences and saved accounts.

## Prerequisites

After having installed the add-on, extracted the scripts and checked that you have a correct version of python3 on your system - as explained on [this page](SCRIPTS_BATCH.md), you'll also need to make sure to:

* Install **Firefox**.
* Install a version of [**selenium**](https://www.seleniumhq.org/) matching your python version ([instructions here](https://selenium-python.readthedocs.io/installation.html)).
* Install the python library **urllib** (```pip install urllib``` or ```conda install urllib```).

## Usage

The script is used as follows:

```
python3.5 downloadSketchfab.py -u URL -o OUTDIR [-m MAIL] [-p PWD]
```
with:

* **URL**: Sketchfab model's url
* **OUTDIR**: Directory for the lowpoly model(s) (must be empty!!)
* **MAIL**: Sketchfab account e-mail
* **PWD**: Sketchfab account password

To download [this stick](https://sketchfab.com/models/644fb3e8dc134d8f994f4446bfaf1718) in */home/loic/tmp*:
```
python3.5 downloadSketchfab.py -u https://sketchfab.com/models/644fb3e8dc134d8f994f4446bfaf1718 -o /home/loic/tmp -m loic@mail.com -p mypassword
```

To download all models from [this collection](https://sketchfab.com/norgeotloic/collections/lowpoly-assets) stored in */home/loic/tmp* (you will be prompted for your Sketchfab user name and password if you don't write them in the command):

```
python3.5 downloadSketchfab.py -u https://sketchfab.com/norgeotloic/collections/lowpoly-assets -o /home/loic/tmp
```

Note that the models name, url and license as well as the author name and profile url are dumped to a *credits.md* file in the output directory, to keep track of the objects you downloaded and allow you to give appropriate credit.

Once the downloads are complete, you can then use the [bakeAll.py](/scripts/bakeAll.py) script to process your models!
