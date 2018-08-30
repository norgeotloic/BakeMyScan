import bpy
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector
import numpy as np
import os
import subprocess

from . import fn_soft

#Blender camera and opengl render functions
def _set_camera_options(camera_data):
    camera_data.type = 'ORTHO'
    camera_data.clip_start = 0.01
    camera_data.clip_end = 10000
    marginFactor = 1.0
    camera_data.ortho_scale = marginFactor * np.max(bpy.context.active_object.dimensions)
def _set_render_options(resolution):
    bpy.context.scene.render.resolution_y = resolution
    bpy.context.scene.render.resolution_x = resolution
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
    bpy.context.scene.render.image_settings.color_mode ='RGBA'
def _set_viewport_options(area):
    area.spaces[0].region_3d.view_perspective = 'ORTHO'
    bpy.context.space_data.show_textured_solid  = False
    bpy.context.space_data.fx_settings.use_ssao = True
    bpy.context.space_data.use_matcap           = True
    bpy.context.space_data.show_only_render     = True
    bpy.context.space_data.matcap_icon          = '06'
def _position_camera(cam, obj, axis, center, maxDim):
    cam.location[0] = cam.location[1] = cam.location[2] = 3*maxDim
    bpy.ops.view3d.viewnumpad(type=axis)
    bpy.ops.view3d.camera_to_view()
    if axis == "TOP" or axis == "BOTTOM":
        cam.location[0] = center[0]
        cam.location[1] = center[1]
        if axis=="TOP":
            cam.location[2] = center[2] + 0.6 * obj.dimensions[2]
        elif axis=="BOTTOM":
            cam.location[2] = center[2] - 0.6 * obj.dimensions[2]
    if axis == "LEFT" or axis == "RIGHT":
        if axis=="LEFT":
            cam.location[0] = center[0] - 0.6 * obj.dimensions[0]
        elif axis=="RIGHT":
            cam.location[0] = center[0] + 0.6 * obj.dimensions[0]
        cam.location[1] = center[1]
        cam.location[2] = center[2]
    if axis == "FRONT" or axis == "BACK":
        cam.location[0] = center[0]
        if axis=="FRONT":
            cam.location[1] = center[1] - 0.6 * obj.dimensions[1]
        elif axis=="BACK":
            cam.location[1] = center[1] + 0.6 * obj.dimensions[1]
        cam.location[2] = center[2]
#Image functions
def create_scale_image(ax, output):

    #Get the scale bar properties
    dim      = object.dimensions[ax]
    name     = ["X", "Y", "Z"][ax]
    nPxScale = int((dim / np.max(object.dimensions)) * R) # nb of pixels inside
    margin   = int((R - nPxScale)/2) # nb of pixels outside of the scalebar
    barSwitch = int(nPxScale/(dim * 10))+1 #Every barSwitch pixel, switch color

    #The blender image object
    if ax == 0:
        image = bpy.data.images.new(name='scale'+name, width=R, height=W, alpha = True)
    else:
        image = bpy.data.images.new(name='scale'+name, width=W, height=R, alpha = True)
    pixels = [(0.) for i in range(len(image.pixels))]

    #Init the colors
    color = [0,0,0,0]


    if ax==0:#Horizontal image
        for col in range(R):
            #Pixels on the left and on the right are transparent
            if col<margin or col>R-margin:
                for row in range(W):
                    pixels[R*4*row + col*4 + 3] = 0.
            #Pixels in the center are white/black according to the size
            else:
                if (col-margin) % barSwitch == 0:
                    color = [0.8,0.8,0.8] if color[0] == 0 else [0,0,0]
                for row in range(W):
                    pixels[R*4*row + col*4 + 0] = color[0]
                    pixels[R*4*row + col*4 + 1] = color[1]
                    pixels[R*4*row + col*4 + 2] = color[2]
                    pixels[R*4*row + col*4 + 3] = 1.
    elif ax==1 or ax==2:#Vertical image
        for row in range(R):
            if row<margin or row>R-margin:
                for col in range(W):
                    pixels[W*4*row + col*4 + 3] = 0.
            #Pixels in the center are white/black according to the size
            else:
                if (row-margin) % barSwitch == 0:
                    color = [0.8,0.8,0.8] if color[0] == 0 else [0,0,0]
                for col in range(W):
                    pixels[W*4*row + col*4 + 0] = color[0]
                    pixels[W*4*row + col*4 + 1] = color[1]
                    pixels[W*4*row + col*4 + 2] = color[2]
                    pixels[W*4*row + col*4 + 3] = 1.

    #save the image
    image.pixels = pixels
    image.filepath_raw = output
    image.save()
    #bpy.ops.image.save_as(save_as_render=False, filepath="/home/loic/Desktop/tmp/scaleX.png")
    return image
