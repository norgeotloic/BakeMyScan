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

    #Remove the duplicated images
    for directory in os.listdir(args.input):
        directory = os.path.abspath(os.path.join(args.input,directory))
        images  = [os.path.join(directory, f) for f in os.listdir(directory) if imghdr.what(os.path.join(directory, f))]
        if len(images) == 1:
            pass
        else:
            albedo = None
            #try to find an "albedo" or "diffuse" in the image names
            for i in images:
                if "albedo" in i.lower() or "diff" in i.lower():
                    albedo = i
            #if we found an albedo image, remove the others
            if albedo is not None:
                for i in images:
                    if i!=albedo:
                        os.remove(i)
            else:
                #find the images with "norm", "rough", "metal", "ao" in their name
                toremove = []
                for i in images:
                    if "norm" in i.lower() or "rough" in i.lower() or "metal" in i.lower() or "ao" in i.lower():
                        toremove.append(i)
                #Delete the images if only one will remain
                if len(toremove) == len(images) - 1:
                    for t in toremove:
                        os.remove(t)
                else:
                    print("Image removal failed for %s" % directory)
