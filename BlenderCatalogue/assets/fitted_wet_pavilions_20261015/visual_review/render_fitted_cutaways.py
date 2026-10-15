from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');r=json.loads((D/'FITTED_NATIVE_VERIFICATION_r010.json').read_text());native=D/'native/VIP_FITTED_SUCCESSORS_r010.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(native)==r['native_sha256'];assert bpy.app.version[:3]==(4,3,2);bpy.ops.wm.open_mainfile(filepath=str(native));sources={};originals={o:o.hide_render for o in bpy.data.objects};context={}
for kit,file in [('TIDAL','AST-RES-TIDAL_lift_fit_r003.glb'),('QUIET','QUIET_GROVE_ARCHITECTURE_lift_r003.glb')]:
 p=G/'assets/models'/file;sources[file]=sha(p);before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(p));new=set(bpy.data.objects)-before;context[kit]=new
 for o in new:
  if o.type!='MESH':continue
  e=o.get('extras',{});key=o.name
  if key in['QG_Batch_171','QG_Batch_172']:o.location.z+=2.2
for m in bpy.data.materials:
 if not m.use_nodes:continue
 node=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if node:m.diffuse_color=tuple(node.inputs['Base Color'].default_value[:3])+(float(node.inputs['Alpha'].default_value),)
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE'and n.image:m.node_tree.nodes.active=n;break
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world.color=(.32,.34,.38);sh=scene.display.shading;sh.light='STUDIO';sh.color_type='TEXTURE';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.display.render_aa='8';scene.view_settings.view_transform='Standard'
B=lambda p:Vector((p[0],-p[2],p[1]));rows=[];out=D/'visual_review';out.mkdir(exist_ok=True)
for kit,at,target in [('TIDAL',[-58,122,-343],[-83,103,-370]),('QUIET',[104,122,-398],[80,103,-371])]:
 for o in originals:
  o.hide_render=True
  if o.type=='MESH'and any(c.name=='FITTED_'+kit+'_R010'for c in o.users_collection):o.hide_render=any(t in o.name for t in['RoofPanel','RoofRib','Clerestory','OuterWall','ChangingRoof','AftRoof'])
 for other,objects in context.items():
  for o in objects:
   o.hide_render=True
   if other!=kit or o.type!='MESH':continue
   ps=[o.matrix_world@Vector(v)for v in o.bound_box];lo=Vector(tuple(min(v[i]for v in ps)for i in range(3)));hi=Vector(tuple(max(v[i]for v in ps)for i in range(3)));ox=-80 if kit=='TIDAL'else 80
   if hi.x<ox-18 or lo.x>ox+18 or hi.z<101.5 or lo.z>109 or -lo.y< -386 or -hi.y> -354:continue
   category=o.get('category',o.get('extras',{}).get('category',''))
   if o.name in['TG_Batch_283','QG_Batch_462','QG_Batch_171','QG_Batch_172']:continue
   if category in['ceiling','roof']and o.name not in['TG_Batch_92','TG_Batch_93']:continue
   o.hide_render=False
 data=bpy.data.cameras.new(kit);data.type='ORTHO';data.ortho_scale=45;obj=bpy.data.objects.new(kit+'_ReviewCamera',data);scene.collection.objects.link(obj);obj.location=B(at);obj.rotation_euler=(B(target)-obj.location).to_track_quat('-Z','Y').to_euler();scene.camera=obj;path=out/(kit+'_R010_BOUNDED_NATIVE_CUTAWAY.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);rows.append({'kit':kit,'file':str(path),'sha256':sha(path)})
(out/'RECEIPT.json').write_text(json.dumps({'status':'NATIVE_COMPONENT_REVIEW_CUTAWAYS','native_sha256':sha(native),'context_sources':sources,'images':rows,'cutaway_hidden':'Pavilion roof panels,ribs,clerestories,outer wall,andchanging roofs;retained principal court roof andcanopies hidden. Original source geometry unchanged.','limitations':'Neutral Blender Workbench;notGodot/CRT orruntime illumination. Context includesretained architecture only;loose furniture andruntime privacy leaves omitted. Runtime contact/controller checks provideaccess evidence.'},indent=2)+'\n');print('PASS_BOUNDED_WET_NATIVE_CUTAWAYS')
