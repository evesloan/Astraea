from pathlib import Path
import sys,json,shutil,hashlib
import numpy as np
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());sys.path.insert(0,str(W.parent));from glb_geometry import triangles
I=json.loads((W/'SOURCE_INTERFACE.json').read_text());T=R/'Game/source_derivatives/group4_controls_20261012';T.mkdir(exist_ok=True);allparts={}
for item in I['exports']:
 p=W/item['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'];shutil.copy2(p,T/p.name);data=list(triangles(p));item['policies']={n:('no_collision_detail' if 'OpalFace' in n or 'OpalLens' in n else ('existing_vehicle_convex_candidate' if item['id']=='AST-TRM-G4-034' else 'fixed_original_gate_triangle_candidate')) for n,t,e in data};allparts.update({n:t for n,t,e in data})
for button in I['car_buttons']+[I['station_call_button']]:
 points=np.unique(allparts[button['source_mesh']].reshape(-1,3),axis=0);axis=np.array(button['axis_xyz']);projection=points@axis;face=points[np.abs(projection-projection.max())<2e-6];assert len(face)>=8;center=face.mean(0);button['surface_center_xyz']=center.tolist();button['target_points_xyz']=[(p-center+axis*depth).tolist() for depth in [-.0003,.0003] for p in face];button['target_face_vertices']=len(face);button['exact_export_face_polygon']=True
I.update(model_root='res://source_derivatives/group4_controls_20261012/',source_blend_sha256=hashlib.sha256((W/I['native']).read_bytes()).hexdigest(),original_runtime_pins={'res://scripts/player.gd':hashlib.sha256((R/'Game/scripts/player.gd').read_bytes()).hexdigest(),'res://assets/models/AST-DOR-003.glb':hashlib.sha256((R/'Game/assets/models/AST-DOR-003.glb').read_bytes()).hexdigest()})
(R/'Game/data/architecture/GROUP4_OPERATING_CONTROLS_SOURCE_CANDIDATE.json').write_text(json.dumps(I,indent=2)+'\n');print('G4_CONTROL_RUNTIME_PREPARED',I['mesh_count'],'members;9 exact source button face polygons;source active false')
