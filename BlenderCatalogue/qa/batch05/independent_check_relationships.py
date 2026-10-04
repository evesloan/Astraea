"""Read-only actual source connectivity screen, not strength or physical validation."""
import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05'
def geometry(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles()
 vs=[o.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles]
 weldmap={};iv=[]
 for v in vs:iv.append(weldmap.setdefault(tuple(round(c,6) for c in v),len(weldmap)))
 edges={}
 for face in fs:
  f=tuple(iv[k] for k in face)
  for a,b in zip(f,f[1:]+f[:1]):
   e=tuple(sorted((a,b)));edges[e]=edges.get(e,0)+1
 g={'v':vs,'f':fs,'bvh':BVHTree.FromPolygons(vs,fs,all_triangles=True),'lo':[min(v[i] for v in vs) for i in range(3)],'hi':[max(v[i] for v in vs) for i in range(3)],'boundary_edges':sum(n==1 for n in edges.values()),'nonmanifold_edges':sum(n>2 for n in edges.values())}
 ev.to_mesh_clear();return g
def check_pair(a,b):
 count=len(a['bvh'].overlap(b['bvh']));dist=math.inf;inside=0
 for p in a['v']:
  co,n,idx,d=b['bvh'].find_nearest(p)
  if co is None:continue
  dist=min(dist,d)
  if d<1e-5 or (p-co).dot(n)<-1e-5:inside+=1
 return {'triangle_intersections':count,'sampled_vertex_to_surface_min_m':dist,'a_vertices_on_or_inside_b_by_nearest_normal':inside,'candidate_connected':bool(count or dist<=1e-5 or inside)}
rows=[]
for folder in ['aquatic_lounge','aquatic_edges','aquatic_float']:
 for p in sorted((ROOT/'assets'/folder).rglob('*.blend')):
  if 'qa' in p.relative_to(ROOT/'assets'/folder).parts:continue
  bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False)
  obs={o.name:o for o in bpy.context.scene.objects if o.type in ['MESH','CURVE'] and not o.get('qa_only',False)}
  geos={n:geometry(o) for n,o in obs.items()}
  row={'source':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'parts':[],'candidate_contact_pairs':[],'isolated_parts':[],'scope':'Independent evaluated source mesh connectivity screen. AABB-gated BVH intersections and sampled signed nearest surfaces detect likely joints; not watertight unions, strength, physics or collision acceptance.'}
  connected={n:[] for n in obs}
  for n,g in geos.items():
   row['parts'].append({'part':n,'min_xyz':g['lo'],'max_xyz':g['hi'],'boundary_edges':g['boundary_edges'],'nonmanifold_edges':g['nonmanifold_edges'],'triangles':len(g['f']),'vertices':len(g['v'])})
  names=list(geos)
  for i,n in enumerate(names):
   a=geos[n]
   for m in names[i+1:]:
    b=geos[m]
    if any(min(a['hi'][k],b['hi'][k])+1e-5<max(a['lo'][k],b['lo'][k]) for k in range(3)):continue
    q=check_pair(a,b)
    if not q['candidate_connected']:
     inv=check_pair(b,a);q['reverse_sample']=inv;q['candidate_connected']|=inv['candidate_connected']
    q.update(a=n,b=m);row['candidate_contact_pairs'].append(q)
    if q['candidate_connected']:connected[n].append(m);connected[m].append(n)
  row['isolated_parts']=[n for n,v in connected.items() if not v]
  row['direct_neighbors']=connected
  rows.append(row)
(OUT/'independent_actual_relationships.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps([{'source':r['source'],'parts':len(r['parts']),'isolated_parts':r['isolated_parts'],'open_parts':[p['part'] for p in r['parts'] if p['boundary_edges'] or p['nonmanifold_edges']]} for r in rows],indent=2))
