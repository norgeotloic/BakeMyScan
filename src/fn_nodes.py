# coding: utf8
import imghdr
import os
import bpy

#The new version, with the simple add option without the blue channel
def node_tree_combine_normals():
    #Get the group if it already exists
    if bpy.data.node_groups.get("combine_normals"):
        _node_tree = bpy.data.node_groups.get("combine_normals")
        return _node_tree
    #Create the group and its input/output sockets
    _node_tree = bpy.data.node_groups.new(type="ShaderNodeTree", name="combine_normals")
    _node_tree.inputs.new('NodeSocketColor','Geometry')
    _node_tree.inputs.new('NodeSocketColor','Surface')
    _node_tree.outputs.new('NodeSocketVector','Normal')
    #Aliases for the functions
    AN = _node_tree.nodes.new
    LN = _node_tree.links.new
    #Inputs and outputs
    _input     = AN(type="NodeGroupInput")
    _output    = AN(type="NodeGroupOutput")
    #Nodes
    _separate1 = AN(type="ShaderNodeSeparateRGB")
    _separate2 = AN(type="ShaderNodeSeparateRGB")
    _add1      = AN(type="ShaderNodeMath")
    _add2      = AN(type="ShaderNodeMath")
    _multiply1 = AN(type="ShaderNodeMath")
    _multiply2 = AN(type="ShaderNodeMath")
    _combine   = AN(type="ShaderNodeCombineRGB")
    _normalMap = AN(type="ShaderNodeNormalMap")
    #Parameters
    _add1.operation = "ADD"
    _add2.operation = "ADD"
    _multiply1.operation = "MULTIPLY"
    _multiply1.inputs[1].default_value = 0.5
    _multiply2.operation = "MULTIPLY"
    _multiply2.inputs[1].default_value = 0.5
    #Links
    LN(_input.outputs["Geometry"],   _separate1.inputs["Image"])
    LN(_input.outputs["Surface"],   _separate2.inputs["Image"])
    LN(_separate1.outputs["R"],   _add1.inputs[0])
    LN(_separate2.outputs["R"],   _add1.inputs[1])
    LN(_separate1.outputs["G"],   _add2.inputs[0])
    LN(_separate2.outputs["G"],   _add2.inputs[1])
    LN(_add1.outputs["Value"],   _multiply1.inputs[0])
    LN(_add2.outputs["Value"],   _multiply2.inputs[0])
    LN(_multiply1.outputs["Value"],   _combine.inputs["R"])
    LN(_multiply2.outputs["Value"],   _combine.inputs["G"])
    LN(_separate1.outputs["B"],   _combine.inputs["B"])
    LN(_combine.outputs["Image"],   _normalMap.inputs["Color"])
    LN(_normalMap.outputs["Normal"], _output.inputs["Normal"])
    #Position
    _input.location     = [0,0]
    _separate1.location = [200,100]
    _separate2.location = [200,-100]
    _add1.location      = [400,100]
    _add2.location      = [400,-100]
    _multiply1.location = [600,100]
    _multiply2.location = [600,-100]
    _combine.location   = [800,0]
    _normalMap.location = [1000,0]
    _output.location    = [1200,0]
    #Return
    return _node_tree

