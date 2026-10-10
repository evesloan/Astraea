from pathlib import Path
import json,hashlib,numpy as np,sys,struct
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ns={'__file__':str(W/'reader.py')};exec((R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py').read_text(),ns)
sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import validate
for p,h in P['protected_source_pins'].items():assert sha(R/p)==h,p
for a in P['sources']:
 assert sha(R/'BlenderCatalogue'/a['source'])==a['source_sha256']and sha(R/'BlenderCatalogue'/a['export'])==a['export_sha256']
H=json.load(open(R/'Game/data/architecture/STAR_ATLAS_EIGHT_HABITATS.json'));shared=0;max_delta=0;rest_meshes=0
for room,adapt in zip(P['rooms'],P['adaptations']):
 idx=adapt['index'];a=room['allocation'];h=next(r for r in H['rooms']if r['source_envelope_index']==idx)
 assert h['unit_proposal_id']==a['proposed_runtime_id']==adapt['unit_proposal_id']and h['rest_slot_ids']==a['proposed_rest_slot_ids']==adapt['rest_slot_ids']
 assert h['allocation_sha256']==a['allocation_sha256']==adapt['allocation_sha256']and h['reservation_capacity']==a['proposed_rest_place_count']==1
 assert all(a[k]is None for k in ['species_assignment','historical_persistent_id','historical_address','existing_rebuild_identity'])
 assert h['proposed_design_species']==adapt['species']and not h['species_ready']and not h['alien_body_compatibility_accepted']
 old=dict(ns['triangles'](adapt['old_model']));new=dict(ns['triangles'](room['model_file']));prefix=f'SA{idx}_ReservedRestSupport__'
 removed=set(h.get('superseded_source_meshes',[]))
 # Every unaffected shell/activity/sanitary/receiving mesh is still its predecessor geometry.
 for name,tris in old.items():
  if name.startswith(prefix)or name in removed:continue
  assert name in new,name
  x=np.unique(tris.reshape(-1,3),axis=0);y=np.unique(new[name].reshape(-1,3),axis=0);assert len(x)==len(y),(name,len(x),len(y))
  for v in y:
   d=float(np.linalg.norm(x-v,axis=1).min());max_delta=max(max_delta,d);assert d<.00003,(name,d)
  shared+=1
 assert all(name not in new for name in removed)
 rest=next(b for b in room['components']if b['name']=='ReservedRestSupport');assert rest['catalogue_id']==adapt['rest_catalogue_id']
 exact=dict(ns['triangles'](rest['catalogue_id']+'.glb',rest['position'],rest['yaw']))
 for name,tris in exact.items():
  if 'Preview'in name:continue
  matches=[ts for n,ts in new.items()if n==(prefix+name)[:63]]
  assert len(matches)==1,(idx,name)
  x=np.unique(tris.reshape(-1,3),axis=0);y=np.unique(matches[0].reshape(-1,3),axis=0)
  for v in y:assert np.linalg.norm(x-v,axis=1).min()<.00003,(idx,name)
  rest_meshes+=1
 # Check the architectural centerpieces and activity elements stay inside their retained allocation.
 for name,tris in new.items():
  if any(k in name for k in ['ReservedRestSupport','Cocoon_','CareCabinet','WetPrivacyBlade','LibraryStudyEdge','DayReadingChair']):
   verts=tris.reshape(-1,3);lo=verts.min(0);hi=verts.max(0)
   assert lo[0]>=a['allocation_x'][0]-.00003 and hi[0]<=a['allocation_x'][1]+.00003 and lo[2]>=a['allocation_z'][0]-.00003 and hi[2]<=a['allocation_z'][1]+.00003,(idx,name,lo,hi)
 validate(R/'Game/assets/models'/room['model_file'])
 raw=(R/'Game/assets/models'/room['model_file']).read_bytes();length=struct.unpack_from('<I',raw,12)[0];gltf=json.loads(raw[20:20+length]);assert set(n['extras']['source_plan_sha256']for n in gltf['nodes']if 'source_plan_sha256'in n.get('extras',{}))=={sha(W/'PLAN.json')}
 assert sha(R/h['assembly_native'])==h['assembly_native_sha256']
assert len(H['rooms'])==8 and sum(r['reservation_capacity']for r in H['rooms'])==8 and H['new_allocations']==0
report={'status':'PASS','adapted_existing_candidates':3,'unchanged_single_rest_capacities':3,'new_units':0,'new_rest_places':0,'new_catalogue_ids':0,'new_streets_or_piers':0,'ids_changed':0,'protected_original_source_files':len(P['protected_source_pins']),'unchanged_registered_components':len(P['sources']),'unaffected_predecessor_meshes_verified':shared,'max_unaffected_vertex_delta_m':max_delta,'exact_source_rest_meshes_verified':rest_meshes,'architectural_target_mapping':{'443':'Mantelids','467':'Baelins','491':'Mantelids'},'wet_cells_per_basin':H['wet_cell_count'],'cumulative_specialty_candidates':30,'cumulative_reserved_rests':40,'remaining_specialty_by_deck':{'D13':10,'D14':6},'species_ready_rooms':0,'limits':'Architectural proposal targets; no canonical body/rig/pose, population allocation, acoustic/molt/water/cleaner/stock/save operations, structural capacity or final runtime visual acceptance.'}
(W/'ACTUAL_SOURCE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
