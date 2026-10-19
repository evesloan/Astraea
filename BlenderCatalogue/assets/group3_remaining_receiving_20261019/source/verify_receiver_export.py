import json,pathlib,struct,hashlib,collections
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=pathlib.Path(__file__).resolve().parents[4];P=R/'BlenderCatalogue/assets/group3_remaining_receiving_20261019';W=pathlib.Path(__file__).resolve().parent/'receiving_inputs';f=P/'exports/G3_REMAINING_BANK_RECEIVERS_r001.glb';b=f.read_bytes();ln=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+ln]);buf=b[28+ln:]
def acc(i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];dim={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];size=np.dtype(dtype).itemsize;off=v.get('byteOffset',0)+a.get('byteOffset',0);return np.ndarray((a['count'],dim),dtype=dtype,buffer=buf,offset=off,strides=(v.get('byteStride',size*dim),size)).copy()
polys=[];floor_nodes=[];wrong=[]
for n in g['nodes']:
 if 'mesh'not in n or n.get('extras',{}).get('category')!='floor':continue
 assert not any(k in n for k in ['matrix','translation','rotation','scale']);floor_nodes.append(n['name'])
 for p in g['meshes'][n['mesh']]['primitives']:
  v=acc(p['attributes']['POSITION']);ids=acc(p['indices']).ravel();tris=v[ids.reshape(-1,3)];norm=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);tops=np.max(np.abs(tris[:,:,1]-12),axis=1)<.0001
  for t,no in zip(tris[tops],norm[tops]):
   if no[1]<=0:wrong.append(n['name'])
   else:polys.append(Polygon(t[:,[0,2]]))
assert not wrong,wrong[:10];U=unary_union(polys);spec=json.load(open(P/'source/RECEIVERS.json'));expected=unary_union([Polygon(q['boundary'],q['holes'])for q in spec['parts']if q['category']=='floor']);assert U.difference(expected.buffer(.0001)).area<.000001;assert expected.difference(U.buffer(.0001)).area<.000001
prior=[]
for name in ['structural_meshes.json','received_structural_meshes.json']:
 for q in json.load(open(R/'Game/data/generated'/name))['regions']:
  if abs(q['floor_y']-12)<.002:prior.extend(Polygon(t)for t in q['triangles'])
for q in json.load(open(W/'ACTUAL_D03_RECEIVING.json'))['floor_parts']:prior.extend(Polygon(t)for t in q['triangles_xz'])
old=unary_union(prior);interior_overlap=U.intersection(old.buffer(-.001)).area;assert interior_overlap<1e-7;held=box(-78,167.25,-66,176.75);assert U.intersection(held).area<1e-7
report={'status':'PASS_INDEPENDENT_RECEIVER_SOURCE_EXPORT','glb_sha256':hashlib.sha256(b).hexdigest(),'native_sha256':hashlib.sha256((P/'source/G3_REMAINING_BANK_RECEIVERS_r001.blend').read_bytes()).hexdigest(),'runtime_floor_meshes':len(floor_nodes),'upward_top_triangles':len(polys),'wrong_top_winding':0,'exported_floor_m2':U.area,'planned_floor_m2':expected.area,'raw_symmetric_difference_m2':U.symmetric_difference(expected).area,'bidirectional_0_1mm_boundary_match':True,'existing_floor_overlap_beyond1mm_boundary_m2':interior_overlap,'held_C036_floor_added_m2':0,'registered_berths_or_room_ids_added':0,'runtime_and_visual_acceptance':False};(P/'qa/INDEPENDENT_RECEIVER_EXPORT.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
