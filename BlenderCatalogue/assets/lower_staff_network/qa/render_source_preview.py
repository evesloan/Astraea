"""Blender-only diagnostic pixels. Preview floors and shared dynamic models are NOT kit exports."""
from pathlib import Path
import bpy,math,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/section_contract.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-STF-009.blend'))
# Preview support floor. Production owns the actual polygon union and overlap subtraction.
m=bpy.data.materials.new('QA_ONLY_floor');m.diffuse_color=(.22,.26,.26,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.22,.26,.26,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9
def union_cells(rects):
 xs=sorted({r[k]for r in rects for k in [0,1]});zs=sorted({r[k]for r in rects for k in [2,3]})
 for x0,x1 in zip(xs,xs[1:]):
  for z0,z1 in zip(zs,zs[1:]):
   if any(r[0]<=(x0+x1)/2<=r[1] and r[2]<=(z0+z1)/2<=r[3]for r in rects):yield x0,x1,z0,z1
for d in D['decks']:
 for x0,x1,z0,z1 in union_cells(d['floor_union_rectangles_x0_x1_z0_z1']):
  bpy.ops.mesh.primitive_cube_add(size=1,location=((x0+x1)/2,-(z0+z1)/2,d['floor_y']-.13));o=bpy.context.object;o.name='QA_ONLY_support';o.dimensions=(x1-x0,z1-z0,.24);o.data.materials.append(m)
for file,xyz,angle in [('commons_lift_cabin/exports/AST-CIR-003_three_stop.glb',(-23.2,490,0),math.pi/2),('telescoping_gate/exports/AST-DOR-003.glb',(-23.08,490,0),3*math.pi/2)]:
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(C/'assets'/file));new=set(bpy.context.scene.objects)-before;root=bpy.data.objects.new('QA_ONLY_dynamic_reference',None);bpy.context.collection.objects.link(root)
 for o in new:
  if o.parent not in new:o.parent=root
 root.location=xyz;root.rotation_euler.z=angle
for mark in D['light_markers']:
 x,y,z=mark['position']
 if mark['deck']!=1 or z> -475:continue
 data=bpy.data.lights.new(mark['name'],'AREA');data.energy=130;data.color=(.79,.9,1);data.shape='DISK';data.size=1.1;obj=bpy.data.objects.new(mark['name']+'_QA_LIGHT',data);bpy.context.collection.objects.link(obj);obj.location=(x,-z,y-.01)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.1,.14,.18,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.1
scene.view_settings.view_transform='AgX'
def render(name,pos,target,lens=24):
 data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.clip_end=1000;scene.camera=o;scene.render.filepath=str(R/'qa'/name);bpy.ops.render.render(write_still=True)
render('source_landing_preview.png',(-19.7,492.0,1.70),(-23.15,490,1.48),20)
render('source_corridor_preview.png',(-55.9,499.9,1.65),(-56.8,482,1.7),23)
