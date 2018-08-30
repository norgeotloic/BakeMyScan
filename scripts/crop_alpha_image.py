import bpy
import os
import numpy as np

def crop(img):
    #Load or pass according to the image type
    if type(img) is bpy.types.Image:
        pass
    elif type(img) is str and os.path.exists(img):
        img = bpy.data.images.load(img)
    else:
        return None

    #Get the image info and pixels
    w      = img.size[0]
    h      = img.size[1]
    pixels = np.array(img.pixels, dtype=float).reshape((w,h,4))
    path   = os.path.abspath(img.filepath_raw)
    bpy.data.images.remove(img)

    #Crop top and bottom
    starth,endh = 0,0
    for i,row in enumerate(pixels):
        if sum(row[:,3]) == 0.0:
            pass
        else:
            starth = i
            break
    for i,row in enumerate(pixels[::-1]):
        if sum(row[:,3]) == 0.0:
            pass
        else:
            endh = h - i
            break
    #Crop left and right
    startw,endw = 0,0
    for i,col in enumerate(np.transpose(pixels,(1,0,2))):
        if sum(col[:,3]) == 0.0:
            pass
        else:
            startw = i
            break
    for i,col in enumerate(np.transpose(pixels,(1,0,2))[::-1]):
        if sum(col[:,3]) == 0.0:
            pass
        else:
            endw = h - i
            break

    #Create a new image
    """
    new = bpy.data.images.new("test", endw-startw, endh-starth, alpha=1)
    new.file_format = "PNG"
    newPath = os.path.join(
        os.path.dirname(path),
        os.path.basename(path).split(".")[0] + "_crop.png"
    )
    new.filepath_raw = newPath
    new.pixels = np.ravel(pixels[starth:endh,startw:endw,:])
    new.save()
    return new
    """
    return pixels[starth:endh,startw:endw,:]
def create_axio_array(a01, a10, a11, a12, a13, a21):
    #check that everything is ok (compatible sizes)
    assert(a01.shape[1] == a11.shape[1] == a21.shape[1])
    assert(a10.shape[0] == a11.shape[0] == a12.shape[0] == a13.shape[0])
    #optionnal sanity check
    assert(a01.shape[0] == a21.shape[0])#top and bottom same height
    assert(a10.shape[1] == a12.shape[1])#left and right same width
    assert(a11.shape[1] == a13.shape[1])#front and back same width
    #Create the new array
    A = np.zeros((
        a01.shape[0] + a11.shape[0] + a21.shape[0],
        a10.shape[1] + a11.shape[1] + a12.shape[1] + a13.shape[1],
        4
    ))
    #And fill it
    #First line
    A[:a01.shape[0],a10.shape[1]:a10.shape[1]+a11.shape[1],:] = a01
    #Second line
    A[a01.shape[0]:a01.shape[0]+a10.shape[0], :a10.shape[1],:] = a10
    A[a01.shape[0]:a01.shape[0]+a10.shape[0], a10.shape[1]:a10.shape[1]+a11.shape[1],:] = a11
    A[a01.shape[0]:a01.shape[0]+a10.shape[0], a10.shape[1]+a11.shape[1]:a10.shape[1]+a11.shape[1]+a12.shape[1],:] = a12
    A[a01.shape[0]:a01.shape[0]+a10.shape[0], a10.shape[1]+a11.shape[1]+a12.shape[1]:a10.shape[1]+a11.shape[1]+a12.shape[1]+a13.shape[1],:] = a13
    #Third line
    A[a01.shape[0]+a10.shape[0]:,a10.shape[1]:a10.shape[1]+a11.shape[1],:] = a21
    return A
def array_to_image(arr, path):
    img = bpy.data.images.new("tmp", arr.shape[1], arr.shape[0], alpha=1)
    img.file_format = "PNG"
    img.filepath_raw = path
    img.pixels = np.ravel(arr)
    img.save()
    bpy.data.images.remove(img)

#Get the different images as a matrix format
a01 = crop(bpy.data.images.load("C://Users/lnorgeot/Desktop/close.png"))
a10 = a01
a11 = a01
a12 = a01
a13 = a01
a21 = a01
#Create a big array by appending the images array into a common one
final = create_axio_array(a01, a10, a11, a12, a13, a21)
#Write the array to an image, taking into account the vertical inversion
array_to_image(final[::-1,:,:], "C://Users/lnorgeot/Desktop/close_crop.png")

"""
newPath = os.path.join(
    os.path.dirname(path),
    os.path.basename(path).split(".")[0] + "_crop.png"
)
"""
