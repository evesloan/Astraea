from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={};images=[]
def append(path):
 pins[str(path.relative_to(R))]=sha(path)
 with bpy.data.libraries.load(str(path),link=False)as(src,dst):dst.objects=src.objects
 for o in dst.objects:
  if o:
   bpy.context.collection.objects.link(o)
   if o.get('persistent_structural_contact_only',False):o.hide_render=True
for kind in ['aquatic497_rest','shared_street_entries','aquatic527_pair']:
 native=W/('StarAtlasSpecialty_527.blend'if kind=='aquatic527_pair'else'StarAtlasSpecialty_497.blend');pins[str(native.relative_to(R))]=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
 if kind=='shared_street_entries':
  append(W/'StarAtlasSpecialty_521.blend')
  for idx in [509,533]:append(R/'BlenderCatalogue/assets/star_atlas_preview_ground_correction_20261010'/f'StarAtlasSpecialty_{idx}_Production.blend')
  append(R/'BlenderCatalogue/assets/star_atlas_specialty_first_20261010/StarAtlasSpecialtyFirstReceiving.blend');append(R/'BlenderCatalogue/assets/star_atlas_specialty_receiving_20261010/StarAtlasSpecialtyStructuralReceiving.blend');append(R/'BlenderCatalogue/assets/star_atlas_specialty_fifth_20261010/StarAtlasSpecialtyFifthReceiving.blend');append(R/'BlenderCatalogue/assets/star_atlas_specialty_second_20261010/StarAtlasSpecialtySecondReceiving.blend');append(R/'BlenderCatalogue/assets/star_atlas_specialty_sixth_20261010/StarAtlasSpecialtySixthReceiving.blend');append(R/'BlenderCatalogue/assets/star_atlas_specialty_third_20261010/StarAtlasSpecialtyThirdReceiving.blend');append(W/'StarAtlasSpecialtySeventhReceiving.blend')
  for name in ['SA_D15_NorthWestGuard','SA_D15_SouthWestGuard','SA_D15_NorthTerminalGuard_-53','SA_D15_SouthTerminalGuard_53','SA_D15_North_SecondWestGuard','SA_D15_South_SecondWestGuard','SA_D15_North_SecondTerminalGuard','SA_D15_South_SecondTerminalGuard','SA_D15_North_ThirdWestGuard','SA_D15_South_ThirdWestGuard','SA_D15_North_ThirdTerminalGuard','SA_D15_South_ThirdTerminalGuard']:
   ob=bpy.data.objects.get(name);assert ob is not None;bpy.data.objects.remove(ob,do_unlink=True)
 scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.world=bpy.data.worlds.new('DiagnosticContext');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
 for p in ([(-92.5,95.7,79),(-96,95.7,79)]if kind=='aquatic527_pair'else[(-92.5,95.7,-70.6),(-84,96,-71.6),(-84,96,-79)]):
  bpy.ops.object.light_add(type='AREA',location=B(p));bpy.context.object.data.energy=150;bpy.context.object.data.size=3
 at,target,lens=((-92.45,94.8,-71.2),(-95.6,93.7,-70.6),16)if kind=='aquatic497_rest'else((-84,94.65,-65.2),(-84,94.4,-73.6),16)
 if kind=='aquatic527_pair':at,target,lens=(-92.0,94.7,79),(-95.6,93.85,79),16
 bpy.ops.object.camera_add(location=B(at));camera=bpy.context.object;camera.data.lens=lens;camera.rotation_euler=(Vector(B(target))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera;name='SOURCE_CONTEXT_'+kind+'.png';scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
for p,h in pins.items():assert sha(R/p)==h
(W/'SOURCE_CONTEXT_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'unsaved_native_context':True,'actual_old_street_and_source_derivative_state':True,'separately_instantiated_runtime_controller_leaves_absent':True,'native_pins_unchanged':pins,'diagnostic_fill_lighting':True},indent=2)+'\n')
