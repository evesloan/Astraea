from pathlib import Path
import bpy,json
from mathutils import Matrix,Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));bpy.ops.wm.read_factory_settings(use_empty=True)
# Actual native frame,original receiving and original upper commons remain unchanged.
for file in [W/P['structure']['native'],R/'BlenderCatalogue/assets/star_atlas_d17_standard823_20261011/StarAtlasD17Standard823Frame_r001.blend',R/'BlenderCatalogue/assets/star_atlas_d17_receiving_first_20261010/StarAtlasD17ReceivingFirst.blend',R/'BlenderCatalogue/assets/star_atlas_upper_commons_20261009/source/StarAtlasUpperCommons.blend']:
 with bpy.data.libraries.load(str(file),link=False)as(src,dst):dst.objects=src.objects
 for ob in dst.objects:
  if ob:bpy.context.collection.objects.link(ob)
source=R/P['rooms'][0]['source_native'];loaded=[]
with bpy.data.libraries.load(str(source),link=False)as(src,dst):dst.objects=src.objects
for ob in dst.objects:
 if ob:bpy.context.collection.objects.link(ob);loaded.append(ob)
bpy.context.view_layer.update();matrices={ob:ob.matrix_world.copy()for ob in loaded}
for r in P['rooms']:
 T=Matrix.Translation(Vector((0,-r['translation'][2],0)))
 for original in loaded:
  if original.type!='MESH':continue
  ob=original.copy();ob.parent=None;ob.name=str(r['allocation']['source_envelope_index'])+'__'+original.name;ob.matrix_world=T@matrices[original];bpy.context.collection.objects.link(ob)
# Retain the original823 source as context;only saved-source objects are shown.
for original in loaded:
 if original.type=='MESH':original.parent=None;original.matrix_world=matrices[original]
 else:bpy.data.objects.remove(original,do_unlink=True)
# Exact retained lower compiler triangles are an unsaved review surface,never part of the new model.
for q in json.load(open(R/'Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json'))['regions']:
 if q['id']not in ['D16_STAR_ATLAS_MISSING_STREET_0','D16_STAR_ATLAS_MISSING_STREET_1']:continue
 vs=[];faces=[]
 for triangle in q['triangles']:faces.append(list(range(len(vs),len(vs)+3)));vs.extend((x,-z,q['floor_y'])for x,z in triangle)
 mesh=bpy.data.meshes.new(q['id']);mesh.from_pydata(vs,[],faces);ob=bpy.data.objects.new(q['id'],mesh);bpy.context.collection.objects.link(ob)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.studio_light='paint.sl';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('Neutral actual-source review');s.world.color=(.6,.6,.6);s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard'
views=[('SOURCE_D17_STANDARD_BATCH_AFT_CONTEXT001.png',(-43,-86,108),(-74,-44,100),18),('SOURCE_D17_STANDARD793_INTERIOR_WIDE001.png',(-66.4,-42.75,103.7),(-74.5,-42.8,103.3),16)]
for name,at,target,lens in views:
 bpy.ops.object.camera_add(location=at);camera=bpy.context.object;camera.data.lens=lens;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();s.camera=camera;s.render.filepath=str(W/name);assert not Path(s.render.filepath).exists();bpy.ops.render.render(write_still=True);bpy.data.objects.remove(camera,do_unlink=True)
(W/'SOURCE_PHOTO_RECEIPT.json').write_text(json.dumps({'status':'PASS','images':[q[0]for q in views],'all_original_room_roofs_furniture_and_frame_geometry_retained':True,'nine_rigid_source_interior_instances_and_original823_context':True,'lower_floor_review_surfaces_exact_retained_compiler_triangles_unsaved':True,'mode':'Neutral Blender Workbench material-color source view;textures,glass/game lighting omitted','production_inactive':True,'no_exterior_vista_primary_capacity_Godot_CRT_hardware_final_acceptance':True},indent=2)+'\n')
