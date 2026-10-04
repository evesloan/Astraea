import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1];api=json.loads((BASE/'interface_api.json').read_text())['assets'];out={'scope':'Evaluated source geometric tests; no physical cloth, load, body/species or host acceptance','assets':{}}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def data(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();v=[o.matrix_world@x.co for x in me.vertices];f=[list(p.vertices)for p in me.polygons];ev.to_mesh_clear();return v,f
def bvh(o):v,f=data(o);return BVHTree.FromPolygons(v,f,all_triangles=False)
def bb(o):v,f=data(o);return [[min(p[k]for p in v)for k in range(3)],[max(p[k]for p in v)for k in range(3)]]
def empty_box(lo,hi,obs):
 overlaps=[]
 for o in obs:
  v,f=data(o);a,b=bb(o)
  if all(min(b[k],hi[k])-max(a[k],lo[k])>1e-7 for k in range(3)):overlaps.append(o.name)
 return overlaps
for ident in('AST-CRW-001','AST-CRW-002'):
 p=BASE/'source'/(ident+'.blend');bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.scene.frame_set(1);bpy.context.view_layer.update();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];markers=[]
 for row in api[ident]['surfaces']:
  obj=bpy.data.objects[row['physical_object']];loc,norm,idx,dist=bvh(obj).find_nearest(Vector(row['point_source_m']));normal_dot=norm.dot(Vector(row['normal_source']));markers.append({'name':row['name'],'object':obj.name,'distance_m':dist,'normal_dot':normal_dot,'passed':dist<2e-6 and normal_dot>.995})
 voids=[]
 for v in api[ident].get('reserved_voids',[]):
  overlaps=empty_box(v['min_source_m'],v['max_source_m'],obs);voids.append({'name':v['name'],'intersecting_object_bounds':overlaps,'passed':not overlaps,'method':'Conservative actual evaluated object bounds; empty bounds proves no mesh overlap'})
 row={'source_sha256':sha(p),'physical_markers':markers,'reserved_voids':voids,'semantic_mesh_count':len(obs),'scene_scale_length':bpy.context.scene.unit_settings.scale_length,'finite_mesh_coordinates':all(all(math.isfinite(x)for x in v)for o in obs for v in data(o)[0]),'mesh_positive_control':bvh(obs[0]).find_nearest(Vector(bb(obs[0])[0]))[3]<.1}
 if ident=='AST-CRW-002':
  m=bpy.data.objects['AST-CRW-002_CURTAIN_MOTION'];samples=[];privacy=[]
  for t in[0,.001,.01,.10,.25,.50,.75,.90,.99,.999,1]:
   m['gather']=t;m.update_tag();bpy.context.scene.frame_set(1+round(t*1000));bpy.context.view_layer.update();fab=bpy.data.objects['002_accordion_privacy_fabric'];v,f=data(fab);rings=[]
   for i in range(25):
    ring=bpy.data.objects[f'002_supported_ring_{i:02}'];tree=bvh(ring);point=Vector((.68,.02+1.8*t+(2.16-1.8*t)*i/24,2.097));dist=tree.find_nearest(point)[3];rings.append(dist)
   # Developed neutral mesh key vertices, before material thickness.
   ev=fab.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[fab.matrix_world@me.vertices[i].co for i in range(25)];ev.to_mesh_clear();developed=sum((pts[i+1]-pts[i]).length for i in range(24));samples.append({'t':t,'root_source_y':m.matrix_world.translation.y,'fabric_bounds':bb(fab),'max_ring_support_distance_m':max(rings),'pleat_developed_width_neutral_plus_solidify_offset_m':developed,'passed':max(rings)<2e-6 and min(p.x for p in v)>.54 and max(p.y for p in v)<2.20 and min(p.y for p in v)>0})
   if t in(0,1):
    tree=bvh(fab)
    for test in api[ident]['privacy_field']['closed_tests']:
     eye=Vector(test['eye_source_m']);tar=Vector(test['target_source_m']);vec=tar-eye;hit=tree.ray_cast(eye,vec.normalized(),vec.length)[0];privacy.append({'t':t,'eye':list(eye),'target':list(tar),'occluded':hit is not None,'expected':t==0,'passed':(hit is not None)==(t==0)})
  row['authored_pose_samples']=samples;row['bounded_side_privacy_rays']=privacy;row['privacy_method']='Actual evaluated fabric BVH per declared state; targets inside same bounded side field; open negative controls expected clear'
 row['passed']=all(x['passed']for x in markers+voids+row.get('authored_pose_samples',[])+row.get('bounded_side_privacy_rays',[])) and row['finite_mesh_coordinates'];out['assets'][ident]=row
out['all_passed']=all(r['passed']for r in out['assets'].values());(BASE/'qa/component_checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
