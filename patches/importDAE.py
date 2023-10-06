# 2016-03-07 - tk	info@tkinnovations.net
#				importDAE.py replacement v 1.0.0
#				customized for clearer naming, and color export
#				*** don't forget code optimization pass ***
#				requires webcolors (used v 1.5) for nice ShapeColor names (https://pypi.python.org/pypi/webcolors/)
#				added date/time stamp & progress bar

import webcolors
import datetime
import FreeCADGui
import PySide

# debug
import time



# thanks for this closest color algo (http://stackoverflow.com/users/1175101/fraxel)
def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    #return actual_name, closest_name
    return closest_name

#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2011                                                    *  
#*   Yorik van Havre <yorik@uncreated.net>                                 *  
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

import FreeCAD, Mesh, os, numpy
if FreeCAD.GuiUp:
    from DraftTools import translate
else:
    def translate(context,text):
        return text

__title__="FreeCAD Collada importer"
__author__ = "Yorik van Havre"
__url__ = "http://www.freecadweb.org"

DEBUG = True

def checkCollada():
    "checks if collada if available"
    global collada
    COLLADA = None
    try:
        import collada
    except ImportError:
        FreeCAD.Console.PrintError(translate("Arch","pycollada not found, collada support is disabled.\n"))
        return False
    else:
        return True
    
def open(filename):
    "called when freecad wants to open a file"
    if not checkCollada(): 
        return
    docname = os.path.splitext(os.path.basename(filename))[0]
    doc = FreeCAD.newDocument(docname)
    doc.Label = decode(docname)
    FreeCAD.ActiveDocument = doc
    read(filename)
    return doc

def insert(filename,docname):
    "called when freecad wants to import a file"
    if not checkCollada(): 
        return
    try:
        doc = FreeCAD.getDocument(docname)
    except NameError:
        doc = FreeCAD.newDocument(docname)
    FreeCAD.ActiveDocument = doc
    read(filename)
    return doc

def decode(name):
    "decodes encoded strings"
    try:
        decodedName = (name.decode("utf8"))
    except UnicodeDecodeError:
        try:
            decodedName = (name.decode("latin1"))
        except UnicodeDecodeError:
            FreeCAD.Console.PrintError(translate("Arch","Error: Couldn't determine character encoding"))
            decodedName = name
    return decodedName

def read(filename):
    global col
    col = collada.Collada(filename, ignore=[collada.DaeUnsupportedError])
    # Read the unitmeter info from dae file and compute unit to convert to mm
    unitmeter = col.assetInfo.unitmeter or 1
    unit = unitmeter / 0.001
    for geom in col.scene.objects('geometry'):
    #for geom in col.geometries:
        for prim in geom.primitives():
        #for prim in geom.primitives:
            #print prim, dir(prim)
            meshdata = []
            if hasattr(prim,"triangles"):
                tset = prim.triangles()
            elif hasattr(prim,"triangleset"):
                tset = prim.triangleset()
            else:
                tset = []
            for tri in tset:
                face = []
                for v in tri.vertices:
                    v = [x * unit for x in v]
                    face.append([v[0],v[1],v[2]])
                meshdata.append(face)
            #print meshdata
            newmesh = Mesh.Mesh(meshdata)
            #print newmesh
            obj = FreeCAD.ActiveDocument.addObject("Mesh::Feature","Mesh")
            obj.Mesh = newmesh

def export(exportList,filename):
    "called when freecad exports a file"
    if not checkCollada(): return
    p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Arch")
    scale = p.GetFloat("ColladaScalingFactor",1.0)
    colmesh = collada.Collada()
    colmesh.assetInfo.upaxis = collada.asset.UP_AXIS.Z_UP
# 2016-03-07 - tk - remove generic effect and mat and generate per object in loop
    #effect = collada.material.Effect("effect0", [], "phong", diffuse=(.7,.7,.7), specular=(1,1,1))
    #mat = collada.material.Material("material0", "mymaterial", effect)
    #colmesh.effects.append(effect)
    #colmesh.materials.append(mat)
    objind = 0
    scenenodes = []
    # setup progress indicator
    pbProgress = PySide.QtGui.QProgressDialog(("Exporting objects to %s" % filename), "", 0, len(exportList))
    pbProgress.setWindowModality(PySide.QtCore.Qt.WindowModality.WindowModal)
    pbProgress.setValue(0)
    pbProgress.setCancelButton(None)
    pbProgress.setMinimumDuration(0)
    pbProgress.show()
    True = 1
    for obj in exportList:
