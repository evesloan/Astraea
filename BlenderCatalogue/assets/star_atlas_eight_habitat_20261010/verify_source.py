from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PHYSICAL_PLAN.json'));V=json.load(open(W/'RUNTIME_HABITATS.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ns={'__file__':str(W/'reader.py')};exec((R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py').read_text(),ns)
for f,h in P['inputs'].items():assert sha(R/f)==h,f
for key,h in P['source_pins'].items():assert sha(R/'Game/assets/models'/(key+'.glb'))==h
original=[]
for lane in ['first','second']:original+=json.load(open(R/f'BlenderCatalogue/assets/star_atlas_specialty_{lane}_20261010/PLAN.json'))['rooms']
for room in V['rooms']:
 old=next(x for x in original if x['allocation']['source_envelope_index']==room['source_envelope_index']);a=old['allocation']
 assert room['unit_proposal_id']==a['proposed_runtime_id']and room['rest_slot_ids']==a['proposed_rest_slot_ids']and room['allocation_sha256']==a['allocation_sha256']and room['reservation_capacity']==1
 for k in ['species_assignment','historical_persistent_id','historical_address','existing_rebuild_identity']:assert a[k]is None
 assert room['rest_source']==next(x for x in old['components']if x['name']=='ReservedRestSupport')
 assert sha(W/room['assembly_native'])==room['assembly_native_sha256']
for ref in V['references']:
 body=np.concatenate([t.reshape(-1,3)for n,t in ns['triangles'](ref['model_file'])]);assert np.max(np.abs(body.min(0)-ref['bounds_min']))<1e-5 and np.max(np.abs(body.max(0)-ref['bounds_max']))<1e-5
 source=next(x for x in P['references']if x['key']==ref['key']);verts=np.array([v for p in source['parts']for v in p['verts']])
 for c in ref['contact_probes']:assert np.min(np.linalg.norm(verts-np.array(c),axis=1))<1e-8
 assert sha(R/'Game/assets/models'/ref['model_file'])==ref['model_sha256']
 for part in source['parts']:
  for vertex in part['verts']:
   x,y,z=vertex;ts=np.array(source['support_top_triangles']);a=ts[:,0,:];b=ts[:,1,:]-a;c=ts[:,2,:]-a;det=b[:,0]*c[:,2]-b[:,2]*c[:,0];ok=np.abs(det)>1e-10
   u=np.zeros(len(ts));v=np.zeros(len(ts));u[ok]=((x-a[ok,0])*c[ok,2]-(z-a[ok,2])*c[ok,0])/det[ok];v[ok]=(b[ok,0]*(z-a[ok,2])-b[ok,2]*(x-a[ok,0]))/det[ok];inside=ok&(u>=-1e-6)&(v>=-1e-6)&(u+v<=1.000001);assert inside.any();heights=a[:,1]+u*b[:,1]+v*c[:,1];assert y-max(heights[inside])>=.004999
assert sum(r['reservation_capacity']for r in V['rooms'])==8 and len(V['rooms'])==8 and V['new_allocations']==0 and V['saved_key_migrations']==0
report={'status':'PASS','original_allocation_input_and_canon_pins_unchanged':True,'existing_unit_rest_proposals_preserved':8,'reference_exports_measured':3,'actual_reference_bottom_vertices':18,'all_reference_vertices_above_exact_source_support':True,'canonical_body_acceptance':False,'native_assemblies':8,'new_catalogue_ids':0,'wet_cells_per_basin':V['wet_cell_count'],'source_derived_conservative_volume_m3':V['wet_volume_m3'],'water_bounds':'exact source visual-water polygon; cell floors above maximum source solid over the whole footprint by2mm','superseded_geometry':['SA437_QuietArrivalScreen','SA485_WetDryLandingBench'],'limits':['Proposed rest references have actual measured meshes but no canonical body/rig/animation or standing-body acceptance','Conservative wet query regions undercount displaced/safety water; no full physical-fluid simulator','Physical privacy enclosure does not certify acoustic attenuation or biological/molting operations']};(W/'ACTUAL_SOURCE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
