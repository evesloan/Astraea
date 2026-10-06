"""Pure source preparation tests; no source/engine work."""
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
class SelectionAndGuards(unittest.TestCase):
    def test_selection_inventory_and_retention(self):
        from gate import gate
        g=gate();self.assertEqual(sum(a['triangles'] for a in g['assets']),9990)
        self.assertEqual(sum(len(a['mesh_parts'])+len(a['empty_objects']) for a in g['assets']),85)
    def test_fresh_path_guard(self):
        from gate import run_path
        for value in ['../escape','UPPER','some/path','x' * 62]:
            with self.assertRaises(AssertionError):run_path(value)
    def test_name_bijection(self):
        from gate import read,INPUTS
        from verify_east_gallery import godot_node_name
        for a in read(INPUTS)['assets']:
            names=a['mesh_parts']+a['empty_objects']
            self.assertEqual(names,[godot_node_name(n) for n in names])
            self.assertEqual(len(names),len(set(names)))
    def test_all_python_compiles_without_engine_import(self):
        import ast
        root=Path(__file__).resolve().parent
        for path in root.rglob('*.py'):
            if 'runs' not in path.parts:ast.parse(path.read_text(),filename=str(path))
if __name__ == '__main__': unittest.main()

