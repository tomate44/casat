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
Face flattening
"""
import os

import FreeCAD as App
import FreeCADGui as Gui
import Part

from freecad.casat import *
from .. import _utils
from ...app import face

TOOL_ICON = os.path.join(ICONPATH, "face_flattening.svg")

class FlattenFace():
    resources = {
        'Pixmap'  : TOOL_ICON,
        'Accel'   : "",
        'MenuText': "Flatten Face",
        'ToolTip' : "Generates a flattened face from a cylindrical or conical face",
        'CmdType' : "ForEdit"
    }

    def GetResources(self):
        return self.resources

    def createFP(self, obj, sub):
        o = App.ActiveDocument.addObject('Part::FeaturePython', 'FlattenFace')
        o.Label = 'Flat Face'
        Flatten(o)
        FlattenVP(o.ViewObject)
        o.Face = [obj, sub]

    def Activated(self):
        debug('Running FlattenFace Command ...')

        sel = Gui.Selection.getSelectionEx()
        faces = []
        for so in sel:
            if so.HasSubObjects:
                for name in so.SubElementNames:
                    if "Face" in name: 
                        self.createFP(so.Object, name)
            else:
                self.createFP(so.Object, [])
        App.ActiveDocument.recompute()
        Gui.SendMsgToActiveView('ViewFit')

    def IsActive(self):
        if (App.ActiveDocument is not None) and (len(Gui.Selection.getSelection()) > 0):
            return True
        else:
            return False

class Flatten:
    "The FlattenFace Proxy object"
    def __init__(self, fp):
        fp.addProperty("App::PropertyLinkSub","Face")
        fp.addProperty("App::PropertyBool","Reverse","Base","Reverse the face orientation").Reverse = False
        fp.addProperty("App::PropertyBool","InPlace","Base","Attach the flattened face to the input face seam").InPlace = True
        fp.Proxy = self

    def execute(self, fp):
        if fp.Face[1] == []:
            faces = []
            for f in fp.Face[0].Shape.Faces:
                nf = face.flatten(f, fp.InPlace)
                if nf is not None:
                    faces.append(nf)
            if faces:
                fp.Shape = Part.Compound(faces)
        else:
            my_face = _utils.getShape(fp, "Face", "Face")
            f = face.flatten(my_face, fp.InPlace)
            if f is not None:
                if fp.Reverse:
                    f.reverse()
                fp.Shape = f

class FlattenVP:
    def __init__(self,vobj):
        vobj.Proxy = self
       
    def getIcon(self):
        return TOOL_ICON

Gui.addCommand('casat_flatten_face', FlattenFace())
