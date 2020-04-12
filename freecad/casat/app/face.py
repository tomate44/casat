# -*- coding: utf-8 -*-

__title__ = "Face module"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = """Various utilities working on topo faces"""

import FreeCAD as App
import FreeCADGui as Gui
from freecad.casat import *
import Part
vec2 = App.Base.Vector2d

debug("face python module")

class Face(object):
    "Face class"
    def __init__(self, face):
        self.face = face

def get_finite_surface_bounds(face):
    """Returns surface bounds of a face, but avoid infinite values
    Input : Topo face
    Output : u0, u1, v0, v1"""
    res = []
    for u,s in zip(face.Surface.bounds(),face.ParameterRange):
        if abs(u) > 1e99:
            res.append(s)
        else:
            res.append(u)
    return res

def get_face_2d_boundary(face):
    """Returns the 2D boundingbox of a face
    Input : Topo face
    Output : list of 4 Line2dSegments"""
    u0, u1, v0, v1 = get_finite_surface_bounds(face)
    l1 = Part.Geom2d.Line2dSegment(vec2(u0,v0), vec2(u1,v0))
    l2 = Part.Geom2d.Line2dSegment(vec2(u1,v0), vec2(u1,v1))
    l3 = Part.Geom2d.Line2dSegment(vec2(u1,v1), vec2(u0,v1))
    l4 = Part.Geom2d.Line2dSegment(vec2(u0,v1), vec2(u0,v0))
    return [l1,l2,l3,l4]

def get_face_boundary_rectangle(face):
    """Returns the 3D boundary wire of the 2D boundingbox of a face
    Input : Topo face
    Output : Topo Wire"""
    lines = get_face_2d_boundary(face)
    edges = [l.toShape(face.Surface) for l in lines]
    return Part.Wire(Part.sortEdges(edges)[0])

def isocurve(face, param, direction="U"):
    """computes a face isoCurve.
    The isoCurve of the underlying surface is trimmed by the face wires.
    list_of_edges = isocurve(face, param, direction="U")
    Input:  Topo face
            param (float) parameter value of the isocurve
            direction (char) "U" or "V"
    Output : list of edges"""
    u0, u1, v0, v1 = get_finite_surface_bounds(face)
    if direction in ("v","V"):
        p0 = vec2(u0, param)
        p1 = vec2(u1, param)
        inter = [u0, u1]
    else:
        p0 = vec2(param, v0)
        p1 = vec2(param, v1)
        inter = [v0, v1]
    line = Part.Geom2d.Line2dSegment(p0, p1)

    for e in face.Edges:
        cos = face.curveOnSurface(e)
        pts = line.intersectCC(cos[0])
        inter.extend([line.parameter(p) for p in pts])
    inter = list(set(inter))
    inter.sort()
    #print("intersections : {}".format(inter))
    edges = []
    #print(inter)
    for i in range(len(inter)-1):
        mid = inter[i] + 0.5*(inter[i+1] - inter[i])
        p2 = line.value(mid)
        if face.isPartOfDomain(p2.x, p2.y):
            edges.append(line.toShape(face.Surface, inter[i], inter[i+1]))
    return edges

def isocurves(face, nbU=8, nbV=8, mode=0):
    """returns a compound of trimmed isocurves
    Compound_of_edges = isocurves(face, nbU=8, nbV=8, mode=0)
    or
    Compound_of_edges = isocurves(face, u_params=[0.0, 0.3, 1.0], v_params=[0.0, 0.5, 1.0], mode=0)
    nbU : number of isocurves in the U direction, or list of parameters
    nbV : number of isocurves in the V direction, or list of parameters
    mode = 0 : no trimming, full surface isocurve
    mode = 1 : trim only with face outerwire
    mode = 2 : trim with all the edges of the face
    """
    coms = []
    u0,u1,v0,v1 = get_finite_surface_bounds(face)
    if mode == 0:
        wire = get_face_boundary_rectangle(face)
        trim_face = Part.Face(face.Surface,wire)
    elif mode == 1:
        wire = face.OuterWire
        trim_face = Part.Face(face.Surface,wire)
    else:
        trim_face = face
    trim_face.validate()
    eU = []
    if isinstance(nbU,(list,tuple)):
        for u in nbU:
            eU.extend(isocurve(trim_face, u, "u"))
    elif nbU == 1:
        u = 0.5*(u0+u1)
        eU.extend(isocurve(trim_face, u, "u"))
    else:
        for i in range(nbU):
            u = u0 + i*(u1-u0)/(nbU-1)
            eU.extend(isocurve(trim_face, u, "u"))

    eV = []
    if isinstance(nbV,(list,tuple)):
        for v in nbV:
            eV.extend(isocurve(trim_face, v, "v"))
    elif nbV == 1:
        v = 0.5*(v0+v1)
        eV.extend(isocurve(trim_face, v, "v"))
    else:
        for i in range(nbV):
            v = v0 + i*(v1-v0)/(nbV-1)
            eV.extend(isocurve(trim_face, v, "v"))
    return Part.Compound([Part.Compound(eU),Part.Compound(eV)])

