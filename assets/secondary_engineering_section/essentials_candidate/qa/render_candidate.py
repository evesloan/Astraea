"""Actual imported GLB source diagnostic, no runtime acceptance. Scratch outputs only."""
from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
assert str(R)=='/workspace/scratch/375c2e438292/engineering-essentials'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(C/'assets/secondary_engineering_section/exports/AST-ENG-008.glb'))
bpy.ops.import_scene.gltf(filepath=str(R/'exports/AST-ENG-008_essentials.glb'))
def cv(p):return Vector((p[0],-p[2],p[1]))
# One explicitly QA-only floor matches the compiler top. No production geometry exports.
bpy.ops.mesh.primitive_plane_add(size=2,location=cv((31,6,-432)));floor=bpy.context.object;floor.name='QA_ONLY_COMPILER_FLOOR';floor.scale=(23,34,1)
mat=bpy.data.materials.new('QA_ONLY_retained_staff_floor');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.87;tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(C/'materials/staff/staff_floor.png'));tex.interpolation='Linear';mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);floor.data.materials.append(mat)
for q in floor.data.uv_layers.active.data:q.uv=(q.uv.x*46/.8,q.uv.y*68/.8)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=48;scene.cycles.use_denoising=False;scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast' if 'Medium High Contrast' in [] else 'None';scene.view_settings.exposure=0
fixtures=json.loads((C/'assets/secondary_engineering_section/source/section_contract.json').read_text())['fixtures']
settings={'plant_inspection_n':((30,8.5,-432.9),850),'plant_inspection_s':((39,8.5,-431.1),850),'control_task':((26,7.4,-462.95),650),'workbay_task':((26.5,7,-401.4),750),'isolation_task':((36,7.2,-441.4),500)}
for f in fixtures:
 p=list(f['position_xyz']);p[1]-=.08;target,power=settings.get(f['purpose'],((p[0],6,p[2]),450));d=bpy.data.lights.new(f['name'],'SPOT');d.energy=power;d.spot_size=math.radians(130);d.spot_blend=.6;d.shadow_soft_size=.1;o=bpy.data.objects.new(f['name']+'_DIAGNOSTIC',d);scene.collection.objects.link(o);o.location=cv(p);o.rotation_euler=(cv(target)-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('QA_CAMERA');o=bpy.data.objects.new('QA_CAMERA',cam);scene.collection.objects.link(o);scene.camera=o;cam.lens=18;cam.clip_start=.05;cam.clip_end=100
views=[('workbay',(27,7.65,-408.2),(27.0,7.5,-400.8)),('control',(30,7.65,-457.2),(26,7.35,-462.8))]
for name,eye,target in views:
 for light in [x for x in scene.objects if x.type=='LIGHT']:light.hide_render=light.name != ('DATUM_workbay_task_DIAGNOSTIC' if name=='workbay' else 'DATUM_control_task_DIAGNOSTIC')
 o.location=cv(eye);o.rotation_euler=(cv(target)-o.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(R/'qa'/('imported_'+name+'.png'));bpy.ops.render.render(write_still=True)
(R/'qa/render_manifest.json').write_text(json.dumps({'scope':'Blender actual imported-GLB furnishing/context diagnostic; not Godot or production illumination','retained_base_sha256':hashlib.sha256((C/'assets/secondary_engineering_section/exports/AST-ENG-008.glb').read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256((R/'exports/AST-ENG-008_essentials.glb').read_bytes()).hexdigest(),'eye_y':7.65,'world_strength':0,'unexplained_fill_lights':0,'source_marker_lights_authored':9,'active_source_lights_per_view':1,'active_sources':{'workbay':['DATUM_workbay_task'],'control':['DATUM_control_task']},'runtime_selection_reproduced':False,'physical_light_watts':settings,'fixture_offset_y':-.08,'views':views,'renderer':'Blender4.3.2 Cycles CPU48samples','production_light_energy_mapping':False,'qa_floor':'Single compiler-top preview using exact retained staff_floor PNG at0.8m tile; no export'},indent=2)+'\n')
