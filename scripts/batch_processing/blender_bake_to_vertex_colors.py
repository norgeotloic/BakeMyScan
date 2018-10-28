import bpy

objects = [o for o in bpy.context.selected_objects if o.type == "MESH"]

#Some baking parameters
bpy.context.scene.render.use_bake_selected_to_active = True
bpy.context.scene.render.bake_type = "TEXTURE"
bpy.context.scene.render.use_bake_to_vertex_color = True

for obj in objects:
    #Select the object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    bpy.context.scene.objects.active = obj
    #Remesh it
    bpy.ops.bakemyscan.remesh_iterative(limit=1500)
    #Select the new object
    new = bpy.context.scene.objects.active
    obj.select = True
    new.select = True
    bpy.context.scene.objects.active = new
    #Rename the new object
    new.name = obj.name + "_lowpoly"
    #Add a vertex color group to it
    new.data.vertex_colors.new()
    bpy.ops.object.vertex_group_add()

    #And a new material
    if not bpy.data.materials.get("baking"):
        bpy.data.materials.new("baking")
    mat = bpy.data.materials.get("baking")
    mat.use_vertex_color_paint = True
    new.material_slots[0].material = mat
    #Bake the color to the vertex color
    if not bpy.data.images.get("baking"):
        bpy.data.images.new("baking", 512, 512)
    image = bpy.data.images.get("baking")
    tex = None
    if not bpy.data.textures.get("baking"):
        bpy.data.textures.new( "baking", type = 'IMAGE')
    tex = bpy.data.textures.get("baking")
    tex.image = image
    slots = mat.texture_slots
    slots.clear(0)
    mtex = slots.add()
    mtex.texture = tex
    mtex.texture_coords = 'UV'
    bpy.ops.paint.vertex_paint_toggle()
    bpy.ops.paint.vertex_paint_toggle()
    bpy.ops.object.editmode_toggle()
    bpy.data.screens['UV Editing'].areas[1].spaces[0].image = image
    bpy.context.object.active_material.use_textures[0] = False
    bpy.ops.object.bake_image()
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.bake_image()

    #Move the object to the last layer
    bpy.ops.object.select_all(action='DESELECT')
    new.select = True
    bpy.ops.object.move_to_layer(layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True))


    #Give info
    print("Successfully remeshed %s" % obj.name)
