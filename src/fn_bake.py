# coding: utf8
import bpy
from . import fn_nodes
import numpy as np

import tempfile

def copy_cycles_material(material, name=None):

    _new_material = material.copy()

    for _n in _new_material.node_tree.nodes:
        if _n.type == "GROUP":
            if _n.node_tree.users > 1:
                _n.node_tree = _n.node_tree.copy()

    if name is not None:
        _new_material.name = name

    return _new_material

def remove_unused_nodes(node, tree, channel):
    def get_neighbor_nodes(node):
        """Returns a list of the node's immediate neighbors"""
        _neighs = []
        for _input in node.inputs:
            if len(_input.links)>0:
                for _link in _input.links:
                    _neighs.append(_link.from_node)
        for _output in node.outputs:
            if len(_output.links)>0:
                for _link in _output.links:
                    _neighs.append(_link.to_node)
        return _neighs
    def get_linked_nodes(node):
        """Returns a list of all the node's connected nodes"""
        _linkedNodes = [node]
        _neighs = [node]
        while len(_neighs):
            _newNeighs = []
            for _node in _neighs:
                for _neigh in get_neighbor_nodes(_node):
                    if _neigh not in _linkedNodes:
                        _newNeighs.append(_neigh)
                        _linkedNodes.append(_neigh)
            _neighs = _newNeighs
        return _linkedNodes
    #Remove the links not connected to the input
    for i in node.inputs:
        if i.name!=channel:
            for l in i.links:
                tree.links.remove(l)
    #Remove the newly isolated nodes
    _isolated = [n for n in tree.nodes if n not in get_linked_nodes(node)]
    for n in _isolated:
        tree.nodes.remove(n)

def get_all_nodes_in_material(material, node_type=None):

    def find_groups_in_node_tree(_node_tree):
        _groups = []
        for _n in _node_tree.nodes:
            if _n.type == "GROUP":
                _groups.append(_n)
                _groups = _groups + find_groups_in_node_tree(_n.node_tree)
        return _groups

    _nodes = [{"node": n, "tree":material.node_tree} for n in material.node_tree.nodes]

    _groups = find_groups_in_node_tree(material.node_tree)

    for _group in _groups:
        _nodes = _nodes + [{"node": n, "tree":_group.node_tree} for n in _group.node_tree.nodes]

    if node_type is None:
        return _nodes
    else:
        return [n for n in _nodes if n["node"].type == node_type]

def fill_input_slot(node, tree, channel):

    #If no input is detected
    if len(node.inputs[channel].links) == 0:
        if channel == "Normal":
            #Add a neutral normal color and gamma correction
            _inputNode = tree.nodes.new(type="ShaderNodeRGB")
            _inputNode.outputs["Color"].default_value = (0.5, 0.5, 1, 1)
            _gamma = tree.nodes.new(type="ShaderNodeGamma")
            _gamma.inputs["Gamma"].default_value = 2.2
            tree.links.new(_inputNode.outputs[0], _gamma.inputs["Color"])
            tree.links.new(_gamma.outputs["Color"], node.inputs["Normal"])
        else:
            _inputNode = tree.nodes.new(type="ShaderNodeRGB")
            x = node.inputs[channel].default_value
            if type(x) is float:
                _inputNode.outputs["Color"].default_value = (x, x, x, 1)
            else:
                _inputNode.outputs["Color"].default_value = x
            tree.links.new(_inputNode.outputs["Color"], node.inputs[channel])

    #If an input is detected
    else:
        _inputNode = node.inputs[channel].links[0].from_node
        if channel == "Normal":
            #Insert a "normal to color node"
            _ntoc = tree.nodes.new(type="ShaderNodeGroup")
            _ntoc.label = "Normal to color"
            _ntoc.node_tree = fn_nodes.node_tree_normal_to_color()
            tree.links.new(_inputNode.outputs["Normal"], _ntoc.inputs["Normal"])
            tree.links.new(_ntoc.outputs["Color"], node.inputs["Normal"])
        else:
            pass

    return node.inputs[channel].links[0].from_node

