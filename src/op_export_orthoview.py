import bpy
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector
import numpy as np
import os
import subprocess

from . import fn_ortho

D = bpy.data
C = bpy.context

class export_orthoview(bpy.types.Operator, ExportHelper):
    bl_idname = "bakemyscan.export_orthoview"
    bl_label  = "Exports the orthoview"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".png"
    filter_glob = bpy.props.StringProperty(default="*.png", options={'HIDDEN'})

    filepath = bpy.props.StringProperty(
        name="Export ortho view",
        description="Image to export the view to",
        maxlen= 1024,
        default= ""
    )

    def execute(self, context):
        obj = context.active_object

        #Get the parameters
        path = os.path.dirname(os.path.abspath(self.properties.filepath))
        name = os.path.splitext(os.path.basename(os.path.abspath(self.properties.filepath)))[0]

        #Split the view to get a blank area to work in
        window = bpy.context.window
        screen = bpy.context.screen
        scene = bpy.context.scene
        for area in screen.areas:
            if area.type == "VIEW_3D":
                break
        else:
            raise Exception("No 3D View!")
        areas = [area.as_pointer() for area in screen.areas]
        override = bpy.context.copy()
        override['area'] = area
        bpy.ops.screen.area_split(override, direction='HORIZONTAL', factor=0.5, mouse_x=-100, mouse_y=-100)
        newArea = [a for a in bpy.context.screen.areas if a.type=="VIEW_3D" and a!=area][0]

        #Add a new camera to the scene and make it active
        camera_data = bpy.data.cameras.new("orthocam")
        camera = bpy.data.objects.new("cam", camera_data)
        bpy.context.scene.objects.link(camera)
        bpy.context.scene.update()
        bpy.context.scene.camera = camera

        #Set final images options
        R      = 512 #thumbnail resolution
        M      = 5   #thumbnail margin
        W      = 10  #scale width
        TW     = 4 * (2*M + R) #Final width
        TH     = 3 * (2*M + R) #Final height
        trim   = True

        #Get the object's center and dimensions to fit the view later
        center = sum((obj.matrix_world*Vector(b) for b in obj.bound_box), Vector()) / 8
        print(center)
        maxDim = np.max(obj.dimensions)

        # 1 - Set the different rendering options
        _set_camera_options(camera_data)
        _set_render_options(resolution=512)
        _set_viewport_options(newArea)

        # 2 - Render the orthographic projections
        axises = ["TOP", "LEFT", "FRONT", "RIGHT", "BACK", "BOTTOM"]
        for axis in axises:
            print("Rendering a view from " + axis)
            _position_camera(camera, obj, axis, center, maxDim)
            bpy.data.scenes["Scene"].render.filepath = os.path.join(path, "render_"+axis+".png")
            bpy.ops.render.opengl(write_still=True)


        # 3 - Trim the images to take less space
        if trim:
            for x in axises:#["TOP", "BOTTOM"]:
                IMAGEMAGICK_trim("TOP",    os.path.join(path, "render_" + x + ".png"))
                IMAGEMAGICK_trim("BOTTOM", os.path.join(path, "render_" + x + ".png"))
                IMAGEMAGICK_trim("LEFT",   os.path.join(path, "render_" + x + ".png"))
                IMAGEMAGICK_trim("RIGHT",  os.path.join(path, "render_" + x + ".png"))

        # 4 - Merge the projections together and create the blueprint image
        IMAGEMAGICK_createAxio(
            trim,
            [ os.path.join(path, img) for img in ["render_" + x + ".png" for x in axises] ],
            os.path.abspath(self.properties.filepath),
            R,
            M
        )

        #Remove the unnecessary images
        for x in axises:
            f = os.path.join(path, "render_" + x + ".png")
            if os.path.exists(f):
                os.remove(f)

        #Once done, delete the camera
        bpy.data.objects.remove(bpy.data.objects[camera.name])

        #Close the double window
        #bpy.ops.screen.area_join(override)

        """
        # 5 - maybe add the scales
        if not trim:
            overlayScale(0)
            overlayScale(1)
        overlayScale(2)
        """

        return {'FINISHED'}

def register() :
    bpy.utils.register_class(orthoproject_project)

def unregister() :
    bpy.utils.unregister_class(orthoproject_project)
