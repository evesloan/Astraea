from pathlib import Path
import bpy,json,math,hashlib,os
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_HABITATS.json'));B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[]
for idx in [int(x)for x in os.environ.get('REVIEW_INDICES','437,419,467').split(',')]:
 room=next(r for r in P['rooms']if r['source_envelope_index']==idx);native=W/room['assembly_native'];before=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));rest=room['rest_source'];ref=next(r for r in P['references']if r['key']==room['reference_key']);body=W/('StarAtlasBodyFit_'+ref['key']+'.blend')
 with bpy.data.libraries.load(str(body),link=False)as(src,dst):dst.objects=src.objects
 root=bpy.data.objects.new('ConstructionReference_NotCanonicalActor',None);bpy.context.collection.objects.link(root)
 for ob in dst.objects:
  if ob:bpy.context.collection.objects.link(ob);ob.parent=root
 root.location=B(rest['position']);root.rotation_euler.z=rest['yaw'];cutaway=[]
 if idx==437:
  for suffix in ['LeftLiner','Roof','FrontLeftJamb']:
   ob=bpy.data.objects[f'SA{idx}_Cocoon_'+suffix];ob.hide_render=True;cutaway.append(ob.name)
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.world=bpy.data.worlds.new('DiagnosticSourceWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.2,.22,.24,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
 cy,sy=math.cos(rest['yaw']),math.sin(rest['yaw']);at=lambda v:[rest['position'][0]+v[0]*cy+v[2]*sy,rest['position'][1]+v[1],rest['position'][2]-v[0]*sy+v[2]*cy]
 for p in [[0,2.2,-.3],[-1.6,2.2,-2.5]]:
  bpy.ops.object.light_add(type='AREA',location=B(at(p)));bpy.context.object.data.energy=140;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=2
 bpy.ops.object.camera_add(location=B(at([-1.5,1.75,-2.9])));cam=bpy.context.object;cam.data.lens=24;cam.rotation_euler=(Vector(B(at([0,.65,0])))-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam;name=f'SOURCE_BODY_FIT_{idx}.png';scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);assert sha(native)==before;records.append({'image':name,'native_sha256':before,'construction_reference':ref['key'],'diagnostic_cutaway_objects':cutaway,'native_unchanged':True})
if (W/'SOURCE_VIEW_RUN.json').exists():
 previous=json.load(open(W/'SOURCE_VIEW_RUN.json'));records += [r for r in previous['images']if r['image']not in [q['image']for q in records]]
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':records,'source_only':True,'diagnostic_fill_lighting':True,'source_native_files_unchanged':True,'limits':'Unsaved source/mannequin diagnostic fit views. Quiet437 liner/roof cutaway explicitly disclosed; actual opaque shell/controller contacts tested in main. No in-engine/CRT/final visual or canonical actor acceptance.'},indent=2)+'\n')
