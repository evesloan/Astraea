from pathlib import Path
import json,hashlib,shutil,sys
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());sys.path.insert(0,str(W.parent));from glb_geometry import triangles
P=json.loads((W/'SUCCESSOR_INTERFACE.json').read_text());T=R/'Game/source_derivatives/group4_aftmid_upper_20261012';T.mkdir(exist_ok=True);src=W/P['selected_model'];assert hashlib.sha256(src.read_bytes()).hexdigest()==P['selected_model_sha256'];shutil.copy2(src,T/src.name)
P.update(model_root='res://source_derivatives/group4_aftmid_upper_20261012/',policies={n:e.get('collision_policy','static_trimesh_candidate') for n,t,e in triangles(src)},replacement_scope='One source station012 instance only, unchanged room/capacity/stop/lift/root/registry; production false.')
(R/'Game/data/architecture/GROUP4_AFTMID_UPPER_SOURCE_CANDIDATE.json').write_text(json.dumps(P,indent=2)+'\n');print('AFTMID_RUNTIME_SOURCE_PREPARED',len(P['policies']),'members')
