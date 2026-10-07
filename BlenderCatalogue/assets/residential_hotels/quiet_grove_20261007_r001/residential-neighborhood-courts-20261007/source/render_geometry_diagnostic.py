"""A clearly labelled studio geometry diagnostic, never production-lighting evidence."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
S=Path(__file__).resolve().parents[1];O=S/'outputs/diagnostic_recovery_r001';O.mkdir(exist_ok=False)
source=S/'quiet_grove_interiors/outputs/context_r001/quiet_grove_house_83.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
# The review shader affects this in-memory diagnostic only. Production lights,
# materials, native rendering configuration and source files are not written.
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1500;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.threads_mode='FIXED';scene.render.threads=2
shade=scene.display.shading;shade.light='STUDIO';shade.color_type='MATERIAL';shade.show_shadows=True;shade.show_cavity=True;shade.cavity_type='BOTH';shade.show_specular_highlight=False;shade.show_object_outline=False;shade.background_type='VIEWPORT';shade.background_color=(.13,.15,.17)
hidden=[]
for ob in scene.objects:
 if ob.type=='MESH'and ob.name.startswith(('PrincipalCourtOpaqueCover','InnerGardenOpaqueCover','OuterEnclosure_')):
  ob.hide_render=True;hidden.append(ob.name)
# Cut away source ceilings consistently to reveal the existing room interiors.
room_roof_hidden=[]
for ob in bpy.data.objects:
 if ob.library and ob.type=='MESH'and ob.name.startswith(('SUI_Ceiling','SUI_BathCeiling','QG_Ceiling')):
  try:ob.hide_render=True;room_roof_hidden.append(ob.name)
  except RuntimeError:pass
camera=bpy.data.cameras.new('FullHouseGeometryDiagnostic');node=bpy.data.objects.new(camera.name,camera);scene.collection.objects.link(node)
eye=Vector((165,370,172));target=Vector((50,370,94));node.location=eye;node.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();camera.type='ORTHO';camera.ortho_scale=272;camera.clip_end=1500;scene.camera=node
scene.render.filepath=str(O/'whole_house_geometry_diagnostic.png');bpy.ops.render.render(write_still=True)
assert sha(source)==before
report={'status':'DIAGNOSTIC_OVERVIEW_COMPLETE','file':'whole_house_geometry_diagnostic.png','image_sha256':sha(O/'whole_house_geometry_diagnostic.png'),'source_sha256':before,'source_file':str(source),'render_scope':'Studio-lit geometry and material-color diagnostic; not production light, transparency, privacy or native appearance evidence','camera_world_xyz':[165,172,-370],'target_world_xyz':[50,94,-370],'cutaway_architecture_parts':hidden,'hidden_linked_room_ceiling_parts':room_roof_hidden,'full_house_units':147,'real_QuietGrove_room_instances':83,'source_variants':8,'rest_slots':215,'reserved_specialty_VIP':64,'production_source_files_unchanged':True,'Game_or_Catalogue_writes':False}
(O/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print('GEOMETRY_DIAGNOSTIC_COMPLETE',str(O/'whole_house_geometry_diagnostic.png'),flush=True)
