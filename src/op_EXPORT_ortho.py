import bpy
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector
import os

from . import fn_ortho

class export_orthoview(bpy.types.Operator, ExportHelper):
    bl_idname = "bakemyscan.export_orthoview"
    bl_label  = "Exports the orthoview"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".png"
    filter_glob = bpy.props.StringProperty(default="*.png", options={'HIDDEN'})
    margin      = bpy.props.IntProperty(default=50, min=5,max=512)
    resolution  = bpy.props.IntProperty(default=512, min=64,max=2048)

    filepath = bpy.props.StringProperty(
        name="Export ortho view",
        description="Image to export the view to",
        maxlen= 1024,
        default= ""
    )

    @classmethod
    def poll(self, context):
        #If more than two objects are selected
        if len(context.selected_objects)!=1:
            return 0
        #If no object is active
        if context.active_object is None:
            return 0
        #If something other than a MESH is selected
        if context.active_object.type != "MESH":
            return 0
        if context.mode!="OBJECT":
            return 0
        return 1

    def execute(self, context):
        obj = context.active_object

        #Hide all other objects
        visibleobjects = [o for o in bpy.data.objects if not o.hide and o!=obj]
        for o in visibleobjects:
            o.hide = True

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

        #Get the object's center and dimensions to fit the view later
        center = sum((obj.matrix_world*Vector(b) for b in obj.bound_box), Vector()) / 8
        print(center)
        maxDim = max( max(obj.dimensions[0], obj.dimensions[1]), obj.dimensions[2] )

        # 1 - Set the different rendering options
        fn_ortho._set_camera_options(camera_data)
        fn_ortho._set_render_options(resolution=self.resolution)
        fn_ortho._set_viewport_options(newArea)

        # 2 - Render the orthographic projections
        axises = ["TOP", "LEFT", "FRONT", "RIGHT", "BACK", "BOTTOM"]
        for axis in axises:
            print("Rendering a view from " + axis)
            fn_ortho._position_camera(camera, obj, axis, center, maxDim)
            bpy.data.scenes["Scene"].render.filepath = os.path.join(path, "render_"+axis+".png")
            bpy.ops.render.opengl(write_still=True)

        #Get the different images as a matrix format
        a01 = fn_ortho.crop(bpy.data.images.load(os.path.join(path, "render_BOTTOM.png")))
        a10 = fn_ortho.crop(bpy.data.images.load(os.path.join(path, "render_LEFT.png")))
        a11 = fn_ortho.crop(bpy.data.images.load(os.path.join(path, "render_FRONT.png")))
        a12 = fn_ortho.crop(bpy.data.images.load(os.path.join(path, "render_RIGHT.png")))
        a13 = fn_ortho.crop(bpy.data.images.load(os.path.join(path, "render_BACK.png")))
        a21 = fn_ortho.crop(bpy.data.images.load(os.path.join(path, "render_TOP.png")))
        #Create a big array by appending the images array into a common one
        final = fn_ortho.create_axio_array(a01, a10, a11, a12, a13, a21, M=self.margin)
        #Write the array to an image, taking into account the vertical inversion
        fn_ortho.array_to_image(final, os.path.join(path, self.properties.filepath))

        #Remove the unnecessary images
        for x in axises:
            f = os.path.join(path, "render_" + x + ".png")
            if os.path.exists(f):
                os.remove(f)

        #Once done, delete the camera
        bpy.data.objects.remove(bpy.data.objects[camera.name])

        #unhide the other objects
        for o in visibleobjects:
            o.hide = False

        #Close the double window !!??
        bottom, top = area, newArea
        bpy.ops.screen.area_join(min_x=bottom.x, min_y=bottom.y, max_x=top.x+top.width, max_y=top.y)
        for a in context.screen.areas:
            if a == bottom:
                context_copy = bpy.context.copy()
                context_copy['area'] = a
                bpy.ops.view3d.toolshelf(context_copy)
                bpy.ops.view3d.toolshelf(context_copy)

        self.report({'INFO'}, 'Orthoview exported')

        return {'FINISHED'}

def register() :
    bpy.utils.register_class(export_orthoview)

def unregister() :
    bpy.utils.unregister_class(export_orthoview)
