import bpy
import os
from . import fn_soft
import tempfile
import time
from mathutils import Vector
import numpy as np

class BaseRemesher(bpy.types.Operator):
    bl_idname = "bakemyscan.empty_remesher"
    bl_label  = "Empty remersher structure"

    bl_options = {"REGISTER", "UNDO"}

    #For executable remeshers
    tmp        = tempfile.TemporaryDirectory()
    executable = None
    results    = []
    keepMaterials = False

    #For remeshers which need to duplicate the object
    workonduplis = False
    hide_old     = False


    @classmethod
    def poll(self, context):
        if self.executable is not None:
            if executable == "":
                return 0
        if len(context.selected_objects)!=1 or context.active_object is None:
            return 0
        for o in context.selected_objects:
            if o.type != "MESH":
                return 0
        if context.mode!="OBJECT" and context.mode!="SCULPT":
            return 0
        return 1
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    #To be overridden
    def setexe(self, context):
        pass
    def export(self, context):
        pass
    def reimport(self, context):
        pass
    def remesh(self, context):
        pass
    def status(self, context):
        if self.results[2] != 0:
            self.report({"ERROR"}, "Remesh error, look in the console")
            print("OUTPUT:\n%s\nERROR:\n%s\CODE:\n%s" % self.results)
            return{"CANCELLED"}

    def preprocess(self, context):
        self.initialobject   = context.active_object
        self.existingobjects = [o for o in bpy.data.objects]
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        #Operators working on a duplicated object
        if self.workonduplis:
            bpy.ops.object.duplicate()
            self.copiedobject = context.scene.objects.active
            #Apply the modifiers
            for m in self.copiedobject.modifiers:
                bpy.ops.object.modifier_apply(modifier=m.name)
    def postprocess(self, context):
        #Check that there is only one new object
        newObjects = [o for o in bpy.data.objects if o not in self.existingobjects]
        if len(newObjects)==0:
            self.report({'ERROR'}, '0 new objects')
        elif len(newObjects)>1:
            self.report({'ERROR'}, '0 new objects')
        else:
            #Get the new object
            self.new = newObjects[0]
            #Make it selected and active
            bpy.ops.object.select_all(action='DESELECT')
            self.new.select=True
            bpy.context.scene.objects.active = self.new
            #Remove edges marked as sharp, and delete the loose geometry
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.mark_sharp(clear=True)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete_loose()
            bpy.ops.object.editmode_toggle()
            #Shade smooth and rename it
            #bpy.ops.object.shade_smooth()
            #bpy.context.object.data.use_auto_smooth = False
            #context.active_object.name = self.initialobject.name + "." + self.bl_label.lower().replace(" ","")
            #Remove hypothetical material
            if not self.keepMaterials:
                while len(context.active_object.material_slots):
                    context.active_object.active_material_index = 0
                    bpy.ops.object.material_slot_remove()
            #Hide the old object
            if self.hide_old:
                self.initialobject.hide = True
    def execute(self, context):
        #Set the executable path
        self.setexe(context)
        #Preprocess
        self.preprocess(context)
        #Export
        if self.executable is not None:
            self.exporttime = time.time()
            self.export(context)
            self.exporttime = time.time() - self.exporttime
        #Remesh
        self.remeshtime = time.time()
        self.remesh(context)
        self.remeshtime = time.time() - self.remeshtime
        #Check the output
        if self.executable is not None:
            self.status(context)
        #Import
        if self.executable is not None:
            self.importtime = time.time()
            try:
                self.reimport(context)
            except:
                self.report({"ERROR"}, "Import error, look in the console")
                print("OUTPUT:\n%s\nERROR:\n%s\CODE:\n%s" % self.results)
            self.importtime = time.time() - self.importtime
        #Post-process
        self.postprocess(context)
        #Show the wireframe (debug)
        #context.object.show_wire = True
        #context.object.show_all_edges = True
        #Report
        self.report({'INFO'}, 'Remeshed to %d polygons' % len(context.active_object.data.polygons))
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(BaseRemesher)

def unregister() :
    bpy.utils.unregister_class(BaseRemesher)
