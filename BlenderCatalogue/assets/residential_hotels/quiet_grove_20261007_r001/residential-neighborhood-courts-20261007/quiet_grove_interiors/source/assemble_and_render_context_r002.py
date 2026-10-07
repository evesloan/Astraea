"""Replace all 83 source instances in a fresh house successor, then source-eye QA."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];P=json.loads((R/'QUIET_GROVE_83_CURRENT_APPLICATION.json').read_text());BASE=R.parent/'outputs/sf_house_r002/house.blend';OUT=R/'outputs/context_r002';OUT.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pin=sha(BASE);bpy.ops.wm.open_mainfile(filepath=str(BASE));scene=bpy.context.scene
shared={};pins={};instances=[]
for r in P['units']:
 key=r['quiet_grove_variant'];source=R/'outputs/source_r002'/key/'assembly.blend';pins[str(source)]=sha(source)
 if key not in shared:
  with bpy.data.libraries.load(str(source),link=True)as(src,dst):dst.objects=list(src.objects)
  col=bpy.data.collections.new('QUIET_GROVE_SHARED_'+key)
  for o in dst.objects:
   if o and o.type in ['MESH','EMPTY','CURVE']:col.objects.link(o)
  shared[key]=col
 ob=bpy.data.objects[r['rebuild_identity']];assert ob.instance_type=='COLLECTION';ob.instance_collection=shared[key];ob['hotel_variant_status']='Quiet Grove architecture-specific successor; actual eight-recipe source library';ob['quiet_grove_variant']=key;ob['rest_slot_ids']=json.dumps([a['unit_slot_key']for a in r['anchor_bindings']]);instances.append({'unit_id':ob.name,'source_index':r['census_source_index'],'variant':key,'matrix_world':[list(row)for row in ob.matrix_world]})
# Light sources sit on actual authored source fixture datums. No camera fill.
lights=[]
for r in P['units']:
 room=bpy.data.objects[r['rebuild_identity']]
 for marker in room.instance_collection.objects:
  if marker.type!='EMPTY' or not marker.name.startswith('DATUM_'):continue
  isbed=marker.name.startswith('DATUM_qg_bed_task_');isceiling=marker.name.startswith('DATUM_light_')
  if not(isbed or isceiling):continue
  assert marker.parent is None, 'Fixture datum parent needs explicit transform composition'
  local=marker.location.copy();assert local.z>1.5, 'Fixture marker must retain authored elevation'
  point=room.matrix_world@local;d=bpy.data.lights.new('QG_SourceFixture_'+room.name+'_'+marker.name,'POINT' if isbed else 'AREA');d.energy=45 if isbed else 200;d.color=(1,.91,.78)
  if isbed:d.shadow_soft_size=.10
  else:d.shape='DISK';d.size=.65
  ob=bpy.data.objects.new(d.name,d);scene.collection.objects.link(ob);ob.location=point;lights.append({'unit':room.name,'datum':marker.name,'local_blender':list(local),'position_blender':list(point),'watts_source':d.energy})
scene['theme_status']='Quiet Grove hotel-specific source interiors applied across all 83 supported ordinary/family instances. 64 specialty/VIP reservations remain unbuilt.'
scene['privacy_status']='Unaccepted source directional preview; sealed r010 aperture unchanged, current Godot variants require fresh runtime tests.'
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1080;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
# Resolve dependencies relative to this new source, without changing original libraries.
for lib in bpy.data.libraries:lib.filepath=bpy.path.abspath(lib.filepath)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'quiet_grove_house_83.blend'))
(OUT/'ASSEMBLY_RECEIPT.json').write_text(json.dumps({'house_units':147,'quiet_grove_real_instances':len(instances),'prototypes':len(shared),'rest_slots':215,'instances':instances,'full_house_input_sha256':pin,'full_house_input':str(BASE),'prototype_pins':pins,'source_fixture_lights':lights,'source_only':True,'runtime_adopted':False,'specialty_vip_reservations_unbuilt':64,'source_blend_sha256':sha(OUT/'quiet_grove_house_83.blend')},indent=2)+'\n')
print('ALL_83_QUIET_GROVE_CONTEXT_READY',flush=True)
for source_index,local_eye,local_target,label in [(283,(-.1,4.86,1.65),(0,11.8,1.65),'family_outer_court_eye')]:
 r=next(x for x in P['units']if x['census_source_index']==source_index);room=bpy.data.objects[r['rebuild_identity']];eye=room.matrix_world@Vector(local_eye);target=room.matrix_world@Vector(local_target)
 d=bpy.data.cameras.new(label);ob=bpy.data.objects.new(label,d);scene.collection.objects.link(ob);ob.location=eye;ob.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();d.lens=22;d.clip_end=1400;scene.camera=ob;scene.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True)
 (OUT/(label+'.json')).write_text(json.dumps({'source_index':source_index,'unit_id':r['rebuild_identity'],'quiet_grove_variant':r['quiet_grove_variant'],'source_house':str(OUT/'quiet_grove_house_83.blend'),'full_house_all83_replaced':True,'eye_local_blender':local_eye,'target_local_blender':local_target,'actual_receiving_architecture':True,'hidden_parts':0,'source_privacy_preview_only':True,'runtime_or_final_art_evidence':False,'reference_sha256_ledger':'qa/REFERENCE_INSPECTION.json'},indent=2)+'\n');print('CONTEXT_EYE_READY',label,flush=True)
assert sha(BASE)==pin and all(sha(p)==h for p,h in pins.items())
print('QUIET_GROVE_CONTEXT_TERMINAL',flush=True)
