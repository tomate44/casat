from freecad.casat import *
debug("edge python module")

class Edge(object):
    "Edge class"
    def __init__(self):
        pass

def scale_edge(edge, factor=1.0):
    fp, lp = edge.ParameterRange
    new_range = (lp - fp) * factor
    return edge.Curve.toShape(fp, fp + new_range)

def get_diff(edge1, edge2, nb_samples=100, factor=1.0):
    tol = 1e-7
    edges = []
    for p in edge1.discretize(nb_samples):
        d, pts, info = Part.Vertex(p).distToShape(edge2)
        if d > tol:
            e = Part.makeLine(*pts[0])
            edges.append(scale_edge(e, factor * edge1.Length))
    return Part.Compound(edges)

def max_diff(edge1, edge2, nb_samples=100, factor=0.5):
    max_dist = 0.0
    max_pts = None
    for p in edge1.discretize(nb_samples):
        d, pts, info = Part.Vertex(p).distToShape(edge2)
        if max_dist < d:
            max_dist = d
            max_pts = pts[0]
    print("Maximum distance : {} at {}".format(max_dist, max_pts[0]))
    e = Part.makeLine(*max_pts)
    return scale_edge(e, factor * edge1.Length)

def approximate(edge, nb_samples=20, tol=1e-3)
