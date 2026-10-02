"""Finite local hull overreach samples and complete clipped void triangle probes."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1];C=json.loads((BASE/'collision_proposals.json').read_text());rows=[]
def tree(vs,ps):return BVHTree.FromPolygons(vs,ps)
def inside(t,p):
 p=Vector(p);near=t.find_nearest(p)
 if near[3]is not None and near[3]<.000025:return True
 d=Vector((.937,.287,.199)).normalized();count=0;start=p.copy()
 for _ in range(100):
  co,no,ix,dist=t.ray_cast(start,d,100)
  if co is None:break
  count+=1;start=co+d*.000001
 return count%2==1
def clip(poly,axis,limit,keep_high):
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  a=p[axis]>=limit if keep_high else p[axis]<=limit;b=q[axis]>=limit if keep_high else q[axis]<=limit
  if a:out.append(p)
  if a!=b:out.append(p.lerp(q,(limit-p[axis])/(q[axis]-p[axis])))
 return out
def boxhits(triangles,lo,hi):
 n=0
 for tri in triangles:
  p=list(tri)
  for a in range(3):
   if p:p=clip(p,a,lo[a],True)
   if p:p=clip(p,a,hi[a],False)
  if p:n+=1
 return n
voids={'AST-BOT-007':[('lower_side_stem_zone',[.53,-.28,.06],[.80,.12,1.03])],'AST-BOT-008':[('front_soil_approach',[-.4,-.32,-.1],[.4,-.13,.35])],'AST-BOT-009':[('front_maintenance_strip',[-.5,-.37,0],[.5,-.28,.8])]}
for ident,c in C.items():
 r=json.loads((BASE/(ident+'.manifest.json')).read_text());bpy.ops.wm.open_mainfile(filepath=str(BASE/r['source']));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];ts={o.name:tree([v.co for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons])for o in obs};alltri=[]
 for o in obs:
  o.data.calc_loop_triangles();alltri += [[o.matrix_world@o.data.vertices[i].co for i in t.vertices]for t in o.data.loop_triangles]
 cols=[];htri=[]
 for h in c['shapes']:
  bm=bmesh.new();[bm.verts.new(p)for p in h['points_source_m']];bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False);bmesh.ops.triangulate(bm,faces=list(bm.faces));faces=[[v.co.copy()for v in f.verts]for f in bm.faces];htri+=faces;samples=[]
  for p in faces:
   for i in range(5):
    for j in range(5-i):samples.append(p[0]*(1-i/4-j/4)+p[1]*(i/4)+p[2]*(j/4))
  # This bounds sampled hull-surface discrepancy only. It does not claim a global Hausdorff proof.
  ds=[min(ts[n].find_nearest(p)[3]for n in h['covered_parts'])for p in samples];outside=[d for p,d in zip(samples,ds)if not any(inside(ts[n],p)for n in h['covered_parts'])];cols.append({'name':h['name'],'surface_samples':len(samples),'maximum_sampled_surface_distance_m':max(ds),'sampled_surface_points_outside_covered_source':len(outside),'maximum_sampled_overreach_m':max(outside or[0]),'scope':'Finite hull-surface-to-covered-source distance; buried adjacent-ring caps included; not global volume/engine proof'});bm.free()
 vv=[]
 for name,lo,hi in voids[ident]:
  vh=boxhits(alltri,lo,hi);ch=boxhits(htri,lo,hi);vv.append({'name':name,'min_source_m':lo,'max_source_m':hi,'visual_triangle_intersections':vh,'collision_hull_triangle_intersections':ch,'passes':vh==0 and ch==0})
 rows.append({'catalogue_id':ident,'source_sha256':r['source_sha256'],'glb_sha256':r['glb_sha256'],'compound_count':len(cols),'shapes':cols,'void_probes':vv,'positive_control_actual_root_marker_count':len([m for m in r['physical_and_proposal_markers']if m['physical_part']]),'no_foliage_bounds_collider':all(not any(x in h['name']for x in ['leaf','fan_petiole','petal'])for h in c['shapes']),'passes':all(v['passes']for v in vv)})
(BASE/'qa/collision_profile_checks.json').write_text(json.dumps({'assets':rows,'all_passed':all(r['passes']for r in rows)},indent=2)+'\n');print([(r['catalogue_id'],r['passes'],r['compound_count'])for r in rows])
