"""
Usage:
python downloadSkecthfabCollection.py -i 3b9b3fa1685c4cb5937cc0e9653bc0f1 -o /home/loic/tmp -u username@gmail.com -p password
"""

import sys
import os
import argparse
import imghdr

src = os.path.join( os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "src")
sys.path.append(src)
import fn_match

#colors for the terminal
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#Create an arguments parser
parser = argparse.ArgumentParser(description="Bake all models present in a directory to lowpoly assets")
parser.add_argument("-i", "--input",      dest="input",      type=str, metavar='FILE', required=True, help="Input directory")
parser.add_argument("-o", "--output",     dest="output",     type=str, metavar='FILE', required=True, help="Output directory")
parser.add_argument("-p", "--prefix",     dest="prefix",     type=str, required=True,  help="Prefix for the reprocessed files")
parser.add_argument("-t", "--target",     dest="target",     type=int, default=1500,   help="Target number of faces")
parser.add_argument("-r", "--resolution", dest="resolution", type=int, default=1024,   help="Baked textures resolution")

#Get the path to the baking script
bakeScript = os.path.join(os.path.dirname(os.path.realpath(__file__)), "bakeOne.py")

#Parse the arguments and check them
args = parser.parse_args(sys.argv[1:])
if not os.path.exists(args.output) or not os.path.isdir(args.output):
    print("ERROR: " + args.output + " is not a directory")
    sys.exit(1)
args.output = os.path.abspath(args.output)
if not os.path.exists(args.input) or not os.path.isdir(args.input):
    print("ERROR: " + args.input + " is not a directory")
    sys.exit(1)
args.input = os.path.abspath(args.input)

#List all the directories in the input directory
directories = [os.path.join(args.input, d) for d in os.listdir(args.input) if os.path.isdir(os.path.join(args.input, d))]
directories.sort()

#Functions to get models and textures from a directory
def get_3d_model_in(_directory, extensions):
    model = None
    for root, directories, filenames in os.walk(_directory):
        for directory in directories:
            pass
        for filename in filenames:
            _f = os.path.abspath(os.path.join(root, filename))
            if _f.split(".")[-1] in extensions:
                model = _f
                break
    return model
def get_textures_in(_directory):
    images = []
    for root, directories, filenames in os.walk(_directory):
        for directory in directories:
            pass
        for filename in filenames:
            _f = os.path.abspath(os.path.join(root, filename))
            if imghdr.what(_f) is not None:
                images.append(_f)
    return images

#Functions to find which is the albedo and which is the normal map if they exist
def separate_albedo_and_normals(images):
    patterns = {
        "albedo"      : ["albedo", "diffuse", "dif", "alb", "basecolor", "color", "_d", "_col","tex"],
        "normal"      : ["normal", "normals", "nor", "_n", "norm", "nrm"]
    }
    albedo = None
    normal = None
    #automatic matching
    for img in images:
        name = os.path.splitext(os.path.basename(img))[0].lower()
        for p in patterns["albedo"]:
            if name.endswith(p):
                albedo = img
                break
        for p in patterns["normal"]:
            if name.endswith(p):
                normal = img
                break
    #if one texture only, then its the albedo
    if len(images) == 1 and albedo is None and normal is None:
        albedo = images[0]
    return albedo, normal
def something_looks_wrong(albedo, normal, texture):
    #If we found at least one candidate, but no match
    if albedo is None and normal is None and len(textures)>0:
        return True
    #If we found more than one candidate, but only one match
    if (albedo is None or normal is None) and len(textures)>1:
        return True
    return False
def manually_set_textures(model, textures):
    print("Available images for \"" + model + "\" :")
    albedo, normal = None, None
    for i,t in enumerate(textures):
        print("\t" + str(i+1) + " - " + t)
    alb = int(input('Albedo (0 if None, -1 to pass): '))
    if alb == -1:
        return None, None, 1
    elif alb > 0:
        albedo = textures[alb-1]
    nor = int(input('Normal (0 if None, -1 to abort): '))
    if nor == -1:
        return None, None, 1
    elif nor > 0:
        normal = textures[nor-1]
    return albedo, normal, 0

#Will contain the models we must process as a list of {model, albedo, normal}
toDo = []
#Will contain the models we have to check as a list of {model, textures}
toConfirm = []
#Will contain the models we must pass as a list of models
notToDo = []

#Prepare the counts
nAutomatic, nToConfirm, nConfirmed, nFailed, nAlready = 0, 0, 0, 0, 0

