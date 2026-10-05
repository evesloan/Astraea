"""Inspect crown bearing chains with read-only existing slab/keel source context."""
from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];G=C.parent/'astraea-godot-production-20261003';bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-CMD-001.blend'))
m=bpy.data.materials.new('QA_ONLY_existing_bands');m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.33,.36,.34,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9
for r in json.loads((G/'data/generated/structural_meshes.json').read_text())['regions']:
 if r['id']not in['D06_atrium_circulation','D09_atrium_circulation','D12_atrium_circulation','D16_atrium_circulation','D18_atrium_structural_cap','D18_fore_apron','D18_aft_apron']:continue
 verts=[];faces=[];top=r['floor_y'];bot=top-r['thickness']
 for tri in r['triangles']:
  n=len(verts);verts.extend((x,-z,y)for y in[bot,top]for x,z in tri);faces.extend([(n+2,n+1,n),(n+3,n+4,n+5)])
 for ring in r['rings']:
  for a,b in zip(ring,ring[1:]+ring[:1]):
   n=len(verts);verts.extend((x,-z,y)for y in[bot,top]for x,z in[a,b]);faces.append((n,n+1,n+3,n+2))
 me=bpy.data.meshes.new('QA_ONLY_'+r['id']);me.from_pydata(verts,[],faces);me.materials.append(m);o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
with bpy.data.libraries.load(str(C/'assets/lower_hull_body/source/AST-HUL-001.blend'),link=False)as(src,dst):dst.objects=[n for n in src.objects if n=='HUL_KeelPan']
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o);o.name='QA_ONLY_existing_'+o.name
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=900;scene.render.resolution_y=660;scene.render.resolution_percentage=100;scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.36,.42,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
# Diagnostic daylight is not exported or an in-engine lighting claim.
l=bpy.data.lights.new('QA_ONLY_key','AREA');l.energy=200000;l.shape='DISK';l.size=100;ob=bpy.data.objects.new(l.name,l);bpy.context.collection.objects.link(ob);ob.location=(80,-150,180);ob.rotation_euler=(Vector((0,0,55))-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('QA_bearing');o=bpy.data.objects.new(cam.name,cam);bpy.context.collection.objects.link(o);o.location=(136,-166,162);o.rotation_euler=(Vector((0,0,55))-o.location).to_track_quat('-Z','Y').to_euler();cam.lens=38;cam.clip_end=1800;scene.camera=o;scene.render.filepath=str(R/'qa/source_bearing_context.png');bpy.ops.render.render(write_still=True)
