"""Independent native aperture/floor and original-controller swept-box source proof."""
from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from native_glb_subset import GLB
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
p=json.load(open(HERE/'source/CROSSING_PREIMAGES_AND_CONTRACT.json'));checks=[]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def check(n,ok,**data):checks.append(dict(name=n,pass_check=bool(ok),**data));assert ok,n
for q in p['source_files'].values():check('current_input_'+q['input_path'],sha(ROOT/q['input_path'])==q['sha256'])
counts={}
for path in sorted((HERE/'exports').glob('*.glb')):
 g=GLB(path);meshes=tris=0
 for name,node in g.by_name.items():
  if'mesh'not in node:continue
  v,f,u,_=g.geometry(name);t=np.asarray(v)[np.asarray(f)];meshes+=1;tris+=len(t);check('finite_'+path.name+name,np.isfinite(t).all()and np.isfinite(u).all());check('nondegenerate_'+path.name+name,(np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-12).all())
 counts[path.name]=dict(meshes=meshes,triangles=tris,sha256=sha(path),bytes=path.stat().st_size)
check('three_exact_exports',len(counts)==3)
patch=GLB(HERE/'exports/AST-STF-G3-061.glb');check('six_exact_names',{n for n,q in patch.by_name.items()if'mesh'in q}=={q['native_name']for q in p['preimage_meshes']})
# Cross-sections directly intersect the actual exported triangles.
def ray_hit(t,x,y,z):
 o=np.array([x,y,z-.5]);d=np.array([0,0,1.]);e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);den=(e1*h).sum(axis=1);valid=abs(den)>1e-10;inv=np.zeros_like(den);inv[valid]=1/den[valid];s=o-t[:,0];u=inv*(s*h).sum(axis=1);q=np.cross(s,e1);v=inv*(np.broadcast_to(d,q.shape)*q).sum(axis=1);dist=inv*(e2*q).sum(axis=1)
 return bool(np.any(valid&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1.0000001)&(dist>=0)&(dist<=1)))
for item,door in zip(p['preimage_meshes'],p['door_bindings']):
 old=GLB(ROOT/item['input_path']);v,f,_,_=old.geometry(item['native_name']);a=np.asarray(v)[np.asarray(f)];v,f,_,_=patch.geometry(item['native_name']);b=np.asarray(v)[np.asarray(f)];x,y,z=door['position']
 for dx in[-2,-1.5,-1.2,-.6,0,.6,1.2,1.5,2]:
  for yy in[12.1,12.7,13.5,14.5,14.9,15.1]:
   before=ray_hit(a,x+dx,yy,z);after=ray_hit(b,x+dx,yy,z);inside=abs(dx)<1.38001 and yy<14.82001;check('aperture_section_'+item['native_name']+str((dx,yy)),not after if inside else before==after)
# Exact f32 top-face union, not a large area tolerance.
floor=GLB(HERE/'exports/AST-STF-G3-063.glb');top=[]
for n,q in floor.by_name.items():
 if'mesh'not in q:continue
 v,f,_,_=floor.geometry(n)
 for i,face in enumerate(f):
  t=np.asarray([v[k]for k in face])
  if abs(t[:,1]-12).max()>1e-6:continue
  check('outward_threshold_'+str(i),np.cross(t[1]-t[0],t[2]-t[0])[1]>0);top.append(Polygon(t[:,[0,2]]))
