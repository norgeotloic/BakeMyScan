# coding: utf8
import imghdr
import os
import bpy

def node_tree_normal_to_color():
    #Get the group if it already exists
    #if bpy.data.node_groups.get("normal_to_color"):
    #    _node_tree = bpy.data.node_groups.get("normal_to_color")
    #    return _node_tree
    #Create the group and its input/output sockets
    _node_tree = bpy.data.node_groups.new(type="ShaderNodeTree", name="normal_to_color")
    #Aliases for the functions
    AN = _node_tree.nodes.new
    LN = _node_tree.links.new
    #Inputs and outputs
    _input     = AN(type="NodeGroupInput")
    _output    = AN(type="NodeGroupOutput")
    _node_tree.inputs.new('NodeSocketVector','Normal')
    _node_tree.outputs.new('NodeSocketColor','Color')


    #Nodes
    _tangent   = AN(type="ShaderNodeTangent")
    _normal    = AN(type="ShaderNodeNewGeometry")
    _bitangent = AN(type="ShaderNodeVectorMath")
    _dot1      = AN(type="ShaderNodeVectorMath")
    _dot2      = AN(type="ShaderNodeVectorMath")
    _dot3      = AN(type="ShaderNodeVectorMath")
    _combine   = AN(type="ShaderNodeCombineXYZ")
    _curve     = AN(type="ShaderNodeVectorCurve")
    _gamma     = AN(type="ShaderNodeGamma")
    #Parameters
    _dot1.operation      = "DOT_PRODUCT"
    _dot2.operation      = "DOT_PRODUCT"
    _dot3.operation      = "DOT_PRODUCT"
    _bitangent.operation = "CROSS_PRODUCT"
    _gamma.inputs[1].default_value = 2.2
    for _c in _curve.mapping.curves:
        _c.points[0].location[1] = 0.0
    #Links
    LN(_input.outputs["Normal"],     _dot1.inputs[0])
    LN(_input.outputs["Normal"],     _dot2.inputs[0])
    LN(_input.outputs["Normal"],     _dot3.inputs[0])
    LN(_tangent.outputs["Tangent"],  _bitangent.inputs[1])
    LN(_normal.outputs["Normal"],    _bitangent.inputs[0])
    LN(_bitangent.outputs["Vector"], _dot2.inputs[1])
    LN(_tangent.outputs["Tangent"],  _dot1.inputs[1])
    LN(_normal.outputs["Normal"],    _dot3.inputs[1])
    LN(_dot1.outputs["Value"],       _combine.inputs[0])
    LN(_dot2.outputs["Value"],       _combine.inputs[1])
    LN(_dot3.outputs["Value"],       _combine.inputs[2])
    LN(_combine.outputs["Vector"],   _curve.inputs["Vector"])
    LN(_curve.outputs["Vector"],     _gamma.inputs["Color"])
    LN(_gamma.outputs["Color"],      _output.inputs["Color"])
    #Position
    _input.location = [0,400]
    _normal.location = [0,200]
    _input.location = [0,0]
    _tangent.location = [0,-200]
    _bitangent.location = [200,0]
    _dot1.location = [400,200]
    _dot2.location = [400,0]
    _dot3.location = [400,-200]
    _combine.location = [600,0]
    _curve.location = [800,0]
    _gamma.location = [1100,0]
    _output.location = [1300,0]
    #Return
    return _node_tree

def parameter_to_node(tree, parameter):
    """Converts an input str, int, float, list or tuple to a color or Image node"""
    _node = None
    #If it is a scalar value or a list or tuple
    if type(parameter) is float or type(parameter) is int or type(parameter) is list or type(parameter) is tuple:
        _col = [1,1,1,1]
        #If it is a tuple of ints or floats of len 3
        if type(parameter) is list or type(parameter) is tuple:
            if len(parameter)==3:
                if type(parameter[0]) is int or type(parameter[0]) is float:
                    _col = list(parameter) + [1]
        #If it is a float or an int
        else:
            _col = [parameter, parameter, parameter, 1]
        _node = tree.nodes.new(type="ShaderNodeRGB")
        _node.outputs["Color"].default_value = _col
    #If it is a blender image
    elif type(parameter) is bpy.types.Image:
        _node = tree.nodes.new(type="ShaderNodeTexImage")
        _node.image = parameter
    #If it is a path
    elif type(parameter) is str and os.path.exists(parameter):
        _node = tree.nodes.new(type="ShaderNodeTexImage")
        _node.image = bpy.data.images.load(parameter, check_existing=False)
    #Else
    else:
        pass
    #print(parameter, _node)
    return _node

