"""Adversarial unit cases for the independent pure-math review predicates."""
import ast, sys, math, collections
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/375c2e438292/pool-market-stock');sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
from geometry import *
import numpy as np
from shapely.geometry import Polygon,Point
from shapely import constrained_delaunay_triangles
TOL=5e-5
src=ast.parse(Path(__file__).with_name('review_finish.py').read_text());exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<pure_review_predicates>','exec'))
def cube(name,lo,hi):
 v=[(x,y,z)for y in [lo[1],hi[1]]for x,z in [(lo[0],lo[2]),(hi[0],lo[2]),(hi[0],hi[2]),(lo[0],hi[2])]];faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];p=record(name,v,[t for f in faces for t in triang_face(v,f)]);p['ta']=np.array(p['triangles']);p['tmin']=p['ta'].min(axis=1);p['tmax']=p['ta'].max(axis=1);return p
A=cube('unit',(0,0,0),(1,1,1));assert topology(A)['closed_after_coordinate_weld'];assert not topology(A)['degenerate_triangles'];assert strict_inside((.5,.5,.5),A);assert not strict_inside((0,.5,.5),A);assert not strict_inside((-0.01,.5,.5),A)
assert not contact_pair(A,cube('clear',(1.1,0,0),(2,1,1)))['touch']
x=contact_pair(A,cube('touch',(1,0,0),(2,1,1)));assert x['touch']and not x['penetration']
assert contact_pair(A,cube('penetrate',(.999,0,0),(2,1,1)))['penetration']
assert contact_pair(A,cube('identical',(0,0,0),(1,1,1)))['penetration']
assert contact_pair(A,cube('contained',(.2,.2,.2),(.8,.8,.8)))['penetration']
assert cone_triangle((0,0,0),(0,1,0),62,[(-1,.03,-1),(1,.03,-1),(0,.03,1)])is not None
assert cone_triangle((0,0,0),(0,1,0),62,[(-1,-.03,-1),(1,-.03,-1),(0,-.03,1)])is None
assert cone_triangle((0,0,0),(0,1,0),62,[(1,.03,0),(1,.04,0),(1,.03,1)])is None
assert cone_triangle((0,0,0),(0,1,0),62,[(-1,.061,-1),(1,.061,-1),(0,.061,1)])is None
print('PASS: topology, boundary/strict containment, disjoint/tangent/1mm/contained solids, finite-cone enclosure/behind/outside/far clipping')
