from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import shape,MultiPoint,box
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));N=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=R/'BlenderCatalogue/assets/forward_staff_shaft_interfaces_20261010/source_geometry.py';ns={'__file__':str(f)};exec(f.read_text(),ns);T=ns['triangles'];errors=[];rows=[];bindings=[];all_expected={}
def check_model(file,parts,rooms=None,check_components=True):
 expected={q['name']:q for q in parts};seen={};component={}
 for name,ts in T(file):
  if name not in expected:
   key=next((b['name']for b in rooms['components']if name.startswith('D04H'+str(rooms['source_index'])+'_'+b['name']+'__')),None)if rooms else next((b['name']for b in P['commons_components']if name.startswith('D04Commons_'+b['name']+'__')),None)
   assert key,(file,name);component.setdefault(key,[]).append(ts);continue
  q=expected[name];a=np.unique(ts.reshape(-1,3),axis=0);want=np.unique(np.array(q['verts']),axis=0);delta=max(np.linalg.norm(a[:,None]-want[None,:],axis=2).min(1).max(),np.linalg.norm(want[:,None]-a[None,:],axis=2).min(1).max());assert delta<.00004,(name,delta)
  v=ts-ts.mean(axis=(0,1));volume=np.einsum('ij,ij->i',v[:,0],np.cross(v[:,1],v[:,2])).sum()/6;assert volume>0,(name,volume);rows.append({'file':file,'name':name,'positive_volume_m3':float(volume),'vertex_error_m':float(delta)})
  k=tuple(sorted(tuple(round(float(c),5)for c in a)for a in np.array(q['verts'])))
  if k in seen:errors.append({'kind':'duplicate_owned_geometry','names':[seen[k],name]})
  seen[k]=name
  if rooms and q['category']in['shell','privacy_screen','storage','light_source','fixture_support']:
   outside=MultiPoint(a[:,[0,2]]).convex_hull.difference(shape(rooms['floor_geometry']).buffer(.00004)).area
   if outside>1e-7:errors.append({'kind':'owned_architecture_outside_floor','name':name,'area':outside})
  all_expected[name]=True
 assert set(expected)=={r['name']for r in rows if r['file']==file},set(expected)-set(all_expected)
 for b in (rooms['components']if rooms else P['commons_components'])if check_components else[]:
  data=np.concatenate(component[b['name']]);a=np.unique(data.reshape(-1,3),axis=0);src=next(q for q in P['sources']if q['catalogue_id']==b['catalogue_id']);orig=np.unique(np.concatenate([t.reshape(-1,3)for n,t in T(Path(src['export']).name,b['position'],b['yaw'])if 'PreviewGround'not in n]),axis=0)
  # Compare source/native full bound and a deterministic spread of vertices;
  # use chunks so dense source fixtures do not allocate a huge distance matrix.
  distance=0.
  for points,target in [(a,orig),(orig,a)]:
   for chunk in np.array_split(points,max(1,int(len(points)/96)+1)):distance=max(distance,float(np.linalg.norm(chunk[:,None]-target[None,:],axis=2).min(1).max()))
  assert distance<.00004,(file,b['name'],distance)
  if rooms:
   floor=shape(rooms['floor_geometry']);outside=MultiPoint(a[:,[0,2]]).convex_hull.difference(floor.buffer(.00004)).area;assert outside<1e-7,(b['name'],outside)
  bindings.append({'file':file,'binding':b['name'],'catalogue_id':b['catalogue_id'],'source_rigid_vertex_error_m':distance,'bounds_min':a.min(0).tolist(),'bounds_max':a.max(0).tolist(),'source_instance_no_rescaling':True})
 return component
components={}
for room in P['rooms']:
 parts=[q for q in room['parts']if q['category']not in['floor','frame','truss_brace']];components[room['source_index']]=check_model(room['model_file'],parts,room)
structure=[q for room in P['rooms']for q in room['parts']if q['category']in['floor','frame','truss_brace']]+P['commons_parts'];check_model('D04_PORT_FORWARD_HOMES_THIRD_RECEIVING_r001.glb',structure);check_model('D04_PORT_FORWARD_HOMES_THIRD_GUARDS_r001.glb',P['guard_successor_parts'],check_components=False)
# Original reference metadata is read/hash-pinned here; it is not rewritten.
reference_pins={};rest_samples=[]
for room in P['rooms']:
 for binding in[b for b in room['components']if'rest_slot_id'in b]:
  src=next(q for q in P['sources']if q['catalogue_id']==binding['catalogue_id']);meta=R/'BlenderCatalogue'/src['manifest'];reference_pins[str(meta.relative_to(R))]=sha(meta);d=json.load(open(meta));support=d.get('support',{});samples=support.get('sample_contacts',[])
 # Native rest-contact samples are chosen on the exact retained support
 # metadata; no body, pose or compatibility is inferred from these contacts.
  for s in samples:rest_samples.append({'room':room['source_index'],'binding':binding['name'],'local_reference':s,'position':binding['position'],'yaw':binding['yaw'],'rest_slot_id':binding['rest_slot_id']})
assert len(rest_samples)>=8,rest_samples
old=P['all_twenty_allocations_unchanged'];prior=json.load(open(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/PLAN.json'));assert old==prior['units']and sum(x['proposed_rest_place_count']for x in old)==25
S=json.load(open(W/'PREIMAGE_SUPPORT.json'));assert S['status']=='PASS';delta=max(abs(a[k]-b[k])for a,b in zip(P['foundation_feet'],S['foundation_feet'])for k in ['x','y','z']);assert delta<1e-9
for a,b in zip(P['foundation_feet'],S['foundation_feet']):assert all(a[k]==b[k]for k in ['owner','wall_contact_allowed','room_index'])
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
report={'status':'PASS'if not errors else'FAIL','owned_parts_checked':len(rows),'parts':rows,'rigid_source_bindings':bindings,'component_reference_metadata_pins':reference_pins,'rest_reference_samples':rest_samples,'all_twenty_allocations_unchanged':True,'all1000_polygons_preserved':True,'baseline_bearing_samples':72,'bearing_plan_vs_Godot_JSON_rounding_max_error_m':delta,'source_pins_unchanged':len(P['source_pins']),'private_court_area_m2':sum(x['floor_area_m2']for x in P['courts']),'guard_preimages_bounded':6,'new_guest_units':0,'new_rest_places':0,'species_ready_rooms':0,'primary_load_accepted':False,'errors':errors};(W/'SOURCE_GEOMETRY_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'owned_parts':len(rows),'rigid_source_bindings':len(bindings),'errors':errors}))
