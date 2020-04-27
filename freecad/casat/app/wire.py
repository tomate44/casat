# -*- coding: utf-8 -*-

__title__ = "Face module"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = """Various utilities working on wires"""

import FreeCAD as App
import FreeCADGui as Gui
import Part
vec2 = App.Base.Vector2d

debug("wire python module")

def close(w):
    "Close an open wire with a straight edge"
    e = Part.makeLine(w.OrderedVertexes[-1].Point, w.OrderedVertexes[0].Point)
    edges = w.Edges
    edges.append(e)
    return Part.Wire(Part.sortEdges(edges)[0])

class BoundarySorter:
    """Sort nested wires in order to build faces"""
    def __init__(self, wires):
        self.wires = []
        self.parents = []
        self.sorted_wires = []
        for w in wires:
            self.wires.append(w)
            self.parents.append([])
            self.sorted_wires.append([])
        self.done = False
    def check_inside(self):
        for i, w1 in enumerate(self.wires):
            for j, w2 in enumerate(self.wires):
                if not i == j:
                    if w2.BoundBox.isInside(w1.BoundBox):
                        self.parents[i].append(j)
    def sort_pass(self):
        to_remove = []
        for i,p in enumerate(self.parents):
            if (p is not None) and p == []:
                to_remove.append(i)
                self.sorted_wires[i].append(self.wires[i])
                self.parents[i] = None
        #print("Removing parents : {}".format(to_remove))
        for i,p in enumerate(self.parents):
            if (p is not None) and len(p) == 1:
                to_remove.append(i)
                self.sorted_wires[p[0]].append(self.wires[i])
                self.parents[i] = None
        #print("Removing full : {}".format(to_remove))
        if len(to_remove) > 0:
            for i,p in enumerate(self.parents):
                if (p is not None):
                    for r in to_remove:
                        if r in p:
                            p.remove(r)
        else:
            self.done = True
    def sort(self):
        self.check_inside()
        #print(self.parents)
        while not self.done:
            #print("Pass {}".format(i))
            self.sort_pass()
        result = []
        for w in self.sorted_wires:
            if w:
                result.append(w)
        return result
    def build_faces(self, surf=None):
        faces = []
        surf = surf or Part.Plane()
        #bs = BoundarySorter(wl)
        for wirelist in self.sort():
            #print(wirelist)
            f = Part.Face(surf, wirelist[0])
            f.validate()
            if len(wirelist) > 1:
                f.cutHoles(wirelist[1:])
                f.validate()
            faces.append(f)
        return faces
