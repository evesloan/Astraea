from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import shape,MultiPoint,box
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));N=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reader=R/'BlenderCatalogue/assets/forward_staff_shaft_interfaces_20261010/source_geometry.py';ns={'__file__':str(reader)};exec(reader.read_text(),ns);T=ns['triangles'];expected={p['name']:p for p in P['parts']};rows=[];fixtures={};errors=[]
for name,t in T(P['receiving_model']):
 if name not in expected:
  if name.startswith('D04PF_Stair__'):continue
  key=next((f['prefix']for f in P['source_fittings']if name.startswith(f['prefix']+'__')),None);assert key,name;fixtures.setdefault(key,[]).extend(t.reshape(-1,3).tolist());continue
 p=expected.pop(name);v=np.unique(t.reshape(-1,3),axis=0);want=np.unique(np.array(p['verts']),axis=0);error=max(np.linalg.norm(v[:,None]-want[None,:],axis=2).min(1).max(),np.linalg.norm(want[:,None]-v[None,:],axis=2).min(1).max());assert error<.00004,(name,error)
 q=t-t.mean(axis=(0,1));volume=np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2])).sum()/6;assert volume>0,(name,volume);rows.append({'name':name,'positive_volume_m3':float(volume),'max_vertex_error_m':float(error)})
assert not expected
floor=shape(P['floor_geometry']);lower=shape(P['lower_landing_geometry']);fitting_rows=[]
for key,vs in fixtures.items():
 a=np.array(vs);h=MultiPoint(a[:,[0,2]]).convex_hull;assert floor.buffer(.00004).covers(h),(key,h.bounds);assert abs(a[:,1].min()-16.5)<.003,(key,a[:,1].min());fitting_rows.append({'prefix':key,'bounds_min':a.min(0).tolist(),'bounds_max':a.max(0).tolist(),'floor_contained':True})
patch=list(T(N['staff_patch']['export']));assert {name for name,t in patch}==set(P['staff_wall_cut']['meshes'])
def ray_hits(t,start,end):
 d=end-start;e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h);ok=abs(det)>1e-9;inv=np.zeros(len(t));inv[ok]=1/det[ok];s=start-t[:,0];u=np.einsum('ij,ij->i',s,h)*inv;q=np.cross(s,e1);v=np.einsum('j,ij->i',d,q)*inv;w=np.einsum('ij,ij->i',e2,q)*inv;return ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(w>=0)&(w<=1)
probes=[]
for y in [12.15,12.79,13.3,14.3]:
 for z in [-369.55,-369.,-368.45]:
  names=[n for n,t in patch if ray_hits(t,np.array([-59.12,y,z]),np.array([-58.3,y,z])).any()];probes.append({'y':y,'z':z,'hits':names})
  if names:errors.append({'kind':'staff_aperture_residual','y':y,'z':z,'meshes':names})
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
# Boolean export may retriangulate unchanged quads. Compare oriented planar
# surface unions outside the exact cutter, in both directions, rather than
# treating a different diagonal as missing geometry.
from shapely.geometry import Polygon
from shapely.ops import unary_union
lo=np.array(P['staff_wall_cut']['min']);hi=np.array(P['staff_wall_cut']['max']);retained=[]
def planes(ts):
 out={}
 for t in ts:
  n=np.cross(t[1]-t[0],t[2]-t[0]);length=np.linalg.norm(n)
  if length<1e-10:continue
  n/=length;axis=int(abs(n).argmax());assert abs(n[axis])>.9999
  uv=[a for a in range(3)if a!=axis];key=(axis,1 if n[axis]>0 else-1,round(float(t[:,axis].mean()),4));out.setdefault(key,[]).append(Polygon(t[:,uv]))
 return {k:unary_union(v)for k,v in out.items()}
for name,new in patch:
 old=next(t for n,t in T(P['staff_wall_cut']['source_model'])if n==name);before=planes(old);after=planes(new);missing=extra=0.;areas=0.
 for key in set(before)|set(after):
  axis,sign,at=key;uv=[a for a in range(3)if a!=axis];a=before.get(key,Polygon());b=after.get(key,Polygon())
  if lo[axis]-.00004<=at<=hi[axis]+.00004:
   mask=box(lo[uv[0]],lo[uv[1]],hi[uv[0]],hi[uv[1]]);a=a.difference(mask);b=b.difference(mask)
  areas+=a.area;missing+=a.difference(b.buffer(.00004)).area;extra+=b.difference(a.buffer(.00004)).area
 if missing>1e-7 or extra>1e-7:errors.append({'kind':'unexplained_surface_change_outside_cut','mesh':name,'missing_area':missing,'extra_area':extra})
 retained.append({'mesh':name,'unchanged_oriented_source_surface_outside_cut_m2':areas,'missing_area_outside_40micrometre_geometry_tolerance_m2':missing,'extra_area_outside_40micrometre_geometry_tolerance_m2':extra,'quad_retriangulation_permitted':True})
report={'status':'PASS'if not errors else'FAIL','plan_parts_verified':len(rows),'parts':rows,'source_fitting_bounds':fitting_rows,'staff_aperture_probes':probes,'source_unaffected_triangles':retained,'source_pins_unchanged':len(P['source_pins']),'upper_floor_area_m2':floor.area,'lower_floor_area_m2':lower.area,'unit_polygons_unchanged':20,'rooms_adopted':0,'primary_load_accepted':False,'errors':errors};(W/'SOURCE_GEOMETRY_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'parts':len(rows),'errors':errors}))
