"""Actual unoccupied aft reservations, source-fitted original riser architecture."""
from pathlib import Path
import json,hashlib,math,copy
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4];PRE=HERE.parent/'port2_clinical_physical_batch016';OLD=HERE.parent/'port2_clinical_batch006'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
write=lambda f,q:f.write_text(json.dumps(q,indent=2)+'\n')
catalogue=json.load(open(ROOT/'BlenderCatalogue/catalogue_manifest.json'))
for aid in ['AST-STF-G3-033','AST-STF-G3-034','AST-STF-G3-035','AST-STF-G3-036']:assert not any(q['catalogue_id']==aid for q in catalogue['assets'])
for line in(PRE/'SHA256SUMS.txt').read_text().splitlines():h,f=line.split('  ',1);assert sha(PRE/f)==h,f
layout=json.load(open(ROOT/'Game/data/whole_ship_layout.json'));template=json.load(open(OLD/'source/PORT_SECOND_STAFF_RISER.json'))
fit=json.load(open(PRE/'source/RISER_FRAME_AND_CALL_PATCH.json'));port=json.load(open(PRE/'source/PHYSICAL_CONTRACT.json'))
survey=json.load(open(HERE/'qa/ACTUAL_MAIN_EXISTING_SURVEY.json'))
ids=['port_service_riser_5','starboard_service_riser_5']
for key in ids:
 q=next(q for q in survey['rows']if q['reservation_id']==key);assert not q['existing_shaft_blockers']and not q['landing_slab_existing_contacts'],key
replace=set(fit['selected_original_semantic_parts'])
parts=[q for q in template['parts']if q['name']not in replace]+fit['parts']
pins={str(f.relative_to(ROOT)):sha(f)for f in [ROOT/'Game/data/whole_ship_layout.json',ROOT/'Game/data/spatial_layout.json',
 ROOT/'Game/data/generated/structural_meshes.json',ROOT/'Game/data/generated/received_structural_meshes.json',
 ROOT/'Game/data/architecture/HULL_BODY_SECTION_PROPOSAL.json',ROOT/'Game/docs/master_source/MASTER_CURRENT_APPLICATION.json',
 OLD/'source/PORT_SECOND_STAFF_RISER.json',PRE/'source/RISER_FRAME_AND_CALL_PATCH.json',PRE/'SHA256SUMS.txt',
 ROOT/'Game/scripts/commons_lift.gd',ROOT/'Game/scripts/lift_gate.gd',ROOT/'Game/assets/models/AST-CIR-003_seventeen_stop.glb',ROOT/'Game/assets/models/AST-DOR-003.glb']}
base=dict(schema=1,family='group3_crew_service_20261009',source_pins=pins,automatic_runtime_adoption=False,persistent_identity_map=None,registered_berths_added=0)
def polygon(q):
 if'boundary'in q:return Polygon(q['boundary'],q['holes'])
 a=q['aabb'];return box(a[0],a[4],a[1],a[5])
def prism(out,name,g,lo,hi,role,category,cell):
 for i,p in enumerate(shapely.get_parts(g)):
  if p.geom_type!='Polygon'or p.area<1e-10:continue
  out.append(dict(name=name+'_'+str(i),boundary=list(p.exterior.coords)[:-1],holes=[list(r.coords)[:-1]for r in p.interiors],triangles=[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms],
   y=[lo,hi],role=role,category=category,batch_cell=cell))
def transform_part(q,side,delta):
 r=copy.deepcopy(q);r['name']=('PA5_'if side==1 else'SA5_')+q['name']
 def xz(v):return [side*v[0],v[1]+delta]
 if'aabb'in r:
  a=r['aabb'];a[0],a[1]=sorted([side*a[0],side*a[1]]);a[4]+=delta;a[5]+=delta
  # Original existing controller call is +1.65 in starboard local/world Z.
  if side==-1 and q['name'].startswith('Port2_CallControlBacking'):a[4]+=3.3;a[5]+=3.3
 else:
  r['boundary']=[xz(v)for v in r['boundary']];r['holes']=[[xz(v)for v in ring]for ring in r['holes']];r['triangles']=[[xz(v)for v in t]for t in r['triangles']]
 return r
