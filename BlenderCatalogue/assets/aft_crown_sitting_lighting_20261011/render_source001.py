from pathlib import Path
import bpy,json
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));bpy.ops.wm.read_factory_settings(use_empty=True)
for f in [R/'BlenderCatalogue/assets/aft_crown_platform/source/AST-CMD-005.blend',R/'BlenderCatalogue/assets/aft_crown_sitting_bays_20261011/AftCrownSittingBays_r001.blend',W/P['structure']['native']]:
 with bpy.data.libraries.load(str(f),link=False)as(src,dst):dst.objects=src.objects
 for o in dst.objects:
  if o:bpy.context.collection.objects.link(o)
mat=bpy.data.materials.new('Compiler floor source-context surface');mat.use_nodes=True;bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.43,.38,.30,1);bsdf.inputs['Roughness'].default_value=.83
for f in ['structural_meshes.json','received_structural_meshes.json']:
 for q in json.load(open(R/'Game/data/generated'/f))['regions']:
  if abs(q['floor_y']-106.5)>.0001:continue
  vs=[];faces=[]
  for tri in q['triangles']:
   faces.append(list(range(len(vs),len(vs)+3)));vs.extend((x,-z,106.5)for x,z in tri)
  me=bpy.data.meshes.new(q['id']);me.from_pydata(vs,[],faces);ob=bpy.data.objects.new(q['id'],me);bpy.context.collection.objects.link(ob);me.materials.append(mat)
for q in P['fixture_instances']:
 at=q['emitter'];bpy.ops.object.light_add(type='POINT',location=(at[0],-at[2],at[1]));lamp=bpy.context.object;lamp.name=q['name']+'__SOURCE_REVIEW_LIGHT';lamp.data.energy=230;lamp.data.color=q['color'];lamp.data.shadow_soft_size=.05
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.cycles.use_denoising=False;s.cycles.max_bounces=4;s.render.threads_mode='FIXED';s.render.threads=4;s.world=bpy.data.worlds.new('Source review ambient');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.75,.81,.86,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.05
s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=1
bpy.ops.object.camera_add(location=(-14,-161.5,108.25));o=bpy.context.object;o.data.lens=18;o.rotation_euler=(Vector((-26,-160.5,108.1))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.filepath=str(W/'SOURCE_AFT_CROWN_SITTING_LIGHTING_CONTEXT001.png');assert not Path(s.render.filepath).exists();bpy.ops.render.render(write_still=True)
(W/'SOURCE_PHOTO_RECEIPT.json').write_text(json.dumps({'status':'PASS_SOURCE_CONTEXT_CAPTURE','image':Path(s.render.filepath).name,'sources':'Exact retained platform,sitting bays,new saved lighting native;original furniture/materials','visible_context':'Port open portal,seating,tables,glazing,roof,source piers and fitted opal lanterns','compiler_floor':'Exact parent triangles;neutral source-review surface','renderer':'Blender Cycles CPU32samples,no denoising,AgX,8 fixture-positioned point lights230W;not Godot radiometric equivalence','no_godot_CRT_hardware_exterior_vista_final_visual_acceptance':True},indent=2)+'\n')
