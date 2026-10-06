"""Small adversarial checks for independent preflight predicates; no Blender."""
import sys
sys.dont_write_bytecode=True
import unittest
import numpy as np
from check_planned_contacts import triangles,surface,inside,hit
from check_contract import in_polygon,in_box
class Predicates(unittest.TestCase):
    def setUp(self):
        self.box=triangles(dict(vertices=[[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]))
    def test_actual_closed_volume(self):
        self.assertTrue(inside(self.box,np.array([.2,.3,.4])));self.assertFalse(inside(self.box,np.array([1.01,0,0])))
    def test_surface_is_not_aabb(self):
        tri=np.array([[[0,0,0],[1,0,0],[0,1,0]]],float);self.assertTrue(surface(tri,[.2,.2,0]));self.assertFalse(surface(tri,[.8,.8,0]));self.assertFalse(surface(tri,[.2,.2,.001]))
    def test_segment_extent(self):
        self.assertTrue(hit(self.box,[-2,0,0],[2,0,0]));self.assertFalse(hit(self.box,[-2,0,0],[-1.1,0,0]));self.assertFalse(hit(self.box,[-2,1.1,0],[2,1.1,0]))
    def test_octagon_chamfer_rejects_rectangle_corner(self):
        poly=[[-.8,-1],[.8,-1],[1,-.8],[1,.8],[.8,1],[-.8,1],[-1,.8],[-1,-.8]];self.assertTrue(in_polygon([0,0],poly));self.assertFalse(in_polygon([.99,.99],poly));self.assertTrue(in_polygon([.90,.85],poly))
    def test_reservation_height_cut(self):
        low=[[-1,0,-1],[1,.42,1]];high=[[0,.42,-1],[1,2,1]];self.assertTrue(in_box([-.5,.40,0],low));self.assertFalse(in_box([-.5,.43,0],low));self.assertFalse(in_box([-.5,.43,0],high))
if __name__=='__main__':unittest.main()