def node_tree_pbr():

    #Create the group and its input/output sockets
    _node_tree = bpy.data.node_groups.new(type="ShaderNodeTree", name="group")
    _node_tree.inputs.new('NodeSocketFloat','UV scale')
    _node_tree.inputs.new('NodeSocketFloat','Height')
    _node_tree.outputs.new('NodeSocketShader','BSDF')

    #Aliases for the functions
    AN = _node_tree.nodes.new
    LN = _node_tree.links.new
    #Inputs and outputs
    _input     = AN(type="NodeGroupInput")
    _output    = AN(type="NodeGroupOutput")
    _input.name = _input.label = "input"
    _output.name = _output.label = "output"
    #Nodes
    _principled  = AN(type="ShaderNodeBsdfPrincipled")
    _principled.name = _principled.label = "BakeMyScan PBR"
    #Create images for each of them
    _albedo     = AN(type="ShaderNodeTexImage")
    _ao         = AN(type="ShaderNodeTexImage")
    _metallic   = AN(type="ShaderNodeTexImage")
    _roughness  = AN(type="ShaderNodeTexImage")
    _glossiness = AN(type="ShaderNodeTexImage")
    _normal     = AN(type="ShaderNodeTexImage")
    _height     = AN(type="ShaderNodeTexImage")
    _opacity    = AN(type="ShaderNodeTexImage")
    _emission   = AN(type="ShaderNodeTexImage")
    _vertexcolors = AN(type="ShaderNodeAttribute")
    #Set the nodes names to get them later
    _albedo.name     = _albedo.label     = "albedo"
    _ao.name         = _ao.label         = "ao"
    _metallic.name   = _metallic.label   = "metallic"
    _roughness.name  = _roughness.label  = "roughness"
    _glossiness.name = _glossiness.label = "glossiness"
    _normal.name     = _normal.label     = "normal"
    _height.name     = _height.label     = "height"
    _opacity.name    = _opacity.label    = "opacity"
    _emission.name   = _emission.label   = "emission"
    _vertexcolors.name = _vertexcolors.label = "vertexcolors"
    #Add te other nodes (mix, inverts, maps...)
    _bump              = AN(type="ShaderNodeBump")
    _nmap              = AN(type="ShaderNodeNormalMap")
    _ao_mix            = AN(type="ShaderNodeMixRGB")
    _opacity_mix       = AN(type="ShaderNodeMixShader")
    _opacity_shader    = AN(type="ShaderNodeBsdfTransparent")
    _emission_mix      = AN(type="ShaderNodeMixShader")
    _emission_shader   = AN(type="ShaderNodeEmission")
    _glossiness_invert = AN(type="ShaderNodeInvert")
    _reroute  = AN(type="NodeReroute")
    _uv       = AN(type="ShaderNodeUVMap")
    _mapping  = AN(type="ShaderNodeMapping")
    _separate = AN(type="ShaderNodeSeparateXYZ")
    _scalex   = AN(type="ShaderNodeMath")
    _scaley   = AN(type="ShaderNodeMath")
    _scalez   = AN(type="ShaderNodeMath")
    _combine  = AN(type="ShaderNodeCombineXYZ")
    #Parameters for opacity and emission
    _emission_mix.inputs[0].default_value = 0.
    _opacity_mix.inputs[0].default_value  = 1.
    #Other nodes names to fill them in
    _bump.label = _bump.name = "bump"
    _nmap.label = _nmap.name = "nmap"
    _ao_mix.label = _ao_mix.name = "ao_mix"
    _opacity_mix.label = _opacity_mix.name = "opacity_mix"
    _opacity_shader.label = _opacity_shader.name = "opacity_shader"
    _emission_mix.label = _emission_mix.name = "emission_mix"
    _emission_shader.label = _emission_shader.name = "emission_shader"
    _glossiness_invert.label = _glossiness_invert.name = "glossiness_invert"
    _reroute.label = _reroute.name = "reroute"
    _uv.label = _uv.name = "uv"
    _mapping.label = _mapping.name = "mapping"
    _separate.label = _separate.name = "separate"
    _scalex.label = _scalex.name = "scalex"
    _scaley.label = _scaley.name = "scaley"
    _scalez.label = _scalez.name = "scalez"
    _combine.label = _combine.name = "combine"
    #Parameters
    _scalex.operation = _scaley.operation = _scalez.operation = 'MULTIPLY'
    _scalex.inputs[1].default_value = _scaley.inputs[1].default_value = _scalez.inputs[1].default_value = 1
    _ao_mix.blend_type = "MULTIPLY"
    _ao_mix.inputs[2].default_value=[1,1,1,1]
    _ao_mix.inputs[1].default_value=[1,1,1,1]
    _vertexcolors.attribute_name = "Col"
    #Links
    LN(_principled.outputs["BSDF"], _output.inputs["BSDF"])
    LN(_input.outputs["UV scale"], _reroute.inputs[0])
    LN(_uv.outputs["UV"], _mapping.inputs["Vector"])
    LN(_mapping.outputs["Vector"], _separate.inputs["Vector"])
    LN(_separate.outputs["X"], _scalex.inputs[0])
    LN(_separate.outputs["Y"], _scaley.inputs[0])
    LN(_separate.outputs["Z"], _scalez.inputs[0])
    LN(_reroute.outputs[0], _scalex.inputs[1])
    LN(_reroute.outputs[0], _scaley.inputs[1])
    LN(_reroute.outputs[0], _scalez.inputs[1])
    LN(_scalex.outputs["Value"], _combine.inputs["X"])
    LN(_scaley.outputs["Value"], _combine.inputs["Y"])
    LN(_scalez.outputs["Value"], _combine.inputs["Z"])
    for node in _node_tree.nodes:
        if node.type == "TEX_IMAGE":
            LN(_combine.outputs["Vector"], node.inputs["Vector"])


    LN(_glossiness.outputs["Color"], _glossiness_invert.inputs["Color"])
    LN(_bump.outputs["Normal"], _principled.inputs["Normal"])
    LN(_input.outputs["Height"], _bump.inputs["Distance"])
    LN(_nmap.outputs["Normal"], _bump.inputs["Normal"])

    #Opacity and emission
    LN(_emission_shader.outputs["Emission"], _emission_mix.inputs[2])
    LN(_principled.outputs["BSDF"], _emission_mix.inputs[1])
    LN(_emission_mix.outputs["Shader"], _opacity_mix.inputs[2])
    LN(_opacity_shader.outputs["BSDF"], _opacity_mix.inputs[1])
    LN(_opacity_mix.outputs["Shader"], _output.inputs["BSDF"])


    #Position everything
    _output.location     = [200,0]
    _principled.location = [0,0]
    #Input mapping and vector
    _uv.location       = [-2000, 0]
    _mapping.location  = [-1800, 0]
    _input.location    = [-1600, 300]
    _reroute.location  = [-1400, 200]
    _separate.location = [-1400, 0]
    _scalex.location   = [-1200, 100]
    _scaley.location   = [-1200, 0]
    _scalez.location   = [-1200,-100]
    _combine.location  = [-1000, 0]
    #Input nodes for the principled node
    _albedo.location = [-200,0]
    _albedo.location = [-400,100]
    _ao.location = [-400,-100]
    _ao_mix.location = [-200, 0]
    _vertexcolors.location = [-400,0]
    _metallic.location = [-200, -200]
    _metallic.color_space = "NONE"
    _roughness.location = [-200, -400]
    _roughness.color_space = "NONE"
    _glossiness.location = [-400, -400]
    _glossiness_invert.location = [-200, -400]
    _glossiness.color_space = "NONE"
    _bump.location = [-200, -600]
    _nmap.location = [-400, -700]
    _height.location = [-400, -500]
    _normal.location = [-600, -700]
    _normal.color_space = "NONE"
    #Post-shader emission and opacity mix

    _emission.location = [-200, 200]
    _emission_shader.location = [0, 200]
    _emission_mix.location = [200, 100]
    off = [400,200]
    _opacity.location = [-200 + off[0], 200 + off[1]]
    _opacity_shader.location = [0 + off[0], 200 + off[1]]
    _opacity_mix.location = [200 + off[0], 100 + off[1]]
    _output.location = [800,400]

    #Collapse all the nodes
    for n in _node_tree.nodes:
        if n.type!="BSDF_PRINCIPLED":
            n.hide = True
    #Return
    return _node_tree

def cycles_material_to_vertex_color(material):
    """Transforms a Cycles material into a blender one"""

    material.use_nodes = False
    material.use_vertex_color_paint = True

    #Bake the color to the vertex color
    if not bpy.data.images.get("vc"):
        bpy.data.images.new("vc", 4, 4)
    image = bpy.data.images.get("vc")
    tex = None
    if not bpy.data.textures.get("baking"):
        bpy.data.textures.new( "baking", type = 'IMAGE')
    tex = bpy.data.textures.get("baking")
    tex.image = image
    slots = mat.texture_slots
    slots.clear(0)
    mtex = slots.add()
    mtex.texture = tex