#A new version, trying to reproduce the Imagemagick overlay behaviour
def node_tree_combine_normals_2():
    #cf https://blenderartists.org/t/baking-normals-within-other-maps/621625/22
    #Get the group if it already exists
    """
    if bpy.data.node_groups.get("combine_normals2"):
        _node_tree = bpy.data.node_groups.get("combine_normals2")
        return _node_tree
    """
    #Create the group and its input/output sockets
    _node_tree = bpy.data.node_groups.new(type="ShaderNodeTree", name="combine_normals2")
    _node_tree.inputs.new('NodeSocketColor','Geometry')
    _node_tree.inputs.new('NodeSocketColor','Surface')
    _node_tree.inputs.new('NodeSocketFloat','Factor')
    _node_tree.outputs.new('NodeSocketColor','Color')
    #Aliases for the functions
    AN = _node_tree.nodes.new
    LN = _node_tree.links.new
    #Inputs and outputs
    _input     = AN(type="NodeGroupInput")
    _output    = AN(type="NodeGroupOutput")
    #Nodes
    _value1    = AN(type="ShaderNodeValue")
    _value2    = AN(type="ShaderNodeValue")
    _value3    = AN(type="ShaderNodeValue")
    _value4    = AN(type="ShaderNodeValue")
    _value5    = AN(type="ShaderNodeValue")
    _value6    = AN(type="ShaderNodeValue")
    _value7    = AN(type="ShaderNodeValue")
    _addval    = AN(type="ShaderNodeMath")
    _combine1  = AN(type="ShaderNodeCombineRGB")
    _combine2  = AN(type="ShaderNodeCombineRGB")
    _combine3  = AN(type="ShaderNodeCombineRGB")
    _multiply1 = AN(type="ShaderNodeMixRGB")
    _multiply2 = AN(type="ShaderNodeMixRGB")
    _multiply3 = AN(type="ShaderNodeMixRGB")
    _multiply4 = AN(type="ShaderNodeMixRGB")
    _add1      = AN(type="ShaderNodeMixRGB")
    _add2      = AN(type="ShaderNodeMixRGB")
    _add3      = AN(type="ShaderNodeMixRGB")
    _dot       = AN(type="ShaderNodeVectorMath")
    _separate  = AN(type="ShaderNodeSeparateRGB")
    _divide    = AN(type="ShaderNodeMixRGB")
    _substract = AN(type="ShaderNodeMixRGB")
    _normalize = AN(type="ShaderNodeVectorMath")
    #Values
    _value1.outputs["Value"].default_value = 2.0
    _value2.outputs["Value"].default_value = -1.0
    _value3.outputs["Value"].default_value = -2.0
    _value4.outputs["Value"].default_value = 2.0
    _value5.outputs["Value"].default_value = 1.0
    _value6.outputs["Value"].default_value = -1.0
    _value7.outputs["Value"].default_value = 0.5
    #RGB Operations
    _multiply1.blend_type = "MULTIPLY"
    _multiply2.blend_type = "MULTIPLY"
    _multiply3.blend_type = "MULTIPLY"
    _multiply4.blend_type = "MULTIPLY"
    _multiply1.inputs["Fac"].default_value = 1.0
    _multiply2.inputs["Fac"].default_value = 1.0
    _multiply3.inputs["Fac"].default_value = 1.0
    _multiply4.inputs["Fac"].default_value = 1.0
    _add1.blend_type = "ADD"
    _add2.blend_type = "ADD"
    _add3.blend_type = "ADD"
    _add1.inputs["Fac"].default_value = 1.0
    _add2.inputs["Fac"].default_value = 1.0
    _add3.inputs["Fac"].default_value = 1.0
    _divide.blend_type="DIVIDE"
    _divide.inputs["Fac"].default_value=1.0
    _substract.blend_type = "SUBTRACT"
    _substract.inputs["Fac"].default_value=1.0
    #Others
    _addval.operation = "ADD"
    _dot.operation = "DOT_PRODUCT"
    _normalize.operation="NORMALIZE"
    #Position
    _input.location = [00,00]
    _value1.location = [00,400]
    _value2.location = [00,200]
    _value3.location = [00,-200]
    _value4.location = [00,-400]
    _value5.location = [00,-600]
    _value6.location = [00,-800]
    _addval.location = [200,100]
    _combine1.location = [200,-300]
    _combine2.location = [200,-700]
    _multiply1.location = [400,300]
    _combine3.location = [400,200]
    _multiply2.location = [400,-200]
    _add1.location = [600,300]
    _add2.location = [600,-400]
    _dot.location = [800,100]
    _separate.location = [800,-100]
    _divide.location = [1000,00]
    _multiply3.location = [1200,00]
    _substract.location = [1400,00]
    _normalize.location = [1600,00]
    _value7.location = [1600,-100]
    _multiply4.location = [1800,00]
    _add3.location = [2000,00]
    _output.location = [2200,00]
    #Links
    LN(_value1.outputs["Value"], _multiply1.inputs["Color1"])
    LN(_value2.outputs["Value"], _combine3.inputs["R"])
    LN(_value2.outputs["Value"], _combine3.inputs["G"])
    LN(_value2.outputs["Value"], _addval.inputs[0])
    LN(_value3.outputs["Value"], _combine1.inputs["R"])
    LN(_value3.outputs["Value"], _combine1.inputs["G"])
    LN(_value4.outputs["Value"], _combine1.inputs["B"])
    LN(_value5.outputs["Value"], _combine2.inputs["R"])
    LN(_value5.outputs["Value"], _combine2.inputs["G"])
    LN(_value6.outputs["Value"], _combine2.inputs["B"])
    LN(_value7.outputs["Value"], _multiply4.inputs["Color2"])
    LN(_value7.outputs["Value"], _add3.inputs["Color2"])
    LN(_addval.outputs["Value"], _combine3.inputs["B"])
    LN(_combine1.outputs["Image"], _multiply2.inputs["Color2"])
    LN(_combine2.outputs["Image"], _add2.inputs["Color2"])
    LN(_multiply1.outputs["Color"], _add1.inputs["Color1"])
    LN(_combine3.outputs["Image"], _add1.inputs["Color2"])
    LN(_multiply2.outputs["Color"], _add2.inputs["Color1"])
    LN(_add1.outputs["Color"], _dot.inputs[0])
    LN(_add1.outputs["Color"], _separate.inputs["Image"])
    LN(_add1.outputs["Color"], _multiply3.inputs["Color1"])
    LN(_add2.outputs["Color"], _dot.inputs[1])
    LN(_add2.outputs["Color"], _substract.inputs["Color2"])
    LN(_dot.outputs["Value"], _divide.inputs["Color1"])
    LN(_separate.outputs["B"], _divide.inputs["Color2"])
    LN(_divide.outputs["Color"], _multiply3.inputs["Color2"])
    LN(_multiply3.outputs["Color"], _substract.inputs["Color1"])
    LN(_substract.outputs["Color"], _normalize.inputs[0])
    LN(_normalize.outputs["Vector"], _multiply4.inputs["Color1"])
    LN(_multiply4.outputs["Color"], _add3.inputs["Color1"])
    LN(_add3.outputs["Color"],     _output.inputs["Color"])
    LN(_input.outputs["Geometry"], _multiply1.inputs["Color2"])
    LN(_input.outputs["Surface"], _multiply2.inputs["Color1"])
    LN(_input.outputs["Factor"], _addval.inputs[1])
    LN(_input.outputs["Factor"], _multiply3.inputs["Fac"])
    LN(_input.outputs["Factor"], _substract.inputs["Fac"])
    #Return
    return _node_tree

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

