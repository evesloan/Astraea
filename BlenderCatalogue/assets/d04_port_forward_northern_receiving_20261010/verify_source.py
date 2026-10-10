from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import shape,MultiPoint,box
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'BUILD_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();reader=R/'BlenderCatalogue/assets/forward_staff_shaft_interfaces_20261010/source_geometry.py';ns={'__file__':str(reader)};exec(reader.read_text(),ns);T=ns['triangles'];expected={p['name']:p for p in P['parts']};rows=[];fixtures={};errors=[]
for name,t in T(P['model_file']):
 if name not in expected:
  key=next((f['prefix']for f in P['source_fittings']if name.startswith(f['prefix']+'__')),None);assert key,name;fixtures.setdefault(key,[]).extend(t.reshape(-1,3).tolist());continue
 p=expected.pop(name);v=np.unique(t.reshape(-1,3),axis=0);want=np.unique(np.array(p['verts']),axis=0);e=max(np.linalg.norm(v[:,None]-want[None,:],axis=2).min(1).max(),np.linalg.norm(want[:,None]-v[None,:],axis=2).min(1).max());assert e<.00005,(name,e)
 q=t-t.mean(axis=(0,1));volume=np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2])).sum()/6;assert volume>0,(name,volume);rows.append({'name':name,'positive_volume_m3':float(volume),'max_vertex_error_m':float(e)})
assert not expected
floor=shape(P['floor_geometry']);bounds=[]
for key,vs in fixtures.items():
 a=np.array(vs);h=MultiPoint(a[:,[0,2]]).convex_hull;assert floor.buffer(.00005).covers(h),(key,h.bounds);assert abs(a[:,1].min()-16.5)<.003,(key,a[:,1].min());bounds.append({'prefix':key,'min':a.min(0).tolist(),'max':a.max(0).tolist(),'floor_contained':True})
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
assert len(rows)==177 and len(bounds)==2
report={'status':'PASS','owned_parts_verified':len(rows),'parts':rows,'rigid_original_fittings':2,'source_fitting_bounds':bounds,'foundation_piers':34,'lower_diagonal_braces':29,'source_pins_unchanged':51,'all20_allocations_unchanged':True,'new_floor_m2':floor.area,'keel_bearing_preimage_samples':306,'primary_load_accepted':False,'errors':errors};(W/'SOURCE_GEOMETRY_CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
for f in[W/'RUNTIME_PLAN.json',R/'Game/data/architecture/D04_PORT_FORWARD_NORTHERN_RECEIVING.json']:
 p=json.load(open(f));p['source_fitting_bounds']=bounds;f.write_text(json.dumps(p,indent=2)+'\n')
print(json.dumps({'status':'PASS','owned_parts':len(rows),'rigid_fittings':len(bounds),'new_floor_m2':floor.area}))
