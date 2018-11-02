import bpy

class BakeMyScanPrefs(bpy.types.AddonPreferences):
    bl_idname     = 'BakeMyScan'
    mmgs          = bpy.props.StringProperty(name="MMGS  Executable", subtype='FILE_PATH')
    instant       = bpy.props.StringProperty(name="Instant Meshes Executable", subtype='FILE_PATH')
    quadriflow    = bpy.props.StringProperty(name="Quadriflow Executable", subtype='FILE_PATH')
    meshlabserver = bpy.props.StringProperty(name="Meshlabserver Executable", subtype='FILE_PATH')

    def draw(self, context):
        layout = self.layout
        layout.label(text="Executable paths")
        layout.prop(self, "instant")
        layout.prop(self, "mmgs")
        layout.prop(self, "quadriflow")
        layout.prop(self, "meshlabserver")

def register():
    bpy.utils.register_class(BakeMyScanPrefs)
def unregister():
    bpy.utils.unregister_class(BakeMyScanPrefs)
