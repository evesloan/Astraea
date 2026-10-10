from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[2]
P=json.loads((W/'PLAN.json').read_text());N=json.loads((W/'NATIVE_EXPORT_CHECK.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reader=R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py'
ns={'__file__':str(reader)};exec(reader.read_text(),ns)
expected={p['name']:p for p in N['replacement_parts']};rows=[]
for name,t in ns['triangles'](P['receiving_model']):
    assert name in expected
    p=expected.pop(name);v=t.reshape(-1,3);lo=np.array(p['min']);hi=np.array(p['max'])
    delta=max(abs(v.min(0)-lo).max(),abs(v.max(0)-hi).max());assert delta<.00003
    corners=np.array([[x,y,z]for x in [lo[0],hi[0]]for y in [lo[1],hi[1]]for z in [lo[2],hi[2]]])
    assert max(min(np.linalg.norm(q-c)for c in corners)for q in v)<.00003
    volume=np.sum(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])))/6
    assert abs(volume-np.prod(hi-lo))<.0003
    rows.append({'name':name,'triangles':len(t),'max_bound_error_m':float(delta),'volume_m3':float(volume),'winding_positive':True})
assert not expected
assert sha(W/'StarAtlasD17StandardPortal.blend')==N['native_sha256']
assert sha(W/P['receiving_model'])==sha(R/'Game/assets/models'/P['receiving_model'])==N['export_sha256']
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
records=json.loads((R/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json').read_text())['records']
group=[r for r in records if r['house']=='port_central_upper_house'and r['deck']=='D17'];assert len(group)==17
standard=[r for r in group if r['source_envelope_index']in P['standard_source_indices']]
vip=[r for r in group if r['source_envelope_index']in P['VIP_source_indices']]
assert len(standard)==10 and len(vip)==7 and all(r['proposed_rest_place_count']==2 for r in standard)
bindings=[{k:r.get(k)for k in ['source_envelope_index','allocation_sha256','proposed_runtime_id','proposed_rest_place_count','proposed_rest_slot_ids','candidate_layout','production_lane']}for r in group]
report={'status':'PASS','scope':'Independent source-only portal geometry/source/allocation preservation','replacement_meshes':rows,'source_pins_unchanged':len(P['source_pins']),'bindings_preserved':bindings,'D17_standard_units_held':10,'D17_standard_rest_reservations':20,'D17_VIP_units_held':7,'new_allocations':0,'new_rest_places':0,'actual_main_wall_changed':False,'new_floor_area_m2':0,'adoption_status':'HOLD_MISSING_ONWARD_FLOOR_SUPPORT','whole_Group1_complete':False,'primary_engineering_load_accepted':False}
(W/'SOURCE_GEOMETRY_CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'PASS','meshes':len(rows),'source_pins':len(P['source_pins']),'standard_held':10,'VIP_held':7}))