def convert_principled_to_emission(node, tree, input_node):
    _emit = tree.nodes.new(type="ShaderNodeEmission")
    _emit.location = node.location
    tree.links.new(input_node.outputs[0], _emit.inputs["Color"])
    for l in node.outputs["BSDF"].links:
        tree.links.new(_emit.outputs["Emission"], l.to_socket)
    tree.nodes.remove(node)

################################################################################
# "API" functions, referenced by the operator
################################################################################

def overlay_normals(image1, image2, name="overlay"):

    assert(image1.size[0] == image2.size[0])
    assert(image1.size[1] == image2.size[1])
    w,h = image1.size[0], image1.size[1]
    pixels1 = np.array(image1.pixels).reshape((w,h,4))
    pixels2 = np.array(image2.pixels).reshape((w,h,4))

    #Remove the blue channel
    pixels2[:,:,2]=0.

    #Get the value from the firdt image
    value = np.max(pixels1[:,:,:3], axis=2)
    val = np.zeros((w,h,4))
    val[:,:,0] = val[:,:,1] = val[:,:,2] = val[:,:,3] = value

    #Compute the overlay
    mult = pixels1*pixels2
    comp = 1.0 - 2*(1.-pixels1)*(1.-pixels2)
    pix = np.where(val<0.5, mult, comp)
    pix[:,:,3]=1.

    img = bpy.data.images.new(name, w, h)
    img.pixels = np.ravel(pix)
    return img

def create_source_baking_material(material, channel):
    #Create the new material
    _new_material = copy_cycles_material(material)

    if channel == "Emission":
        #We do nothing
        pass

    elif channel == "Opacity":
        #Link the "fac" of the "BSDF_TRANSPARENT" nodes to an emission node
        _alpha_nodes = get_all_nodes_in_material(_new_material, "BSDF_TRANSPARENT")
        for n in _alpha_nodes:
            for _link in n["node"].outputs["BSDF"].links:
                _mix = _link.to_node
                if _mix.type == "MIX_SHADER" or _mix.type == "ADD_SHADER":
                    if len(_mix.outputs["Shader"].links)>0:
                        _out_socket = _mix.outputs["Shader"].links[0].to_socket
                        if len(_mix.inputs["Fac"].links)==1:
                            _fac = _mix.inputs["Fac"].links[0].from_node
                            _emission = n["tree"].nodes.new(type="ShaderNodeEmission")
                            n["tree"].links.new(_fac.outputs[0], _emission.inputs["Color"])
                            n["tree"].links.new(_emission.outputs["Emission"], _out_socket)
                        else:
                            _input_node = fill_input_slot(_mix, n["tree"], "Fac")
                            _emission = n["tree"].nodes.new(type="ShaderNodeEmission")
                            n["tree"].links.new(_input_node.outputs[0], _emission.inputs["Color"])
                            n["tree"].links.new(_emission.outputs["Emission"], _out_socket)
    else:
        #Convert the principled nodes  to emission materials
        _principled_nodes = get_all_nodes_in_material(_new_material, "BSDF_PRINCIPLED")
        for n in _principled_nodes:
            remove_unused_nodes(n["node"], n["tree"], channel)
            _input_node = fill_input_slot(n["node"], n["tree"], channel)
            convert_principled_to_emission(n["node"], n["tree"], _input_node)

    #Turn all non colors textures, except normals, to colors
    _image_nodes = get_all_nodes_in_material(_new_material, "TEX_IMAGE")
    for n in [x["node"] for x in _image_nodes]:
        if len(n.outputs["Color"].links)>0:
            isNormal = False
            for l in n.outputs["Color"].links:
                if l.to_node is not None:
                    if l.to_node.type=="NORMAL_MAP":
                        isNormal = True
            if not isNormal:
                n.color_space = "COLOR"
    return _new_material

def create_target_baking_material(obj):
    #Remove all materials from the target
    while len(obj.material_slots):
        obj.active_material_index = 0
        bpy.ops.object.material_slot_remove()

    #Add a new material called "baking" to the target
    bpy.ops.object.material_slot_add()
    _material = bpy.data.materials.new("baking")
    obj.active_material = _material
    _material.use_nodes = True

    return _material
