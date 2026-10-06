"""Adversarial preparation tests only. No Blender/Godot or source export."""
import sys,copy,unittest
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from check_binary import check_storage,proven

def sample():
 p=np.array([[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]],[[1.,0.,0.],[1.,1.,0.],[0.,1.,0.]]]);normal=np.zeros_like(p);normal[:,:,2]=1
 return {'positions':p,'local_positions':p.copy(),'normals':normal,'uvs':p[:,:,:2].copy()}
class ArrayTests(unittest.TestCase):
 def test_identity(self):self.assertTrue(check_storage(sample(),sample())['complete_bijection'])
 def test_permuted_cyclic(self):
  source=sample();actual={k:np.roll(v[::-1],1,axis=1)for k,v in source.items()};self.assertTrue(check_storage(source,actual)['complete_bijection'])
 def test_reversed_winding_rejected(self):
  s=sample();a={k:v[:,::-1]for k,v in s.items()}
  with self.assertRaises(AssertionError):check_storage(s,a)
 def test_one_ulp_local_change_rejected(self):
  s=sample();a=copy.deepcopy(s);a['local_positions'][0,0,0]=float(np.nextafter(np.float32(0),np.float32(1)))
  with self.assertRaises(AssertionError):check_storage(s,a)
 def test_one_ulp_uv_change_rejected(self):
  s=sample();a=copy.deepcopy(s);a['uvs'][0,0,0]=float(np.nextafter(np.float32(0),np.float32(1)))
  with self.assertRaises(AssertionError):check_storage(s,a)
 def test_normal_rounding_rejected(self):
  s=sample();a=copy.deepcopy(s);a['normals'][0,0]=[1e-5,0,(1-1e-10)**.5]
  with self.assertRaises(AssertionError):check_storage(s,a)
 def test_triangle_loss_rejected(self):
  s=sample();a={k:v[:1]for k,v in s.items()}
  with self.assertRaises(AssertionError):check_storage(s,a)
 def test_duplicate_triangle_rejected(self):
  s=sample();a={k:np.repeat(v[:1],2,axis=0)for k,v in s.items()}
  with self.assertRaises(AssertionError):check_storage(s,a)
 def test_float32_uv_export_accepted(self):
  s=sample();s['uvs'][:,:,1]+=.12345679104328156;a=copy.deepcopy(s);a['uvs']=a['uvs'].astype(np.float32).astype(float);self.assertTrue(check_storage(s,a)['uvs_exact_float32_export'])
 def test_missing_attachment_semantic_rejected(self):
  with self.assertRaises(AssertionError):proven.compare_properties({'physical_fixture_lens':'INWARD_LENS'},{},'marker')
class MaterialTests(unittest.TestCase):
 def setUp(self):
  self.source={'name':'TestMetal','extras':{'material_family':'champagne_metal'},'double_sided':True,'nodes':[{'name':'Output','type':'OUTPUT_MATERIAL','active_output':True,'inputs':{}},{'name':'Principled','type':'BSDF_PRINCIPLED','inputs':{'Metallic':.72,'Roughness':.47,'Alpha':1.,'Base Color':[1.,1.,1.,1.],'Emission Strength':.45,'Emission Color':[1.,.86,.65,1.]}},{'name':'Image','type':'TEX_IMAGE','image':{'projection':'FLAT','colorspace':'sRGB','packed_sha256':'a'*64,'size':[256,256],'extension':'REPEAT','interpolation':'Linear'}}],'links':[['Principled','BSDF','Output','Surface'],['Image','Color','Principled','Base Color']]}
  self.decoded={'doc':{'materials':[{'name':'TestMetal','extras':{'material_family':'champagne_metal'},'doubleSided':True,'pbrMetallicRoughness':{'metallicFactor':.72,'roughnessFactor':.47,'baseColorTexture':{'index':0}},'emissiveFactor':[.45,.387,.2925]}],'textures':[{'source':0}]},'images':[{'sha256':'a'*64,'size':[256,256]}]}
 def test_source_material_model_passes(self):proven.material_check(self.source,0,self.decoded)
 def test_material_factor_edit_rejected(self):
  self.decoded['doc']['materials'][0]['pbrMetallicRoughness']['metallicFactor']=.5
  with self.assertRaises(AssertionError):proven.material_check(self.source,0,self.decoded)
 def test_emission_edit_rejected(self):
  self.decoded['doc']['materials'][0]['emissiveFactor']=[0,0,0]
  with self.assertRaises(AssertionError):proven.material_check(self.source,0,self.decoded)
 def test_texture_byte_change_rejected(self):
  self.decoded['images'][0]['sha256']='b'*64
  with self.assertRaises(AssertionError):proven.material_check(self.source,0,self.decoded)
 def test_uv_transform_rejected(self):
  self.decoded['doc']['materials'][0]['pbrMetallicRoughness']['baseColorTexture']['extensions']={'KHR_texture_transform':{'offset':[.1,0]}}
  with self.assertRaises(AssertionError):proven.material_check(self.source,0,self.decoded)
if __name__=='__main__':unittest.main(verbosity=2)
