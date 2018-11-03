import imghdr
import os
import re

def rreplace(s, old, new):
    li = s.rsplit(old, 1)
    return new.join(li)

def normalize_name(str):
    #https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string
    _rep     = {
        "texturestom_":"",
        "_1024":"",
        "2x2_":"",
        "3x3_":"",
        "2.5x2.5_":"",
        " ":"_",
        "_6k":"",
        "_4k":"",
        "_3k":"",
        "_2k":""
    }
    _rep     = dict((re.escape(k), _rep[k]) for k in _rep)
    _pattern = re.compile("|".join(_rep.keys()))
    _text    = _pattern.sub(lambda m: _rep[re.escape(m.group(0))], str)
    return _text
def ignore_trailing_variations(images):
    imageVariations = [i for i in images if "_var" in i["name"]]
    toIgnore = []
    a,b,c,d = 0,0,0,0
    for i1 in imageVariations:
        for i2 in imageVariations:
            i1Splitted = "".join([x for x in i1["file"].split("_") if "var" not in x.lower()])
            i2Splitted = "".join([x for x in i2["file"].split("_") if "var" not in x.lower()])
            if i1Splitted == i2Splitted and i1!=i2:
                a+=1
                try:
                    n1 = int(i1["name"][-1])
                    n2 = int(i2["name"][-1])
                    if n1<n2:
                        toIgnore.append(i2)
                        i1["name"] = i1["name"].replace("_var","")[:-1]
                        break
                    else:
                        toIgnore.append(i1)
                        i2["name"] = i2["name"].replace("_var","")[:-1]
                        break
                except:
                    pass
    for i in images:
        if "_var" in i["name"]:
            for i2 in toIgnore:
                if i["file"] == i2["file"]:
                    images.remove(i)
    for i in images:
        if "_var" in i["name"]:
            i["name"] = i["name"].replace("_var","")[:-1]
    for i in images:
        try:
            n = int(i["name"][-1])
            try:
                x = int(i["name"][-2])
            except:
                i["name"] = i["name"][:-1]
        except:
            pass
    return images

def find_pattern_in_image(f):
    patterns = {
        "albedo"      : ["albedo", "diffuse", "dif", "alb", "base_color", "basecolor", "color", "_d", "_col","tex"],
        "ao"          : ["ao", "ambient_occlusion", "occlusion", "occ"],
        "metallic"    : ["metallic", "metal", "metalness"],
        "roughness"   : ["roughness", "rou", "rough", "_r"],
        "glossiness"  : ["specular", "ref", "spec", "glossiness", "reflect", "refl", "gloss"],
        "normal"      : ["normal", "normals", "nor", "_n", "norm", "nrm"],
        "height"      : ["height", "dis", "disp", "displacement"],
        "emission"    : ["emission", "emit", "emissive"],
        "opacity"     : ["alpha", "transparent", "opacity", "transp", "mask"],
    }
    for slot in patterns:
        for suffix in patterns[slot]:
            name = os.path.splitext(f)[0].lower().strip()
            if name.endswith(suffix):
                name = rreplace(name, suffix,"")#This fixes a case like "greasy_metal_roughness"
                while name.endswith("_"):
                    name = name[:-1]
                return slot, name
    return None, None

def material_names_in_images(images):
    for i in images:
        slot, name = find_pattern_in_image(i["name"])
        i["type"] = slot
        i["material"] = name
    return images
