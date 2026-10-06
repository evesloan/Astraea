import sys
sys.dont_write_bytecode=True
import unittest,copy
import numpy as np
from glb_equivalence import match_triangles
class CornerEquivalence(unittest.TestCase):
    def setUp(self):
        self.e=dict(positions=[[[0,0,0],[1,0,0],[0,1,0]],[[0,0,1],[1,0,1],[0,1,1]]],uvs=[[[0,0],[1,0],[0,1]],[[.1,.2],[.8,.1],[.2,.9]]],normals=[[[0,0,1]]*3,[[0,0,1]]*3])
    def test_reordered_cyclic_corners(self):
        a={k:np.roll(np.asarray(v)[::-1],1,axis=1).tolist() for k,v in self.e.items()};self.assertEqual(match_triangles(self.e,a)['triangles'],2)
    def test_reversed_winding_is_rejected(self):
        a={k:np.asarray(v)[:,::-1].tolist() for k,v in self.e.items()}
        with self.assertRaises(AssertionError):match_triangles(self.e,a)
    def test_uv_damage_is_rejected(self):
        a=copy.deepcopy(self.e);a['uvs'][0][0][0]+=.00001
        with self.assertRaises(AssertionError):match_triangles(self.e,a)
    def test_normal_damage_is_rejected(self):
        a=copy.deepcopy(self.e);a['normals'][0][0]=[0,0,-1]
        with self.assertRaises(AssertionError):match_triangles(self.e,a)
    def test_fixed_geometry_tolerance(self):
        a=copy.deepcopy(self.e);a['positions'][0][0][0]+=1.5e-6;self.assertGreater(match_triangles(self.e,a)['max_position_deviation_m'],0);a['positions'][0][0][0]+=1e-6
        with self.assertRaises(AssertionError):match_triangles(self.e,a)
    def test_duplicate_triangle_cannot_cover_missing_triangle(self):
        a={k:[copy.deepcopy(v[0]),copy.deepcopy(v[0])] for k,v in self.e.items()}
        with self.assertRaises(AssertionError):match_triangles(self.e,a)
if __name__=='__main__':unittest.main()
