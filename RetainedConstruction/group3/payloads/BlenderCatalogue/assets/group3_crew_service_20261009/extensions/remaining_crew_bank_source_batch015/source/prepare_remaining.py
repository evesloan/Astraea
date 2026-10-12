"""Rigid construction in anonymous surviving atlas envelopes; no inferred room-ID adoption."""
from pathlib import Path
import json,hashlib,math
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
FIRST=HERE.parent.parent;PRIOR=HERE.parent/'labelled_crew_bank_batch014'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=json.load(open(PRIOR/'source/LABELLED_BANK_CONTRACT.json'))
old=json.load(open(FIRST/'source/CREW_BANK_PLACEMENTS_PROPOSAL.json'))
original=json.load(open(FIRST/'source/CREW_BANK_HOME.json'))
remaining=[q for q in old['instances']if q['identity_join_status']!='exact_labelled_atlas_detail'and q['physical_rest_places']==2]
held=[q for q in old['instances']if q['physical_rest_places']!=2]
assert len(remaining)==183 and len(held)==1 and held[0]['proposed_retained_room_id']=='C036'
instances=[];surfaces=[];fixtures=[];doors=[]
def transform(q,p):
 c=math.cos(q['yaw']);s=math.sin(q['yaw']);x,y,z=q['position'];a,b,d=p
 return [x+c*a+s*d,y+b,z-s*a+c*d]
# Original measured rest heights from batch014 are invariant under a rigid room pose.
reference=next(q for q in base['instances']if q['reference_room_id']=='C118')
def untransform(q,p):
 c=math.cos(q['yaw']);s=math.sin(q['yaw']);x,y,z=q['position'];a,b,d=[p[i]-q['position'][i]for i in range(3)]
 return [c*a-s*d,b,s*a+c*d]
local_rest={s['place']:untransform(reference,s['surface'])for s in base['rest_surfaces']if s['reference_room_id']=='C118'}
for q in remaining:
 key=q['allocation_key']
 instances.append(dict(reference_room_id=key,reference_kind='anonymous_source_allocation_not_room_id',
  allocation_key=key,source_drawing_index=q['source_drawing_index'],source_envelope=q['source_envelope'],
  position=q['position'],yaw=q['yaw'],identity_evidence='retained_atlas_envelope_only',
  original_berth_keys=None,assigned_people=None,physical_rest_surfaces=2))
 for place,at in local_rest.items():surfaces.append(dict(allocation_key=key,reference_room_id=key,reference_kind='anonymous_source_allocation_not_room_id',
  place=place,surface=transform(q,at),actual_native_surface_measured=True,registered_berth_key=None))
 for f in original['fixtures']:fixtures.append(dict(name=key+'_'+f['name'],position=transform(q,f['position']),range_m=f['range_m'],energy=f['energy'],color=f['color']))
 for bed in original['beds']:
  doors.append(dict(allocation_key=key,place=bed['local_place'],curtain_position=transform(q,bed['curtain_position']),curtain_yaw=q['yaw']+bed['curtain_yaw'],placement_interface='original shared_crew_home.gd component placement; curtain behaviour remains unbound',runtime_bound=False))
pins={f:h for f,h in base['source_pins'].items()if not f.startswith('BlenderCatalogue/assets/group3_crew_service_20261009/extensions/d03_remaining')}
pins[str((PRIOR/'source/LABELLED_BANK_CONTRACT.json').relative_to(ROOT))]=sha(PRIOR/'source/LABELLED_BANK_CONTRACT.json')
spec=dict(schema=1,catalogue_id='AST-CRW-G3-003',family='group3_crew_service_20261009',source_pins=pins,
 template_spec_path=base['template_spec_path'],native_shell_path=base['native_shell_path'],instances=instances,rest_surfaces=surfaces,fixtures=fixtures,
 immutable_dependencies=base['immutable_dependencies'],physical_unassigned_rest_surfaces=366,new_registered_berths=0,
 automatic_runtime_adoption=False,original_shared_home_unchanged=True,C036_migration_applied=False,
 retained_C036_hold=dict(allocation_key=held[0]['allocation_key'],envelope=held[0]['source_envelope'],original_hold=held[0]['hold'],no_geometry_or_key_changed=True),
 inferred_room_ID_joins_adopted=0,room_IDs_created=0,floor_exported=False,curtain_construction_interfaces=doors,
 construction_accounting=dict(batch014_physical_source_rests=32,batch015_physical_source_rests=366,retained_installed_shared_home_rests=2,
  source_component_total=400,authoritative_400_berth_identity_or_species_or_live_scene_acceptance=False),
 integration_holds=['Original missing-only floor and screened streets need current actual-main integration.',
  'The 183 source names are geometric allocation references, never original cabin/person/berth/save IDs.',
  'Do not infer a C036 migration or demographic/species split.',
  'Beds, curtains, wash fixtures and light housings are source construction; runtime curtain/occupancy/plumbing/stock/lighting remain unbound.'])
(HERE/'source/REMAINING_BANK_CONTRACT.json').write_text(json.dumps(spec,indent=2)+'\n')
report=dict(status='PASS_SOURCE_PLAN',anonymous_allocations=183,physical_unassigned_rest_surfaces=366,source_component_total_including_batch014_and_retained_shared_home=400,
 registered_berths_added=0,C036_migration_applied=False,source_only=True)
(HERE/'qa/PLAN_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