def material_dictionnary(images):
    materials = {}
    for i in images:
        if i["material"] is not None:
            #Create the material if it does not exist
            if i["material"] not in materials:
                materials[i["material"]] = {}
            #Check if the texture slot already exists
            if i["type"] in materials[i["material"]]:
                existing = materials[i["material"]][i["type"]]
                #If it is a diffuse vs albedo conflict
                if ("Dif" in i["file"] or "Dif" in existing) and ("Alb" in i["file"] or "Alb" in existing):
                    if "Alb" in i["file"]:
                        materials[i["material"]][i["type"]] = i
                    else:
                        images.remove(i)
                        continue
                #if it is a JaoPaulo "SD" vs normal conflict, keep the normal
                if "SD" in i["file"] or "SD" in existing:
                    if "SD" in existing:
                        materials[i["material"]][i["type"]] = i
                    else:
                        images.remove(i)
                        continue
                #if the ends are _3K and _6K for instance, keep the _6K
                end3letters = i["file"].split(".")[-2][-3:]
                if end3letters[0] == "_" and end3letters[2] == "K":
                    old = materials[i["material"]][i["type"]]
                    oldend3letters = old.split(".")[-2][-3:]
                    if int(oldend3letters[1])<int(end3letters[1]):
                        materials[i["material"]][i["type"]] = i
                    else:
                        images.remove(i)
                        continue
                else:
                    print("ERROR on %s" % (i["file"]))
                    print("\tthe slot %s is already in use by %s" % (i["type"], materials[i["material"]][i["type"]]))
            materials[i["material"]][i["type"]] = i["file"]

    return materials

def findMaterials(directory, recursive = True):
    """Recursively looks for sets of texture in the specified directory"""

    #List all availables images in the specified directory
    images = []
    if recursive:
        for root, subFolders, files in os.walk(directory):
            files = [f for f in files if not f[0] == '.']
            subFolders[:] = [d for d in subFolders if not d[0] == '.']
            for f in files:
                if imghdr.what(os.path.join(root, f)) is not None:
                    images.append({
                        "file": os.path.join(root, f),
                        "dir":  os.path.dirname(os.path.join(root, f)),
                        "name": normalize_name(os.path.splitext(f)[0].lower().strip())
                    })
    else:
        for f in [f for f in os.listdir(directory) if f[0]!="." and not os.path.isdir(os.path.join(directory,f))]:
            if imghdr.what(os.path.join(directory, f)) is not None:
                images.append({
                    "file": os.path.join(directory, f),
                    "dir":  os.path.dirname(os.path.join(directory, f)),
                    "name": normalize_name(os.path.splitext(f)[0].lower().strip())
                })

    images.sort(key = lambda image : image["file"])
    images    = ignore_trailing_variations(images)
    images    = material_names_in_images(images)

    #Display some information about how it went
    print( "Found %d images corresponding to a pattern" % (len([i for i in images if i["type"] is not None])) )
    if(len([ i for i in images if i["type"] is None ])):
        print("%d images still not matched:" % (len([i for i in images if i["type"] is None])) )
        print(", ".join([ i["name"] for i in images if i["type"] is None ]))

    materials = material_dictionnary(images)
    return materials

def findMaterialFromTexture(texture):
    """Find textures similar to the one passed as argument in a directory"""

    #Normalize names and paths
    texture   = os.path.abspath(texture)
    directory = os.path.dirname(texture)
    name      = os.path.splitext(os.path.basename(texture))[0]

    #All other images in the directory
    candidates = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    candidates = [f for f in candidates if imghdr.what(f)]

    #Create the appropriate structure to match materials
    images = [{"file": f, "dir": directory, "name": normalize_name(os.path.splitext(os.path.basename(f))[0])} for f in candidates]

    #Sort them
    images.sort(key = lambda image : image["file"])

    #Assign materials to them
    images    = ignore_trailing_variations(images)
    images    = material_names_in_images(images)

    #Get the matching ones
    liste = [i for i in images if i["file"]==texture]
    if len(liste)>0:
        image     = liste[0]
        images    = [i for i in images if i["material"] == image["material"]]

    #Display some information about how it went
    """
    print( "Found %d images corresponding to a pattern" % (len([i for i in images if i["type"] is not None])) )
    if(len([ i for i in images if i["type"] is None ])):
        print("%d images still not matched:" % (len([i for i in images if i["type"] is None])) )
        print(", ".join([ i["name"] for i in images if i["type"] is None ]))
    """

    #Create the dictionnary
    materials = material_dictionnary(images)

    #Return the material containing the texture
    if len(materials.keys()) == 1:
        n = list(materials.keys())[0]
        return n, materials[n]
    else:
        return None, None




def images_in_directory(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if imghdr.what(os.path.join(directory, f)) is not None]
