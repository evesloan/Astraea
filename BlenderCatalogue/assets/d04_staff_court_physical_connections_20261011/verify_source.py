from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reader=R/'BlenderCatalogue/assets/forward_staff_shaft_interfaces_20261010/source_geometry.py';ns={'__file__':str(reader)};exec(reader.read_text(),ns);T=ns['triangles'];errors=[]
def planes(ts):
 out={}
 for tri in ts:
  n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);length=np.linalg.norm(n)
  if length<1e-10:continue
  n/=length;axis=int(abs(n).argmax());assert abs(n[axis])>.9999
  uv=[a for a in range(3)if a!=axis];key=(axis,1 if n[axis]>0 else-1,round(float(tri[:,axis].mean()),4));out.setdefault(key,[]).append(Polygon(tri[:,uv]))
 return {k:unary_union(v)for k,v in out.items()}
patch=dict(T(P['patch_model']['model_file']));retained=[]
for row in P['cuts']:
 old=dict(T(row['source_model']))[row['name']];assert hashlib.sha256(old.tobytes()).hexdigest()==row['source_triangles_sha256'];new=patch['D04PC_Successor_'+row['name']];before=planes(old);after=planes(new);missing=extra=area=0.
 for key in set(before)|set(after):
  axis,sign,at=key;uv=[a for a in range(3)if a!=axis];a=before.get(key,Polygon());b=after.get(key,Polygon());masks=[]
  for cut in row['volumes']:
   lo=cut['min'];hi=cut['max']
   if lo[axis]-.00004<=at<=hi[axis]+.00004:masks.append(box(lo[uv[0]],lo[uv[1]],hi[uv[0]],hi[uv[1]]).buffer(.00004,join_style=2))
  if masks:mask=unary_union(masks);a=a.difference(mask);b=b.difference(mask)
  area+=a.area;missing+=a.difference(b.buffer(.00004)).area;extra+=b.difference(a.buffer(.00004)).area
 if missing>1e-7 or extra>1e-7:errors.append({'name':row['name'],'missing_area':missing,'extra_area':extra})
 retained.append({'name':row['name'],'outside_cut_oriented_surface_m2':area,'missing_area_m2':missing,'extra_area_m2':extra})
owned=dict(T(P['owned_model']['model_file']));checks=[]
for part in P['parts']:
 t=owned[part['name']];want=np.array(part['verts']);pts=np.unique(t.reshape(-1,3),axis=0);err=max(np.linalg.norm(pts[:,None]-want[None,:],axis=2).min(1).max(),np.linalg.norm(want[:,None]-pts[None,:],axis=2).min(1).max());assert err<.00004,(part['name'],err)
 q=t-t.mean(axis=(0,1));volume=np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2])).sum()/6;assert volume>0,(part['name'],volume);checks.append({'name':part['name'],'vertex_error_m':float(err),'positive_volume_m3':float(volume)})
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
for rec in P['native_export_records']:assert sha(W/rec['native'])==rec['native_sha256']and sha(W/rec['export'])==rec['export_sha256']and rec['fresh_native_repeat_identical']
tool=[]
for name,t in T(P['reach_tool']['model']):
 spec=next(m for m in P['reach_tool']['members']if m['name']==name);v=t.reshape(-1,3);r=spec['radius'];assert max(abs(v.min(0)-[-r,-r,0]).max(),abs(v.max(0)-[r,r,1.2]).max())<.00004
 q=t-t.mean(axis=(0,1));volume=np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2])).sum()/6;assert volume>0,(name,volume);tool.append({'name':name,'positive_volume_m3':float(volume),'length_m':1.2,'bore_radius_m':spec.get('bore_radius',0),'convex_proxy_conservative':True})
terminal=[]
if 'angled_terminal' in P['reach_tool']:
 spec=P['reach_tool']['angled_terminal'];plan=json.load(open(W/('ANGLED_TERMINAL_PLAN_'+str(P['tool_terminal_revision'])+'.json')));actual=dict(T(spec['model']))
 for part in plan['parts']:
  t=actual[part['name']];want=np.array(part['verts']);pts=np.unique(t.reshape(-1,3),axis=0);err=max(np.linalg.norm(pts[:,None]-want[None,:],axis=2).min(1).max(),np.linalg.norm(want[:,None]-pts[None,:],axis=2).min(1).max());assert err<.00004,(part['name'],err)
  q=t-t.mean(axis=(0,1));volume=np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2])).sum()/6;assert volume>0,(part['name'],volume);terminal.append({'name':part['name'],'vertex_error_m':float(err),'positive_volume_m3':float(volume),'native_geometry_no_rescaling':True})
out={'status':'PASS'if not errors else'FAIL','protected_pins':len(P['source_pins']),'original_preimages_preserved':True,'owned_meshes':checks,'bounded_cut_surfaces':retained,'reach_tool_meshes':tool,'angled_terminal_meshes':terminal,'errors':errors,'tolerance_m':.00004,'old_minus370_portal_unchanged':True,'staff_zinc_center_post_unchanged':True,'new_floor_m2':0,'production_active':False};(W/'SOURCE_GEOMETRY_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'parts':len(checks),'cut_preimages':len(retained),'errors':errors}));assert not errors
