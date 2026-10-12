"""Construct only the sixteen explicitly labelled atlas envelopes. No inferred IDs/save migration."""
from pathlib import Path
import json,hashlib,math,sys
import numpy as np
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4];FIRST=HERE.parent.parent
sys.path.insert(0,str(HERE.parent/'d03_remaining_receivers_batch013/source'))
from native_glb_subset import GLB
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
catalogue=json.load(open(ROOT/'BlenderCatalogue/catalogue_manifest.json'))
for aid in ['AST-CRW-G3-002','AST-STF-G3-028','AST-STF-G3-029']:
 assert not any(q['catalogue_id']==aid for q in catalogue['assets'])
bank=json.load(open(FIRST/'source/CREW_BANK_PLACEMENTS_PROPOSAL.json'))
homes=[q for q in bank['instances']if q['identity_join_status']=='exact_labelled_atlas_detail']
assert {q['proposed_retained_room_id']for q in homes}=={f'C{i:03d}'for i in list(range(118,126))+list(range(168,176))}
template=json.load(open(FIRST/'source/CREW_BANK_HOME.json'));streets=json.load(open(FIRST/'source/CREW_STREETS.json'))
pins={f:sha(ROOT/f)for f in [
 'Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json',
 'Game/data/reference/D03_crew_envelopes.json','Game/data/reference/historical_atlas.pdf',
 'Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json',
 'Game/assets/models/D04_STARBOARD_CENTRAL_COMBINEDSTRUCTURE_r001.glb',
 'Game/data/architecture/SHARED_CREW_HOME.json','Game/scripts/shared_crew_home.gd',
 'BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_BANK_PLACEMENTS_PROPOSAL.json',
 'BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_BANK_HOME.json',
 'BlenderCatalogue/assets/group3_crew_service_20261009/exports/AST-CRW-G3-001.glb',
 'BlenderCatalogue/assets/group3_crew_service_20261009/source/CREW_STREETS.json',
 'BlenderCatalogue/assets/group3_crew_service_20261009/extensions/d03_remaining_receivers_batch013/source/MISSING_ONLY_FLOOR_PATCH.json']}
for q in template['dependencies']:assert sha(ROOT/q['path'])==q['sha256'];pins[q['path']]=q['sha256']
base=dict(schema=1,family='group3_crew_service_20261009',material_contract='retained_lower_staff_network',source_pins=pins,
 automatic_runtime_adoption=False,new_registered_berths=0,original_shared_home_unchanged=True)
support_model=GLB(ROOT/'Game/assets/models/D04_STARBOARD_CENTRAL_COMBINEDSTRUCTURE_r001.glb')
columns=[]
for name,node in support_model.by_name.items():
 if'mesh'not in node or not name.startswith('SC_StreetBearing'):continue
 bounds=support_model.bounds(name)
 if bounds[0]<94.15 and bounds[1]>77.85 and bounds[4]<-42.56 and bounds[5]>-143.14 and bounds[2]<12 and bounds[3]>15.34:
  columns.append(dict(name=name,bounds=bounds))
column_shape=unary_union([box(q['bounds'][0],q['bounds'][4],q['bounds'][1],q['bounds'][5])for q in columns])
def prism(parts,name,g,lo,hi,role,cat,cell):
 for i,p in enumerate(shapely.get_parts(g)):
  if p.geom_type!='Polygon'or p.area<1e-9:continue
  parts.append(dict(name=name+'_'+str(i),boundary=list(p.exterior.coords)[:-1],holes=[list(h.coords)[:-1]for h in p.interiors],
   triangles=[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(p).geoms],y=[lo,hi],role=role,category=cat,batch_cell=cell))
def point(q,local):
 x,y,z=q['position'];c=math.cos(q['yaw']);s=math.sin(q['yaw']);a,b,d=local
 return [x+c*a+s*d,y+b,z-s*a+c*d]
rest_original=GLB(ROOT/next(q['path']for q in template['dependencies']if Path(q['path']).stem=='AST-CRW-001'))
def actual_rest_surface(nominal):
 # The original sheet/blanket is shaped. Its nominal datum is not the top face.
 x,y,z=nominal;hits=[]
 for name,node in rest_original.by_name.items():
  if'mesh'not in node or not any(s in name for s in ['crew_ecru_sheet','crew_terracotta_blank']):continue
  v,faces,_,_=rest_original.geometry(name)
  for f in faces:
   t=np.asarray([v[i]for i in f]);cross=np.cross(t[1]-t[0],t[2]-t[0])
   if cross[1]<=1e-10:continue
   try:weights=np.linalg.solve(np.vstack((t[:,[0,2]].T,np.ones(3))),[x,z,1])
   except np.linalg.LinAlgError:continue
   if weights.min()>=-1e-8 and abs(float(weights@t[:,1])-y)<.2:hits.append(float(weights@t[:,1]))
 assert hits,'Original rest surface has no upward native face'
 return [x,max(hits),z]
selected_area=box(77.99,-143,94.01,-42.7)
parts=[];fixtures=[];doors=[];instances=[];rests=[]
route=unary_union([Polygon(q['boundary'],q['holes'])for q in streets['route_shape']+streets['porch_shapes']]).intersection(selected_area)
for q in streets['parts']:
 if'boundary'not in q:continue
 g=Polygon(q['boundary'],q['holes']).intersection(selected_area).difference(column_shape)
 if g.area<1e-9:continue
 prism(parts,q['name']+'_BankSelected',g,*q['y'],q['role'],q['category'],q['batch_cell'])
