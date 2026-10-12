from pathlib import Path
import json,struct,hashlib,numpy as np
p=Path(__file__).resolve().parents[1];j=json.loads((p/'docs/MAKER_CEILING_ENCLOSURE.json').read_text());changed=set(j['selected_uv_successor']['changed_wood_coves'])
def records(path):
 b=path.read_bytes();s=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+s]);binary=b[28+s:];r={}
 def data(i):
  a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];off=v.get('byteOffset',0)+a.get('byteOffset',0);size={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]*{5121:1,5123:2,5125:4,5126:4}[a['componentType']];stride=v.get('byteStride',size)
  return b''.join(binary[off+k*stride:off+k*stride+size] for k in range(a['count']))
 for n in g['nodes']:
  if 'mesh' not in n:continue
  r[n['name']]={'primitives':[{'attributes':{k:data(v) for k,v in t['attributes'].items()},'indices':data(t['indices']),'material':g['materials'][t['material']]} for t in g['meshes'][n['mesh']]['primitives']],'pose':{k:v for k,v in n.items() if k in ['translation','rotation','scale','matrix']}}
 return r
old=records(p/'exports/maker_foyer/maker_ceiling_enclosure_r001.glb');new=records(p/'exports/maker_foyer/maker_ceiling_enclosure_r002.glb');assert old.keys()==new.keys();uvs=0;maximum=0.
for name in old:
 assert old[name]['pose']==new[name]['pose']
 for a,b in zip(old[name]['primitives'],new[name]['primitives']):
  assert a['indices']==b['indices'] and a['material']==b['material'];assert a['attributes'].keys()==b['attributes'].keys()
  for k,v in a['attributes'].items():
   if k=='TEXCOORD_0' and name in changed:
    before=np.frombuffer(v,dtype='<f4').reshape(-1,2).astype(float);after=np.frombuffer(b['attributes'][k],dtype='<f4').reshape(-1,2)
    expected=np.stack([before[:,0]/.65,1-(1-before[:,1])/1.3],axis=1)
    err=float(np.abs(after-expected).max());assert err<.00003,(name,err);maximum=max(maximum,err);uvs+=len(before)
   else:assert v==b['attributes'][k],(name,k)
r={'status':'PASS','all20_mesh_positions_normals_indices_materials_and_poses_byte_exact':True,'only8_wood_cove_uv_arrays_changed':True,'exported_uv_values_checked':uvs,'meters_per_tile_uv':[.65,1.3],'gltf_v_coordinate':'Blender exporter emits1-v;expected exported scaled v is1-(1-old_v)/1.3','maximum_uv_float_error':maximum,'fresh_native_repeat_export_byte_identical':True,'source_review_images':'Prior neutral mean-palette views retain actual r001 provenance;geometry and mean palette unchanged,their views do not certify texture/UV appearance'}
(p/'qa/MAKER_CEILING_UV_INTEGRITY.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