def node_tree_pbr(settings, name="Material"):
    #Get the group if it already exists
    """
    if bpy.data.node_groups.get(name):
        _node_tree = bpy.data.node_groups.get(name)
        return _node_tree
    """
    #Create the group and its input/output sockets
    _node_tree = bpy.data.node_groups.new(type="ShaderNodeTree", name=name)
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
    _albedo      = parameter_to_node(_node_tree, settings["albedo"])     if "albedo"     in settings else None
    _ao          = parameter_to_node(_node_tree, settings["ao"])         if "ao"         in settings else None
    _metallic    = parameter_to_node(_node_tree, settings["metallic"])   if "metallic"   in settings else None
    _roughness   = parameter_to_node(_node_tree, settings["roughness"])  if "roughness"  in settings else None
    _glossiness  = parameter_to_node(_node_tree, settings["glossiness"]) if "glossiness" in settings else None
    _normal      = parameter_to_node(_node_tree, settings["normal"])     if "normal"     in settings else None
    _surface     = parameter_to_node(_node_tree, settings["surface"])    if "surface"    in settings else None
    _height      = parameter_to_node(_node_tree, settings["height"])     if "height"     in settings else None
    _opacity     = parameter_to_node(_node_tree, settings["opacity"])    if "opacity"    in settings else None
    _emission    = parameter_to_node(_node_tree, settings["emission"])   if "emission"   in settings else None
    _vertexcolors = AN(type="ShaderNodeAttribute") if "vertexcolors" in settings else None
    #If the dictionnary is empty, create images for each of them
    if len(settings)==0:
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
    if _albedo is not None:
        _albedo.name     = _albedo.label     = "albedo"
    if _ao is not None:
        _ao.name         = _ao.label         = "ao"
    if _metallic is not None:
        _metallic.name   = _metallic.label   = "metallic"
    if _roughness is not None:
        _roughness.name  = _roughness.label  = "roughness"
    if _glossiness is not None:
        _glossiness.name = _glossiness.label = "glossiness"
    if _normal is not None:
        _normal.name     = _normal.label     = "normal"
    if _height is not None:
        _height.name     = _height.label     = "height"
    if _opacity is not None:
        _opacity.name    = _opacity.label    = "opacity"
    if _emission is not None:
        _emission.name   = _emission.label   = "emission"
    #Add te other nodes (mix, inverts, maps...)
    _bump              = AN(type="ShaderNodeBump") if (_normal is not None or _height is not None) else None
    _nmap              = AN(type="ShaderNodeNormalMap") if (_normal is not None) else None
    _ao_mix            = AN(type="ShaderNodeMixRGB") if (_ao is not None) else None
    _opacity_mix       = AN(type="ShaderNodeMixShader") if (_opacity  is not None) else None
    _opacity_shader    = AN(type="ShaderNodeBsdfTransparent") if (_opacity  is not None) else None
    _emission_mix      = AN(type="ShaderNodeMixShader") if (_emission is not None) else None
    _emission_shader   = AN(type="ShaderNodeEmission") if (_emission  is not None) else None
    _glossiness_invert = AN(type="ShaderNodeInvert") if (_glossiness is not None) else None
    _reroute  = AN(type="NodeReroute")
    _uv       = AN(type="ShaderNodeUVMap")
    _mapping  = AN(type="ShaderNodeMapping")
    _separate = AN(type="ShaderNodeSeparateXYZ")
    _scalex   = AN(type="ShaderNodeMath")
    _scaley   = AN(type="ShaderNodeMath")
    _scalez   = AN(type="ShaderNodeMath")
    _combine  = AN(type="ShaderNodeCombineXYZ")
    #Other nodes names to fill them in
    if len(settings)==0:
        _vertexcolors.label = _vertexcolors.name = "vertexcolors"
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
    if _ao_mix is not None:
        _ao_mix.blend_type = "MULTIPLY"
    if _vertexcolors is not None:
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
    if _albedo is not None and "albedo" in settings:
        LN(_albedo.outputs["Color"], _principled.inputs["Base Color"])
    if _ao is not None and "ao" in settings:
        LN(_albedo.outputs["Color"], _ao_mix.inputs[1])
        LN(_ao.outputs["Color"], _ao_mix.inputs[2])
        LN(_ao_mix.outputs["Color"], _principled.inputs["Base Color"])
    if _vertexcolors is not None and "vertexcolors" in settings:
        LN(_vertexcolors.outputs["Color"], _principled.inputs["Base Color"])
    if _metallic is not None and "metallic" in settings:
        LN(_metallic.outputs["Color"], _principled.inputs["Metallic"])
    if _roughness is not None and "roughness" in settings:
        LN(_roughness.outputs["Color"], _principled.inputs["Roughness"])
    if _glossiness is not None and "glossiness" in settings:
        LN(_glossiness.outputs["Color"], _glossiness_invert.inputs["Color"])
        LN(_glossiness_invert.outputs["Color"], _principled.inputs["Roughness"])
    if _bump is not None and ("normal" in settings or "surface" in settings or "height" in settings):
        LN(_bump.outputs["Normal"], _principled.inputs["Normal"])
        if _height is not None and "height" in settings:
            LN(_input.outputs["Height"], _bump.inputs["Distance"])
            LN(_height.outputs["Color"], _bump.inputs["Height"])
        if _nmap is not None and ("normal" in settings or "surface" in settings):
            LN(_normal.outputs["Color"], _nmap.inputs["Color"])
            LN(_nmap.outputs["Normal"], _bump.inputs["Normal"])
    #Post shader emission and opacity mix
    if _emission is not None and "emission" in settings:
        LN(_emission.outputs["Color"], _emission_shader.inputs["Color"])
        LN(_emission.outputs["Color"], _emission_mix.inputs[0])
        LN(_emission_shader.outputs["Emission"], _emission_mix.inputs[2])
        LN(_principled.outputs["BSDF"], _emission_mix.inputs[1])
        LN(_emission_mix.outputs["Shader"], _output.inputs["BSDF"])
    if _opacity is not None and "opacity" in settings:
        LN(_opacity.outputs["Color"], _opacity_shader.inputs["Color"])
        LN(_opacity.outputs["Color"], _opacity_mix.inputs[0])
        LN(_opacity_shader.outputs["BSDF"], _opacity_mix.inputs[1])
        LN(_opacity_mix.outputs["Shader"], _output.inputs["BSDF"])
        if _emission is not None and "emission" in settings:
            LN(_emission_mix.outputs["Shader"], _opacity_mix.inputs[2])
        else:
            LN(_principled.outputs["BSDF"], _opacity_mix.inputs[2])
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
    if _albedo is not None:
        _albedo.location = [-200,0]
    if _ao is not None:
        _albedo.location = [-400,100]
        _ao.location = [-400,-100]
        _ao_mix.location = [-200, 0]
    if _vertexcolors is not None:
        _vertexcolors.location = [-400,0]
    if _metallic is not None:
        _metallic.location = [-200, -200]
        if _metallic.type == "TEX_IMAGE":
            _metallic.color_space = "NONE"
    if _roughness is not None:
        _roughness.location = [-200, -400]
        if _roughness.type == "TEX_IMAGE":
            _roughness.color_space = "NONE"
    if _glossiness is not None:
        _glossiness.location = [-400, -400]
        _glossiness_invert.location = [-200, -400]
        if _glossiness.type == "TEX_IMAGE":
            _glossiness.color_space = "NONE"
    if _bump is not None:
        _bump.location = [-200, -600]
    if _nmap is not None:
        _nmap.location = [-400, -700]
    if _height is not None:
        _height.location = [-400, -500]
    if _normal is not None:
        _normal.location = [-600, -700]
        if _normal.type == "TEX_IMAGE":
            _normal.color_space = "NONE"
    #Post-shader emission and opacity mix
    if _emission is not None:
        _emission.location = [-200, 200]
        _emission_shader.location = [0, 200]
        _emission_mix.location = [200, 100]
    if _opacity is not None:
        off = [400,200] if _emission is not None else [0,0]
        _opacity.location = [-200 + off[0], 200 + off[1]]
        _opacity_shader.location = [0 + off[0], 200 + off[1]]
        _opacity_mix.location = [200 + off[0], 100 + off[1]]
    if (_emission is not None and _opacity is None) or (_emission is None and _opacity is not None):
        _output.location = [400,200]
    if _emission is not None and _opacity is not None:
        _output.location = [800,400]
    #Collapse all the nodes
    for n in _node_tree.nodes:
        if n.type!="BSDF_PRINCIPLED":
            n.hide = True
    #Return
    return _node_tree
