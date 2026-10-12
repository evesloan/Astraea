from pathlib import Path
import json,hashlib,shutil,sys
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());sys.path.insert(0,str(W.parent));from glb_geometry import triangles
I=json.loads((W/'SOURCE_INTERFACE.json').read_text());T=R/'Game/source_derivatives/group4_station_information_20261012';T.mkdir(exist_ok=True);p=W/I['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==I['sha256'];shutil.copy2(p,T/p.name);parts=list(triangles(p));I['policies']={n:('no_collision_detail' if '_Opal' in n else 'fixed_original_gate_triangle_candidate') for n,t,e in parts};assert len(parts)==18
I.update(model_root='res://source_derivatives/group4_station_information_20261012/',source_blend_sha256=hashlib.sha256((W/I['native']).read_bytes()).hexdigest());(R/'Game/data/architecture/GROUP4_STATION_INFORMATION_SOURCE_CANDIDATE.json').write_text(json.dumps(I,indent=2)+'\n');print('G4_STATION_INFORMATION_RUNTIME_PREPARED18')
