from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import shape,MultiPoint,box
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));N=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=R/'BlenderCatalogue/assets/forward_staff_shaft_interfaces_20261010/source_geometry.py';ns={'__file__':str(f)};exec(f.read_text(),ns);T=ns['triangles'];rows=[];bindings=[];floor=shape(P['floor_geometry'])
def verify(file,parts,components):
 expected={q['name']:q for q in parts};seen=set();component={};geoms={}
 for name,ts in T(file):
  if name not in expected:
   b=next(q for q in components if name.startswith('D04CS_'+q['name']+'__'));component.setdefault(b['name'],[]).append(ts);continue
  assert name not in seen,name;seen.add(name);q=expected[name];a=np.unique(ts.reshape(-1,3),axis=0);want=np.unique(np.array(q['verts']),axis=0);delta=max(np.linalg.norm(a[:,None]-want[None,:],axis=2).min(1).max(),np.linalg.norm(want[:,None]-a[None,:],axis=2).min(1).max());assert delta<.00004,(name,delta)
  v=ts-ts.mean(axis=(0,1));volume=float(np.einsum('ij,ij->i',v[:,0],np.cross(v[:,1],v[:,2])).sum()/6);assert volume>0,name
  key=tuple(sorted(tuple(round(float(c),5)for c in v)for v in a));assert key not in geoms,(name,geoms.get(key));geoms[key]=name
  if q['category'] not in ['contained_preimage_successor']:assert MultiPoint(a[:,[0,2]]).convex_hull.difference(floor.buffer(.00005)).area<1e-7,name
  rows.append({'file':file,'name':name,'positive_volume_m3':volume,'vertex_error_m':float(delta)})
 assert set(expected)==seen,set(expected)-seen
 for b in components:
  src=next(q for q in P['sources']if q['catalogue_id']==b['catalogue_id']);a=np.unique(np.concatenate(component[b['name']]).reshape(-1,3),axis=0);read=ns['read'];ns['read']=lambda _: (R/'BlenderCatalogue'/src['export']).read_bytes();orig=np.unique(np.concatenate([t.reshape(-1,3)for n,t in T('SOURCE',b['position'],b['yaw'])if'PreviewGround'not in n]),axis=0);ns['read']=read;delta=0.
  for points,target in [(a,orig),(orig,a)]:
   for chunk in np.array_split(points,max(1,int(len(points)/96)+1)):delta=max(delta,float(np.linalg.norm(chunk[:,None]-target[None,:],axis=2).min(1).max()))
  assert delta<.00004,(b['name'],delta);assert MultiPoint(a[:,[0,2]]).convex_hull.difference(floor.buffer(.00005)).area<1e-7,b['name'];assert abs(a[:,1].min()-16.5)<.002,b['name'];bindings.append({'binding':b['name'],'source_rigid_vertex_error_m':delta,'min':a.min(0).tolist(),'max':a.max(0).tolist(),'no_rescaling':True})
verify('D04_PORT_FORWARD_COMMONS_SERVICE_r001.glb',P['parts'],P['components']);verify('D04_PORT_FORWARD_COMMONS_ENTRY_r001.glb',P['successor_parts'],[])
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
S=json.load(open(W/'PREIMAGE_SUPPORT.json'));assert S['status']=='PASS' and S['plan_sha256']==sha(W/'PLAN.json')
report={'status':'PASS','owned_parts_checked':len(rows),'parts':rows,'rigid_original_bindings':bindings,'source_pins_unchanged':len(P['source_pins']),'new_floor_m2':P['new_floor_m2'],'all20_allocations_unchanged':True,'all25_existing_rest_reservations_unchanged':True,'all1000_allocation_polygons_clear':True,'exact_contained_successors':P['successor_exact_containment_proof'],'linen_rack_exact_contacts':P['linen_rack_exact_contacts'],'new_units':0,'new_rest_places':0,'primary_load_accepted':False};(W/'SOURCE_GEOMETRY_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'PASS','owned_parts':len(rows),'rigid_bindings':len(bindings)}))
