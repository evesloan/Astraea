"""Parent-scheduled source-only CPU review; never save/export preview floors."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=json.loads((R/'review/RENDER_PLAN.json').read_text())
for path,sha in D['frozen_inputs'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==sha,'Frozen input changed: '+path
bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-STF-010.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=800;scene.render.resolution_y=500;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
# All original source geometry stays visible; no wall/roof removal for camera staging.
source_meshes=[o for o in scene.objects if o.type=='MESH'];assert len(source_meshes)==8407
for o in source_meshes:o.hide_render=False;o.hide_viewport=False;o.hide_set(False)
scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.28,.34,.38,1);bg.inputs['Strength'].default_value=.12
preview=bpy.data.collections.new('PREVIEW_ONLY_COMPILER_FLOORS_NEVER_SAVE_EXPORT');scene.collection.children.link(preview)
vs=[];faces=[]
for tri in D['floor_triangle_xz']:
 start=len(vs);vs.extend([(x,-z,12) for x,z in tri]);a,b,c=tri;signed=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);faces.append((start,start+2,start+1) if signed>0 else (start,start+1,start+2))
mesh=bpy.data.meshes.new('PREVIEW_ONLY_APPROVED_FLOOR');mesh.from_pydata(vs,[],faces);mesh.update();ob=bpy.data.objects.new('PREVIEW_ONLY_COMPILER_FLOOR',mesh);preview.objects.link(ob);ob['preview_only']=True;ob['never_export']=True;ob['provenance']=D['floor_provenance']
# Physical floor is compiler-owned; this top-surface preview is intentionally ephemeral.
mat=bpy.data.materials.get('ASTRAEA_staff_floor')
if mat is None:
 C=R.parents[1];role=json.loads((C/'materials/staff/manifest.json').read_text())['materials']['staff_floor'];mat=bpy.data.materials.new('PREVIEW_ONLY_staff_floor');mat.use_nodes=True;nodes=mat.node_tree.nodes;bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=role['roughness'];bs.inputs['Metallic'].default_value=role['metallic'];tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(C/'materials/staff'/role['file']),check_existing=True);tex.interpolation='Closest';mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
mesh.materials.append(mat);uv=mesh.uv_layers.new(name='MetreScaled')
for f in mesh.polygons:
 for li in f.loop_indices:
  q=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(q.x,-q.y)
# Fixture lens sits15mm below the actual opal face, avoiding self-shadowing; every lamp has source datum provenance.
datums=sorted([o for o in scene.objects if o.name.startswith('CRW_TASK_LIGHT_DATUM_')],key=lambda o:o.name);assert len(datums)==166
for datum in datums:
 assert datum['datum_kind']=='supported_staff_task_light';assert datum['source_housing'] in bpy.data.objects
 data=bpy.data.lights.new('SOURCE_REVIEW_'+datum.name,type='AREA');data.energy=160;data.color=(.76,.87,.95);data.shape='RECTANGLE';data.size=1.22;data.size_y=.18
 lamp=bpy.data.objects.new(data.name,data);preview.objects.link(lamp);lamp.location=datum.location.copy();lamp.location.z=float(datum['lowest_fixture_y'])-.015;lamp.rotation_euler=(0,0,0);lamp['source_datum']=datum.name;lamp['source_housing']=datum['source_housing'];lamp['source_only']=True
# Blender area light local-Z downward is Godot-world-Y downward.
camdata=bpy.data.cameras.new('SOURCE_REVIEW_CAMERA');camdata.lens=25;camdata.clip_start=.08;camdata.clip_end=180;camera=bpy.data.objects.new(camdata.name,camdata);preview.objects.link(camera);scene.camera=camera
scene.render.use_stamp=True;scene.render.use_stamp_note=True;scene.render.stamp_note='SOURCE ONLY | APPROVED SUPPORT PREVIEW | NO RUNTIME ADOPTION';scene.render.use_stamp_date=False;scene.render.use_stamp_time=False;scene.render.use_stamp_render_time=False;scene.render.use_stamp_frame=False;scene.render.use_stamp_scene=False;scene.render.use_stamp_camera=False;scene.render.use_stamp_filename=False;scene.render.stamp_font_size=12
for row in D['cameras']:
 x,y,z=row['eye_xyz'];tx,ty,tz=row['target_xyz'];camera.location=(x,-z,y);target=Vector((tx,-tz,ty));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(R/'review'/('SOURCE_ONLY_'+row['name']+'.png'));bpy.ops.render.render(write_still=True)
# No save_as_mainfile or export call exists. Verify original frozen bytes survived the transient preview.
for path,sha in D['frozen_inputs'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==sha
print('SOURCE ONLY render review completed; source/export preserved; preview geometry never saved/exported')
