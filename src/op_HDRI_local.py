import os
import bpy
import imghdr

def enum_previews_from_directory_items(self, context):
    """EnumProperty callback"""
    enum_items = []

    if context is None:
        return enum_items

    directory = context.window_manager.my_previews_dir

    # Get the preview collection (defined in register func).
    pcoll = preview_collections["main"]

    if directory == pcoll.my_previews_dir:
        return pcoll.my_previews
    else:
        pcoll.clear()

    print("Scanning directory: %s" % directory)

    if directory and os.path.exists(directory):
        # Scan the directory for png files
        image_paths = []
        for fn in os.listdir(directory):
            f = os.path.join( directory, fn)
            if not os.path.isdir(f):
                if imghdr.what(f) is not None or f.endswith(".hdr"):
                    image_paths.append(f)

        for i, image in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            name = os.path.basename(image)
            thumb = pcoll.load(image, image, 'IMAGE', force_reload=True)
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.my_previews = enum_items
    pcoll.my_previews_dir = directory

    return pcoll.my_previews

preview_collections = {}

def update_hdri_background(self, context):
    #Get the image
    directory = context.window_manager.my_previews_dir
    hdri      = context.window_manager.my_previews
    hdri      = os.path.join(directory, hdri)
    #Load it into the world
    world = bpy.data.worlds['World']
    world.use_nodes = True
    #Find an envrionment texture node or create it
    env = world.node_tree.nodes.get('Environment Texture')
    if env is None:
        env = world.node_tree.nodes.new(type="ShaderNodeTexEnvironment")
    #Assign an image to the node
    env.image = bpy.data.images.load(hdri, check_existing=True)
    #Link it to the background
    background = world.node_tree.nodes.get('Background')
    world.node_tree.links.new(env.outputs["Color"], background.inputs["Color"])
    #Try to switch to render mode
    try:
        bpy.context.space_data.viewport_shade = 'RENDERED'
    except:
        pass

    return None

def register():
    import bpy
    bpy.types.WindowManager.my_previews_dir = bpy.props.StringProperty(name="Directory",subtype='DIR_PATH',default="")
    bpy.types.WindowManager.my_previews = bpy.props.EnumProperty(items=enum_previews_from_directory_items,update=update_hdri_background)

    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    pcoll.my_previews_dir = ""
    pcoll.my_previews = ()
    preview_collections["main"] = pcoll

def unregister():

    del bpy.types.WindowManager.my_previews_dir
    del bpy.types.WindowManager.my_previews

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
