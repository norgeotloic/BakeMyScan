import sys
import os
import argparse
import imghdr
import argparse
import zipfile
import tempfile
import time

#Functions to recursively extract archives in a directory
def list_archives(_directory):
    files = []
    for root, directories, filenames in os.walk(_directory):
        for directory in directories:
            pass
        for filename in filenames:
            if filename[0]!=".":
                files.append(os.path.join(root, filename).strip())
    files = [ f for f in files if sum( [ x[0]=="." for x in f.split("/")[1:] ] ) == 0 ]
    archives = [ f for f in files if f.lower().endswith(".zip") or f.lower().endswith(".7z") or f.lower().endswith(".rar") ]
    return archives
def unzip_archive(_archive, keep=False):
    _unzip_to = os.path.abspath(_archive)[:-4]
    if _archive.endswith(".zip") or _archive.endswith(".ZIP"):
        zip_ref = zipfile.ZipFile(_archive, 'r')
        zip_ref.extractall(_unzip_to)
        zip_ref.close()
    elif _archive.endswith(".7z") or _archive.endswith(".7Z"):
        os.system("7zr x '" + _archive + "' -o" + os.path.dirname(_unzip_to) + " > /dev/null 2>&1")
    elif _archive.endswith(".rar") or _archive.endswith(".RAR"):
        os.system("unrar e '" + _archive + "' " + _unzip_to + "/ > /dev/null 2>&1" )
    else:
        print("The archive " + _archive + " is not in a known format!, aborting")
        sys.exit(1)
    if not keep:
        os.remove(_archive)
def extract_all_archives(_directory, keep=False):
    compteur = 0
    done = []
    while len([a for a in list_archives(_directory) if a not in done]) > 0:
        archives = [a for a in list_archives(_directory) if a not in done]
        for a in archives:
            if a not in done:
                print("Unzipping " + a)
                unzip_archive(a, keep)
                done.append(a)
        compteur+=1
        if compteur > 10:
            print("More than 10 recursions, exiting!")
            sys.exit()

if __name__ == "__main__":

    #Parse and check the arguments
    parser = argparse.ArgumentParser(description="Process all models from a Sketchfab collection to lowpoly")
    parser.add_argument("-i", "--input",    type=str, required=True, help="Model or collection url")
    parser.add_argument("-t", "--textures", dest="output", default=False, action="store_true", help="Move the textures to the root folder")
    args = parser.parse_args()

    #Extract the archives
    extract_all_archives(args.input)
