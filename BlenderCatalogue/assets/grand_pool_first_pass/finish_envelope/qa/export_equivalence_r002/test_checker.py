"""Small adversarial pure-Python tests. No Blender, engine or source mutation."""
import copy, unittest, json
from pathlib import Path
import numpy as np
import check_glb as c

def mesh():
    p=np.array([[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]],[[1.,0.,0.],[1.,1.,0.],[0.,1.,0.]]])
    uv=p[:,:,:2].copy();n=np.zeros_like(p);n[:,:,2]=1
    return dict(positions=p,local_positions=p.copy(),normals=n,uvs=uv)

class MatcherTest(unittest.TestCase):
    def test_identity(self):self.assertEqual(c.match_triangles(mesh(),mesh())['triangles'],2)
    def test_permuted_cyclic_corners(self):
        m=mesh();a={k:np.roll(v[::-1],1,axis=1) for k,v in m.items()}
        self.assertTrue(c.match_triangles(m,a)['complete_bijection'])
    def test_reverse_winding_rejected(self):
        m=mesh();a={k:v[:,::-1] for k,v in m.items()}
        with self.assertRaises(AssertionError):c.match_triangles(m,a)
    def test_uv_swap_rejected(self):
        m=mesh();a=copy.deepcopy(m);a['uvs'][0]=a['uvs'][0][::-1]
        with self.assertRaises(AssertionError):c.match_triangles(m,a)
    def test_uv_one_ulp_edit_rejected(self):
        m=mesh();a=copy.deepcopy(m);a['uvs'][0,0,0]=float(np.nextafter(np.float32(0),np.float32(1)))
        with self.assertRaises(AssertionError):c.match_triangles(m,a)
    def test_normal_rounding_rejected(self):
        m=mesh();a=copy.deepcopy(m);a['normals'][0,0]=[1e-5,0,(1-1e-10)**.5]
        with self.assertRaises(AssertionError):c.match_triangles(m,a)
    def test_triangle_loss_rejected(self):
        m=mesh();a={k:v[:1] for k,v in m.items()}
        with self.assertRaises(AssertionError):c.match_triangles(m,a)
    def test_duplicate_triangle_rejected(self):
        m=mesh();a={k:np.repeat(v[:1],2,axis=0) for k,v in m.items()}
        with self.assertRaises(AssertionError):c.match_triangles(m,a)
    def test_sub_limit_local_vertex_edit_rejected(self):
        m=mesh();a=copy.deepcopy(m);a['positions'][0,0,0]+=1e-5;a['local_positions'][0,0,0]+=1e-5
        with self.assertRaises(AssertionError):c.match_triangles(m,a)
    def test_hash_boundary_not_used(self):
        m=mesh();a=copy.deepcopy(m);delta=1e-10
        m['positions']+=delta;a['positions']-=delta
        self.assertTrue(c.match_triangles(m,a)['complete_bijection'])
    def test_float32_uv_rounding_only(self):
        m=mesh();m['uvs'][:,:,1]=[1-256.1234436035156,1-.12345679104328156,1+510.1234436035156]
        a=copy.deepcopy(m);a['uvs']=a['uvs'].astype(np.float32).astype(float)
        self.assertTrue(c.match_triangles(m,a)['uvs_exact_float32_export'])

class SourceMaterialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_pool_first_pass/finish_envelope')
        cls.source=json.loads(Path(__file__).with_name('envelope_snapshot001.json').read_text())
        cls.glb=c.decode(root/'exports/AST-AQU-016_finish_envelope.glb')
        cls.material=cls.source['materials']['ASTRAEA_warm_walnut']
        cls.index=next(i for i,m in enumerate(cls.glb['doc']['materials']) if m['name']==cls.material['name'])
    def test_actual_material_passes(self):c.material_check(self.material,self.index,self.glb)
    def test_metallic_edit_rejected(self):
        g=copy.deepcopy(self.glb);g['doc']['materials'][self.index]['pbrMetallicRoughness']['metallicFactor']=.1
        with self.assertRaises(AssertionError):c.material_check(self.material,self.index,g)
    def test_emission_edit_rejected(self):
        g=copy.deepcopy(self.glb);g['doc']['materials'][self.index]['emissiveFactor']=[.1,.1,.1]
        with self.assertRaises(AssertionError):c.material_check(self.material,self.index,g)
    def test_texture_transform_rejected(self):
        g=copy.deepcopy(self.glb);g['doc']['materials'][self.index]['pbrMetallicRoughness']['baseColorTexture']['extensions']={'KHR_texture_transform':{'offset':[.1,0]}}
        with self.assertRaises(AssertionError):c.material_check(self.material,self.index,g)
    def test_image_replacement_rejected(self):
        g=copy.deepcopy(self.glb)
        for im in g['images']:im['sha256']='0'*64
        with self.assertRaises(AssertionError):c.material_check(self.material,self.index,g)
    def test_marker_property_removed_rejected(self):
        with self.assertRaises(AssertionError):c.compare_properties({'physical_lens':'x'},{},'marker')

if __name__=='__main__':unittest.main(verbosity=2)
