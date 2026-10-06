"""Prepared pure tests; no source/engine work. Run only when parent reviews stage."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import copy, unittest
import numpy as np
from provenance_match import match_with_provenance

class ExactProvenanceTests(unittest.TestCase):
    def source(self):
        p = np.array([[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]],[[2.,0.,0.],[3.,0.,0.],[2.,1.,0.]]])
        return dict(positions=p, local_positions=p.copy(), normals=np.tile([0.,0.,1.], (2,3,1)), uvs=np.array([[[0.,0.],[1.,0.],[0.,1.]],[[0.,0.],[1.,0.],[0.,1.]]]))
    def test_permuted_triangles_cyclic_corners(self):
        s = self.source(); a = {k: np.roll(v[::-1], 1, axis=1) for k,v in s.items()}; r = match_with_provenance(s,a)
        self.assertEqual([x['source_triangle'] for x in r['triangle_correspondence']], [1,0]); self.assertTrue(r['complete_bijection'])
    def test_duplicate_lost_triangle_fails(self):
        s = self.source(); a = {k:v[[0,0]] for k,v in s.items()}
        with self.assertRaises(AssertionError): match_with_provenance(s,a)
    def test_reversed_winding_fails(self):
        s = self.source(); a = {k:v[:,::-1] for k,v in s.items()}
        with self.assertRaises(AssertionError): match_with_provenance(s,a)
    def test_corner_uv_change_fails(self):
        s = self.source(); a = copy.deepcopy(s); a['uvs'][0,1,0] += .0001
        with self.assertRaises(AssertionError): match_with_provenance(s,a)
    def test_normal_change_fails(self):
        s = self.source(); a = copy.deepcopy(s); a['normals'][0,1] = [0,1,0]
        with self.assertRaises(AssertionError): match_with_provenance(s,a)
    def test_small_shape_change_still_fails_local(self):
        s = self.source(); a = copy.deepcopy(s); a['positions'][0,0,0] += 1e-6; a['local_positions'][0,0,0] += 1e-6
        with self.assertRaises(AssertionError): match_with_provenance(s,a)
    def test_exact_duplicate_triangles_bijective(self):
        s = self.source(); s = {k:v[[0,0]] for k,v in s.items()}; r = match_with_provenance(s,s)
        self.assertEqual({x['source_triangle'] for x in r['triangle_correspondence']}, {0,1})
    def test_nonfinite_fails(self):
        s = self.source(); a = copy.deepcopy(s); a['positions'][0,0,0] = np.nan
        with self.assertRaises((AssertionError, ValueError)): match_with_provenance(s,a)
if __name__ == '__main__': unittest.main()