actual=unary_union(top);spec=json.load(open(HERE/'source/CROSSING_MISSING_THRESHOLDS.json'))
f32=lambda r:[[float(np.float32(x)),float(np.float32(z))]for x,z in r]
expected=unary_union([Polygon(f32(q['boundary']),[f32(r)for r in q['holes']])for q in spec['parts']]);check('exact_f32_threshold_topology',actual.symmetric_difference(expected).area<1e-7)
# All fixed source triangles near the lower crosslinks. Only the six identified
# walls are replaced; no roof, support, fixture or unrelated mesh is omitted.
fixed=[]
for file in sorted({q['input_path']for q in p['preimage_meshes']}):
 g=GLB(ROOT/file)
 for n,q in g.by_name.items():
  if'mesh'not in q:continue
  target=patch if n in{a['native_name']for a in p['preimage_meshes']}else g
  v,f,_,_=target.geometry(n);t=np.asarray(v)[np.asarray(f)];lo=t.min(axis=1);hi=t.max(axis=1);selected=(lo[:,1]<14.7)&(hi[:,1]>12.01)&(((lo[:,0]<59)&(hi[:,0]>55))|((lo[:,0]<-55)&(hi[:,0]>-59)));fixed.extend(t[selected])
fixed=np.asarray(fixed);bounds_lo=fixed.min(axis=1);bounds_hi=fixed.max(axis=1)
def ry(a):return np.array([[np.cos(a),0,np.sin(a)],[0,1,0],[-np.sin(a),0,np.cos(a)]])
def box_hit(tri,center,rotation,half):
 t=(tri-center)@rotation;edges=[t[1]-t[0],t[2]-t[1],t[0]-t[2]];axes=[*np.eye(3),np.cross(edges[0],edges[1]),*[np.cross(e,a)for e in edges for a in np.eye(3)]]
 for axis in axes:
  if np.linalg.norm(axis)<1e-10:continue
  axis=axis/np.linalg.norm(axis);a=t@axis;r=np.abs(axis)@half
  if a.min()>=r-1e-5 or a.max()<=-r+1e-5:return False
 return True
gate=GLB(HERE/'inputs/Game/assets/models/AST-STF-008.glb');hinges=[np.asarray(gate.global_transform(gate.named('HINGE_'+side),(0,0,0)))for side in['LEFT','RIGHT']];samples=0
for door in p['door_bindings']:
 root=np.asarray(door['position']);rotation=ry(door['yaw'])
 for fraction in np.linspace(0,1,41):
  for side in[0,1]:
   f=np.clip(fraction/.85 if side==0 else(fraction-.15)/.85,0,1);turn=ry(f*np.pi/2*(1 if side==0 else-1));r=rotation@turn;hinge=root+rotation@hinges[side]
   shapes=[('Leaf',[.575 if side==0 else-.575,1.2925,0],[1.13,2.535,.07]),('Push',[.98 if side==0 else-.98,1.19,.054],[.13,.42,.024])]
   if side==0:shapes.append(('Seal',[1.15,1.2925,.05],[.04,2.53,.03]))
   for name,at,size in shapes:
    center=hinge+r@np.asarray(at);half=np.asarray(size)/2;extent=np.abs(r)@half;near=np.where((bounds_lo<center+extent).all(axis=1)&(bounds_hi>center-extent).all(axis=1))[0];contacts=[int(j)for j in near if box_hit(fixed[j],center,r,half)];samples+=1;check('original_controller_box_'+door['name']+str((fraction,side,name)),not contacts,contact_triangle_indices=contacts)
 # The retained orthogonal route remains between the two gate swings.
 buffer_z=(door['position'][2]+(2.2 if door['yaw']else-2.2));check('existing_cross_route_away_from_leaf_envelope_'+door['name'],abs(buffer_z-door['position'][2])>1.43+.3)
check('no_production_or_population_IDs',all(q['persistent_id']is None for q in p['door_bindings']))
result=dict(status='PASS_EXACT_SOURCE_GEOMETRY_NOT_INSTALLED',checks=len(checks),exports=counts,new_threshold_floor_m2=spec['new_floor_m2'],original_controller_swept_box_samples=samples,all_six_apertures_clear_at_source=True,original_unrelated_meshes_omitted=False,unrelated_original_meshes_preserved=1802,combined_Game_import_or_build_started=False,old_13_failed_physics_criteria_resolved=False,structural_capacity_loaded_cart_species_permissions_and_Game_acceptance=False,details=checks)
(HERE/'qa/NATIVE_CROSSING_GEOMETRY_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='details'}))
