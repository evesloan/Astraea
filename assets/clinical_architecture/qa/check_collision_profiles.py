"""Finite structural collision approximation sampling against evaluated source union."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tree(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();v=[ob.matrix_world@x.co for x in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();return BVHTree.FromPolygons(v,f,all_triangles=True)
def points(c):
 if c['type']=='box':return [[c[('min_'if i==0 else'max_')+'source_m'][0],c[('min_'if j==0 else'max_')+'source_m'][1],c[('min_'if k==0 else'max_')+'source_m'][2]]for i in(0,1)for j in(0,1)for k in(0,1)]
 return c['points_source_m']
records=[]
for ident,col in json.loads((BASE/'collision_proposals.json').read_text()).items():
 p=BASE/'source'/f'{ident}.blend';before=sha(p);bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.scene.frame_set(1);trees=[tree(o)for o in bpy.context.scene.objects if o.type=='MESH'and'material_role'in o];results=[]
 for c in col['shapes']:
  bm=bmesh.new();verts=[bm.verts.new(v)for v in points(c)];bmesh.ops.convex_hull(bm,input=verts,use_existing_faces=False);bmesh.ops.triangulate(bm,faces=list(bm.faces));samples=[]
  for f in bm.faces:
   if len(f.verts)!=3:continue
   a,b,d=[v.co.copy()for v in f.verts]
   for i in range(7):
    for j in range(7-i):samples.append(a*(1-(i+j)/6)+b*(i/6)+d*(j/6))
  maximum=0;worst=None
  for pt in samples:
   nearest=[t.find_nearest(pt)for t in trees];inside=any((pt-h[0]).dot(h[1])< -1e-7 for h in nearest if h[0] is not None)
   dist=0 if inside else min(h[3]for h in nearest if h[0] is not None)
   if dist>maximum:maximum=dist;worst=list(pt)
  results.append({'name':c['name'],'surface_sample_count':len(samples),'sampled_exterior_overreach_max_m':maximum,'worst_sample_source_m':worst});bm.free()
 records.append({'catalogue_id':ident,'source_sha256':before,'compound_count':len(col['shapes']),'samples':results,'maximum_sampled_exterior_overreach_m':max(x['sampled_exterior_overreach_max_m']for x in results),'unchanged':before==sha(p)})
report={'scope':'Finite surface samples on structural boxes/convex hulls; nearest evaluated union sign test. Not an exhaustive bound, engine profile/actor guarantee, or motion physics. Decorative contours and rounded edges may be overcovered. Full declared void exclusion is separately checked.','results':records,'checker_sha256':sha(Path(__file__))};(BASE/'qa/collision_profile_samples.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
