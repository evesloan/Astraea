from pathlib import Path
import sys,json,shutil,hashlib
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());sys.path.insert(0,str(W.parent));from glb_geometry import triangles
I=json.loads((W/'SOURCE_INTERFACE.json').read_text());T=R/'Game/source_derivatives/group4_theater_upper_20261012';T.mkdir(exist_ok=True)
for e in I['exports']:
 p=W/e['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'];shutil.copy2(p,T/p.name);e['policies']={n:x.get('collision_policy','static_trimesh_candidate') for n,t,x in triangles(p)}
I['model_root']='res://source_derivatives/group4_theater_upper_20261012/';I['source_blend_sha256']=hashlib.sha256((W/I['native']).read_bytes()).hexdigest();I['shared_root_or_registry_changed']=False
(R/'Game/data/architecture/GROUP4_THEATER_UPPER_SOURCE_CANDIDATE.json').write_text(json.dumps(I,indent=2)+'\n');print('THEATER_UPPER_RUNTIME_PREPARED',I['new_selected_mesh_count'],'source meshes,6 fixture light bindings;production false')
