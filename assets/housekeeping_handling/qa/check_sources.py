"""Focused real-surface, retention and useful-void checks; hash-bound component QA only."""
import bpy,json,hashlib,math,itertools
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tree(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();t=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(p.vertices)for p in me.polygons]);ev.to_mesh_clear();return t

def inside(t,p):
 p=Vector(p);near=t.find_nearest(p)
 if near[3] is not None and near[3]<.00005:return True
 d=Vector((.937,.287,.199)).normalized();count=0;s=p.copy()
 for _ in range(120):
  c,n,i,dist=t.ray_cast(s,d,10)
  if c is None:break
  count+=1;s=c+d*.000002
 return count%2==1

def clear_box(trees,lo,hi):
 hits=[]
 # 75 cross-volume rays cover each axis, plus all 27 internal point witnesses.
 for axis in range(3):
  others=[k for k in range(3)if k!=axis]
  for a,b in itertools.product(range(5),repeat=2):
   p=Vector(lo);p[others[0]]+=(hi[others[0]]-lo[others[0]])*(a+.5)/5;p[others[1]]+=(hi[others[1]]-lo[others[1]])*(b+.5)/5;d=Vector((0,0,0));d[axis]=1
   for name,t in trees.items():
    c,n,i,dist=t.ray_cast(p,d,hi[axis]-lo[axis])
    if c is not None:hits.append({'part':name,'point':list(c)})
 for xyz in itertools.product((.12,.5,.88),repeat=3):
  p=[lo[k]+(hi[k]-lo[k])*xyz[k]for k in range(3)]
  for name,t in trees.items():
   if inside(t,p):hits.append({'part':name,'interior_point':p})
 return hits
rows=[]
for path in sorted(BASE.glob('AST-HSK-*.manifest.json')):
 r=json.loads(path.read_text());bpy.ops.wm.open_mainfile(filepath=str(BASE/r['source']));bpy.context.view_layer.update();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];trees={o.name:tree(o)for o in obs};markers=[];joins=[];voids=[]
 for m in r['physical_and_proposal_markers']:
  p=bpy.data.objects[m['name']].matrix_world.translation;record={'name':m['name'],'position_matches':(p-Vector(m['source_m'])).length<1e-6}
  if m['physical_part']:
   near=trees[m['physical_part']].find_nearest(p);record.update(surface_distance_m=near[3],surface_matches=near[3]<.0001)
   if 'normal_source'in m:record.update(normal_dot=Vector(m['normal_source']).dot(near[1]),normal_matches=Vector(m['normal_source']).dot(near[1])>.99)
  record['passes']=record['position_matches']and record.get('surface_matches',True)and record.get('normal_matches',True);markers.append(record)
 for j in r['joins']:
  p=j['probe_source_m'];dist=[trees[n].find_nearest(Vector(p))[3]for n in j['parts']];both=[inside(trees[n],p)for n in j['parts']];joins.append({'name':j['name'],'parts':j['parts'],'distances_m':dist,'inside_or_on_both':both,'passes':all(both)})
 for v in r['receiver_voids']:
  hits=clear_box(trees,v['min_source_m'],v['max_source_m']);voids.append({'name':v['name'],'ray_count':75,'point_count':27,'hits':hits,'passes':not hits})
 # Positive control: translating a claimed work/load contact upward must fail actual surface correspondence.
 control=next(m for m in r['physical_and_proposal_markers']if m['kind']in('physical_work_surface','physical_load_surface'));bad=Vector(control['source_m'])+Vector((0,0,.025));d=trees[control['physical_part']].find_nearest(bad)[3]
 # Independent economical collision omission distance: sample omitted original shape vertices to retained source mesh surfaces.
 retained={o.name:trees[o.name]for o in obs if o['body_candidate_retained']};omissions=[]
 for ob in obs:
  if ob['body_candidate_retained']:continue
  ds=[min(t.find_nearest(ob.matrix_world@v.co)[3]for t in retained.values())for v in ob.data.vertices]
  omissions.append({'part':ob.name,'vertex_sample_count':len(ds),'maximum_vertex_distance_to_retained_visual_surface_m':max(ds),'note':'Finite omitted-detail sample distance, not material thickness, safety margin or full Hausdorff proof'})
 rows.append({'id':r['catalogue_id'],'source_sha256':sha(BASE/r['source']),'markers':markers,'joins':joins,'voids':voids,'negative_controls':{'offset_contact_distance_m':d,'offset_contact_rejected':d>.02},'collision_optional_subset':{'precise_shape_count':len(obs),'body_shape_count':len(retained),'omitted_detail_distances':omissions,'body_retains_all_declared_work_load_grip_floor_surfaces':all(m['physical_part']in retained for m in r['physical_and_proposal_markers']if m['physical_part']and m['kind']!='physical_identification_surface')},'all_images_packed':all(im.packed_file for im in bpy.data.images if im.source=='FILE'and im.users),'passes':all(v['passes']for v in markers+joins+voids)and d>.02})
out={'results':rows,'all_passed':all(r['passes']for r in rows),'scope':'Static source geometry, surface directions, finite useful-void probes and literal body subset; no engine/room/physics/hygiene claim'};(BASE/'qa/source_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'all_passed':out['all_passed'],'failed':{r['id']:[v['name']for v in r['markers']+r['joins']+r['voids']if not v['passes']]for r in rows}},indent=2))