def IMAGEMAGICK_trim(side, image, output=None):
    cmd = fn_soft.convertExe
    cmd+= image + " "
    #Get the side
    if side=="LEFT":
        cmd+= "-gravity East "
    elif side=="RIGHT":
        cmd+="-gravity West "
    elif side=="TOP":
        cmd+= "-gravity South "
    elif side=="BOTTOM":
        cmd+="-gravity North "
    else:
        return
    px  = "1x0" if (side=="LEFT" or side=="RIGHT") else "0x1"
    cmd+= "-background white -splice " + px + " -background black -splice " + px + " "
    cmd+= "-trim  +repage -chop " + px + " "
    #If an output is specified, write to it, else write to the original image
    if output is not None:
        cmd+= output
    else:
        cmd+= image
    fn_soft.execute(cmd)
def IMAGEMAGICK_createAxio(trim, images, output, thumbres, marg):
    if not trim:
        #images = [top, left, front, right, back, bottom]
        #creates a grid of 3 rows, 4 columns
        cmd = fn_soft.montageExe + "-background transparent "
        cmd+= "null: " + images[0] + " null: null: "
        cmd+= " ".join( images[1:5] )  + " "
        cmd+= "null: " + images[5] + " null: null: "
        cmd+= "-tile 4x3  -geometry "
        cmd+= str(thumbres) + "x" + str(thumbres) + "+" + str(marg) + "+" + str(marg) + " "
        cmd+= output
        fn_soft.execute(cmd)
    else:
        #Do the middle line first
        cmd = fn_soft.montageExe + "-background transparent "
        cmd+= " ".join( images[1:5] )  + " "
        cmd+= "-tile 4x1 -geometry +50+50 "
        cmd+= output
        fn_soft.execute(cmd)
        #Make a bigger canvas
        finalHeight = 6*50 + 2*IMAGEMAGICK_getsize(images[0])[1] + IMAGEMAGICK_getsize(images[1])[1]
        cmd = fn_soft.convertExe + output + " "
        cmd+= "-gravity center -background transparent -extent 0x" + str(finalHeight) + " " + output
        fn_soft.execute(cmd)
        #Then add the top and bottom views
        IMAGEMAGICK_overlay(output, images[0], x=3*50 + IMAGEMAGICK_getsize(images[1])[0], y=50)
        IMAGEMAGICK_overlay(output, images[5], x=3*50 + IMAGEMAGICK_getsize(images[1])[0], y=50 + IMAGEMAGICK_getsize(images[0])[1] + 2*50 + IMAGEMAGICK_getsize(images[1])[1] + 50)
def IMAGEMAGICK_overlay(baseImage, overlayImage, output=None, x=0, y=0):
    cmd = fn_soft.composeExe
    cmd+= overlayImage + " "
    cmd+= "-geometry +" + str(x) + "+" + str(y) + " "
    if output is not None:
        cmd+= baseImage + " " + output
    else:
        cmd+= baseImage + " " + baseImage
    fn_soft.execute(cmd)
