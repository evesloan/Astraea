from pathlib import Path
import json,hashlib,shutil,sys
W=Path(__file__).resolve().parent;R=W.parents[3];sys.path.insert(0,str(W.parent))
from glb_geometry import triangles
P=json.loads((W/'SAFETY_PLAN.json').read_text());I=json.loads((W/'TERMINAL_INTERFACE.json').read_text())
T=R/'Game/source_derivatives/group4_boarding_safety_20261011';T.mkdir(parents=True,exist_ok=True)
models=[]
for role,name in [('vehicle',P['vehicle_successor']),('barrier_receivers',P['station_receiver_asset']),('restraint',P['restraint_asset']),('terminals',I['asset'])]:
 p=W/name;assert p.exists(),p;shutil.copy2(p,T/name)
 policies={n:e.get('collision_policy','static_trimesh_candidate') for n,t,e in triangles(p)}
 models.append({'role':role,'file':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'policies':policies})
shutil.copy2(W/'VEHICLE_COLLISION_PROPOSAL.json',T/'VEHICLE_COLLISION_PROPOSAL.json')
if 'AST-TRM-G4-027' not in P['ids']:P['ids'].append('AST-TRM-G4-027')
P.update(terminal_active=False,models=models,terminal_interface=I,model_root='res://source_derivatives/group4_boarding_safety_20261011/',
 existing_gate_model_sha256=hashlib.sha256((R/'Game/assets/models/AST-DOR-003.glb').read_bytes()).hexdigest(),
 source_operation='Five standard gate bindings and bridge sequencing; two scaled powered car portals; four clamp mechanisms. Actual tram travel/cart restraint joint/save remain open.')
(R/'Game/data/architecture/GROUP4_BOARDING_SAFETY_CANDIDATE.json').write_text(json.dumps(P,indent=2)+'\n')
print('SAFETY_RUNTIME_PREPARED',len(models),'pinned models; five barrier roots, two vehicle doors, four mechanisms and two terminals')
