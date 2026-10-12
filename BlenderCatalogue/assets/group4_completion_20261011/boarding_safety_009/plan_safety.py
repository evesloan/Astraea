from pathlib import Path
import json,hashlib,math,sys
import numpy as np
W=Path(__file__).resolve().parent;R=W.parents[3];sys.path.insert(0,str(W.parent))
from glb_geometry import triangles
P=json.loads((R/'Game/data/architecture/GROUP4_COMPLETION_CANDIDATE.json').read_text())
cat=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text())
ids=['AST-TRM-G4-024','AST-TRM-G4-025','AST-TRM-G4-026']
assert not any(i in json.dumps(cat) for i in ids),'Source identity already owned'
body=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/AST-TRM-G4-011_cart_tram_component.glb'
cuts=[]
for name,t,x in triangles(body):
 if 'Tram_PortPocket_' not in name and 'Tram_Door_Post_' not in name:continue
 side=1 if t[:,:,0].mean()>0 else -1
 bands=[[1.055,1.07875],[1.0893,1.1225]]
 if side<0:bands=[[-b,-a] for a,b in bands]
 cuts.append(dict(mesh=name,source_min=t.min(axis=(0,1)).tolist(),source_max=t.max(axis=(0,1)).tolist(),
   slot_boxes_xyz=[[a,.020,-1.800,b,2.497,1.800] for a,b in bands],
   reason='Two preserved-width sliding leaf channels; outside skin/geometry and UV retained'))
assert len(cuts)==8
mounts=[]
for s in P['stations']:
 yaw=0 if s['vehicle_door_side']=='port' else math.pi
 origin=[s['boarding_edge_x'],56.1,s['physical_docking_z']]
 mounts.append(dict(station=s['label'],origin=origin,yaw=yaw,
   gate_local_origin=[-.32,0,0],gate_local_yaw=math.pi/2,gate_scale=[2.18/2.4,2.41/2.65,1.0],
   retained_portal_width_m=2.22,nominal_gate_clear_width_m=2.18,gate_clear_header_m=2.41,
   floor_receiver='retained '+s['asset'],root_authority='Shared single tram docking authority; default shut'))
plan=dict(schema='astraea.group4.boarding_safety.source.v1',active=False,whole_group_complete=False,
 prior_checkpoint='02a25202c1331f7db0ea9834ccec468b12ba5fbb',ids=ids,
 vehicle_original=str(body.relative_to(R)),vehicle_successor='AST-TRM-G4-024_powered_portal_body_r001.glb',
 vehicle_cuts=cuts,vehicle_unchanged_mesh_count=31,
 vehicle_gate_placements=[dict(side='PORT',origin=[-1.08,0,0],yaw=-math.pi/2,scale=[2.33/2.4,2.51/2.65,.65]),dict(side='STARBOARD',origin=[1.08,0,0],yaw=math.pi/2,scale=[2.33/2.4,2.51/2.65,.65])],
 station_mounts=mounts,station_receiver_asset='AST-TRM-G4-025_boarding_barrier_receivers_r003.glb',
 restraint_asset='AST-TRM-G4-026_cart_restraint_hardware_r003.glb',
 restraint_dock=[0,0,.15],clamp_open_inner_x=.490,clamp_closed_inner_x=.351,
 clamp_stroke_m=.139,cart_side_chassis_x=.350,closed_nominal_cart_clearance_m=.001,
 limits=['Source dimensions and mounting contacts do not prove engineering or mechanical capacity',
 'Powered gate adaptation and bridge sequencing require scoped actual physics checks',
 'No moving tram, second cart, stock/refill/save provider or shared root edit',
 'Vehicle channels are a new immutable successor; original011 remains unchanged',
 'Cart hardware may move without forcing, snapping, reparenting or respawning the existing cart'])
(W/'SAFETY_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('PLANNED',len(cuts),'bounded source channels; five original gate adaptations and four clamp positions')
