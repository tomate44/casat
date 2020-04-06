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
Face isocurves
"""
import os

import FreeCAD as App
import FreeCADGui as Gui
import Part

from freecad.casat import ICONPATH
from .. import _utils
from ...app import face

TOOL_ICON = os.path.join(ICONPATH, "face_isocurves.svg")

class FaceIsocurves():
    """
    Face isocurves Command
    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Resource definition allows customization of the command icon,
    # hotkey, text, tooltip and whether or not the command is active
    # when a task panel is open
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    resources = {
        'Pixmap'  : TOOL_ICON,
        'Accel'   : "Shift+1",
        'MenuText': "FaceIsocurves",
        'ToolTip' : "Creates isocurves on a face",
        'CmdType' : "ForEdit"
    }

    def GetResources(self):
        """
        Return the command resources dictionary
        """
        return self.resources

    def Activated(self):
        """
        Activation callback
        """
        print('\n\tRunning FaceIsocurves Command ...')

        sel = Gui.Selection.getSelectionEx()
        faces = []
        for so in sel:
            if so.HasSubObjects:
                for name in so.SubElementNames:
                    o = App.ActiveDocument.addObject('Part::FeaturePython', 'IsoCurves')
                    o.Label = 'IsoCurves'
                    IsoCurve(o)
                    IsoCurveVP(o.ViewObject)
                    o.Face = [so.Object,name]
            else:
                for i in range(len(so.Shape.Faces)):
                    o = App.ActiveDocument.addObject('Part::FeaturePython', 'IsoCurves')
                    o.Label = 'IsoCurves'
                    IsoCurve(o)
                    IsoCurveVP(o.ViewObject)
                    o.Face = [so.Object,"Face{}".format(i)]
        App.ActiveDocument.recompute()
        Gui.SendMsgToActiveView('ViewFit')

    def IsActive(self):
        """
        Returns always active
        """
        if (App.ActiveDocument is not None) and (len(Gui.Selection.getSelection()) > 0):
            return True
        else:
            return False

