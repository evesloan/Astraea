"""Read-only source screen. No engine, imports, installation, publication or archive extraction."""
from pathlib import Path
import hashlib,json,struct,zipfile
H=Path(__file__).resolve().parent; B=H.parent
G=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/Game')
I=B.parent/'sol_batch_intake_20261008/A'
def digest(b):return hashlib.sha256(b).hexdigest()
def doc(p):return json.loads(p.read_text())
def gltf(b):
 assert b[:4]==b'glTF' and struct.unpack_from('<I',b,4)[0]==2 and struct.unpack_from('<I',b,8)[0]==len(b)
 n=struct.unpack_from('<I',b,12)[0];assert b[16:20]==b'JSON';return json.loads(b[20:20+n])
def screen(j):
 assert not j.get('extensionsRequired') and not j.get('animations') and not j.get('cameras')
 assert not j.get('extensions',{}).get('KHR_lights_punctual')
 for obj in j.get('buffers',[])+j.get('images',[]):assert 'uri' not in obj
 assert all('camera' not in n and 'skin' not in n for n in j['nodes'])
 triangles=0
 for m in j['meshes']:
  for p in m['primitives']:
   assert p.get('mode',4)==4
   assert {'POSITION','NORMAL','TEXCOORD_0'} <= p['attributes'].keys()
   count=j['accessors'][p['indices']]['count'] if 'indices'in p else j['accessors'][p['attributes']['POSITION']]['count']
   assert count%3==0;triangles+=count//3
 return triangles
pins=doc(H/'INPUT_SHA256.json')
for path,sha in pins.items():assert digest(Path(path).read_bytes())==sha,path
m=doc(H/'runtime_manifest.proposed.json');old=doc(G/'data/architecture/CENTRAL_CROWN_RUNTIME.json');new=doc(H/'CENTRAL_CROWN_RUNTIME.proposed.json')
count=0;results=[]
for s in m['sections']:
 p=B/s['source_folder'];a=doc(p/'artifact_manifest.json');c=doc(p/'contract.json')
 with zipfile.ZipFile(I/s['archive_file']) as z:
  for f in a['files']:
   data=z.read(s['source_folder']+'/'+f['path']);assert len(data)==f['bytes'] and digest(data)==f['sha256'],f['path'];count+=1
  assert digest(z.read(s['source_folder']+'/source/native.blend'))==s['native_sha256']
  b=z.read(s['source_folder']+'/exports/'+s['model_file']);assert digest(b)==s['runtime_sha256']
  assert b==(p/'exports'/s['model_file']).read_bytes()
  j=gltf(b);triangles=screen(j);assert triangles==s['triangle_count'];assert len(j['meshes'])==s['mesh_count']
 predecessor=next(x for x in old['programmes'] if x['programme_key']==s['programme_key'])
 for k in ['boundary','floor_y','entry_xz','door_yaw','door_file']:assert c[k]==predecessor[k]
 assert s['existing_door'] in old['doors'];assert s['source_paths_xz']==c['paths'];assert s['source_views']==c['views']
 results.append({'programme_key':s['programme_key'],'triangles':triangles,'meshes':len(j['meshes']),'paths':len(s['source_paths_xz'])})
# No candidate floor ownership and exact old floor support; no compiler invocation.
compiled=doc(G/'data/generated/structural_meshes.json')
# Reuse pinned independent receiving coverage evidence; do not silently replace it
# with a sampled grid or claim a fresh polygon-union proof here.
for s in m['sections']:
 for owner in s['existing_floor_owners']:
  regions=[r for r in compiled['regions'] if r['id']==owner]
  assert len(regions)==1 and abs(regions[0]['floor_y']-106.5)<1e-6
assert not m['new_floor_regions'] and not m['new_doors'] and not m['new_lights'] and not m['new_catalogue_ids']
proof=doc(H/'RUNTIME_CONTRACT_INVERSE_PROOF.json');inverse=json.loads(json.dumps(new))
inverse.pop('runtime_model_file');inverse['export_sha256']=old['export_sha256']
for op in proof['changes']:
 if op['op']=='test':inverse['light_markers'][int(op['path'].split('/')[2])]['position']=op['value']
assert inverse==old
r=doc(H/'COMMON_MESH_ROSTER.json');v=B/'shared_fixture_variant'/m['common_model_file'];b=v.read_bytes();assert digest(b)==m['common_runtime_sha256']==new['export_sha256'];j=gltf(b)
active={n['name'] for n in j['nodes'] if 'mesh'in n};assert active==set(r['retained_cell_meshes']+r['relocated_fixture_meshes'])
assert len(active)==651 and len(r['retained_cell_meshes'])==631 and len(r['relocated_fixture_meshes'])==20
assert all(any(n.get('name')==name and 'mesh'not in n for n in j['nodes']) for name in r['retired_mesh_bindings_nodes_preserved'])
# Count only active primitive references, avoiding retained predecessor orphan meshes.
triangles=sum(j['accessors'][p['indices']]['count']//3 for n in j['nodes'] if 'mesh'in n for p in j['meshes'][n['mesh']]['primitives']);assert triangles==32724
for path,sha in pins.items():assert digest(Path(path).read_bytes())==sha,path
print(json.dumps({'status':'PASS static source screen only','pinned_inputs':len(pins),'archive_manifest_files_verified':count,'sections':results,'source_paths':sum(x['paths'] for x in results),'common_active_meshes':651,'common_triangles':triangles,'inverse_runtime_contract_exact':True,'live_pins_unchanged':True,'not_run':['Godot parse/import/runtime','Blender','renders','backups/publication'],'application':'BLOCKED pending independent r002 retention and root receiving gates'},indent=2))
