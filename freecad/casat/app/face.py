# -*- coding: utf-8 -*-

__title__ = "Face module"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = """Various utilities working on topo faces"""

import FreeCAD as App
import FreeCADGui as Gui
from freecad.casat import *
import Part
from . import wire as wt
vec3 = App.Vector
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

def flat_cone_surface(face, in_place=False):
    """
    Creates a flat nurbs surface from input conical face
    if in_place is True, the surface is located at the seam edge of the face.
    """
    u0,u1,v0,v1 = face.ParameterRange
    seam = face.Surface.uIso(0)
    p1 = seam.value(v0)
    p2 = seam.value(v1)
    radius1 = face.Surface.Apex.distanceToPoint(p1)
    radius2 = face.Surface.Apex.distanceToPoint(p2)
    t = seam.tangent(v0)[0]
    normal = t.cross(face.Surface.Axis.cross(t))
    c1 = Part.Circle(face.Surface.Apex, normal, radius1)
    c2 = Part.Circle(face.Surface.Apex, normal, radius2)
    ci1 = face.Surface.vIso(v0)
    ci2 = face.Surface.vIso(v1)
    fp1 = c1.parameter(p1)
    fp2 = c2.parameter(p2)
    lp1 = c1.parameterAtDistance(ci1.length(), fp1)
    lp2 = c2.parameterAtDistance(ci2.length(), fp2)
    if not in_place:
        c1 = Part.Circle(vec3(), vec3(0,0,1), radius1)
        c2 = Part.Circle(vec3(), vec3(0,0,1), radius2)
    ce1 = c1.toShape(fp1,lp1)
    ce2 = c2.toShape(fp2,lp2)
    rs = Part.makeRuledSurface(ce1,ce2)
    bs = rs.Surface
    bs.setUKnots([0, 2*pi])
    bs.setVKnots([v0, v1])
    return bs

def flat_cylinder_surface(face):
    """
    Creates a flat nurbs surface from input cylindrical face
    """
    l1 = face.Surface.uIso(0)
    e1 = l1.toShape(*face.ParameterRange[2:])
    c1 = face.Surface.vIso(face.ParameterRange[2])
    t1 = c1.tangent(c1.FirstParameter)[0]
    l = c1.length()
    e2 = e1.copy()
    e2.translate(t1*l)
    rs = Part.makeRuledSurface(e1,e2)
    bs = rs.Surface
    bs.exchangeUV()
    bs.setUKnots([0, 2*pi])
    return bs

def flatten(face):
    """
    Flattens a face.
    Currently, this works only on conical and cylindrical faces.
    Returns the flat face, or a compound of wires, if face creation fails.
    """
    tol = 1e-7
    if isinstance(face.Surface, Part.Cylinder):
        flat_face = flat_cylinder_surface(face)
    elif isinstance(face.Surface, Part.Cone):
        flat_face = flat_cone_surface(face)
    else:
        return None
    u0,u1,v0,v1 = face.Surface.bounds()
    seam = face.Surface.uIso(0)
    wires = []
    for w in face.Wires:
        edges = []
        additional_edges = []
        for e in w.Edges:
            c, fp, lp = face.curveOnSurface(e)
            if isinstance(c, Part.Geom2d.Line2d):
                p1 = c.value(fp)
                p2 = c.value(lp)
                if abs(p1.x-u0)+abs(p2.x-u0) < tol:
                    print("seam edge detected at u0")
                    p1.x = u1
                    p2.x = u1
                    nl = Part.Geom2d.Line2dSegment(p1,p2)
                    additional_edges.append(nl.toShape(flat_face))
                elif abs(p1.x-u1)+abs(p2.x-u1) < tol:
                    print("seam edge detected at u1")
                    p1.x = u0
                    p2.x = u0
                    nl = Part.Geom2d.Line2dSegment(p1,p2)
                    additional_edges.append(nl.toShape(flat_face))
            edges.append(c.toShape(flat_face, fp, lp))
        se = Part.sortEdges(edges)
        if len(se) > 1:
            print("multiple wires : trying to join them")
            se = Part.sortEdges(edges+additional_edges)
        if len(se) > 1:
            print("Failed to join wires ???")
        w = Part.Wire(se[0])
        if not w.isClosed():
            print("Closing open wire")
            w = wt.close(w)
        wires.append(w)
    f = Part.Face(wires)
    f.validate()
    if f.isValid():
        return f
    else:
        return Part.Compound(wires)

