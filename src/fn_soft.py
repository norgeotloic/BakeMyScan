import subprocess
import os
import shutil

DEBUG = False

def run(cmd):

    print("Running %s" % cmd)

    result = subprocess.run(
        ' '.join(cmd.split()),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=os.name!="nt"
    )

    return result.stdout.decode('utf-8'), result.stderr.decode('utf-8'), result.returncode

#Remeshers
def mmgs(
    input_mesh,
    output_mesh=None,
    input_sol=None,
    hausd=None,
    hgrad=None,
    hmin=None,
    hmax=None,
    ar=None,
    nr=False,
    aniso=False,
    nreg=False,
    executable="mmgs_O3"
    ):
    cmd = '"' + executable + '" %s ' % input_mesh
    if output_mesh is None:
        output_mesh = input_mesh
    cmd += "-out %s " % output_mesh
    if input_sol is not None:
        cmd += "-sol %s " % input_sol
    if hausd is not None:
        cmd += "-hausd %f " % hausd
    if hgrad is not None:
        cmd += "-hgrad %f " % hgrad
    if hmin is not None:
        cmd += "-hmin %f " % hmin
    if hmax is not None:
        cmd += "-hmax %f " % hmax
    if ar is not None:
        cmd += "-ar %f " % ar
    if nr:
        cmd += "-nr "
    if aniso:
        cmd += "-A "
    if nreg:
        cmd += "-nreg "
    return run(cmd)

def meshlabserver(
    input_mesh,
    script_file,
    output_mesh=None,
    log_file=None,
    executable="meshlabserver"
    ):
    cmd = '"' + executable + '" -i %s -s %s ' % (input_mesh, script_file)
    if output_mesh is None:
        output_mesh = input_mesh
    cmd += "-o %s" % output_mesh
    if log_file is not None:
        cmd += "-l %s" % log_file
    return run(cmd)

def instant_meshes_cmd(
    input_mesh,
    output_mesh=None,
    face_count=None,
    vertex_count=None,
    edge_length=None,
    executable="instantMeshes",
    d=False,
    D=False,
    i=False,
    b=False,
    C=False,
    c=None,
    S=None,
    r=None,
    p=None,
    ):
    cmd = '"' + executable + '" %s ' % input_mesh
    if output_mesh is None:
        output_mesh = input_mesh
    cmd += "-o %s " % output_mesh
    if face_count is not None:
        cmd += "-f %d " % face_count
    elif vertex_count is not None:
        cmd += "-v %d " % vertex_count
    elif edge_length is not None:
        cmd += "-s %f " % edge_length
    if d:
        cmd += "-d "
    if D:
        cmd += "-D "
    if i:
        cmd += "-i "
    if b:
        cmd += "-b "
    if C:
        cmd += "-C "
    if c is not None:
        cmd+= "-c %f " % c
    if S is not None:
        cmd+= "-S %d " % S
    if p is not None:
        cmd+= "-p %s " % p
    if r is not None:
        cmd+= "-r %s " % r
    return run(cmd)
def quadriflow(
    input_mesh,
    output_mesh=None,
    face_count=None,
    mincost=False,
    sharp=False,
    satflip=False,
    executable="quadriflow"
    ):
    cmd = '"' + executable + '" -i %s ' % input_mesh
    if output_mesh is None:
        output_mesh = input_mesh
    cmd += "-o %s " % output_mesh
    if face_count is not None:
        cmd += "-f %d " % face_count
    if sharp:
        cmd += "-sharp "
    if mincost:
        cmd+= "-mcf "
    if satflip:
        cmd+= "-sat "

    return run(cmd)
def meshlab(input_mesh):
    return run("meshlab %s" % input_mesh)
def instant_meshes_gui(input_mesh, executable="instantMeshes"):
    return run('"' + executable + '" %s' % input_mesh)

def createReconDir(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
    os.mkdir(path)

def colmap_auto(
    workspace,
    images,
    quality="medium",
    single_camera=1,
    sparse=1,
    dense=1,
    mesher="delaunay",
    colmap="colmap",
    gpu=False
    ):
    createReconDir(workspace)
    cmd  = '"' + colmap + '" automatic_reconstructor '
    cmd += "--workspace_path %s " % workspace
    cmd += "--image_path %s " % images
    cmd += "--quality %s " % quality
    cmd += "--single_camera %d " % single_camera
    cmd += "--sparse %d " % sparse
    cmd += "--mesher %s " % mesher
    if gpu:
        cmd += "--dense %d " % dense
    else:
        cmd += "--SiftExtraction.use_gpu 0 --SiftMatching.use_gpu 0 "
        cmd += "--dense 0 "
    return run(cmd)

def colmap_openmvs(
    workspace,
    images,
    colmap="colmap",
    interfacevisualsfm = "InterfaceVisualSFM",
    densifypointcloud = "DensifyPointCloud",
    reconstructmesh = "ReconstructMesh",
    texturemesh = "TextureMesh",
    meshlabserver = "meshlabserver",
    single_camera = 1,
    gpu           = 1,
    densify_resolution=2,
    reconstruct_distance=2.5,
    texture_resolution=2,
    min_size=640,
    ):
    #createReconDir(workspace)

    DB = os.path.join(workspace, "database.db")
    SP = os.path.join(workspace, "sparse")
    os.mkdir(SP)

    old = os.getcwd()

    #Colmap
    os.chdir(images)
    cmd1 = colmap + " feature_extractor --database_path %s --image_path %s --ImageReader.single_camera %d --SiftExtraction.use_gpu %d" % (DB, images, single_camera, gpu)
    cmd2 = colmap + " exhaustive_matcher --database_path %s --SiftMatching.use_gpu %d" % (DB, gpu)
    cmd3 = colmap + " mapper --database_path %s --image_path %s --output_path %s" % ( DB, images, SP )
    cmd4 = colmap + " model_converter --input_path %s --output_path %s --output_type NVM" % (os.path.join(SP, "0"), os.path.join(workspace, "model.nvm"))

    #OpenMVS
    os.chdir(workspace)
    cmd5 = interfacevisualsfm + " -w %s -i %s" % (workspace, os.path.join(workspace, "model.nvm"))
    cmd6 = densifypointcloud + " -w %s -i %s --resolution-level %d --min-resolution %d" % (workspace, os.path.join(workspace, "model.mvs"), densify_resolution, min_size)
    cmd7 = reconstructmesh + " -w %s -i %s --export-type obj" % (workspace, os.path.join(workspace, "model_dense.mvs"))
    cmd8 = texturemesh + " -w %s -i %s --resolution-level %d --min-resolution %d -o result.ply" % (workspace, os.path.join(workspace, "model_dense_mesh.mvs"), texture_resolution, min_size)

    #Conversion
    cmd9 = meshlabserver + " -om wt -i %s -o %s" % (os.path.join(workspace, "result.ply"), os.path.join(workspace, "result.obj"))

    #Run the commands
    os.chdir(old)
    for cmd in [cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7, cmd8, cmd9]:
        out, err, code = run(cmd)
        if code!=0:
            print(out)
            print(err)
        print("")
