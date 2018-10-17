import bpy
import numpy as np
import os

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

    return pixels[starth:endh,startw:endw,:]
def create_axio_array(a01, a10, a11, a12, a13, a21, M=50):
    """
    assert(a01.shape[1] == a11.shape[1] == a21.shape[1])
    assert(a10.shape[0] == a11.shape[0] == a12.shape[0] == a13.shape[0])
    """
    #Are the size compatible?? If not, correct them
    if not a01.shape[1] == a11.shape[1] == a21.shape[1]:
        print("Width do not correspond")
        maxWidth = np.max([a01.shape[1], a11.shape[1], a21.shape[1]])

        tmp = np.zeros((a01.shape[0], maxWidth, 4))
        tmp[:a01.shape[0],:a01.shape[1],:] = a01
        a01 = tmp

        tmp = np.zeros((a11.shape[0], maxWidth, 4))
        tmp[:a11.shape[0],:a11.shape[1],:] = a11
        a11 = tmp

        tmp = np.zeros((a21.shape[0], maxWidth, 4))
        tmp[:a21.shape[0],:a21.shape[1],:] = a21
        a21 = tmp

    if not a10.shape[0] == a11.shape[0] == a12.shape[0] == a13.shape[0]:
        print("Height do not correspond")
        maxHeight = np.max([a10.shape[0], a11.shape[0], a12.shape[0], a13.shape[0]])

        tmp = np.zeros((maxHeight, a10.shape[1], 4))
        tmp[:a10.shape[0],:a10.shape[1], :] = a10
        a10 = tmp

        tmp = np.zeros((maxHeight, a11.shape[1], 4))
        tmp[:a11.shape[0],:a11.shape[1], :] = a11
        a11 = tmp

        tmp = np.zeros((maxHeight, a12.shape[1], 4))
        tmp[:a12.shape[0],:a12.shape[1], :] = a12
        a12 = tmp

        tmp = np.zeros((maxHeight, a13.shape[1], 4))
        tmp[:a13.shape[0],:a13.shape[1], :] = a13
        a13 = tmp

    #optionnal sanity check
    """
    assert(a01.shape[0] == a21.shape[0])#top and bottom same height
    assert(a10.shape[1] == a12.shape[1])#left and right same width
    assert(a11.shape[1] == a13.shape[1])#front and back same width
    """

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
