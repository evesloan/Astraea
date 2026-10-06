import unittest,math
from glyph_cap_retriangulate import repair_cap_triangles,_area
class CapRepair(unittest.TestCase):
    def test_exact_collinear_each_axis_and_reversed(self):
        flat=[(-1.,0.,0.),(0.,0.,0.),(1.,0.,0.),(0.,1.,0.)]
        for axis in range(3):
            v=[tuple(p[(i+axis)%3]*.07 for i in range(3)) for p in flat]
            for tri in [[(0,1,2),(0,2,3)],[(2,1,0),(3,2,0)]]:
                fixed,steps=repair_cap_triangles(v,tri)
                self.assertEqual(len(steps),1);self.assertEqual(len(fixed),len(tri))
                self.assertEqual(set(i for t in fixed for i in t),{0,1,2,3})
                self.assertTrue(all(_area(v,t)>1e-12 for t in fixed))
    def test_near_collinear_preserves_exact_area(self):
        v=[(-1.,0.,0.),(0.,-1e-14,0.),(1.,0.,0.),(0.,1.,0.)]
        fixed,steps=repair_cap_triangles(v,[(0,1,2),(2,3,0)])
        self.assertEqual(len(steps),1)
        self.assertAlmostEqual(sum(_area(v,t) for t in fixed),sum(_area(v,t) for t in [(0,1,2),(2,3,0)]))
    def test_already_valid_unchanged(self):
        v=[(0.,0.,0.),(1.,0.,0.),(0.,1.,0.)];tri=[(0,1,2)]
        self.assertEqual(repair_cap_triangles(v,tri),(tri,[]))
    def test_unrooted_boundary_fails(self):
        with self.assertRaises(ValueError):repair_cap_triangles([(-1.,0.,0.),(0.,0.,0.),(1.,0.,0.)],[(0,1,2)])
    def test_nonplanar_adjacent_surface_fails(self):
        with self.assertRaises(ValueError):repair_cap_triangles([(-1.,0.,0.),(0.,0.,0.),(1.,0.,0.),(0.,1.,.1)],[(0,1,2),(0,2,3)])
    def test_same_winding_shared_edge_fails(self):
        with self.assertRaises(ValueError):repair_cap_triangles([(-1.,0.,0.),(0.,0.,0.),(1.,0.,0.),(0.,1.,0.)],[(0,1,2),(2,0,3)])
if __name__=='__main__':unittest.main(verbosity=2)
