"""Diagnostic render using the actual two exports; temporary floor/light only."""
from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for file,anchor in [(R/'exports/AST-STF-009.glb',(0,0,0)),(C/'assets/arrivals_fusion/exports/AST-ARR-002.glb',(-31,432,0))]:
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(file));new=set(bpy.context.scene.objects)-before;root=bpy.data.objects.new('QA_Anchor',None);bpy.context.collection.objects.link(root)
 for o in new:
  if o.parent not in new:o.parent=root
 root.location=anchor
m=bpy.data.materials.new('QA_Floor');m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.22,.26,.26,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
bpy.ops.mesh.primitive_cube_add(size=1,location=(-54,432,5.87));o=bpy.context.object;o.dimensions=(12,6,.24);o.data.materials.append(m)
for p,power,size in [((-56,432,8.995),160,1.1),((-52,432,9.8),160,2.2)]:
 data=bpy.data.lights.new('QA_Area','AREA');data.energy=power;data.color=(.8,.9,1);data.shape='DISK';data.size=size;o=bpy.data.objects.new('QA_Area',data);bpy.context.collection.objects.link(o);o.location=p
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=False;scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.1,.14,.18,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.1;scene.view_settings.view_transform='AgX'
data=bpy.data.cameras.new('QA_Fusion');o=bpy.data.objects.new('QA_Fusion',data);bpy.context.collection.objects.link(o);o.location=(-51.8,432,7.65);o.rotation_euler=(Vector((-56,432,7.65))-o.location).to_track_quat('-Z','Y').to_euler();data.lens=19;scene.camera=o;scene.render.filepath=str(R/'qa/fusion_collar_source_preview.png');bpy.ops.render.render(write_still=True)