class IsoCurve:
    "The IsoCurve feature object"
    def __init__(self,selfobj):
        self.trim_modes = ["No Trimming","Boundary", "Full"]
        selfobj.addProperty("App::PropertyLinkSub","Face","IsoCurve","Input face")
        selfobj.addProperty("App::PropertyFloat","Parameter","IsoCurve","IsoCurve parameter").Parameter=0.
        selfobj.addProperty("App::PropertyInteger","NumberU","IsoCurve","Number of IsoCurve in U direction").NumberU=5
        selfobj.addProperty("App::PropertyInteger","NumberV","IsoCurve","Number of IsoCurve in V direction").NumberV=5
        selfobj.addProperty("App::PropertyEnumeration","Mode","IsoCurve","Number of IsoCurve").Mode=["Single","Multi"]
        selfobj.addProperty("App::PropertyEnumeration","Orientation","IsoCurve","Curve Orientation").Orientation=["U","V"]
        selfobj.addProperty("App::PropertyEnumeration","TrimMode","IsoCurve","How the isocurves are trimmed").TrimMode=self.trim_modes
        selfobj.Mode = "Multi"
        selfobj.TrimMode = "No Trimming"
        selfobj.setEditorMode("Parameter", 2)
        selfobj.setEditorMode("Orientation", 2)
        selfobj.setEditorMode("NumberU", 0)
        selfobj.setEditorMode("NumberV", 0)
        selfobj.Proxy = self

    def split(self, e, t0, t1):
        p0,p1 = e.ParameterRange
        if (t0 > p0) & (t1 < p1):
            w = e.split([t0,t1])
            return w.Edges[1]
        elif (t0 > p0):
            w = e.split(t0)
            return w.Edges[1]
        elif (t1 < p1):
            w = e.split(t1)
            return w.Edges[0]
        else:
            return e

    def getBounds(self, obj):
        face = self.getFace(obj)
        self.u0, self.u1, self.v0, self.v1 = face.ParameterRange

    def getFace(self, obj):
        return _utils.getShape(obj, "Face", "Face")

    def tangentAt(self, selfobj, p):
        if selfobj.Orientation == 'U':
            if (p >= self.v0) & (p <= self.v1):
                return selfobj.Shape.tangentAt(p)
            else:
                App.Console.PrintError("Parameter out of range (%f, %f)\n"%(self.v0,self.v1))
        if selfobj.Orientation == 'V':
            if (p >= self.u0) & (p <= self.u1):
                return selfobj.Shape.tangentAt(p)
            else:
                App.Console.PrintError("Parameter out of range (%f, %f)\n"%(self.u0,self.u1))

    def normalAt(self, selfobj, p):
        face = self.getFace(selfobj)
        if selfobj.Orientation == 'U':
            if (p >= self.v0) & (p <= self.v1):
                return face.normalAt(selfobj.Parameter, p)
            else:
                App.Console.PrintError("Parameter out of range (%f, %f)\n"%(self.v0,self.v1))
        if selfobj.Orientation == 'V':
            if (p >= self.u0) & (p <= self.u1):
                return face.normalAt(p, selfobj.Parameter)
            else:
                App.Console.PrintError("Parameter out of range (%f, %f)\n"%(self.u0,self.u1))


    def execute(self,selfobj):

        my_face = self.getFace(selfobj)
        #try:
            #trim = self.trim_modes.index(selfobj.TrimMode)
        #except:
            #trim = 0
        trim = self.trim_modes.index(selfobj.TrimMode)
        #print("trim : {}".format(trim))
        if my_face:
            if selfobj.Mode == 'Multi':
                w = face.face_isocurves(my_face, selfobj.NumberU, selfobj.NumberV, trim)
            else:
                if selfobj.Orientation == "V":
                    w = face.face_isocurves(my_face, [], [selfobj.Parameter], trim)
                else:
                    w = face.face_isocurves(my_face, [selfobj.Parameter], [], trim)
            selfobj.Shape = w
            #selfobj.Placement = my_face.Placement
        else:
            return False

    def onChanged(self, selfobj, prop):
        if prop == 'Face':
            face = self.getFace(selfobj)
            if not face:
                return
            self.getBounds(selfobj)
            if selfobj.Orientation == "U":
                self.p0 = self.u0
                self.p1 = self.u1
            else:
                self.p0 = self.v0
                self.p1 = self.v1
        if prop == 'Mode':
            if selfobj.Mode  == "Single":
                selfobj.setEditorMode("Parameter", 0)
                selfobj.setEditorMode("Orientation", 0)
                selfobj.setEditorMode("NumberU", 2)
                selfobj.setEditorMode("NumberV", 2)
            elif selfobj.Mode  == "Multi":
                selfobj.setEditorMode("Parameter", 2)
                selfobj.setEditorMode("Orientation", 2)
                selfobj.setEditorMode("NumberU", 0)
                selfobj.setEditorMode("NumberV", 0)
            self.execute(selfobj)
        if prop == 'Parameter':
            if  selfobj.Parameter  < self.p0:
                selfobj.Parameter  = self.p0
            elif selfobj.Parameter  > self.p1:
                selfobj.Parameter  = self.p1
            self.execute(selfobj)
        if prop == 'NumberU':
            if  selfobj.NumberU  < 0:
                selfobj.NumberU  = 0
            elif selfobj.NumberU  > 1000:
                selfobj.NumberU  = 1000
            self.execute(selfobj)
        if prop == 'NumberV':
            if  selfobj.NumberV  < 0:
                selfobj.NumberV  = 0
            elif selfobj.NumberV  > 1000:
                selfobj.NumberV  = 1000
            self.execute(selfobj)
        if prop == 'Orientation':
            self.getBounds(selfobj)
            if selfobj.Orientation == "U":
                self.p0 = self.u0
                self.p1 = self.u1
            else:
                self.p0 = self.v0
                self.p1 = self.v1
            self.execute(selfobj)
        if prop == 'TrimMode':
            self.execute(selfobj)

class IsoCurveVP:
    def __init__(self,vobj):
        vobj.Proxy = self
       
    def getIcon(self):
        return TOOL_ICON

    #def attach(self, vobj):
        #self.ViewObject = vobj
        #self.Object = vobj.Object

Gui.addCommand('casat_FaceIsocurves', FaceIsocurves())
