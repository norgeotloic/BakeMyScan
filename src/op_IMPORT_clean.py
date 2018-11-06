import bpy
import addon_utils

class clean_object(bpy.types.Operator):
    bl_idname = "bakemyscan.clean_object"
    bl_label  = "Preprocess"
    bl_options = {"REGISTER", "UNDO"}

    materials   = bpy.props.BoolProperty(name="materials",   description="Materials", default=True)
    doubles     = bpy.props.BoolProperty(name="doubles",     description="Duplicate vertices", default=True)
    loose       = bpy.props.BoolProperty(name="loose",       description="Loose geometry", default=True)
    sharp       = bpy.props.BoolProperty(name="sharp",       description="Sharp", default=True)
    normals     = bpy.props.BoolProperty(name="normals",     description="Normals", default=True)
    center      = bpy.props.BoolProperty(name="center",      description="Center", default=True)
    scale       = bpy.props.BoolProperty(name="scale",       description="Scale", default=True)
    smooth      = bpy.props.IntProperty( name="smooth",      description="Smoothing iterations", default=1, min=0, max=10)
    shade       = bpy.props.BoolProperty(name="shade",       description="Shade smooth", default=True)
    manifold    = bpy.props.BoolProperty(name="manifold",    description="Make manifold", default=False)

    @classmethod
    def poll(cls, context):
        #Need to be in object mode
        if context.mode!="OBJECT":
            return 0
        #At least one object of type MESH must be selected
        if len([o for o in context.selected_objects if o.type=="MESH"]) == 0:
            return 0
        return 1

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.label("Global")
        self.layout.prop(self, "materials", text="Clean materials")
        self.layout.prop(self, "center",    text="Center the object")
        self.layout.prop(self, "scale",     text="Scale to unit box")
        self.layout.label("Geometry")
        self.layout.prop(self, "doubles",   text="Remove duplicated vertices")
        self.layout.prop(self, "loose",     text="Delete loose geometry")
        self.layout.prop(self, "manifold",  text="Make manifold")
        self.layout.label("Normals")
        self.layout.prop(self, "sharp",     text="Remove sharp marks")
        self.layout.prop(self, "normals",   text="Normalize normals")
        self.layout.prop(self, "shade",    text="Shade smooth")
        self.layout.prop(self, "smooth",    text="Smoothing iterations")
        col = self.layout.column(align=True)

    def execute(self, context):

        #Get the mesh objects currently selected
        objects = [o for o in context.selected_objects if o.type=="MESH"]

        for obj in objects:

            #Select the new mesh, and make it the active object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            context.scene.objects.active = obj

            #Remove the material slots
            if self.materials:
                while len(obj.material_slots):
                    obj.active_material_index = 0
                    bpy.ops.object.material_slot_remove()

            #Go into edit mode
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')

            #Sharp edges
            if self.sharp:
                bpy.ops.mesh.mark_sharp(clear=True)

            #Duplicated vertices
            if self.doubles:
                bpy.ops.mesh.remove_doubles()

            #Loose geometry
            if self.loose:
                bpy.ops.mesh.delete_loose()

            #Normals:
            if self.normals:
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
                bpy.ops.mesh.normals_make_consistent(inside=False)

            #Go out of edit mode
            bpy.ops.object.editmode_toggle()

            #Non manifold
            if self.manifold:
                addon_utils.enable("object_print3d_utils")
                bpy.ops.mesh.print3d_clean_non_manifold()

            #Smoothing
            if self.smooth>0:
                bpy.ops.object.modifier_add(type='SMOOTH')
                bpy.context.object.modifiers["Smooth"].iterations = self.smooth
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")

            if self.shade:
                bpy.ops.object.shade_smooth()

            #Center
            if self.center:
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
                bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

            #Scale
            if self.scale:
                s = 1.0/(max(max(obj.dimensions[0], obj.dimensions[1]), obj.dimensions[2]))
                obj.scale = [s,s,s]
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

            #Zoom on it
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = {'area': area, 'region': area.regions[-1]}
                    bpy.ops.view3d.view_selected(override, use_all_regions=False)

        self.report({'INFO'}, 'Pre-processing complete')
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(clean_object)

def unregister() :
    bpy.utils.unregister_class(clean_object)
