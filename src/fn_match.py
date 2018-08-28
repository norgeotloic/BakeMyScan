import imghdr
import os

def findMaterials(directory):
    """Recursively looks for sets of texture in the specified directory"""

    #lowercase versions of the matching patterns
    patterns = {
        "albedo"      : ["albedo", "diffuse", "dif", "alb", "basecolor", "color", "_d", "_col"],
        "ao"          : ["ao", "occlusion", "occ"],
        "metallic"    : ["metallic", "metal", "metalness"],
        "roughness"   : ["roughness", "rou", "rough", "_r"],
        "glossiness"  : ["specular", "ref", "spec", "glossiness", "reflect", "refl", "gloss"],
        "normal"      : ["normal", "normals", "nor", "_n", "norm", "nrm"],
        "height"      : ["height", "dis", "disp", "displacement"],
        "emission"    : ["emission", "emit", "emissive"],
        "opacity"     : ["alpha", "transparent", "opacity", "transp", "mask"],
    }

    #List all availables images in the specified directory
    images, materials = [], []
    for root, subFolders, files in os.walk(directory):
        for f in files:
            if imghdr.what(os.path.join(root, f)) is not None:
                image = {}
                #Get some basic info: path, directory name, cleaned image name
                image["file"] = os.path.join(root, f)
                image["dir"]  = os.path.dirname(os.path.join(root, f))
                #clean the name
                name = os.path.splitext(f)[0].lower().strip()
                name = name.replace("texturestom_","")
                name = name.replace("_1024", "")
                name = name.replace("2x2_", "")
                name = name.replace("3x3_", "")
                name = name.replace("2.5x2.5_","")
                name = name.replace(" ","_")
                name = name.replace("_6k", "")
                name = name.replace("_4k", "")
                name = name.replace("_3k", "")
                name = name.replace("_2k", "")
                image["name"] = name
                #Append the image to the images list
                images.append(image)

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

    #Rename the images ending with a number
    for i in images:
        try:
            n = int(i["name"][-1])
            try:
                x = int(i["name"][-2])
            except:
                i["name"] = i["name"][:-1]
        except:
            pass



    for i in images:
        #Look for one of the patterns in the image name
        patternFound = False
        for type in patterns:
            for suffix in patterns[type]:
                #If the image contains one of the suffixes, set its type and its material
                if i["name"].endswith(suffix):
                    i["type"] = type
                    i["material"] = i["name"].replace(suffix,"")
                    if i["material"].endswith("_"):
                        i["material"] = i["material"][:-1]
                    materials.append(i["material"])
                    patternFound = True
                    break
        #If we found nothing, set the variables to None for later usage
        if not patternFound:
            i["type"] = None
            i["material"] = None







    #sort the images and create a set of the material names
    images.sort(key = lambda image : image["file"])
    materials = set(materials)

    #Display some information about how it went
    print( "Found %d images corresponding to a pattern" % (len([i for i in images if i["type"] is not None])) )
    if(len([ i for i in images if i["type"] is None ])):
        print("%d images still not matched:" % (len([i for i in images if i["type"] is None])) )
        print(", ".join([ i["name"] for i in images if i["type"] is None ]))

    #Create some objects corresponding to the materials and textures
    MATERIALS = {}
    for i in images:
        if i["material"] is not None:
            #Create the material if it does not exist
            if i["material"] not in MATERIALS:
                MATERIALS[i["material"]] = {}
            #Check if the texture slot already exists
            if i["type"] in MATERIALS[i["material"]]:
                existing = MATERIALS[i["material"]][i["type"]]
                #If it is a diffuse vs albedo conflict
                if ("Dif" in i["file"] or "Dif" in existing) and ("Alb" in i["file"] or "Alb" in existing):
                    if "Alb" in i["file"]:
                        MATERIALS[i["material"]][i["type"]] = i
                    else:
                        images.remove(i)
                        continue
                #if it is a JaoPaulo "SD" vs normal conflict, keep the normal
                if "SD" in i["file"] or "SD" in existing:
                    if "SD" in existing:
                        MATERIALS[i["material"]][i["type"]] = i
                    else:
                        images.remove(i)
                        continue
                #if the ends are _3K and _6K for instance, keep the _6K
                end3letters = i["file"].split(".")[-2][-3:]
                if end3letters[0] == "_" and end3letters[2] == "K":
                    old = MATERIALS[i["material"]][i["type"]]
                    oldend3letters = old.split(".")[-2][-3:]
                    if int(oldend3letters[1])<int(end3letters[1]):
                        MATERIALS[i["material"]][i["type"]] = i
                    else:
                        images.remove(i)
                        continue
                else:
                    print("ERROR on %s" % (i["file"]))
                    print("\tthe slot %s is already in use by %s" % (i["type"], MATERIALS[i["material"]][i["type"]]))
            MATERIALS[i["material"]][i["type"]] = i["file"]

    return MATERIALS
