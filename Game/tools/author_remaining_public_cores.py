"""Complete three public spine cores without consuming the fitted district courts."""
from pathlib import Path
import copy,json
from shapely.geometry import Polygon,box
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text())
def ring(p):return [list(v) for v in p.exterior.coords[:-1]]
layout=read('data/spatial_layout.json');base=read('data/architecture/FORWARD_PUBLIC_CORE.json')
records=read('data/reference/directory_allocations.json')['records']+read('data/reference/historical_guest_census.json')['guest_envelopes']+read('data/reference/D03_crew_envelopes.json')['records']
cores=[('fore_midship_public_core','ForeMidshipPublicCore_WIP','ForeMidshipPublicLift','FORE_MIDSHIP_PUBLIC_CORE.json',-272,-216,'fore_midship_vertical_core','Fore midship'),('aft_midship_public_core','AftMidshipPublicCore_WIP','AftMidshipPublicLift','AFT_MIDSHIP_PUBLIC_CORE.json',272,216,'aft_midship_vertical_core','Aft midship'),('aft_public_core','AftPublicCore_WIP','AftPublicLift','AFT_PUBLIC_CORE.json',432,432,'aft_vertical_core','Aft public core')]
owners={c[0] for c in cores}
layout['regions']=[v for v in layout['regions'] if v.get('authoring_owner') not in owners]
layout['voids']=[v for v in layout['voids'] if v.get('authoring_owner') not in owners]
for owner,root,lift_name,file,z,catchment,reservation,label in cores:
 foot=box(-7.8,z-13,7.8,z+20);physical=box(-7.88,z-13.04,7.88,z+20.04)
 assert all(physical.intersection(box(v['x'][0],v['z'][0],v['x'][1],v['z'][1])).area<1e-6 for v in records)
 assert Polygon(read('data/hull_envelope.json')['plan_xz_m']).buffer(-2).covers(physical)
 for v in layout['regions']:
  if any(key in v['id'] for key in ['fore_route','aft_route','fore_apron','aft_apron']):continue
  assert physical.intersection(Polygon(v['boundary'])).area<1e-6, (owner,v['id'])
 assert all(physical.intersection(Polygon(v['boundary'])).area<1e-6 for v in layout['voids'])
 shaft=box(-1.82,z-8.02,1.82,z-3.98);stairs=box(-3.1,z+4,3.1,z+14.7)
 for i in range(17):layout['regions'].append({'id':f'D{i+1:02}_{owner}_floor','authoring_owner':owner,'deck':f'D{i+1:02}','boundary':ring(foot),'holes':[],'priority':80,'thickness':.24,'material_role':'guest_floor','status':'Public travel platform; destination branches and final architecture unfinished'})
 layout['voids'] += [{'id':owner+'_lift','authoring_owner':owner,'decks':[f'D{i:02}' for i in range(1,18)],'boundary':ring(shaft),'source':'Authored seventeen-stop physical shaft; lower pit pan retains floor support'},{'id':owner+'_stairs','authoring_owner':owner,'decks':[f'D{i:02}' for i in range(2,18)],'boundary':ring(stairs),'source':'Sixteen actual switchbacks; lower base retained'}]
 d=copy.deepcopy(base);d.update(id=owner,core_reservation=reservation,root_name=root,persistent_id=owner+'_001',origin=[0,0,z],enclosure_file='AST-CIR-005_spine_core.glb',floor_boundary=ring(foot),lift_opening=ring(shaft),stair_opening=ring(stairs),lateral_portal_decks=[],lateral_portal_side=None,sign_x=-7.66,sign_yaw=1.5707963267948966,transport_catchment_z=catchment,planning_shift_m=z-catchment,scope='D01-D17 public spine connection. Sidewalls remain closed until supported branches are authored. Existing fitted courts and programme identities preserved.')
 d.pop('lateral_portal_z',None);d.pop('lateral_clear_height_m',None)
 d['lift'].update(name=lift_name,identity_prefix=owner,district_label=label,gate_origin_xz=[-1.8,z-6],shaft_outer_z=[z-8.2,z-3.8])
 for s in d['stairs']:s['origin']=[3,s['base_y'],z+4]
 (R/'data/architecture'/file).write_text(json.dumps(d,indent=2)+'\n')
(R/'data/spatial_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
print('Authored three D01-D17 spine cores; shifted midship cores preserve the fitted retail/aquatic courts')
