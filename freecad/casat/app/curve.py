# -*- coding: utf-8 -*-

__title__ = "Curve module"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = """Various utilities working on curves"""

import FreeCAD as App
import FreeCADGui as Gui
from freecad.casat import *
import Part
from . import nurbs_tools
from .nurbs_tools import parameterization
import numpy as np
vec2 = App.Base.Vector2d

debug("curve python module")

class Curve:
    "Curve class"
    def __init__(self):
        self.curve = None
    
class InterpolationCurve(Curve):
    "BSpline curve that interpolates a list of constraints"
    
    def __init__(self, constraints=[]):
        self.degree = 1
        self.constraints = constraints
        self.parameters = 1.0
        self.poles = []
        
    @property
    def constraints(self):
        return self._constraints
    
    @constraints.setter
    def constraints(self, cons):
        self._constraints = []
        self._params = []
        self._num_constraints = 0
        self._num_points = 0
        for c in cons:
            if isinstance(c,(list,tuple)):
                self._constraints.append(c)
                self._num_constraints += len(c)
            else:
                self._constraints.append([c,])
                self._num_constraints += 1
            self._num_points += 1

    @property
    def parameters(self):
        return self._params
    
    @parameters.setter
    def parameters(self, par):
        self._params = []
        if isinstance(par,(list,tuple)) and (len(par) == self._num_points):
            self._params = par
        elif (par >= 0.) and (par <= 1.):
            self._params = parameterization(self.get_points(), par)
        elif par == "Chordlength":
            self.parameters = 1.0
        elif par == "Centripetal":
            self.parameters = 0.5
        else: # default "Uniform"
            self.parameters = 0.0
        para = [p/self._params[-1] for p in self._params]
        self._params = para
    
    def get_points(self):
        pts = []
        for c in self._constraints:
            pts.append(c[0])
        return pts            
    
    def compute(self):
        num_poles = self._num_constraints
        num_interior_knots = num_poles - self.degree - 1
        start = [0.] * (self.degree + 1)
        end = [1.] * (self.degree + 1)
        mid = [(i+1)/(num_interior_knots+1) for i in range(num_interior_knots)]
        self.flatknots = start + mid + end
        #knots = list(set(self.flatknots))
        bb = nurbs_tools.BsplineBasis()
        bb.knots = self.flatknots
        bb.degree = self.degree
        matrix  = list()
        vecs = list()
        for c,p in zip(self._constraints, self._params):
            for i,v in enumerate(c):
                matrix.append(bb.evaluate(p,d=i))
                vecs.append(v)
        mat = np.array(matrix)
        print("Coeff matrix :\n%s\n"%np.array(mat))
        res = np.linalg.solve(mat,vecs)
        print("Control points :\n%s\n"%res)
        self.poles = [App.Vector(s) for s in res]

    def get_curve(self):
        if len(self.poles) == 0:
            self.compute()
        knots = list(set(self.flatknots))
        knots.sort()
        mults = [self.flatknots.count(k) for k in knots]
        bs = Part.BSplineCurve()
        bs.buildFromPolesMultsKnots(self.poles, mults, knots, False, self.degree)
        self.curve = bs
        return bs

    def get_edge(self):
        return self.get_curve().toShape()

    def show(self):
        Part.show(self.get_edge())
