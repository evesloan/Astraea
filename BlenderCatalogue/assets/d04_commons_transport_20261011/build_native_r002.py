from pathlib import Path
import bpy,json,hashlib,sys,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1])
sys.path.insert(0,str(R/'Game/tools'));from validate_production_glb import preview_only
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
manifest=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'))
# Original registered ID/source family; no catalogue entry added or replaced.
assert P['sources'][0]['catalogue_id']=='AST-FUR-002'and P['sources'][0]['family']=='view_day_furniture'
assert json.load(open(R/'Game/artifacts/d04_commons_vertical_route_probe006.json'))['status']=='PASS_STATIC_POSE_SWEEPS'
def start():
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;return{}

def components(bindings,prefix):
 records=[]
 for binding in bindings:
  a=next(a for a in P['sources']if a['catalogue_id']==binding['catalogue_id']);source=R/'BlenderCatalogue'/a['source'];assert sha(source)==P['source_pins'][str(source.relative_to(R))]
  with bpy.data.libraries.load(str(source),link=False)as(src,dst):dst.objects=src.objects
  obs=[o for o in dst.objects if o];worlds={}
  for o in obs:bpy.context.collection.objects.link(o)
  bpy.context.view_layer.update()
  for o in obs:worlds[o]=o.matrix_world.copy()
  root=bpy.data.objects.new(prefix+binding['name'],None);bpy.context.collection.objects.link(root);T=Matrix.Translation(Vector(B(binding['position'])))@Matrix.Rotation(binding['yaw'],4,'Z');root.matrix_world=T;count=0;excluded=[]
  for o in obs:
   oldname=o.name
   if o.type not in['MESH','EMPTY']or preview_only(oldname,{k:o.get(k,False)for k in ['preview_only','presentation_only','exclude_from_production']}):excluded.append(oldname);bpy.data.objects.remove(o,do_unlink=True);continue
   o.parent=root;o.matrix_world=T@worlds[o];o.name=prefix+binding['name']+'__'+oldname
   if o.type=='MESH':
    policy=str(o.get('collision_policy',''));o['runtime_collision']='NO_SOLID_COLLISION'not in policy and policy!='no_collision_detail'and not any(t in oldname for t in['WaterSurface_VisualOnly','Ripple']);o['category']='source_fitting';o['source_catalogue_id']=a['catalogue_id'];o['source_file_sha256']=sha(source);count+=1
  records.append({'binding':binding['name'],'catalogue_id':a['catalogue_id'],'source':a['source'],'source_sha256':sha(source),'origin':binding['position'],'yaw':binding['yaw'],'rigid_instance_no_rescaling':True,'mesh_count':count,'excluded_presentation':excluded})
 return records
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import require_new,export_native
require_new([W/'D04CommonsSouthChairRouting_r002.blend',W/'D04_COMMONS_SOUTH_CHAIR_ROUTING_r002.glb',R/'Game/assets/models/D04_COMMONS_SOUTH_CHAIR_ROUTING_r002.glb'])
start();c=P['chair_revision'];records=components([{'catalogue_id':'AST-FUR-002','name':'CommonsSouthChair','position':c['position'],'yaw':c['yaw']}],'D04Commons_');rec=export_native(bpy,W,R,'D04CommonsSouthChairRouting_r002.blend','D04_COMMONS_SOUTH_CHAIR_ROUTING_r002.glb')
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
(W/'NATIVE_EXPORT_CHECK_r002.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'source_pins_unchanged':len(P['source_pins']),'records':[rec],'original_registered_rigid_components':records,'original_source_bytes_preserved':True,'new_meshes_or_furniture':0,'new_floor_m2':0,'new_units':0,'new_rest_places':0,'runtime_reuses_exact_original_chair_node_geometry_with_only_rigid_transform':True},indent=2)+'\n')