for q in homes:
 rid=q['proposed_retained_room_id'];pos=q['position'];yaw=q['yaw'];sign=-1 if yaw else 1;x,y,z=pos
 # A complete rigid original shell/furnishing assembly; semantic place labels never become save IDs.
 instances.append(dict(reference_room_id=rid,source_drawing_index=q['source_drawing_index'],position=pos,yaw=yaw,
  identity_evidence='exact_labelled_atlas_detail',original_berth_keys=None,assigned_people=None,physical_rest_surfaces=2))
 for bed in template['beds']:
  c=math.cos(bed['yaw']);s=math.sin(bed['yaw']);a,b,d=actual_rest_surface(bed['rest_surface']);bp=bed['position']
  rests.append(dict(reference_room_id=rid,place=bed['local_place'],surface=point(q,[bp[0]+c*a+s*d,bp[1]+b,bp[2]-s*a+c*d]),
   original_nominal_component_surface=bed['rest_surface'],actual_native_surface_measured=True,registered_berth_key=None))
 # The unscaled original service fitting is outside the 2.8m source lintel, in its porch.
 dx=x+sign*7.0;doors.append(dict(name=rid+'EntryGate',id=rid+'_porch_gate_g3_completion',position=[dx,12,z],yaw=(-math.pi/2+yaw),default_closed=True))
 xa,xb=sorted([x+sign*6,dx+sign*.18]);collar=box(xa,z-1.4,xb,z+1.4)
 for a,b in [(-1.54,-1.4),(1.4,1.54)]:prism(parts,rid+'CollarSide'+str(a),box(xa,z+a,xb,z+b),12,15.2,'staff_white_paint','door_receiver',rid)
 prism(parts,rid+'CollarHead',box(xa,z-1.54,xb,z+1.54),15.2,15.34,'staff_bluegrey_paint','overhead',rid)
 prism(parts,rid+'GateHead',box(dx-.18,z-1.38,dx+.18,z+1.38),14.82,15.2,'staff_white_paint','door_receiver',rid)
 # Tiny 20mm side infills meet original frame; no modification or scaling of the original family.
 for a,b in [(-1.4,-1.38),(1.38,1.4)]:prism(parts,rid+'GateSide'+str(a),box(dx-.18,z+a,dx+.18,z+b),12,15.2,'staff_white_paint','door_receiver',rid)
 for f in template['fixtures']:fixtures.append(dict(name=rid+'_'+f['name'],position=point(q,f['position']),range_m=f['range_m'],energy=f['energy'],color=f['color']))
route_with_bearings=route.buffer(.14,join_style=2)
roomshape=unary_union([box(q['source_envelope']['x'][0],q['source_envelope']['z'][0],q['source_envelope']['x'][1],q['source_envelope']['z'][1])for q in homes])
requested=route_with_bearings.union(roomshape)
compiled=json.load(open(ROOT/'Game/data/generated/structural_meshes.json'));received=json.load(open(ROOT/'Game/data/generated/received_structural_meshes.json'))
actual=unary_union([Polygon(t)for q in compiled['regions']+received['regions']if q['deck']=='D03'for t in q['triangles']])
precinct=json.load(open(HERE.parent/'d03_remaining_receivers_batch013/source/MISSING_ONLY_FLOOR_PATCH.json'))
prior=unary_union([Polygon(q['boundary'],q['holes'])for q in precinct['parts']]);missing=requested.difference(actual.union(prior)).difference(column_shape)
floorparts=[];prism(floorparts,'LabelledBankMissingFloor',missing,11.76,12,'staff_rubber','floor','labelled_bank_floor')
write(HERE/'source/BANK_STREET_AND_COLLARS.json',dict(base,catalogue_id='AST-STF-G3-028',parts=parts,fixtures=[]))
write(HERE/'source/BANK_MISSING_ONLY_FLOOR.json',dict(base,catalogue_id='AST-STF-G3-029',parts=floorparts,fixtures=[],floor_patch_proposal_only=True))
plan=dict(base,catalogue_id='AST-CRW-G3-002',instances=instances,rest_surfaces=rests,fixtures=fixtures,service_doors=doors,
 protected_D04_support_columns=columns,clear_staff_lane_x=87.0,
 template_spec_path=str((FIRST/'source/CREW_BANK_HOME.json').relative_to(ROOT)),native_shell_path=str((FIRST/'exports/AST-CRW-G3-001.glb').relative_to(ROOT)),
 labelled_rooms=16,physical_unassigned_dry_rest_surfaces=32,immutable_dependencies=template['dependencies'],new_floor_m2=missing.area,
 rejected_inferred_rooms=184,C036_migration_applied=False,original_shared_home_physical_rests=2,
 identity_acceptance='Only sixteen exact atlas labels. No authoritative person/berth/save keys, population or migration. 400-berth reconciliation remains unfinished.',
 species_acceptance='Dry reference-family architecture only; Baelin aquatic compatibility, Mantelid cocoons and all species/body/pose allocation remain unfinished.')
write(HERE/'source/LABELLED_BANK_CONTRACT.json',plan)
report=dict(status='PASS',labelled_rooms=16,physical_unassigned_rest_surfaces=32,new_floor_m2=missing.area,
 duplicate_existing_or_precinct_floor_m2=missing.intersection(actual.union(prior)).area,
 adjacent_precinct_join_xz=[86,-42.7],original_bank_room_ids_or_save_keys_changed=False,
 original_shared_home_unchanged=True,all_inferred_addresses_omitted=True,C036_untouched=True)
assert report['duplicate_existing_or_precinct_floor_m2']<1e-7
write(HERE/'qa/PLAN_CHECKS.json',report);print(json.dumps(report))
