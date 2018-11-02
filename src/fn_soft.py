import subprocess
import os

DEBUG = False

def run(cmd):
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

    #Create the command
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

    #Execute it, and return stdout, stderr and exit code
    print("Running %s" % cmd)
    return run(cmd)
def meshlabserver(
    input_mesh,
    script_file,
    output_mesh=None,
    log_file=None,
    executable="meshlabserver"
    ):

    #Create the command
    cmd = '"' + executable + '" -i %s -s %s ' % (input_mesh, script_file)
    if output_mesh is None:
        output_mesh = input_mesh
    cmd += "-o %s" % output_mesh
    if log_file is not None:
        cmd += "-l %s" % log_file

    #Execute it, and return stdout, stderr and exit code
    print("Running %s" % cmd)
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

    #Create the command
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

    #Execute it, and return stdout, stderr and exit code
    print("Running %s" % cmd)
    return run(cmd)
def quadriflow(
    input_mesh,
    output_mesh=None,
    face_count=None,
    executable="quadriflow"
    ):

    #Create the command
    cmd = '"' + executable + '" -i %s ' % input_mesh
    if output_mesh is None:
        output_mesh = input_mesh
    cmd += "-o %s " % output_mesh
    if face_count is not None:
        cmd += "-f %d " % face_count

    #Execute it, and return stdout, stderr and exit code
    print("Running %s" % cmd)
    return run(cmd)
def meshlab(input_mesh):
    return run("meshlab %s" % input_mesh)
def instant_meshes_gui(input_mesh, executable="instantMeshes"):
    return run('"' + executable + '" %s' % input_mesh)
