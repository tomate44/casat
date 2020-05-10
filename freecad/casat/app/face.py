# -*- coding: utf-8 -*-

__title__ = "Face module"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = """Various utilities working on topo faces"""

from math import pi
import FreeCAD as App
import FreeCADGui as Gui
import Part
from freecad.casat import *
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
    flat_face = flat_cone_surface(face, in_place=False)
    Creates a flat nurbs surface from input conical face, with same parametrization.
    If in_place is True, the surface is located at the seam edge of the face.
    """
    u0,u1,v0,v1 = get_finite_surface_bounds(face)
    seam = face.Surface.uIso(u0)
    p1 = seam.value(v0)
    p2 = seam.value(v1)
    radius1 = face.Surface.Apex.distanceToPoint(p1)
    radius2 = face.Surface.Apex.distanceToPoint(p2)
    t = seam.tangent(v0)[0]
    normal = -t.cross(face.Surface.Axis.cross(t))
    c1 = Part.Circle(face.Surface.Apex, normal, radius1)
    c2 = Part.Circle(face.Surface.Apex, normal, radius2)
    ci1 = face.Surface.vIso(v0)
    ci2 = face.Surface.vIso(v1)
    fp1 = c1.parameter(p1)
    fp2 = c2.parameter(p2)
    lp1 = c1.parameterAtDistance(ci1.length(), fp1)
    lp2 = c2.parameterAtDistance(ci2.length(), fp2)
    if not in_place:
        c1 = Part.Circle(vec3(0,0,0), vec3(0,0,1), radius1)
        c2 = Part.Circle(vec3(0,0,0), vec3(0,0,1), radius2)
    else:
        c1.Axis = -c1.Axis
        c2.Axis = -c2.Axis
    ce1 = c1.toShape(fp1,lp1)
    ce2 = c2.toShape(fp2,lp2)
    rs = Part.makeRuledSurface(ce1,ce2)
    bs = rs.Surface
    bs.setUKnots([0, 2*pi])
    bs.setVKnots([v0, v1])
    return bs

def flat_cylinder_surface(face, in_place=False):
    """
    flat_face = flat_cylinder_surface(face, in_place=False)
    Creates a flat nurbs surface from input cylindrical face, with same parametrization.
    If in_place is True, the surface is located at the seam edge of the face.
    """
    u0,u1,v0,v1 = get_finite_surface_bounds(face)
    c1 = face.Surface.uIso(u0) # seam line
    e1 = c1.toShape(v0,v1)
    l1 = e1.Length
    c2 = face.Surface.vIso(v0) # circle
    e2 = c2.toShape(u0,u1)
    l2 = e2.Length
    if in_place:
        t1 = c2.tangent(c2.FirstParameter)[0]
        e3 = e1.copy()
        e3.translate(t1*l2)
        rs = Part.makeRuledSurface(e1,e3)
        bs = rs.Surface
        bs.exchangeUV()
    else:
        bs = Part.BSplineSurface()
        bs.setPole(1, 1, vec3(v0, 0, 0))
        bs.setPole(1, 2, vec3(v1,0, 0))
        bs.setPole(2, 1, vec3(v0, l2,0))
        bs.setPole(2, 2, vec3(v1,l2,0))
    bs.setUKnots([0, 2*pi])
    bs.setVKnots([v0, v1])
    return bs

def flatten(face, in_place=False):
    """
    Flattens a face.
    Currently, this works only on conical and cylindrical faces.
    Returns the flat face, or a compound of wires, if face creation fails.
    """
    tol = 1e-7
    if isinstance(face.Surface, Part.Cylinder):
        flat_face = flat_cylinder_surface(face, in_place)
    elif isinstance(face.Surface, Part.Cone):
        flat_face = flat_cone_surface(face, in_place)
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
                    debug("seam edge detected at u0")
                    p1.x = u1
                    p2.x = u1
                    nl = Part.Geom2d.Line2dSegment(p1,p2)
                    additional_edges.append(nl.toShape(flat_face))
                elif abs(p1.x-u1)+abs(p2.x-u1) < tol:
                    debug("seam edge detected at u1")
                    p1.x = u0
                    p2.x = u0
                    nl = Part.Geom2d.Line2dSegment(p1,p2)
                    additional_edges.append(nl.toShape(flat_face))
            edges.append(c.toShape(flat_face, fp, lp))
        se = Part.sortEdges(edges)
        if len(se) > 1:
            debug("multiple wires : trying to join them")
            se = Part.sortEdges(edges+additional_edges)
        if len(se) > 1:
            error("Failed to join wires ???")
            for el in se:
                w = Part.Wire(el)
                wires.append(w)
            return Part.Compound(wires)
        
        w = Part.Wire(se[0])
        if not w.isClosed():
            debug("Closing open wire")
            w = wt.close(w)
        wires.append(w)
    f = Part.Face(wires)
    f.validate()
    if f.isValid():
        f.reverse()
        return f
    else:
        return Part.Compound(wires)

def map_shape(face, shape, transfer):
    """
    mapped_shape = map_shape(face, shapes, transfer)
    Maps the shape on the target face
    transfer is a nurbs rectangle that has the same parameters as the target face.
    shape is projected onto transfer, to get the 2D geometry.
    """
    proj = transfer.project(shape.Edges)
    new_edges = []
    for e in proj.Edges:
        try:
            c2d, fp, lp = transfer.curveOnSurface(e)
            ne = c2d.toShape(face.Surface, fp, lp)
            new_edges.append(ne)
        except TypeError:
            debug("Failed to get 2D curve")
    #sorted_edges = Part.sortEdges(new_edges)
    #wirelist = [Part.Wire(el) for el in sorted_edges]
    if len(new_edges) == 0:
        return []
    else:
        se = Part.sortEdges(new_edges)
        if len(se) > 1:
            wires = []
            for el in se:
                wires.append(Part.Wire(el))
            return Part.Compound(wires)
        else:
            return Part.Wire(se[0])
        #debug("wires has {} edges".format(len(nw.Edges)))
        #cleaned = nw.removeSplitter()
        #cleaned.sewShape()
        #debug("reduced to {} edges".format(len(cleaned.Edges)))
        #return cleaned

def map_shapes(shapes, face, transfer=None):
    """
    mapped_shapes = map_shapes(shapes, face, transfer)
    Maps the shapes on the target face
    transfer is a nurbs quad surface that has the same parameters as the target face.
    (see nurbs_tools.projection_quad)
    shapes are projected onto transfer, to get the 2D geometries.
    """
    def get_nurbs_rectangle(shapes):
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
        bs = Part.BSplineSurface()
        bs.setPole(1, 1, pts[0])
        bs.setPole(1, 2, pts[1])
        bs.setPole(2, 2, pts[2])
        bs.setPole(2, 1, pts[3])
        return bs

    u0, u1, v0, v1 = face.ParameterRange
    if transfer is None:
        transfer = get_nurbs_rectangle(shapes)
    transfer.setUKnots([u0, u1])
    transfer.setVKnots([v0, v1])
    transfer = transfer.toShape()
    
    mapped = []
    for sh in shapes:
        if isinstance(sh, Part.Face):
            ow = sh.OuterWire
            holes = []
            for w in sh.Wires:
                if not w.isSame(ow):
                    holes.append(w)
            mapped_ow = map_shape(face, ow, transfer)
            nf = Part.Face(face.Surface, mapped_ow)
            if not nf.isValid():
                nf.validate()
            if holes:
                mapped_holes = [map_shape(face, w, transfer) for w in holes]
                nf.cutHoles(mapped_holes)
                nf.validate()
            mapped.append(nf)
        else:
            mapped.append(map_shape(face, sh, transfer))
    return mapped
