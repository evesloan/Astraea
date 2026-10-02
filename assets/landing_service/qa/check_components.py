"""Read-only Blender reload/source witnesses and actual imported GLB check."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
API=json.loads((BASE/'interface_api.json').read_text())['assets'];out=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def geo(o):
 dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();vs=[o.matrix_world@v.co for v in m.vertices];fs=[tuple(t.vertices) for t in m.loop_triangles];e.to_mesh_clear();return vs,fs

def tree(o):
 v,f=geo(o);return BVHTree.FromPolygons(v,f,all_triangles=True)
def near(o,p):
 hit,n,index,d=tree(o).find_nearest(Vector(p));return float(d),list(n),list(hit)
def reset():bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def bounds(obs):
 vs=[v for o in obs for v in geo(o)[0]];return {'min':[min(p[k] for p in vs) for k in range(3)],'max':[max(p[k] for p in vs) for k in range(3)]}
# Axial advisory screen excludes opposing buried bearings and tests projected polygon triangle overlap.
def tri_clip(subject,clip):
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 if cross(clip[0],clip[1],clip[2])<0:clip=list(reversed(clip))
 result=list(subject)
 for a,b in zip(clip,clip[1:]+clip[:1]):
  source=result;result=[]
  if not source:break
  for p,q in zip(source,source[1:]+source[:1]):
   dp=cross(a,b,p);dq=cross(a,b,q);inside_p=dp>=-1e-9;inside_q=dq>=-1e-9
   if inside_p:result.append(p)
   if inside_p != inside_q:
    t=dp/(dp-dq);result.append([p[k]+t*(q[k]-p[k]) for k in range(2)])
 return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(result,result[1:]+result[:1])))*.5 if result else 0

def axial_screen(obs):
 groups={};pairs={}
 for o in obs:
  vs,fs=geo(o)
  for inds in fs:
   a,b,c=[vs[i] for i in inds];n=(b-a).cross(c-a).normalized();axis=max(range(3),key=lambda i:abs(n[i]))
   if abs(n[axis])<.999999:continue
   key=(axis,1 if n[axis]>0 else -1,round(a[axis],6));axes=[i for i in range(3) if i!=axis];poly=[[p[k] for k in axes] for p in(a,b,c)]
   groups.setdefault(key,[]).append((o.name,o['material_role'],poly))
 for key,rows in groups.items():
  for i,(name,role,poly) in enumerate(rows):
   for name2,role2,poly2 in rows[i+1:]:
    if role==role2 or name==name2:continue
    if any(max(p[k] for p in poly)<=min(p[k] for p in poly2)+1e-8 or max(p[k] for p in poly2)<=min(p[k] for p in poly)+1e-8 for k in(0,1)):continue
    area=tri_clip(poly,poly2)
    if area>1e-7:
     pair=tuple(sorted((name,name2)))+(str(key),);pairs[pair]=pairs.get(pair,0)+area
 return [{'objects':list(k[:2]),'axis_sign_plane':k[2],'projected_overlap_m2':v} for k,v in pairs.items()]

for ident,api in API.items():
 p=BASE/'source'/f'{ident}.blend';before=sha(p);bpy.ops.wm.open_mainfile(filepath=str(p));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];parts=[]
 for o in obs:
  bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free();parts.append({'object':o.name,'nonmanifold_edges':bad,'positive_volume':vol>0,'volume_m3':vol,'modifiers':[m.type for m in o.modifiers]})
 surfaces=[]
 for s in api['surfaces']:
  d,n,h=near(bpy.data.objects[s['physical_object']],s['point_source_m']);dot=Vector(n).dot(Vector(s['normal_source']));surfaces.append({'marker':s['name'],'object':s['physical_object'],'surface_distance_m':d,'normal_dot':dot,'passed':d<2e-6 and dot>.999})
 joins=[]
 for j in api['joins']:
  da,na,ha=near(bpy.data.objects[j['a']],j['witness_source_m']);db,nb,hb=near(bpy.data.objects[j['b']],j['witness_source_m']);dot=Vector(na).dot(Vector(nb));joins.append({'parts':[j['a'],j['b']],'witness_source_m':j['witness_source_m'],'distance_a_m':da,'distance_b_m':db,'opposing_normal_dot':dot,'passed':max(da,db)<2e-6 and dot<-.999})
 cop=axial_screen(obs);row={'id':ident,'source_sha256':before,'parts':parts,'surfaces':surfaces,'joins':joins,'axial_same_facing_different_material_overlap_candidates':cop,'axial_screen_scope':'Advisory axial planes only; deliberate opposing butt joints excluded; no general nonaxial overlap proof','source_unchanged':sha(p)==before}
 # Actual importer basis resolution, preserving whole fixture in QA only.
 srcbd=bounds(obs);reset();bpy.ops.import_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'));newobs=[o for o in bpy.context.scene.objects if o.type=='MESH'];actual=bounds(newobs);row['actual_imported_bounds_source_basis']=actual;row['source_imported_bounds_max_error_m']=max(abs(actual[k][j]-srcbd[k][j]) for k in('min','max') for j in range(3))
 if api.get('fixture_context'):
  ctx=api['fixture_context'];existing=set(bpy.data.objects);fpath=(BASE/ctx['existing_export']).resolve();bpy.ops.import_scene.gltf(filepath=str(fpath));fixture=[o for o in bpy.data.objects if o not in existing and o.type=='MESH'];T=Matrix(ctx['matrix_source_local'])
  for o in fixture:o.matrix_world=T@o.matrix_world
  fbd=bounds(fixture);fixture_mounts=[]
  for pnt in ctx['anchor_source_m']:
   nearest=min((near(o,pnt)+(o.name,) for o in fixture),key=lambda v:v[0]);fixture_mounts.append({'anchor_source_m':pnt,'distance_m':nearest[0],'normal_source':nearest[1],'physical_imported_node':nearest[3]})
  # Intersection pairs are reported for geometric judgement; plane touches may yield pairs.
  overlaps=[]
  for a in newobs:
   at=tree(a)
   for b in fixture:
    count=len(at.overlap(tree(b)))
    if count:overlaps.append({'new_component_node':a.name,'fixture_node':b.name,'intersecting_triangle_pairs':count})
  row['fixture_context']={'path':str(fpath.relative_to(CAT)),'sha256':sha(fpath),'actual_full_bounds_source_m':fbd,'inside_component_target':all(fbd['min'][k]>= [-.65,0,0][k]-1e-6 and fbd['max'][k]<=[.65,.45,2.5][k]+1e-6 for k in range(3)),'physical_mount_witnesses':fixture_mounts,'surface_intersection_candidates':overlaps,'scope':'Full housing, guard, brackets, label and mount from actual imported GLB; fixture is QA context only'}
 row['passed']=all(p['nonmanifold_edges']==0 and p['positive_volume'] for p in parts) and all(s['passed'] for s in surfaces) and all(j['passed'] for j in joins) and not cop and row['source_imported_bounds_max_error_m']<1e-6 and row['source_unchanged']
 out.append(row)
result={'scope':'Source/imported-component QA only; no host/game/actor acceptance','results':out,'all_passed':all(r['passed'] for r in out)}
(BASE/'qa/component_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps({'all_passed':result['all_passed'],'results':[{'id':r['id'],'passed':r['passed'],'coplanar':r['axial_same_facing_different_material_overlap_candidates'],'fixture':r.get('fixture_context')} for r in out]},indent=2))
