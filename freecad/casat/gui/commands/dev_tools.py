# -*- coding: utf-8 -*-

__title__ = "to console"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Objects to python console."

import os
import FreeCAD
import FreeCADGui
import Part
from freecad.casat import error
from freecad.casat import ICONPATH

class ToConsole:
    "Brings the selected objects to the python console"
    def GetResources(self):
        return {'Pixmap'  : os.path.join(ICONPATH, "toconsole.svg"),
                'MenuText': "to Console",
                'Accel': "",
                'ToolTip': "Objects to console"}

    def Activated(self):
        doc = ''
        obj = ''
        sob = ''
        sublinks = '('

        doc_num = 0
        obj_num = 0
        face_num = 0
        edge_num = 0
        vert_num = 0

        selection = FreeCADGui.Selection.getSelectionEx()
        if selection == []:
            error('Selection is empty.')

        for selobj in selection:
            if not selobj.DocumentName == doc:
                doc = selobj.DocumentName
                doc_num += 1
                FreeCADGui.doCommand("doc{} = FreeCAD.getDocument('{}')".format(doc_num,doc))
            if not selobj.ObjectName == obj:
                obj = selobj.ObjectName
                obj_num += 1
                FreeCADGui.doCommand("o{} = doc{}.getObject('{}')".format(obj_num,doc_num,obj))
            if selobj.HasSubObjects:
                for sub in selobj.SubElementNames:
                    sublinks += "(o{},('{}')),".format(obj_num,sub)
                    if 'Vertex' in sub:
                        vert_num += 1
                        FreeCADGui.doCommand("v{} = o{}.Shape.{}".format(vert_num,obj_num,sub))
                    if 'Edge' in sub:
                        edge_num += 1
                        FreeCADGui.doCommand("e{} = o{}.Shape.{}".format(edge_num,obj_num,sub))
                    if 'Face' in sub:
                        face_num += 1
                        FreeCADGui.doCommand("f{} = o{}.Shape.{}".format(face_num,obj_num,sub))
        sublinks += ")"
        if len(sublinks) > 1:
            FreeCADGui.doCommand("_sub_link_buffer = {}".format(sublinks))
        if obj_num > 1:
            ol = ''
            for oi in range(obj_num):
                ol += "o{},".format(oi+1)
            FreeCADGui.doCommand("ol = ({})".format(ol))
        if vert_num > 1:
            vl = ''
            for vi in range(vert_num):
                vl += "v{},".format(vi+1)
            FreeCADGui.doCommand("vl = ({})".format(vl))
            FreeCADGui.doCommand("pts = [v.Point for v in vl]".format(vl))
        if edge_num > 1:
            el = ''
            for ei in range(edge_num):
                el += "e{},".format(ei+1)
            FreeCADGui.doCommand("el = ({})".format(el))
        if face_num > 1:
            fl = ''
            for fi in range(face_num):
                fl += "f{},".format(fi+1)
            FreeCADGui.doCommand("fl = ({})".format(fl))

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            selection = FreeCADGui.Selection.getSelectionEx()
            if selection:
                return True
        else:
            return False

def curve_to_script(i,c):
    com = ["import FreeCAD",
           "from FreeCAD import Vector",
           "import Part",""]
    if isinstance(c,Part.BSplineCurve):
        com.append("poles%d = %r"%(i,c.getPoles()))
        com.append("weights%d = %r"%(i,c.getWeights()))
        com.append("knots%d = %r"%(i,c.getKnots()))
        com.append("mults%d = %r"%(i,c.getMultiplicities()))
        com.append("periodic%d = %r"%(i,c.isPeriodic()))
        com.append("degree%d = %s"%(i,c.Degree))
        com.append("rational%d = %r"%(i,c.isRational()))
        com.append("bs%d = Part.BSplineCurve()"%i)
        #com.append("bs%d.buildFromPolesMultsKnots(poles%d, mults%d, knots%d, periodic%d, degree%d, )"%(i,i,i,i,i,i))
        com.append("bs%d.buildFromPolesMultsKnots(poles%d, mults%d, knots%d, periodic%d, degree%d, weights%d, rational%d)"%(i,i,i,i,i,i,i,i))
        com.append('obj%d = FreeCAD.ActiveDocument.addObject("Part::Spline","BSplineCurve%d")'%(i,i))
        com.append('obj%d.Shape = bs%d.toShape()'%(i,i))
    elif isinstance(c,Part.BezierCurve):
        com.append("poles%d = %r"%(i,c.getPoles()))
        #com.append("degree%d = %s"%(i,c.Degree))
        com.append("be%d = Part.BezierCurve()"%i)
        com.append("be%d.increase(%s)"%(i,c.Degree))
        com.append("be%d.setPoles(poles%d)"%(i,i))
        if c.isRational():
            w = c.getWeights()
            for j in range(len(w)):
                com.append("be%d.setWeight(%i,%f)"%(i,j+1,w[j]))
        com.append('obj%d = FreeCAD.ActiveDocument.addObject("Part::Spline","BezierCurve%d")'%(i,i))
        com.append('obj%d.Shape = be%d.toShape()'%(i,i))
    com.append("")
    
    for s in com:
        FreeCADGui.doCommand(s)


class NurbsToConsole:
    "Brings the selected BSpline curves to the python console"
    def GetResources(self):
        return {'Pixmap'  : os.path.join(ICONPATH, "toconsole.svg"),
                'MenuText': "BSpline to Console",
                'Accel': "",
                'ToolTip': "BSpline curves to python console"}

    def Activated(self):
        s = FreeCADGui.Selection.getSelectionEx()
        i = 0
        for so in s:
            for sso in so.SubObjects:
                if hasattr(sso,"Curve"):
                    c = sso.Curve
                    curve_to_script(i,c)
                    i += 1

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            selection = FreeCADGui.Selection.getSelectionEx()
            if selection:
                return True
        else:
            return False

FreeCADGui.addCommand('bspline_to_console',NurbsToConsole())

FreeCADGui.addCommand('to_console',ToConsole())