compiled=json.load(open(ROOT/'Game/data/generated/structural_meshes.json'))['regions']+json.load(open(ROOT/'Game/data/generated/received_structural_meshes.json'))['regions']
hull={q['deck']:Polygon(q['inner_reservation_boundary'])for q in json.load(open(ROOT/'Game/data/architecture/HULL_BODY_SECTION_PROPOSAL.json'))['levels']}
voids=json.load(open(ROOT/'Game/data/spatial_layout.json'))['voids'];sites=[];floorparts=[];checks=[]
for key,aid in zip(ids,['AST-STF-G3-033','AST-STF-G3-034']):
 res=next(q for q in layout['staff_riser_reservations']if q['id']==key);side=1 if key.startswith('port')else-1;delta=res['center_xz'][1]+283
 transformed=[transform_part(q,side,delta)for q in parts];fixtures=[];contacts=[]
 for q in template['fixtures']:
  r=dict(q,name=key+'_'+q['name'],position=[side*q['position'][0],q['position'][1],q['position'][2]+delta]);fixtures.append(r)
 for q in port['source_sill_remainder_contacts']:
  r=copy.deepcopy(q);r['name']=key+'_'+q['name'];a=r['aabb'];a[0],a[1]=sorted([side*a[0],side*a[1]]);a[4]+=delta;a[5]+=delta;contacts.append(r)
 write(HERE/'source'/(key+'.json'),dict(base,catalogue_id=aid,parts=transformed,fixtures=fixtures,original_source_template_only_rigid_or_mirrored_architecture=True,
  unscaled_original_cabin_and_gate_required=True,source_front_gate_trim_preserved=True,call_backings_match_original_controller=True))
 floorchecks=[]
 for landing in template['floor_proposals']:
  y=landing['floor_y'];deck=landing['deck'];request=box(-23.18,484,-18.8,496)if side==1 else box(18.8,484,23.18,496)
  actual=unary_union([Polygon(t)for q in compiled if q['deck']==deck for t in q['triangles']])
  sill=next(q for q in transformed if q['name'].endswith('Port2_LandingSill_'+deck));missing=request.difference(actual).difference(polygon(sill))
  prism(floorparts,key+'_'+deck,missing,y-.24,y,'staff_floor','floor',key+'_'+deck)
  programme=unary_union([box(q['allocation_x'][0],q['allocation_z'][0],q['allocation_x'][1],q['allocation_z'][1])for q in layout['programmes']if q['deck']==deck])
  intrusion=request.intersection(programme).area;outside=request.difference(hull[deck]).area
  void=sum(request.intersection(Polygon(q['boundary'])).area for q in voids if deck in q['decks'])
  assert intrusion<1e-7 and outside<1e-7 and void<1e-7,(key,deck,intrusion,outside,void)
  row=dict(reservation_id=key,deck=deck,floor_y=y,new_floor_m2=missing.area,old_floor_overlap_m2=missing.intersection(actual).area,programme_overlap_m2=intrusion,outside_hull_m2=outside,protected_void_overlap_m2=void)
  floorchecks.append(row);checks.append(row)
 sites.append(dict(reservation_id=key,center_xz=res['center_xz'],architecture_file=aid+'.glb',fixtures=fixtures,source_sill_remainder_contacts=contacts,floor_checks=floorchecks,
  lift_root_position=[res['center_xz'][0],0,res['center_xz'][1]],lift_root_yaw=math.pi if side==1 else 0,
  cabin_origin_xz=[-23.2 if side==1 else 23.2,490],landing_gate_origin_xz=[-23.08 if side==1 else 23.08,490],
  cabin_world_yaw=math.pi/2 if side==1 else-math.pi/2,landing_gate_world_yaw=3*math.pi/2 if side==1 else math.pi/2,
  controller_binding=port['controller_binding'],authoritative_identity_map=None,D18_added=False))
write(HERE/'source/AFT_PAIR_MISSING_ONLY_FLOORS.json',dict(base,catalogue_id='AST-STF-G3-035',material_contract='retained_lower_staff_network',parts=floorparts,fixtures=[],floor_proposal_only=True))
write(HERE/'source/AFT_PAIR_CONTRACT.json',dict(base,parent_handoff_commit='53f92bacd9f6ff3c20688324d408596cebde9d72',sites=sites,
 new_floor_m2=sum(q['new_floor_m2']for q in checks),source_fixture_profiles=34,
 held_existing_D04_conflicts=[q for q in survey['rows']if q['existing_shaft_blockers']],
 held_starboard3_existing_landings=next(q for q in survey['rows']if q['reservation_id']=='starboard_service_riser_3'),
 original_D01_shared_circuit_and_D04_routes_modified=False,default_main_adopted=False))
write(HERE/'qa/PLAN_CHECKS.json',dict(status='PASS',sites=2,landings=34,new_floor_m2=sum(q['new_floor_m2']for q in checks),protected_overlap=0,identity_keys_created=0,details=checks))
print(json.dumps(dict(sites=2,landings=34,new_floor_m2=sum(q['new_floor_m2']for q in checks),fixture_profiles=34)))
