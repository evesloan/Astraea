"""Representative editable-source views; presentation world fill explicitly recorded."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'source/aquatic_district.blend'))
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.world=bpy.data.worlds.new('QA presentation ambient');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.76,.8,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.4
s.view_settings.view_transform='AgX';s.view_settings.exposure=1.1
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=24;cam.data.clip_start=.05;cam.data.clip_end=400
views=[('arrival',(62,47.15,242),(80,46.25,212),False),('island',(80,47.1,217.5),(81.5,46.25,211.5),False),('launch_gallery',(96,51,196.2),(81,47.5,188.5),False),('cutaway',(115,93,281),(78,46,216),True),('cascade_interface',(19,46,220),(24,44.2,215),False)]
records=[]
def xyz(p):return Vector((p[0],-p[2],p[1]))
for name,eye,target,cut in views:
 hidden=[]
 if name=='cascade_interface':
  q=P.parents[1]/'Game/assets/models/AST-AQU-015.glb'
  if q.exists():
   before=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(q));new=set(s.objects)-before
   for o in new:
    if o.parent not in new:o.location+=xyz((21.5,61,207))
   basin=json.loads((P/'dependencies/Game/data/aquatic_section.json').read_text())['basin']['boundary']
   me=bpy.data.meshes.new('QA_retained_basin_water_outline');me.from_pydata([xyz((x,43.8,z)) for x,z in basin],[],[tuple(range(len(basin)))]);me.materials.append(bpy.data.materials['AQD_water']);o=bpy.data.objects.new('QA_context_basin_water_NOT_DELIVERY',me);s.collection.objects.link(o)
   bpy.ops.mesh.primitive_cube_add(size=1,location=xyz((17,43.88,215)));o=bpy.context.object;o.name='QA_schematic_dry_shore_NOT_DELIVERY';o.dimensions=(8,10,.24);o.data.materials.append(bpy.data.materials['ASTRAEA_warm_stone'])
 if cut:
  for o in s.objects:
   if 'AQD__' in o.name and any(q in o.name for q in ['opaque_roof','roof_cap','enclosure','west_threshold','east_threshold','east_boundary','outer_wall','west_portal_header','portal_canopy']):
    if not o.hide_render:o.hide_render=True;hidden.append(o)
 cam.location=xyz(eye);cam.rotation_euler=(xyz(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if cut else 'PERSP';cam.data.ortho_scale=83
 s.render.filepath=str(P/'qa'/('source_'+name+'.png'));bpy.ops.render.render(write_still=True)
 records.append({'view':name,'eye_xyz':eye,'target_xyz':target,'cutaway_hidden_objects':[o.name for o in hidden],'ambient_presentation_fill':.4,'exposure':1.1,'source_lights_retained':14,'source_saved_changes':False,'cascade_context':('Actual retained AST-AQU-015 GLB at existing placement, current basin outline water visual and schematic dry shore; context not delivered geometry' if name=='cascade_interface' else None)})
 for o in hidden:o.hide_render=False
(P/'qa/source_view_receipt.json').write_text(json.dumps(records,indent=2))
