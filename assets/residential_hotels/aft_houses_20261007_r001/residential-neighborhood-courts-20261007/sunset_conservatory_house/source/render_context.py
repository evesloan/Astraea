"""One real full-house source eye, with lights on authored source fixtures."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];BASE=R/'outputs/house_r002/house.blend';OUT=R/'outputs/context_r001';assert not OUT.exists(),'Preserve previous context';OUT.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pin=sha(BASE);P=json.loads((R/'SUNSET_83_PLACEMENT_MAP.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(BASE));scene=bpy.context.scene
lights=[];instances=[];libraries={}
for r in P['units']:
 room=bpy.data.objects[r['rebuild_identity']];assert room.instance_type=='COLLECTION';instances.append({'source_index':r['census_source_index'],'unit_id':room.name,'variant':r['source_recipe_key'],'matrix_world':[list(v)for v in room.matrix_world]})
 for marker in room.instance_collection.objects:
  bed=marker.name.startswith('DATUM_sunset_bed_light_');ceiling=marker.name.startswith('DATUM_sunset_room_light_');bath=marker.name.startswith('DATUM_bath_light')
  if marker.type!='EMPTY'or not(bed or ceiling or bath):continue
  assert marker.parent is None
  point=room.matrix_world@marker.location;d=bpy.data.lights.new('SC_SourceFixture_'+str(r['census_source_index'])+'_'+marker.name,'POINT'if bed else'AREA');d.energy=40 if bed else 180 if bath else 210;d.color=(1,.88,.73)
  if bed:d.shadow_soft_size=.09
  else:d.shape='DISK';d.size=.62
  o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=point
  lights.append({'source_index':r['census_source_index'],'datum':marker.name,'position_blender':list(point),'watts_source':d.energy,'source_fixture_only':True})
for lib in bpy.data.libraries:
 lib.filepath=bpy.path.abspath(lib.filepath);libraries[lib.filepath]=sha(lib.filepath);lib.filepath=bpy.path.relpath(lib.filepath,start=str(OUT))
scene['scope']='Full Sunset Conservatory source:83 authored ordinary/family interiors and64 explicit specialty/VIP holds; no Game change';scene['privacy_status']='Directional source preview only; finite sealed profile preserved; runtime privacy remains held';scene['lower_support_status']='All base receiving reactions held, no lower members'
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1080;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
r=next(x for x in P['units']if x['census_source_index']==282);room=bpy.data.objects[r['rebuild_identity']];local_eye=(.05,4.90,1.65);local_target=(.0,12.6,1.78);eye=room.matrix_world@Vector(local_eye);target=room.matrix_world@Vector(local_target)
d=bpy.data.cameras.new('SunsetActualFamilyCourtEye');o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=eye;o.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();d.lens=22;d.clip_start=.07;d.clip_end=1400;scene.camera=o
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'sunset_house_with_source_fixture_lights.blend'))
scene.render.filepath=str(OUT/'sunset_family_court_eye.png');bpy.ops.render.render(write_still=True)
receipt={'status':'ONE_SOURCE_EYE_RENDERED_NOT_RUNTIME_ACCEPTED','house_units':147,'source_interiors':83,'unbuilt_specialty_VIP':64,'unit_id':r['rebuild_identity'],'source_index':282,'variant':r['source_recipe_key'],'eye_local_blender':local_eye,'target_local_blender':local_target,'eye_world_xyz':[eye.x,eye.z,-eye.y],'source_house_sha256':pin,'source_house':str(BASE),'source_context_sha256':sha(OUT/'sunset_house_with_source_fixture_lights.blend'),'image_sha256':sha(OUT/'sunset_family_court_eye.png'),'all_83_instances':instances,'source_fixture_lights':lights,'linked_library_hashes':libraries,'hidden_geometry':0,'denoising':False,'threads':2,'samples':16,'actual_receiving_architecture':True,'preview_directional_privacy_only':True,'runtime_or_final_art_acceptance':False}
(OUT/'CONTEXT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');assert sha(BASE)==pin and all(sha(p)==h for p,h in libraries.items());print('SUNSET_CONTEXT_TERMINAL',len(instances),len(lights),flush=True)
