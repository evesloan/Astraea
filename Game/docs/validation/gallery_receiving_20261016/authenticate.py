from pathlib import Path
import json,struct,numpy as np,hashlib
R=Path('/workspace/Astraea');E=Path('/workspace/gallery-evidence')
def load(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def acc(j,b,k):
 a=j['accessors'][k];v=j['bufferViews'][a['bufferView']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]);n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.ndarray((a['count'],n),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*dt.itemsize),dt.itemsize))
a,ab=load(E/'retained_export.glb');b,bb=load(R/'Game/assets/models/D12_directory_07_entry_successor.glb');aa={n['name']:n for n in a['nodes']if'mesh'in n};ba={n['name']:n for n in b['nodes']if'mesh'in n};assert aa.keys()==ba.keys();changed=[]
for name,n in aa.items():
 m=ba[name];diff=[]
 for k in ['translation','rotation','scale','matrix']:
  if n.get(k)!=m.get(k):diff.append(k)
 ps=a['meshes'][n['mesh']]['primitives'];qs=b['meshes'][m['mesh']]['primitives'];assert len(ps)==len(qs)
 for p,q in zip(ps,qs):
  for key in set(p['attributes'])|set(q['attributes']):
   if key not in p['attributes']or key not in q['attributes']or not np.array_equal(acc(a,ab,p['attributes'][key]),acc(b,bb,q['attributes'][key])):diff.append(key)
  if 'indices'in p and 'indices'in q and not np.array_equal(acc(a,ab,p['indices']),acc(b,bb,q['indices'])):diff.append('indices')
 if diff:changed.append({'name':name,'fields':diff})
assert {v['name']for v in changed}=={'D12_directory_07__entry_left','D12_directory_07__entry_right'},changed
r=dict(status='PASS_ORIGINAL_AND_INSTALLED_CORRECTED_ENTRIES_DISTINGUISHED',source_nodes=len(aa),unchanged_nodes=len(aa)-len(changed),historical_entry_changes=changed,new_service_wall_original_unchanged='D12_directory_07__enclosure_1',source_native_sha256=hashlib.sha256((R/'Game/data/architecture/packages/d12_pair_sources/D12_directory_07/source/section_entry_successor.blend').read_bytes()).hexdigest());(E/'SOURCE_AUTHENTICATION.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
