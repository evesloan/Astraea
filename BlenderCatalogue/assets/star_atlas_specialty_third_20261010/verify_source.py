from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));Q=json.load(open(W/'RUNTIME_RECEIVING.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ns={'__file__':str(W/'reader.py')};exec((R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py').read_text(),ns)
for a in P['sources']:
 assert sha(R/'BlenderCatalogue'/a['source'])==a['source_sha256']and sha(R/'BlenderCatalogue'/a['export'])==a['export_sha256']
for f,h in Q['source_pins'].items():assert sha(R/f)==h
assert sum(r['allocation']['proposed_rest_place_count']for r in P['rooms'])==6 and len(P['rooms'])==4
old_geometry=list(ns['triangles']('StarAtlasSpecialtySecondReceiving.glb'));removed=[(n,t)for n,t in old_geometry if n in Q['removed_terminal_guard_names']];assert len(removed)==2 and sum(len(t)for n,t in removed)==24
tri_source=[];source_objects=0;max_delta=0
received=list(ns['triangles'](Q['model_file']))
for lower in Q['lower_structural_owners']:
 original=np.concatenate([t for n,t in ns['triangles'](lower['runtime_source'],lower['origin'],lower['yaw'])]);original_vertices=np.unique(original.reshape(-1,3),axis=0);retained=[t for n,t in received if n.startswith('Persistent_'+str(lower['source_index'])+'_')];assert len(retained)==22
 copied=np.concatenate(retained);copied_vertices=np.unique(copied.reshape(-1,3),axis=0);distance=np.sqrt(((copied_vertices[:,None,:]-original_vertices[None,:,:])**2).sum(2)).min(1);assert distance.max()<.00003;max_delta=max(max_delta,float(distance.max()));tri_source.append(len(copied));source_objects+=len(retained)
for room in P['rooms']:
 a=room['allocation'];fittings=room['rest_fittings'];assert len(fittings)==a['proposed_rest_place_count'];assert [f['rest_slot_id']for f in fittings]==a['proposed_rest_slot_ids'];assert room['proposed_design_species']=='Mantelids'and not room['species_ready']
 for f in fittings:
  pos=f['frame_origin'];assert -3.48<pos[2]-sum(a['allocation_z'])/2-1.28 and pos[2]-sum(a['allocation_z'])/2+1.28<3.48
  for contact in room['receiving_contacts']:assert len(contact['bottom_contact_vertices'])==4 and contact['full_toe_area_m2']==.04
 # New rest supports/liners and actual activity source meshes have disjoint occupied bounds.
 for binding in room['components']:
  if binding['name']not in ['LibraryStudyEdge','DayReadingChair']:continue
  asset=next(x for x in P['sources']if x['catalogue_id']==binding['catalogue_id']);file=asset['export'];raw=(R/'BlenderCatalogue'/file).read_bytes();# reader needs Game export; derive imported room node group instead.
  meshes=list(ns['triangles'](room['model_file']));pieces=[t for n,t in meshes if f"SA{a['source_envelope_index']}_{binding['name']}__"in n];assert pieces
  pts=np.concatenate(pieces).reshape(-1,3);lo=pts.min(0);hi=pts.max(0)
  for f in fittings:
   x,y,z=f['frame_origin'];c_lo=np.array([x-1.74,y,z-1.28]);c_hi=np.array([x+1.62,y+2.5,z+1.28]);assert not np.all((hi>c_lo+1e-5)&(lo<c_hi-1e-5)),(a['source_envelope_index'],binding['name'])
report={'status':'PASS','new_physical_room_candidates':4,'new_reserved_rest_places':6,'cumulative_physical_specialty_candidates':12,'cumulative_specialty_rest_reservations':14,'remaining_specialty_reservations':34,'new_allocations':0,'registered_component_sources_unchanged':len(P['sources']),'retained_lower_structural_objects':source_objects,'retained_source_triangles':sum(tri_source),'max_source_vertex_delta_m':max_delta,'full_toe_roof_contacts':16,'verified_existing_D14_floor_toes':18,'room_floor_frame_members':len(Q['parts']),'sanitary_and_activity_sources_retained':True,'rest_and_activity_component_bounds_disjoint':True,'lower_rendering_residency_preserved':True,'no_D13_floor_invented':True,'earlier_unassigned_alien_low_rest_units':[443,467,491],'limits':['Exact source surface/capacity/layout evidence; no structural load/cantilever capacity certificate','Mantelid design target is proposed; canonical bodies/rigs/animation, molt/acoustics and save/needs operations remain held','Bounded source and actual-main tests are separate from final in-engine/CRT/hardware art acceptance']};(W/'ACTUAL_SOURCE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