# 2016-03-07 - tk - group objects cause issues with ShapeColor so detect and ignore; will be working to create group handling
        bHandled = False    
        if obj.isDerivedFrom("Part::Feature"):
            bHandled = True            
            print "exporting part ",obj.Name, obj.Shape
            FreeCAD.Console.PrintMessage(translate("Arch","\nexporting part: %s\t%s\n") % (obj.Name, obj.Label))
            m = obj.Shape.tessellate(1)
            vindex = []
            nindex = []
            findex = []
            # vertex indices
            for v in m[0]:
                vindex.extend([v.x*scale,v.y*scale,v.z*scale])
            # normals
            for f in obj.Shape.Faces:
                n = f.normalAt(0,0)
                for i in range(len(f.tessellate(1)[1])):
                    nindex.extend([n.x,n.y,n.z])
            # face indices
            for i in range(len(m[1])):
                f = m[1][i]
                findex.extend([f[0],i,f[1],i,f[2],i])
        elif obj.isDerivedFrom("Mesh::Feature"):
            bHandled = True            
            print "exporting mesh ",obj.Name, obj.Mesh
            FreeCAD.Console.PrintMessage(translate("Arch","\nexporting mesh %s\t%s\n") % (obj.Name, obj.Label))
            m = obj.Mesh
            vindex = []
            nindex = []
            findex = []
            # vertex indices
            for v in m.Topology[0]:
                vindex.extend([v.x*scale,v.y*scale,v.z*scale])
            # normals
            for f in m.Facets:
                n = f.Normal
                nindex.extend([n.x,n.y,n.z])
            # face indices
            for i in range(len(m.Topology[1])):
                f = m.Topology[1][i]
                findex.extend([f[0],i,f[1],i,f[2],i])
        if bHandled:
            print len(vindex), " vert indices, ", len(nindex), " norm indices, ", len(findex), " face indices."
            vert_src = collada.source.FloatSource("cubeverts-array"+str(objind), numpy.array(vindex), ('X', 'Y', 'Z'))
            normal_src = collada.source.FloatSource("cubenormals-array"+str(objind), numpy.array(nindex), ('X', 'Y', 'Z'))
# 2016-03-07 - tk - allow object label from user controlled properties to be used, eg. "End Cap 20x40mm-001" may read better than "Fillet004_solid001"
            #geom = collada.geometry.Geometry(colmesh, "geometry"+str(objind), obj.Name, [vert_src, normal_src])
            geom = collada.geometry.Geometry(colmesh, "geometry"+str(objind), obj.Label, [vert_src, normal_src])
            input_list = collada.source.InputList()
            input_list.addInput(0, 'VERTEX', "#cubeverts-array"+str(objind))
            input_list.addInput(1, 'NORMAL', "#cubenormals-array"+str(objind))
            triset = geom.createTriangleSet(numpy.array(findex), input_list, "materialref")
            geom.primitives.append(triset)
            colmesh.geometries.append(geom)
# 2016-03-07 - tk - customize per obj shape color value; future this can be snazed up in the property editor
        # generate effect and material
        #colName = ''.join(map(str, obj.ShapeColor)).translate(None, '.') # want a real name instead of jamming RGB into a string; will try webcolors 1.5 package
            objGUI = FreeCADGui.getDocument(obj.Document.Name).getObject(obj.Name)
            colTmp = [0, 0, 0]
            colTmp[0] = int(objGUI.ShapeColor[0] * 255)
            colTmp[1] = int(objGUI.ShapeColor[1] * 255)
            colTmp[2] = int(objGUI.ShapeColor[2] * 255)
            colName = get_colour_name([colTmp[0], colTmp[1], colTmp[2]])
            effName = "eff_" + colName
            matName = "mat_" + colName
            # allow object color from user controlled properties to be used and a more true representation of the color
            #effect = collada.material.Effect(effName, [], "phong", diffuse=(.7,.7,.7), specular=(1,1,1))
            effect = collada.material.Effect(effName, [], "phong", diffuse=(objGUI.ShapeColor), specular=(0.01, 0.01, 0.01))
            mat = collada.material.Material(matName, matName, effect)
            # only allow unique eff/mat references
            bEffNotExist = 1
            for eff in colmesh.effects:
                if eff.id == effect.id:
                    bEffNotExist = False
                    break
            if bEffNotExist:
                colmesh.effects.append(effect)
                colmesh.materials.append(mat)
            ########
            matnode = collada.scene.MaterialNode("materialref", mat, inputs=[])
            geomnode = collada.scene.GeometryNode(geom, [matnode])
            node = collada.scene.Node("node"+str(objind), children=[geomnode])
            scenenodes.append(node)
        objind += 1
        pbProgress.setValue(objind)
        #time.sleep(3)

    myscene = collada.scene.Scene("myscene", scenenodes)
    colmesh.scenes.append(myscene)
    colmesh.scene = myscene
    colmesh.write(filename)
    FreeCAD.Console.PrintMessage(translate("Arch","\n\nfile %s successfully created %s\n\n") % (filename, datetime.datetime.now()))


###############
# DEBUG TESTS #
###############

#__objs__=[]
#__objs__.append(FreeCAD.getDocument("tk_FULL_V_1").getObject("Fillet004_solid"))
#__objs__.append(FreeCAD.getDocument("tk_FULL_V_1").getObject("Fillet004_solid001"))
#__objs__.append(FreeCAD.getDocument("tk_FULL_V_1").getObject("Cut_solid002"))

#__objs__.append(FreeCAD.getDocument("tk_FULL_V_1").getObject("Group016"))


#export(__objs__,u"C:/temp/fr-test-tk-1.dae")

#del __objs__