#Check if some models were already processed
#Remove from the file the models which should exist but were deleted or moved
log     = os.path.join(args.output, "list.csv")
already = []
if os.path.exists(log):
    with open(log, "r") as f:
        already = [l.strip().split(",") for l in f.readlines()]
if len(already)>0:
    with open(log, "w") as f:
        for a in already:
            if os.path.exists(a[1]):
                f.write(",".join(a) + "\n")
already = [a for a in already if os.path.exists(a[1])]

#First, try to automatically match the texture files with the models
for i,d in enumerate(directories):
    model    = get_3d_model_in(d, extensions=["obj","ply","stl","fbx","dae","wrl","x3d"])
    #If the model was not previously processed
    if model not in [a[0] for a in already]:
        textures = get_textures_in(d)
        albedo, normal = separate_albedo_and_normals(textures)
        if something_looks_wrong(albedo, normal, textures):
            nToConfirm += 1
            toConfirm.append({"model": model, "textures":textures})
        else:
            nAutomatic += 1
            toDo.append({"model": model, "albedo":albedo, "normal":normal})
    #If the model was processed before
    else:
        nAlready += 1

if nAlready > 0:
    print("\nWARNING:\n" + bcolors.WARNING + str(nAlready) + " out of " + str(len(directories)) + " models have been processed previously and will be ignored" + bcolors.ENDC)

#If some textures did not match, ask for the user confirmation
if nToConfirm > 0:
    print("\nWARNING:\n" + bcolors.WARNING + str(nToConfirm) + " out of " + str(len(directories)) + " models do not have matching textures:" + bcolors.ENDC)
    for case in toConfirm:
        albedo, normal, error = manually_set_textures(case['model'], case['textures'])
        if error:
            nFailed += 1
            notToDo.append(model)
        else:
            nConfirmed += 1
            toDo.append({"model": case['model'], "albedo":albedo, "normal":normal})

#Print some info about the models we'll process
if len(toDo)>0:
    print("\nPROCESSING:")
    if nAutomatic>0:
        print(bcolors.OKGREEN + str(nAutomatic) + " models and texture sets were automatically matched" + bcolors.ENDC)
    if nConfirmed>0:
        print(bcolors.WARNING + str(nConfirmed) + " out of " + str(nToConfirm) + " models and texture sets were manually configured" + bcolors.ENDC)
    if nFailed>0:
        print(bcolors.FAIL + str(nFailed) + " models were discarded" + bcolors.ENDC)

#Do not take into account the models were deleted or moved in between
already = [a for a in already if os.path.exists(a[1])]

#Process the models for which we found texture matches
with open(log, "a") as f:
    for i,case in enumerate(toDo):

        #Destination file
        destination = os.path.join(args.output, args.prefix + "_" + str(i+1).zfill(3) + ".fbx" )

        #Check that the numbering does not already exist
        j = i
        while os.path.exists(destination):
            j+=1
            destination = os.path.join(args.output, args.prefix + "_" + str(j+1).zfill(3) + ".fbx" )

        #Create the appropriate command line
        cmd = ("blender --background --python " + bakeScript + " --"
        + " -i " + case["model"]
        + " -o " + destination
        + " -t " + str(args.target)
        + " -r " + str(args.resolution))
        if case["albedo"] is not None:
            cmd += " -a " + case["albedo"]
        if case["normal"] is not None:
            cmd += " -n " + case["normal"]
        cmd += " > " + os.path.join(args.output, "blender_log_" + str(j).zfill(3) + ".txt")

        print(cmd)
        sys.exit(0)

        #launch the command in a shell
        print(str(i+1).zfill(3) + " / " + str(len(toDo)).zfill(3) + " - " + case["model"][len(args.input)+1:] + " -> " + destination[len(args.output)+1:])
        err = os.system(cmd)
        if err:
            notToDo.append(case["model"])
        else:
            #Write the processed file to the log
            f.write(case["model"] + "," + destination + "\n")

#Say that we did not process some models
print("\nSUMMARY:")
for c in toDo:
    if c["model"] not in notToDo:
        print(bcolors.OKGREEN + "OK: " + c["model"][len(args.input)+1:] + bcolors.ENDC)
for a in already:
    print(bcolors.WARNING + "OK: " + a[0][len(args.input)+1:] + bcolors.ENDC)
for m in notToDo:
    print(bcolors.FAIL + "ERROR: " + m[len(args.input)+1:] + bcolors.ENDC)
print("")
