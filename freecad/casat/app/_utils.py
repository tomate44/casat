# -*- coding: utf-8 -*-

__title__ = "casat workbench utilities"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "casat workbench utilities"

import FreeCAD

DEBUG = True

def message(s):
    FreeCAD.Console.PrintMessage("Casat::{}\n".format(str(s)))
def warning(s):
    FreeCAD.Console.PrintWarning("Casat::{}\n".format(str(s)))
def error(s):
    FreeCAD.Console.PrintError("Casat::{}\n".format(str(s)))
def debug(s):
    if DEBUG:
        message(s)

def setEditorMode(fp, group, mode):
    """set the editor mode of a group of properties"""
    for prop in group:
        fp.setEditorMode(prop, mode)

def getSubShape(shape, shape_type, n):
    if shape_type == "Vertex" and len(shape.Vertexes) >= n:
        return shape.Vertexes[n-1]
    elif shape_type == "Edge" and len(shape.Edges) >= n:
        return shape.Edges[n-1]
    elif shape_type == "Face" and len(shape.Faces) >= n:
        return shape.Faces[n-1]
    else:
        return None

def getShape(obj, prop, shape_type):
    if hasattr(obj, prop) and obj.getPropertyByName(prop):
        if obj.getTypeIdOfProperty(prop) == "App::PropertyLinkSub":
            n = eval(obj.getPropertyByName(prop)[1][0].lstrip(shape_type))
            sh = obj.getPropertyByName(prop)[0].Shape.copy()
            if sh and hasattr(obj.getPropertyByName(prop)[0], "getGlobalPlacement"):
                pl = obj.getPropertyByName(prop)[0].getGlobalPlacement()
                sh.Placement = pl
            return getSubShape(sh, shape_type, n)
        elif obj.getTypeIdOfProperty(prop) == "App::PropertyLinkSubList":
            res = []
            for tup in obj.getPropertyByName(prop):
                for ss in tup[1]:
                    n = eval(ss.lstrip(shape_type))
                    sh = tup[0].Shape.copy()
                    if sh and hasattr(tup[0], "getGlobalPlacement"):
                        pl = tup[0].getGlobalPlacement()
                        sh.Placement = pl
                    res.append(getSubShape(sh, shape_type, n))
            return res
        else:
            FreeCAD.Console.PrintError("CurvesWB._utils.getShape: wrong property type.\n")
            return None
    else:
        FreeCAD.Console.PrintError("CurvesWB._utils.getShape: %r has no property %r\n"%(obj, prop))
        return None

def same_direction(e1, e2, num=10):
    """bool = same_direction(e1, e2, num=10)
    Check if the 2 entities have same direction,
    by comparing them on 'num' samples.
    Entities can be : edges, wires or curves
    """
    v1 = []
    v2 = []
    pts1 = e1.discretize(num)
    pts2 = e2.discretize(num)
    for i in range(num):
        v1.append(pts1[i].distanceToPoint(pts2[i]))
        v2.append(pts1[i].distanceToPoint(pts2[num-1-i]))
    if sum(v1) < sum(v2):
        return True
    else:
        return False

def ruled_surface(e1,e2):
    """ creates a ruled surface between 2 edges, with automatic orientation."""
    import Part
    if not same_direction(e1,e2):
        e = e2.copy()
        e.reverse()
        return Part.makeRuledSurface(e1,e)
    else:
        return Part.makeRuledSurface(e1,e2)

def info_subshapes(shape):
    """Print the list of subshapes of a shape in FreeCAD console.
    info_subshapes(my_shape)
    """
    sh = ["Solids",
          "Compounds",
          "CompSolids",
          "Shells",
          "Faces",
          "Wires",
          "Edges",
          "Vertexes"]
    info("-> Content of {}".format(shape.ShapeType))
    for s in sh:
        subs = shape.__getattribute__(s)
        if subs:
            if (len(subs) == 1) and (subs[0].isEqual(shape)):
                pass # hide self
            else:
                info("{}: {}".format(s, len(subs)))

def ancestors(shape, sub):
    '''list_of_shapes = ancestors(shape, sub)
    Returns the closest ancestors of "sub" in "shape"'''
    def cleanup(shape):
        s = str(shape)
        ss = s.split()[0]
        return ss.split('<')[1]
    shd = (Part.Vertex,
           Part.Edge,
           Part.Wire,
           Part.Face,
           Part.Shell,
           Part.Solid,
           Part.CompSolid,
           Part.Compound)
    for i in range(len(shd)-1):
        if isinstance(sub, shd[i]):
            for j in range(i+1,len(shd)):
                manc = shape.ancestorsOfType(sub, shd[j])
                if manc:
                    print("{} belongs to {} {}.".format(cleanup(sub), len(manc), cleanup(manc[0])))
                    return manc