def IMAGEMAGICK_annotate(image, annotation, x=0, y=0):
    cmd = fn_soft.convertExe + image + " "
    cmd+= "-gravity center -pointsize 30 -fill black "
    cmd+= "-annotate "
    cmd+= "-" + str(x) if x < TW/2 else "+" + str(x)
    cmd+= "-" + str(y) if y > TH/2 else "+" + str(y)
    cmd+= " '" + annotation + "' "
    cmd+= image
    fn_soft.execute(cmd)
def IMAGEMAGICK_getsize(image):
    out = subprocess.check_output(fn_soft.convertExe + image + ' -format "%w %h" info:', shell=True)
    size = [int(x) for x in out.strip().split()]
    return size
#Wrapper for the different scale images
def overlayScale(ax):
    name = ["X", "Y", "Z"][ax]
    #Define the offsets for every scale
    imgOffset = [
        [M + R + 2*M,    M + R + 2*M + R + M - 50], #X
        [M + R + M + 15, M                       ], #Y
        [M + R + M + 15, M + R + 2*M             ]  #Z
    ][ax]
    txtOffset = [
        [TW/2 - (M + R + 2*M + R/2), R/2 + M -10],      #X
        [R + 2*M - 50,               -(R/2 + M + R/2)], #Y
        [R + 2*M - 50,               0]                 #Z
    ][ax]
    #Run the processes
    scaleImage = create_scale_image(ax, os.path.join(path, "scale" + name + ".png"))
    IMAGEMAGICK_overlay( PROJ, scaleImage.filepath_raw, x = imgOffset[0], y = imgOffset[1])
    IMAGEMAGICK_annotate( PROJ, '%.2f m' % object.dimensions[ax], x = txtOffset[0], y = txtOffset[1])

#Functions to remove Imagemagick dependency
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
def create_axio_array(a01, a10, a11, a12, a13, a21, M=50):
    #check that everything is ok (compatible sizes)
    assert(a01.shape[1] == a11.shape[1] == a21.shape[1])
    assert(a10.shape[0] == a11.shape[0] == a12.shape[0] == a13.shape[0])
    #optionnal sanity check
    assert(a01.shape[0] == a21.shape[0])#top and bottom same height
    assert(a10.shape[1] == a12.shape[1])#left and right same width
    assert(a11.shape[1] == a13.shape[1])#front and back same width
    #Create the new array
    A = np.zeros((
        a01.shape[0] + a11.shape[0] + a21.shape[0] + 4*M,
        a10.shape[1] + a11.shape[1] + a12.shape[1] + a13.shape[1] + 5*M,
        4
    ))
    #And fill it
    #First line
    A[M:M+a01.shape[0],2*M+a10.shape[1]:2*M+a10.shape[1]+a11.shape[1],:] = a01
    #Second line
    A[2*M+a01.shape[0]:2*M+a01.shape[0]+a10.shape[0], M:M+a10.shape[1],:] = a10
    A[2*M+a01.shape[0]:2*M+a01.shape[0]+a10.shape[0], 2*M+a10.shape[1]:2*M+a10.shape[1]+a11.shape[1],:] = a11
    A[2*M+a01.shape[0]:2*M+a01.shape[0]+a10.shape[0], 3*M+a10.shape[1]+a11.shape[1]:3*M+a10.shape[1]+a11.shape[1]+a12.shape[1],:] = a12
    A[2*M+a01.shape[0]:2*M+a01.shape[0]+a10.shape[0], 4*M+a10.shape[1]+a11.shape[1]+a12.shape[1]:4*M+a10.shape[1]+a11.shape[1]+a12.shape[1]+a13.shape[1],:] = a13
    #Third line
    A[3*M+a01.shape[0]+a10.shape[0]:-M,2*M+a10.shape[1]:2*M+a10.shape[1]+a11.shape[1],:] = a21
    return A
def array_to_image(arr, path):
    img = bpy.data.images.new("tmp", arr.shape[1], arr.shape[0], alpha=1)
    img.file_format = "PNG"
    img.filepath_raw = path
    img.pixels = np.ravel(arr)
    img.save()
    bpy.data.images.remove(img)
