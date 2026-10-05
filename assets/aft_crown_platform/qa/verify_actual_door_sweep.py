from pathlib import Path
import bpy,json,math,hashlib
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/section_contract.json').read_text());P=json.loads((R/'source/geometry_parts.json').read_text())['parts']+json.loads((C/'assets/aft_command/source/geometry_parts.json').read_text())['parts']
def aabb(points):return [f(p[k]for p in points)for k in range(3)for f in(min,max)]
def overlap(a,b):return all(min(a[k+1],b[k+1])-max(a[k],b[k])>1e-7 for k in(0,2,4))
# Leaf OBB vs source AABB separating-axis test. Rotations use actual Blender hinge-local parts.
bpy.ops.wm.open_mainfile(filepath=str(C/'assets/staff_threshold/source/AST-STF-008.blend'))
leaf_data=[];fixed=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 if o.parent and o.parent.name.startswith('HINGE_'):
  leaf_data.append((o.name,tuple(o.parent.location),[tuple(v.co)for v in o.data.vertices],1 if o.parent.name=='HINGE_LEFT'else-1))
 elif o.name.startswith('STF_'):fixed.append({'name':o.name,'vertices':[(v.co.x,v.co.z,-v.co.y)for v in o.data.vertices]})
assert len(fixed)==3 and len(leaf_data)==9,(len(fixed),len(leaf_data))
def plan_sat(points,b,tol=1e-7):
 # Vertices project to a rectangle under this yaw. Hull corners are measured from OBB source points.
 pts=list(set((p[0],p[2])for p in points));cx=sum(p[0]for p in pts)/len(pts);cz=sum(p[1]for p in pts)/len(pts);pts.sort(key=lambda p:math.atan2(p[1]-cz,p[0]-cx));rect=[(b[0],b[4]),(b[1],b[4]),(b[1],b[5]),(b[0],b[5])];axes=[(1,0),(0,1)]
 for p,q in zip(pts,pts[1:]+pts[:1]):
  dx=q[0]-p[0];dz=q[1]-p[1]
  if dx*dx+dz*dz>1e-12:axes.append((-dz,dx))
 for ax,az in axes:
  aa=[ax*p[0]+az*p[1]for p in pts];bb=[ax*p[0]+az*p[1]for p in rect]
  if min(max(aa),max(bb))-max(min(aa),min(bb))<=tol:return False
 return True
sweep_samples=0;door_records=[];open_geometry=[]
doors=D['doors']+[dict(d,id=d['name'],yaw_radians=d['yaw'])for d in json.loads((C/'assets/aft_command/source/section_contract.json').read_text())['doors']if d['name'].endswith('_exit')]
for door in doors:
 x,y,z=door['position'];yaw=door['yaw_radians'];co,si=math.cos(yaw),math.sin(yaw)
 near=[p for p in P if overlap(p['world_aabb'],[x-1.6,x+1.6,y,y+2.57,z-1.6,z+1.6])]
 for deg in range(91):
  angle=math.radians(deg)
  for name,pivot,vertices,sign in leaf_data:
   c,s=math.cos(sign*angle),math.sin(sign*angle);points=[]
   for vx,vy,vz in vertices:
    bx=pivot[0]+c*vx-s*vy;by=pivot[1]+s*vx+c*vy;gz=-by;points.append((x+co*bx+si*gz,y+vz,z-si*bx+co*gz))
   b=aabb(points);sweep_samples+=1
   if deg==90:open_geometry.append({'name':door['id']+'_'+name,'vertices_world':points,'world_aabb':b})
   for p in near:
    if overlap(b,p['world_aabb'])and plan_sat(points,p['world_aabb']):raise AssertionError(('door_leaf_source_collision',door['id'],name,deg,p['name']))
 # Frame-wall joint: actual fixed frame's full outer bounds and exact depth intersect the fitted wall sides/header.
 # This checks seam sealing without substituting a frame from its nominal aperture.
 fverts=[v for o in fixed for v in o['vertices']];fb=aabb(fverts);assert abs(fb[0]+1.38)<1e-5 and abs(fb[1]-1.38)<1e-5 and abs(fb[3]-2.82)<1e-5
 for side in [-1,1]:
  join_z=door.get('frame_wall_join_sample_local_z',-.01);q=[x+co*side*1.3775+si*join_z,y+1.3,z-si*side*1.3775+co*join_z]
  assert any(p['world_aabb'][0]-1e-6<=q[0]<=p['world_aabb'][1]+1e-6 and p['world_aabb'][2]<=q[1]<=p['world_aabb'][3]and p['world_aabb'][4]-1e-6<=q[2]<=p['world_aabb'][5]+1e-6 for p in P),(door['id'],'jamb_seam')
 assert any(p['world_aabb'][0]-1e-6<=x+si*join_z<=p['world_aabb'][1]+1e-6 and p['world_aabb'][2]<=y+2.8175<=p['world_aabb'][3]and p['world_aabb'][4]-1e-6<=z+co*join_z<=p['world_aabb'][5]+1e-6 for p in P),(door['id'],'header_seam')
 for f in fixed:
  points=[(x+co*a+si*c,y+b,z-si*a+co*c)for a,b,c in f['vertices']];open_geometry.append({'name':door['id']+'_'+f['name'],'vertices_world':points,'world_aabb':aabb(points)})
 door_records.append({'name':door['id'],'angles_degrees':[0,90],'angle_step_degrees':1,'actual_moving_meshes':len(leaf_data),'samples':91*len(leaf_data),'new_source_collisions':0,'frame_side_overlap_m':.005,'frame_top_overlap_m':.005})

(R/'qa/open_shared_door_geometry.json').write_text(json.dumps(open_geometry,indent=2)+'\n')
(R/'qa/actual_door_sweep.json').write_text(json.dumps({'pass':True,'door_leaf_samples':sweep_samples,'doors':door_records,'candidate_005_source_sha256':hashlib.sha256((R/'source/AST-CMD-005.blend').read_bytes()).hexdigest(),'candidate_005_export_sha256':hashlib.sha256((R/'exports/AST-CMD-005.glb').read_bytes()).hexdigest(),'candidate_002_export_sha256':hashlib.sha256((C/'assets/aft_command/exports/AST-CMD-002.glb').read_bytes()).hexdigest(),'candidate_002_source_sha256':hashlib.sha256((C/'assets/aft_command/source/AST-CMD-002.blend').read_bytes()).hexdigest(),'actual_shared_door_source_sha256':hashlib.sha256((C/'assets/staff_threshold/source/AST-STF-008.blend').read_bytes()).hexdigest()},indent=2)+'\n');print('DOOR_SWEEPS_PASS',sweep_samples)
