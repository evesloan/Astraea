from pathlib import Path
import bpy,json,hashlib,math,sys
from mathutils import Vector,Matrix
S=Path(__file__).resolve().parents[1];O=S/'outputs/sf_house_r002';P=json.loads((O/'PLAN.json').read_text());source=O/'house.blend';before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1440;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
# Actual retained source fixture datums, with source-only watt values. No invisible camera fill.
room_lights=[]
for room in [o for o in scene.objects if o.instance_type=='COLLECTION'and o.name.startswith('AST-UNIT-')]:
 for marker in room.instance_collection.objects:
  if marker.type!='EMPTY' or 'DATUM'not in marker.name or 'light'not in marker.name:continue
  point=room.matrix_world@marker.matrix_world.translation;bed='bed_light'in marker.name
  d=bpy.data.lights.new('Fixture_'+room.name+'_'+marker.name,'POINT'if bed else'AREA');d.energy=70 if bed else 220;d.color=(1,.93,.84)
  if bed:d.shadow_soft_size=.1
  else:d.shape='DISK';d.size=1.6
  o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=point;room_lights.append({'room':room.name,'source_marker':marker.name,'world_blender_xyz':list(point),'source_watts':d.energy})
views=[('whole_house_cutaway',[160,144,-553],[51,91,-365],315),('principal_court_eye',[83,85.65,-401],[79,95,-365],None)]
for name,eye,target,ortho in views:
 hidden=[]
 if ortho:
  for ob in scene.objects:
   if ob.type=='MESH'and (ob.name.startswith(('PrincipalCourtOpaqueCover','InnerGardenOpaqueCover','OuterEnclosure_'))):ob.hide_render=True;hidden.append(ob)
 camera=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,camera);scene.collection.objects.link(obj);obj.location=(eye[0],-eye[2],eye[1]);point=Vector((target[0],-target[2],target[1]));obj.rotation_euler=(point-obj.location).to_track_quat('-Z','Y').to_euler();camera.lens=22;camera.clip_end=1400
 if ortho:camera.type='ORTHO';camera.ortho_scale=ortho
 scene.camera=obj;scene.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
 caption={'view':name,'source_blend_sha256':before,'plan_sha256':hashlib.sha256((O/'PLAN.json').read_bytes()).hexdigest(),'actual_source_geometry':True,'game_installed':False,'camera_world_xyz':eye,'target_world_xyz':target,'cutaway_hidden_parts':len(hidden),'room_source_lights':room_lights,'scope':'Whole147-unit house composition;83real shared regular/family interiors are construction inputs,64specialty/VIPreserved. Hotel-specific interiors in separate active source pass. WP06receiving span unresolved; not a completed district or runtime material acceptance.'}
 (O/(name+'.json')).write_text(json.dumps(caption,indent=2)+'\n');print('FULL_HOUSE_PREVIEW_READY',str(O/(name+'.png')),flush=True)
 for ob in hidden:ob.hide_render=False
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
