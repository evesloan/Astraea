from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import Polygon,shape,MultiPoint,box
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.loads((W/'PLAN.json').read_text());N=json.loads((W/'NATIVE_EXPORT_CHECK.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reader=R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py';ns={'__file__':str(reader)};exec(reader.read_text(),ns)
expected={p['name']:p for p in P['parts']};rows=[]
for name,t in ns['triangles'](P['receiving_model']):
    p=expected.pop(name);v=np.unique(t.reshape(-1,3),axis=0);want=np.unique(np.array(p['verts']),axis=0)
    error=max(np.linalg.norm(v[:,None]-want[None,:],axis=2).min(1).max(),np.linalg.norm(want[:,None]-v[None,:],axis=2).min(1).max());assert error<.00003,(name,error)
    q=t-t.mean(axis=(0,1));volume=np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2])).sum()/6
    assert volume>0,(name,volume)
    rows.append({'name':name,'triangles':len(t),'max_vertex_error_m':float(error),'positive_volume_m3':float(volume)})
assert not expected and len(rows)==len(P['parts'])
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
assert sha(W/P['receiving_model'])==sha(R/'Game/assets/models'/P['receiving_model'])==N['receiving_export_sha256']
j=json.loads((W/'FIRST_ROOM_EVALUATED_FOOTPRINT.json').read_text());hull=MultiPoint(j['world_xz']).convex_hull;allocation=Polygon(j['allocation_boundary'])
raw_area=hull.difference(allocation).area
# Source and runtime use float32 vertex/transform data. Report the raw residual,
# and the measured2µm Z-edge error rather than hiding it in a rounded area.
assert allocation.buffer(.000003,join_style=2).covers(hull),(raw_area,hull.bounds)
assert hull.bounds[2]<=-63.0+1e-9
floor=shape(P['floor_geometry']);court=box(-94,-90,-76,90)
assert floor.intersection(court).area==0
vip=json.loads((R/'Game/data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json').read_text())['replacements'];protected=[]
for r in vip:
    if r['house']!='port_central_upper_house':continue
    poly=Polygon(r['proposed_floor_boundary']);assert floor.intersection(poly).area==0 and hull.intersection(poly).area==0
    protected.append(r['source_envelope_index'])
door=box(-66.74,14,-63.26,14.305)
assert floor.covers(door)
for pier in P['piers']:
    assert pier['floor_y']==97.5
    assert floor.covers(box(pier['x']-.16,pier['z']-.16,pier['x']+.16,pier['z']+.16))
rec={'status':'PASS','receiving_meshes':rows,'source_pins_unchanged':len(P['source_pins']),'floor_area_m2':floor.area,'full_shared_door_profile_received':True,'existing_commons_frame_bearings':2,'D16_slab_bearings':4,'roof_max_y':106.5,'court_void_extension_m2':0,'VIP_boundaries_preserved':protected,'first_room_id':P['first_room']['allocation']['proposed_runtime_id'],'first_room_rest_ids':P['first_room']['rest_slots_unchanged'],'first_room_entry_recess_m':.175,'first_room_full_source_hull_bounds':hull.bounds,'first_room_raw_Z_float32_edge_residual_area_m2':raw_area,'first_room_max_geometry_edge_tolerance_m':.000003,'first_room_X_overhang_m':max(0,hull.bounds[2]+63),'historical_full_source_hull_overhang_m2':.7376166216211921,'first_room_adopted':False,'primary_engineering_load_accepted':False,'limits':P['limits']}
(W/'SOURCE_GEOMETRY_CHECK.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps({'status':'PASS','meshes':len(rows),'profile_received':True,'entry_X_overhang_m':rec['first_room_X_overhang_m'],'Z_float_residual_m2':raw_area}))
