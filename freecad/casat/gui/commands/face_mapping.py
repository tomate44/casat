# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) Christophe Grellier <cg@grellier.fr>                  *
#*                                                                     *
#* This program is free software; you can redistribute it and/or modify*
#* it under the terms of the GNU Lesser General Public License (LGPL)  *
#* as published by the Free Software Foundation; either version 2 of   *
#* the License, or (at your option) any later version.                 *
#* for detail see the LICENCE text file.                               *
#*                                                                     *
#* This program is distributed in the hope that it will be useful,     *
#* but WITHOUT ANY WARRANTY; without even the implied warranty of      *
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
#* GNU Library General Public License for more details.                *
#*                                                                     *
#* You should have received a copy of the GNU Library General Public   *
#* License along with this program; if not, write to the Free Software *
#* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#* USA                                                                 *
#*                                                                     *
#***********************************************************************
"""
Face mapping
"""
import os

import FreeCAD as App
import FreeCADGui as Gui
import Part

from freecad.casat import *
from .. import _utils
from ...app import face

vec3 = App.Vector

TOOL_ICON = os.path.join(ICONPATH, "face_mapping.svg")

class FaceMapping():
    resources = {
        'Pixmap'  : TOOL_ICON,
        'Accel'   : "",
        'MenuText': "Face Mapping",
        'ToolTip' : "Map shapes on a target face"
    }

    def GetResources(self):
        return self.resources

    def createFP(self, objs, face):
        o = App.ActiveDocument.addObject('Part::FeaturePython', 'FaceMapping')
        o.Label = 'Mapping'
        Mapping(o)
        MappingVP(o.ViewObject)
        o.Target = face
        o.Source = objs

    def Activated(self):
        debug('Running FaceMapping Command ...')
        sel = Gui.Selection.getSelectionEx()
        objs = []
        face = None
        for so in sel:
            if so.HasSubObjects:
                for name in so.SubElementNames:
                    if "Face" in name:
                        face = (so.Object, name)
                        break
            else:
                objs.append(so.Object)
        if face:
            self.createFP(objs, face)
        App.ActiveDocument.recompute()
        Gui.SendMsgToActiveView('ViewFit')

    def IsActive(self):
        if (App.ActiveDocument is not None) and (len(Gui.Selection.getSelection()) > 0):
            return True
        else:
            return False

class Mapping:
    "The FaceMapping Proxy object"
    def __init__(self, fp):
        fp.addProperty("App::PropertyLinkList", "Source", "Base", "The source objects that will be mapped")
        fp.addProperty("App::PropertyLinkSub", "Target", "Base", "The target face")
        fp.addProperty("App::PropertyLink", "Transfer", "Base", "The quad surface used for projection")
        #fp.addProperty("App::PropertyFloat", "Offset", "Settings", "Offset distance of mapped sketch").Offset = 0.0
        fp.addProperty("App::PropertyFloatList", "Offset","Settings", "Offset distance of mapped shapes")
        fp.addProperty("App::PropertyBool", "ReverseU", "Settings", "Reverse U direction").ReverseU = False
        fp.addProperty("App::PropertyBool", "ReverseV", "Settings", "Reverse V direction").ReverseV = False
        fp.Proxy = self

    def get_quad(self, shapes):
        bb = Part.Compound(shapes).BoundBox
        dims = [bb.XLength, bb.YLength, bb.ZLength]
        if min(dims) == dims[0]:
            pts = [vec3(bb.XMin, bb.YMin, bb.ZMin),
                vec3(bb.XMin, bb.YMax, bb.ZMin),
                vec3(bb.XMin, bb.YMax, bb.ZMax),
                vec3(bb.XMin, bb.YMin, bb.ZMax)]
        elif min(dims) == dims[1]:
            pts = [vec3(bb.XMin, bb.YMin, bb.ZMin),
                vec3(bb.XMax, bb.YMin, bb.ZMin),
                vec3(bb.XMax, bb.YMin, bb.ZMax),
                vec3(bb.XMin, bb.YMin, bb.ZMax)]
        else:
            pts = [vec3(bb.XMin, bb.YMin, bb.ZMin),
                vec3(bb.XMax, bb.YMin, bb.ZMin),
                vec3(bb.XMax, bb.YMax, bb.ZMin),
                vec3(bb.XMin, bb.YMax, bb.ZMin)]
        return pts

    def execute(self, fp):
        target = fp.Target[0].Shape.getElement(fp.Target[1][0])
        targets = []
        if fp.Offset:
            for v in fp.Offset:
                if not v == 0.0:
                    f = target.makeOffsetShape(v, 1e-3)
                    targets.append(f.Face1)
        if not targets:
            targets = [target]
        shapes = []
        for o in fp.Source:
            if o.Shape.Faces:
                shapes.extend(o.Shape.Faces)
            elif o.Shape.Wires:
                shapes.extend(o.Shape.Wires)
            elif o.Shape.Edges:
                shapes.extend(o.Shape.Edges)
        if fp.Transfer:
            pts = [v.Point for v in fp.Transfer.Shape.Vertexes]
        else:
            pts = self.get_quad(shapes)
        if fp.ReverseU:
            pts = [pts[1], pts[0], pts[3], pts[2]]
        if fp.ReverseV:
            pts = [pts[3], pts[2], pts[1], pts[0]]
        bs = Part.BSplineSurface()
        bs.setPole(1, 1, pts[0])
        bs.setPole(2, 1, pts[1])
        bs.setPole(2, 2, pts[2])
        bs.setPole(1, 2, pts[3])
        results = []
        for t in targets:
            results.append(Part.Compound(face.map_shapes(shapes, t, bs)))
        if results:
            fp.Shape = Part.Compound(results)

class MappingVP:
    
    def __init__(self,vobj):
        vobj.Proxy = self
        self.children = []
       
    def getIcon(self):
        return TOOL_ICON

    def attach(self, vobj):
        self.Object = vobj.Object

    def __getstate__(self):
        return {"name": self.Object.Name}

    def __setstate__(self,state):
        self.Object = FreeCAD.ActiveDocument.getObject(state["name"])

    def claimChildren(self):
        return self.Object.Source


Gui.addCommand('casat_face_mapping', FaceMapping())
