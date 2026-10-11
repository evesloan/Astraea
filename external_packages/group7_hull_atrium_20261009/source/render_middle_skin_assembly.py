"""Read-only diagnostic assembly of checked compact frame/skin GLBs in Blender."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];frame=json.loads((P/'docs/MIDDLE_EXTERIOR_PLACEMENT_AND_SEAMS.json').read_text());skin=json.loads((P/'docs/MIDDLE_SKIN_PLACEMENT_AND_INTERFACES.json').read_text());natives=[P/frame['source'],P/skin['source']];hashes=[hashlib.sha256(f.read_bytes()).hexdigest() for f in natives]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for row in frame['exports']+skin['exports']:bpy.ops.import_scene.gltf(filepath=str(P/row['path']))
# Exact retained D05 slab supports the first camera; no room walls/fittings added.
rows=json.loads((P/'dependencies/canonical_9d6f85/Game/data/generated/received_structural_meshes.json').read_text())['regions'];r=next(r for r in rows if r['id']=='D05_directory_05_authored_floor');v=[];faces=[]
for t in r['triangles']:i=len(v);v.extend((q[0],-q[1],r['floor_y']) for q in t);faces.append((i,i+1,i+2))
me=bpy.data.meshes.new('QA exact retained D05 floor');me.from_pydata(v,[],faces);o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);m=bpy.data.materials.new('QA neutral floor');m.diffuse_color=(.28,.31,.34,1);me.materials.append(m)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world=bpy.data.worlds.new('QA assembly daylight');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.64,.71,.82,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
sun=bpy.data.objects.new('QA diagnostic sun',bpy.data.lights.new('QA diagnostic sun','SUN'));s.collection.objects.link(sun);sun.data.energy=2;sun.rotation_euler=(.6,-.3,-.5)
c=bpy.data.objects.new('QA camera',bpy.data.cameras.new('QA camera'));s.collection.objects.link(c);s.camera=c;receipts=[]
for name,eye,target,lens,kind in [('middle_skin_directory05_normal_eye',(-96,22.6,-22),(-119.7,24.5,-18),32,'Supported at retained D05 floor+1.6m; occupied room architecture absent'),('middle_skin_west_diagnostic',(-156,44,-96),(-119.7,39,-86),42,'External diagnostic camera; not a supported route')]:
 c.location=(eye[0],-eye[2],eye[1]);q=Vector((target[0],-target[2],target[1]));c.rotation_euler=(q-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;s.render.filepath=str(P/'qa/exterior_views'/(name+'.png'));bpy.ops.render.render(write_still=True);receipts.append({'image':s.render.filepath,'eye_world_xyz':eye,'scope':kind})
assert hashes==[hashlib.sha256(f.read_bytes()).hexdigest() for f in natives]
(P/'qa/middle_skin_source_view_receipt.json').write_text(json.dumps({'views':receipts,'native_hashes':hashes,'natives_resaved':False,'context':'Frame plus skin compact GLBs inspected in Blender only. Diagnostic daylight; no Game importer/engine. Wider retained room source meshes absent. Transparency/material performance and privacy/view rays require integrated root checks.','final_art_accepted':False},indent=2)+'\n');print('MIDDLE_SKIN_SOURCE_VIEWS',len(receipts))
