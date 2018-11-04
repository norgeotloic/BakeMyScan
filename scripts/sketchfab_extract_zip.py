import sys
import os
import argparse
import imghdr
import argparse
import zipfile
import shutil

def extract_all_archives(_directory, keep=False):
    """Recursively extract all archives in a directory"""

    def list_available_archives():
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

    def extract_one_archive(archive_path):
        _unzip_to = os.path.abspath(archive_path)[:-4]
        if archive_path.endswith(".zip") or archive_path.endswith(".ZIP"):
            zip_ref = zipfile.ZipFile(archive_path, 'r')
            zip_ref.extractall(_unzip_to)
            zip_ref.close()
        elif archive_path.endswith(".7z") or archive_path.endswith(".7Z"):
            os.system("7zr x '" + archive_path + "' -o" + os.path.dirname(_unzip_to) + " > /dev/null 2>&1")
        elif archive_path.endswith(".rar") or archive_path.endswith(".RAR"):
            os.system("unrar e '" + archive_path + "' " + _unzip_to + "/ > /dev/null 2>&1" )
        else:
            print("The archive " + archive_path + " is not in a known format!, aborting")
            sys.exit(1)
        if not keep:
            os.remove(archive_path)

    compteur = 0
    done = []
    while len([a for a in list_available_archives() if a not in done]) > 0:
        archives = [a for a in list_available_archives() if a not in done]
        for a in archives:
            if a not in done:
                print("Unzipping " + a)
                extract_one_archive(a)
                done.append(a)
        compteur+=1
        if compteur > 10:
            print("More than 10 recursions, exiting!")
            sys.exit()

def move_files_to_root(_directory):
    """Move images and models from subdirectories to the root directory"""
    #Move the textures and models in the root of every subdirectory
    for directory in os.listdir(_directory):
        directory = os.path.abspath(os.path.join(_directory,directory))
        if os.path.isdir(directory):
            for root, directories, filenames in os.walk(directory):
                for d in directories:
                    pass
                for filename in filenames:
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
    for directory in os.listdir(_directory):
        directory = os.path.abspath(os.path.join(_directory,directory))
        if os.path.isdir(directory):
            for root, directories, filenames in os.walk(directory):
                for d in directories:
                    shutil.rmtree(os.path.join(root, d))
    #Remove the duplicated images
    for directory in os.listdir(_directory):
        directory = os.path.abspath(os.path.join(_directory,directory))
        images  = [os.path.join(directory, f) for f in os.listdir(directory) if imghdr.what(os.path.join(directory, f))]
        while len(set([os.path.splitext(i)[0] for i in images])) != len(images):
            found = False
            for i1 in images:
                for i2 in images:
                    if i1!=i2 and os.path.splitext(i1)[0] == os.path.splitext(i2)[0]:
                        print("Removed %s" % os.path.join(directory, i2))
                        os.remove(os.path.join(directory, i2))
                        images.remove(i2)
                        found = True
                        break
                if found:
                    break

def remove_images_not_like_albedo(_directory):
    """obsolete: delete all the images which don't seem like an albedo"""
    for directory in os.listdir(_directory):
        directory = os.path.abspath(os.path.join(_directory,directory))
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

if __name__ == "__main__":

    #Parse and check the arguments
    parser = argparse.ArgumentParser(description="Extract all .zip downloaded from Sketchfab into clean directories")
    parser.add_argument("-i", "--input",  type=str, required=True, help="Input directory")
    args = parser.parse_args()

    #Extract and process the archives
    extract_all_archives(args.input)
    move_files_to_root(args.input)
    #remove_images_not_like_albedo(args.input)
