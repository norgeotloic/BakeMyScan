import sys
import os
import argparse
import imghdr
import argparse
import tempfile
import time
import shutil

if __name__ == "__main__":

    #Parse and check the arguments
    parser = argparse.ArgumentParser(description="Process all models from a Sketchfab collection to lowpoly")
    parser.add_argument("-i", "--input",    type=str, required=True, help="Model or collection url")
    args = parser.parse_args()

    #Move the textures and models in the root of every subdirectory
    for directory in os.listdir(args.input):
        directory = os.path.abspath(os.path.join(args.input,directory))
        if os.path.isdir(directory):
            for root, directories, filenames in os.walk(directory):
                for d in directories:
                    pass
                for filename in filenames:
                    #Textures and models
                    isImage = imghdr.what(os.path.join(root, filename))
                    isModel = os.path.splitext(filename)[1].lower() in [".obj", ".dae", ".stl", ".fbx", ".wrl", ".ply", ".x3d"]
                    if isImage or isModel:
                        IN  = os.path.join(root, filename)
                        OUT = os.path.join(directory, filename)
                        try:
                            os.rename(IN, OUT)
                        except:
                            print("Could not move %s to %s" % (IN, OUT))

    #Remove the unnecessary directories
    files = []
    for directory in os.listdir(args.input):
        directory = os.path.abspath(os.path.join(args.input,directory))
        if os.path.isdir(directory):
            for root, directories, filenames in os.walk(directory):
                for d in directories:
                    shutil.rmtree(os.path.join(root, d))

    #Remove the duplicated images
    for directory in os.listdir(args.input):
        directory = os.path.abspath(os.path.join(args.input,directory))
        images  = [os.path.join(directory, f) for f in os.listdir(directory) if imghdr.what(os.path.join(directory, f))]
        while len(set([os.path.splitext(i)[0] for i in images])) != len(images):
            found = False
            for i1 in images:
                for i2 in images:
                    if i1!=i2 and os.path.splitext(i1)[0] == os.path.splitext(i2)[0]:
                        print("Removed %s", os.path.join(directory, i2))
                        os.remove(os.path.join(directory, i2))
                        images.remove(i2)
                        found = True
                        break
                if found:
                    break
