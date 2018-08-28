#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import numpy as np
import itertools

class Mesh:

    # .mesh import functions
    keywords = ["Vertices", "Triangles", "Quadrilaterals","Tetrahedra","SolAtVertices"]
    def analyse(self, index, line):
        for k,kwd in enumerate(self.keywords):
            if self.found[k] and kwd not in self.done:
                self.numItems[k] = int(line)
                self.offset += self.numItems[k]
                self.found[k] = False
                self.done.append(kwd)
                return 1
            if kwd in line:
                if kwd not in self.done and line[0]!="#":
                    self.begin[k] = index+3 if kwd=="SolAtVertices" else index+2
                    self.found[k] = True
    def get_infos(self, path):
        for j in range(len(self.keywords)):
            with open(path) as f:
                f.seek(0)
                for i,l in enumerate(f):
                    if i>self.offset:
                        if self.analyse(i,l):
                            break
                f.seek(0)
    def readArray(self,f, ind, dim, dt=None):
        #Allows for searching through n empty lines
        maxNumberOfEmptylines = 20
        for i in range(maxNumberOfEmptylines):
            f.seek(0)
            firstValidLine = f.readlines()[self.begin[ind]].strip()
            if firstValidLine == "":
                self.begin[ind]+=1
            else:
                break
        try:
            f.seek(0)
            X = " ".join([l for l in itertools.islice(f, self.begin[ind], self.begin[ind] + self.numItems[ind])])
            if dt:
                return np.fromstring(X, sep=" ", dtype=dt).reshape((self.numItems[ind],dim))
            else:
                return np.fromstring(X, sep=" ").reshape((self.numItems[ind],dim))
        except:
            #print "Invalid format", ind, dim
            f.seek(0)
            try:
                for i in range(self.begin[ind]):
                    f.readline()

                arr = []
                for l in f:
                    if len(l.strip())>0:
                        arr.append([int(x) for x in l.strip().split()])
                    else:
                        break
                return np.array(arr,dtype=dt)
            except:
                print("Did not manage to read the array")
                sys.exit()
            sys.exit()
    def readSol(self,path=None):
        try:
            if self.path and not path:
                self.offset=0
                self.get_infos(self.path[:-5]+".sol")
                with open(self.path[:-5]+".sol") as f:
                        if self.numItems[4]:
                            #Allows for searching through n empty lines
                            maxNumberOfEmptylines = 20
                            for i in range(maxNumberOfEmptylines):
                                f.seek(0)
                                firstValidLine = f.readlines()[self.begin[4]].strip()
                                if firstValidLine == "":
                                    self.begin[4]+=1
                                else:
                                    break
                            f.seek(0)
                            nItems = len(f.readlines()[self.begin[4]].strip().split())
                            f.seek(0)
                            #Read a scalar
                            if nItems == 1:
                                self.scalars = np.array([float(l) for l in itertools.islice(f, self.begin[4], self.begin[4] + self.numItems[4])])
                                self.solMin = np.min(self.scalars)
                                self.solMax = np.max(self.scalars)
                                self.vectors = np.array([])
                            #Read a vector
                            if nItems == 3:
                                self.vectors = np.array([ [float(x) for x in l.strip().split()[:3]] for l in itertools.islice(f, self.begin[4], self.begin[4] + self.numItems[4])])
                                self.vecMin = np.min(np.linalg.norm(self.vectors,axis=1))
                                self.vecMax = np.min(np.linalg.norm(self.vectors,axis=1))
                                self.scalars=np.array([])
                            #Read a scalar after a vector
                            if nItems == 4:
                                self.vectors = np.array([ [float(x) for x in l.strip().split()[:3]] for l in itertools.islice(f, self.begin[4], self.begin[4] + self.numItems[4])])
                                self.vecMin = np.min(np.linalg.norm(self.vectors,axis=1))
                                self.vecMax = np.min(np.linalg.norm(self.vectors,axis=1))
                                f.seek(0)
                                self.scalars = np.array([float(l.split()[3]) for l in itertools.islice(f, self.begin[4], self.begin[4] + self.numItems[4])])
                                self.solMin = np.min(self.scalars)
                                self.solMax = np.max(self.scalars)
                        else:
                            self.scalars = np.array([])
                            self.vectors = np.array([])
        except:
            print("No .sol file associated with the .mesh file")

    # Constructor
    def __init__(self, path=None, cube=None):
        if cube:
            self.path = None
            self.verts = np.array([
                [cube[0], cube[2], cube[4]],
                [cube[0], cube[2], cube[5]],
                [cube[1], cube[2], cube[4]],
                [cube[1], cube[2], cube[5]],
                [cube[0], cube[3], cube[4]],
                [cube[0], cube[3], cube[5]],
                [cube[1], cube[3], cube[4]],
                [cube[1], cube[3], cube[5]]
            ])
            self.tris = np.array([
                [0,1,2],
                [1,3,2],
                [4,6,5],
                [5,6,7],
                [1,5,3],
                [3,5,7],
                [2,6,4],
                [0,2,4],
                [3,7,6],
                [2,3,6],
                [0,4,1],
                [1,4,5]
            ])
            self.verts = np.insert(self.verts,3,0,axis=1)
            self.tris  = np.insert(self.tris,3,0,axis=1)
            self.quads=np.array([])
            self.tets=np.array([])
            self.computeBBox()
        elif path:
            self.done     = []
            self.found    = [False for k in self.keywords]
            self.begin    = [0 for k in self.keywords]
            self.numItems = [0 for k in self.keywords]
            self.offset   = 0

            self.path = path
            self.get_infos(path)
            with open(path) as f:
                if self.numItems[0]:
                    self.verts = self.readArray(f,0,4,np.float)
                if self.numItems[1]:
                    self.tris  = self.readArray(f,1,4,np.int)
                    self.tris[:,:3]-=1
                else:
                    self.tris = np.array([])
                if self.numItems[2]:
                    self.quads = self.readArray(f,2,5,np.int)
                    self.quads[:,:4]-=1
                else:
                    self.quads = np.array([])
                if self.numItems[3]:
                    self.tets  = self.readArray(f,3,5,np.int)
                    self.tets[:,:4]-=1
                else:
                    self.tets = np.array([])
            self.computeBBox()
        else:
            self.path = None
            self.verts=np.array([])
            self.tris=np.array([])
            self.quads=np.array([])
            self.tets=np.array([])
        self.scalars=np.array([])
        self.vectors=np.array([])
        self.edges=np.array([])

    def caracterize(self):
        if self.path is not None:
            print("File " + self.path)
        if len(self.verts):
            print("\tVertices:        ", len(self.verts))
            #try:
            #    print("\tBounding box:    ", "[%.2f, %.2f] [%.2f, %.2f] [%.2f, %.2f]" % (self.xmin, self.xmax,self.ymin, self.ymax, self.zmin, self.zmax))
            #except:
            #    pass
        if len(self.tris):
            print("\tTriangles:       ", len(self.tris))
        if len(self.quads):
            print("\tQuadrilaterals:  ", len(self.quads))
        if len(self.tets):
            print("\tTetrahedra:      ", len(self.tets))
        if len(self.scalars):
            print("\tScalars:         ", len(self.scalars))
        if len(self.vectors):
            print("\tVectors:         ", len(self.vectors))
    def computeBBox(self):
        self.xmin, self.ymin, self.zmin = np.amin(self.verts[:,:3],axis=0)
        self.xmax, self.ymax, self.zmax = np.amax(self.verts[:,:3],axis=0)
        self.dims = np.array([self.xmax - self.xmin, self.ymax - self.ymin, self.zmax - self.zmin])
        self.center = np.array([self.xmin + (self.xmax - self.xmin)/2, self.ymin + (self.ymax - self.ymin)/2, self.zmin + (self.zmax - self.zmin)/2])
    def fondre(self, otherMesh):
        off = len(self.verts)
        if len(otherMesh.tris)>0:
            self.tris  = np.append(self.tris,  otherMesh.tris + [off, off, off, 0],  axis=0) if len(self.tris)>0 else otherMesh.tris + [off, off, off, 0]
        if len(otherMesh.tets)>0:
            self.tets  = np.append(self.tets,  otherMesh.tets + [off, off, off, off, 0],  axis=0) if len(self.tets)>0 else otherMesh.tets + [off, off, off, 0]
        if len(otherMesh.quads)>0:
            self.quads = np.append(self.quads, otherMesh.quads + [off, off, off, off, 0], axis=0) if len(self.quads)>0 else otherMesh.quads + [off, off, off, 0]
        if len(otherMesh.scalars)>0:
            self.scalars = np.append(self.scalars, otherMesh.scalars, axis=0) if len(self.scalars)>0 else np.append(np.zeros((len(self.verts))), otherMesh.scalars, axis=0)
        if len(otherMesh.vectors)>0:
            self.vectors = np.append(self.vectors, otherMesh.vectors, axis=0) if len(self.vectors)>0 else np.append(np.zeros((len(self.verts),3)), otherMesh.vectors, axis=0)
        if len(otherMesh.verts)>0:
            self.verts = np.append(self.verts, otherMesh.verts, axis=0) if len(self.verts)>0 else otherMesh.verts

    def replaceRef(self, oldRef, newRef):
        if len(self.tris)!=0:
            self.tris[self.tris[:,-1]==oldRef,-1] = newRef
        if len(self.quads)!=0:
            self.quads[self.quads[:,-1]==oldRef,-1] = newRef
        if len(self.tets)!=0:
            self.tets[self.tets[:,-1]==oldRef,-1] = newRef
    def removeRef(self, ref, keepTris=False, keepTets=False, keepQuads=False):
        if len(self.tris)!=0 and not keepTris:
            self.tris = self.tris[self.tris[:,-1]!=ref]
        if len(self.quads)!=0 and not keepQuads:
            self.quads = self.quads[self.quads[:,-1]!=ref]
        if len(self.tets)!=0 and not keepTets:
            self.tets = self.tets[self.tets[:,-1]!=ref]
    def writeVertsRef(self):
        self.tets = self.tets[self.tets[:,-1].argsort()]
        for i, t in enumerate(self.tets):
            for iPt in t[:-1]:
                self.verts[iPt][-1] = t[-1]
        self.tris = self.tris[self.tris[:,-1].argsort()]
        for i, t in enumerate(self.tris):
            for iPt in t[:-1]:
                self.verts[iPt][-1] = t[-1]
    def scale(self,sc,center=[]):
        if len(center)>0:
            self.verts[:,:3] -= center
        else:
            self.verts[:,:3] -= self.center
        self.verts[:,:3] *= sc
        if len(center)>0:
            self.verts[:,:3] += center
        else:
            self.verts[:,:3] += self.center
        self.computeBBox()
    def inflate(self,sc):
        self.verts[:,:3] -= self.center
        self.verts[:,:3] += sc/np.linalg.norm(self.verts[:,:3],axis=1)[:,None] * self.verts[:,:3]
        self.verts[:,:3] += self.center
        self.computeBBox()
    def fitTo(self, otherMesh, keepRatio=True):
        otherDim = [
            otherMesh.dims[0]/self.dims[0],
            otherMesh.dims[1]/self.dims[1],
            otherMesh.dims[2]/self.dims[2]
        ]
        if keepRatio:
            scale = np.min(otherDim)
        else:
            scale = otherDim
        self.verts[:,:3]-=self.center
        self.verts[:,:3]*=scale
        self.verts[:,:3]+=otherMesh.center
        self.computeBBox()
    def discardUnused(self):
        used = np.zeros(shape=(len(self.verts)),dtype="bool_")
        if len(self.tris)>0:
            used[np.ravel(self.tris[:,:3])]=True
        if len(self.tets)>0:
            used[np.ravel(self.tets[:,:4])]=True
        if len(self.quads)>0:
            used[np.ravel(self.quads[:,:4])]=True
        newUsed = np.cumsum(used)
        self.verts = self.verts[used==True]
        if len(self.scalars)>0:
            self.scalars = self.scalars[used==True]
        if len(self.vectors)>0:
            self.vectors = self.vectors[used==True]
        if len(self.tris)>0:
            newTris = np.zeros(shape=(len(self.tris),4),dtype=int)
            newTris[:,-1] = self.tris[:,-1]
            for i,triangle in enumerate(self.tris):
                for j,t in enumerate(triangle[:-1]):
                    newTris[i,j] = newUsed[t]-1
            self.tris = newTris
        if len(self.tets)>0:
            newTets = np.zeros(shape=(len(self.tets),5),dtype=int)
            newTets[:,-1] = self.tets[:,-1]
            for i,tet in enumerate(self.tets):
                for j,t in enumerate(tet[:-1]):
                    newTets[i][j] = newUsed[t]-1
            self.tets = newTets
        self.computeBBox()

    def getHull(self):
        with open("tmp.node","w") as f:
            f.write( str(len(self.verts)) + " 3 0 0\n")
            for i,v in enumerate(self.verts):
                f.write(str(i+1) + " " + " ".join([str(x) for x in v]) + "\n")
        import os
        os.system("tetgen -cAzn tmp.node > /dev/null 2>&1")

        neigh = []
        with open("tmp.1.neigh") as f:
            for l in f.readlines()[1:-1]:
                neigh.append( [int(l.split()[i]) for i in range(1,5)] )
        tets = []
        with open("tmp.1.ele") as f:
            for l in f.readlines()[1:-1]:
                tets.append( [int(l.split()[i]) for i in range(1,5)] )
        verts = []
        with open("tmp.1.node") as f:
            for l in f.readlines()[1:-1]:
                verts.append( [float(l.split()[i]) for i in range(1,4)]+[0] )
        tris = []
        for i,n in enumerate(neigh):
            for j,c in enumerate(n):
                if c==-1:
                    tris.append([tets[i][k] for k in range(4) if k!=j]+[0])
        refs = [1 for t in tris]

        mesh = Mesh()
        mesh.verts = np.array(verts)
        mesh.tris  = np.array(tris,dtype=int)
        mesh.discardUnused()
        mesh.computeBBox()

        return mesh

    # .mesh export functions
    def writeArray(self, path, head, array, form, firstOpening=False, incrementIndex=False):
        if len(array):
            f = open(path,"wb") if firstOpening else open(path, "ab")
            if incrementIndex:
                array = np.copy(array)
                array[:,:-1]+=1
            try:
                np.savetxt(
                    f,
                    array,
                    fmt=form,
                    newline="\n",
                    header=head,
                    footer=" ",
                    comments=""
                )
            except:
                print("Error while writing array", head, array)
            f.close()
    def write(self, path):
        self.writeArray(path, "MeshVersionFormatted 2\nDimension 3\n\nVertices\n" + str(len(self.verts)), self.verts, '%.8f %.8f %.8f %i', firstOpening=True)
        self.writeArray(path, "Triangles\n"+ str(len(self.tris)), self.tris, '%i %i %i %i', incrementIndex=True)
        self.writeArray(path, "Quadrilaterals\n"+str(len(self.quads)), self.quads, '%i %i %i %i %i', incrementIndex=True)
        self.writeArray(path, "Tetrahedra\n"+str(len(self.tets)), self.tets, '%i %i %i %i %i', incrementIndex=True)
        self.writeArray(path, "Edges\n"+str(len(self.edges)), self.edges, '%i %i %i', incrementIndex=True)
        self.writeArray(path, "RequiredEdges\n"+str(len(self.edges)), [[e] for e in range(len(self.edges))], '%i', incrementIndex=True)
        with open(path,"a") as f:
            f.write("\nEnd")
    def writeSol(self,path):
        self.writeArray(path,"MeshVersionFormatted 2\nDimension 3\n\nSolAtVertices\n"+str(len(self.scalars))+"\n1 1", self.scalars, '%.8f', firstOpening=True)

    # other export functions
    def writeOBJ(self, path):
        with open(path, "w") as f:
            f.write("o MeshExport\n")
            for v in self.verts:
                f.write( "v %.8f %.8f %.8f\n" % (v[0], v[1], v[2]) )
            f.write("\n")
            f.write("usemtl None\ns off\n")
            for t in self.tris:
                f.write( "f %i %i %i\n" % (t[0]+1, t[1]+1, t[2]+1) )
            for t in self.quads:
                f.write( "f %i %i %i %i\n" % (t[0]+1, t[1]+1, t[2]+1, t[3]+1) )
            f.write("\n")
    def writeSTL(self, path):
        with open(path, "w") as f:
            f.write("solid meshExport\n")
            for t in self.tris:
                output = "facet normal " + str(1) + " " + str(1) + " " + str(1) + "\n"
                output+= "   outer loop\n"
                output+= "     vertex %.8f %.8f %.8f\n" % (self.verts[t[0],0], self.verts[t[0],1], self.verts[t[0],2])
                output+= "     vertex %.8f %.8f %.8f\n" % (self.verts[t[1],0], self.verts[t[1],1], self.verts[t[1],2])
                output+= "     vertex %.8f %.8f %.8f\n" % (self.verts[t[2],0], self.verts[t[2],1], self.verts[t[2],2])
                output+= "   endloop\n"
                output+= "endfacet\n"
                f.write(output)
            f.write("end solid")
    def writeVTK(self, path):
        with open(path, "w") as f:
            header =  "# vtk DataFile Version 2.0\nMesh export\nASCII\n"
            header += "DATASET UNSTRUCTURED_GRID\n\n"
            f.write(header)
            # Writing vertices
            f.write("POINTS " + str(len(self.verts)) + " float\n")
            for v in self.verts:
                f.write('%.8f %.8f %.8f\n' % (v[0],v[1],v[2]))
            f.write("\n")
            #Writing the cells
            f.write("CELLS "
            #+ str(len(self.tets)) + " "
            #+ str(5 * len(self.tets)) + "\n"
            + str(len(self.tets) + len(self.tris)) + " "
            + str(5 * len(self.tets) + 4 * len(self.tris)) + "\n"
            )
            if len(self.tris)>0:
                for t in self.tris:
                    f.write("3 %i %i %i\n" % (t[0], t[1], t[2]))
                f.write("\n")
            if len(self.tets)>0:
                for t in self.tets:
                    f.write("4 %i %i %i %i\n" % (t[0], t[1], t[2], t[3]))
                f.write("\n")
            f.write("CELL_TYPES " + str(len(self.tets) + len(self.tris)) + "\n")
            if len(self.tris)>0:
                for t in self.tris:
                    f.write("5\n")
            if len(self.tets)>0:
                for t in self.tets:
                    f.write("10\n")
            f.write("\n")
            # Writing the scalar and vector data
            if len(self.scalars)>0 or len(self.vectors)>0:
                f.write("POINT_DATA " + str(len(self.verts)) + "\n")
                #Writing the scalar fields
                if len(self.scalars)>0:
                    f.write("SCALARS pressure float\nLOOKUP_TABLE default\n")
                    for v in self.scalars:
                        f.write("%.8f\n" % v)
                    f.write("\n")
                if len(self.vectors)>0:
                    f.write("VECTORS velocity float\n")
                    for v in self.vectors:
                        f.write("%.8f %.8f %.8f\n" % (v[0],v[1],v[2]))
    def writeXYZ(self, path):
        with open(path,"w") as f:
            for v in self.verts:
                f.write("%.8f %.8f %.8f\n" % (v[0], v[1], v[2]))
