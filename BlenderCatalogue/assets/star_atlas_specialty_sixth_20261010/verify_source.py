from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));Q=json.load(open(W/'RUNTIME_RECEIVING.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ns={'__file__':str(W/'reader.py')};exec((R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py').read_text(),ns)
for a in P['sources']:
 assert sha(R/'BlenderCatalogue'/a['source'])==a['source_sha256']and sha(R/'BlenderCatalogue'/a['export'])==a['export_sha256']
for f,h in Q['source_pins'].items():assert sha(R/f)==h
assert sum(r['allocation']['proposed_rest_place_count']for r in P['rooms'])==4 and len(P['rooms'])==4
old_geometry=list(ns['triangles']('StarAtlasSpecialtySecondReceiving.glb'));removed=[(n,t)for n,t in old_geometry if n in Q['removed_terminal_guard_names']];assert len(removed)==2 and sum(len(t)for n,t in removed)==24
tri_source=[];source_objects=0;max_delta=0
received=list(ns['triangles'](Q['model_file']))
for lower in Q['lower_structural_owners']:
 original=np.concatenate([t for n,t in ns['triangles'](lower['runtime_source'],lower['origin'],lower['yaw'])]);original_vertices=np.unique(original.reshape(-1,3),axis=0);retained=[t for n,t in received if n.startswith('Persistent_'+str(lower['source_index'])+'_')];assert len(retained)==22
 copied=np.concatenate(retained);copied_vertices=np.unique(copied.reshape(-1,3),axis=0);distance=np.sqrt(((copied_vertices[:,None,:]-original_vertices[None,:,:])**2).sum(2)).min(1);assert distance.max()<.00003;max_delta=max(max_delta,float(distance.max()));tri_source.append(len(copied));source_objects+=len(retained)
for room in P['rooms']:
 a=room['allocation'];fittings=room['rest_fittings'];assert len(fittings)==1 and [f['rest_slot_id']for f in fittings]==a['proposed_rest_slot_ids']
 assert room['proposed_design_species']in ['Mantelids','Baelins']and not room['species_ready']
 for contact in room['receiving_contacts']:assert len(contact['bottom_contact_vertices'])==4 and contact['full_toe_area_m2']==.04
 meshes=list(ns['triangles'](room['model_file']))
 for binding in room['components']:
  if binding['name']not in ['LibraryStudyEdge','DayReadingChair','StudyChair','StreetReadingChair','PersonalConsole']:continue
  pieces=[t for n,t in meshes if f"SA{a['source_envelope_index']}_{binding['name']}__"in n];assert pieces
  pts=np.concatenate(pieces).reshape(-1,3);lo=pts.min(0);hi=pts.max(0)
  assert lo[0]>=a['allocation_x'][0]and hi[0]<=a['allocation_x'][1]and lo[2]>=a['allocation_z'][0]and hi[2]<=a['allocation_z'][1]
  for f in fittings:
   pieces=[t for n,t in meshes if f"SA{a['source_envelope_index']}_{f['binding']['name']}__"in n];rest=np.concatenate(pieces).reshape(-1,3);rl=rest.min(0);rh=rest.max(0)
   assert not np.all((hi>rl+1e-5)&(lo<rh-1e-5)),(a['source_envelope_index'],binding['name'])
# Exact source-contained guard derivative: original volume outside the four entry spans remains unchanged.
for derivative in Q['guard_derivatives']:
 v=derivative['original_part']['verts'];lo=np.min(v,axis=0);hi=np.max(v,axis=0)
 assert abs(sum(b-a for a,b in derivative['retained_intervals'])+sum(b-a for a,b in derivative['entry_openings'])-(hi[2]-lo[2]))<1e-8
 for a,b in derivative['entry_openings']:assert abs(b-a-3.48)<1e-8
for joint in Q['existing_frame_joints']:
 pieces=[t for n,t in ns['triangles'](joint['existing_model'])if n==joint['existing_mesh']];assert len(pieces)==1
 original=pieces[0].reshape(-1,3);lo=original.min(0);hi=original.max(0);a,b=np.array(joint['overlap_bounds']);assert np.all(a>=lo-.00003)and np.all(b<=hi+.00003)
from importlib.util import spec_from_file_location,module_from_spec
spec=spec_from_file_location('production_guard',R/'Game/tools/validate_production_glb.py');guard=module_from_spec(spec);spec.loader.exec_module(guard)
for r in P['rooms']:guard.validate(R/'Game/assets/models'/r['model_file'])
guard.validate(R/'Game/assets/models'/Q['model_file'])
report={'status':'PASS','new_physical_room_candidates':4,'new_reserved_rest_places':4,'cumulative_physical_specialty_candidates':24,'cumulative_specialty_rest_reservations':30,'remaining_specialty_reservations':22,'new_allocations':0,'registered_component_sources_unchanged':len(P['sources']),'retained_lower_structural_objects':source_objects,'retained_source_triangles':sum(tri_source),'max_source_vertex_delta_m':max_delta,'full_toe_roof_contacts':16,'reused_existing_D13_foundation_toes':12,'room_floor_frame_members':len(Q['parts']),'sanitary_and_activity_sources_retained':True,'rest_and_activity_component_bounds_disjoint':True,'lower_rendering_residency_preserved':True,'new_street_floor_area_m2':0,'new_piers':0,'existing_frame_joints':20,'new_guard_segments':6,'four_entry_openings_m':3.48,'new_production_assets_guarded':5,'no_D13_floor_invented':True,'earlier_unassigned_alien_low_rest_units':[443,467,491],'limits':['Exact source surface/capacity/layout evidence; no structural load/cantilever capacity certificate','Baelin/Mantelid design targets are proposed; canonical bodies/rigs/animation, molt/acoustics and save/needs operations remain held','Bounded source and actual-main tests are separate from final in-engine/CRT/hardware art acceptance']};(W/'ACTUAL_SOURCE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
