import sys
import os
sys.path.append( os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src") )
import fn_msh

# Import, modify and save a .mesh as .vtk file
if __name__=="__main__":
    if len(sys.argv)!=2:
        print("The script takes a .mesh file as only argument!")
        sys.exit()
    mesh = fn_msh.Mesh(sys.argv[1])
    mesh.readSol()
    mesh.writeVTK(sys.argv[1][:-4] + "vtk")
print("Paraview file written to " + sys.argv[1][:-4] + "vtk")
