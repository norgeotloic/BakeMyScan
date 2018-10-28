import bpy
import time

F = open("/home/loic/log.txt", "w")

def wrapper(
    original_object,
    operator_wrapper,
    parameter,
    prefix,
    ):
    #Select the original object only
    bpy.ops.object.select_all(action='DESELECT')
    original_object.select = True
    bpy.context.scene.objects.active = original_object
    #Get the starting time
    t = time.time()
    #Run the operator
    operator_wrapper(parameter)
    #Get the ending time
    t = int(time.time() - t)
    #Get the object
    res = None
    if bpy.context.scene.objects.active is not None:
        res = bpy.context.scene.objects.active
    else:
        if len(bpy.context.selected_objects)==1:
            res = bpy.context.selected_objects[0]
    #Rename it
    res.name = "%s_%f_%ds_%dv" % (prefix, parameter, t, len(res.data.vertices))
    #Print the result
    info = "%s: %d verts in %d s, parameter = %f" % (prefix, len(res.data.vertices), t, parameter)
    print(info)
    F.write(info + "\n")

# 0 - Get the active object
obj = bpy.context.scene.objects.active

def mmgs(h):
    bpy.ops.remeshme.remesh_mmgs(hausd=h, smooth=True)
for hausd in [0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 0.0005, 0.0002, 0.0001]:
    wrapper(obj, mmgs, hausd, "MMGS")

def meshlab_quadratic(n):
    bpy.ops.remeshme.remesh_meshlab(facescount=n)
for n in [1000, 2000, 5000, 10000, 20000, 50000]:
    wrapper(obj, meshlab_quadratic, n, "MESHLAB")

def instant(n):
    bpy.ops.remeshme.remesh_instant(facescount=n, interactive=False)
for n in [100, 200, 500, 1000, 2000, 5000, 10000]:
    wrapper(obj, instant, n, "INSTANT")

def quadriflow(n):
    bpy.ops.remeshme.remesh_quadriflow(resolution=n)
for n in [100, 200, 500, 1000, 2000, 5000, 10000]:
    wrapper(obj, quadriflow, n, "QUADRIFLOW")

def decimate(n):
    bpy.ops.remeshme.remesh_decimate(limit=n, vertex_group=True)
for n in [1000, 2000, 5000, 10000, 20000, 50000]:
    wrapper(obj, decimate, n, "DECIMATE")

def quads(r):
    bpy.ops.remeshme.remesh_quads(ratio=r, smooth=3)
for r in [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1]:
    wrapper(obj, quads, r, "NAIVEQUADS")

def iterative(n):
    bpy.ops.remeshme.remesh_iterative(limit=n, manifold=False, vertex_group=True)
for n in [1000, 2000, 5000, 10000, 20000, 50000]:
    wrapper(obj, iterative, n, "ITERATIVE")
