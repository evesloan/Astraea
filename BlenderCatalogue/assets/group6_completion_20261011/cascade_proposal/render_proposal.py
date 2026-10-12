"""Saved-source interface review with original compiler/water context previews."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;R=P.parents[3]
bpy.ops.wm.open_mainfile(filepath=str(P/'Group6CascadeInterfaceProposal_r002.blend'));s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1800;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.world=bpy.data.worlds.new('Cascade source review world');s.world.color=(.3,.35,.4);s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD'
for m in bpy.data.materials:
 if m.use_nodes:
  b=m.node_tree.nodes.get('Principled BSDF')
  if b:m.diffuse_color=b.inputs['Base Color'].default_value
def xyz(p):return Vector((p[0],-p[2],p[1]))
# Compiler context preview uses the original records, never new floor ownership.
context=[]
source=R/'Game/data/generated/structural_meshes.json';d=json.loads(source.read_text())
for r in d['regions']:
 if r['id'] not in ['D08_aquatic_district_arrival','D08_gentle_waters_basin']:continue
 vertices=[];faces=[]
 for t in r['triangles']:
  j=len(vertices);vertices.extend([xyz((p[0],r['floor_y'],p[1])) for p in t]);faces.append((j,j+1,j+2))
 m=bpy.data.meshes.new('Review only '+r['id']);m.from_pydata(vertices,[],faces);m.update();o=bpy.data.objects.new(m.name,m);s.collection.objects.link(o);o.data.materials.append(bpy.data.materials['ASTRAEA_warm_stone']);context.append(o.name)
water_source=R/'Game/data/aquatic_section.json';water=json.loads(water_source.read_text())['basin'];mesh=bpy.data.meshes.new('Review original basin visual surface');mesh.from_pydata([xyz((p[0],water['water_y'],p[1])) for p in water['boundary']],[],[tuple(range(len(water['boundary'])))]);mesh.update();o=bpy.data.objects.new(mesh.name,mesh);s.collection.objects.link(o);material=bpy.data.materials.new('Review original water face');material.diffuse_color=(.10,.39,.44,1);o.data.materials.append(material);context.append(o.name)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=11;cam.data.clip_end=200;eye=(16.5,47.4,218.3);target=(23.1,44.6,215)
cam.location=xyz(eye);cam.rotation_euler=(xyz(target)-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(P/'SOURCE_CASCADE_PROPOSAL002.png');bpy.ops.render.render(write_still=True)
(P/'SOURCE_VIEW_RECEIPT002.json').write_text(json.dumps({'image':'SOURCE_CASCADE_PROPOSAL002.png','native':'Group6CascadeInterfaceProposal_r002.blend','eye_xyz':eye,'target_xyz':target,'orthographic_scale_m':11,'review_context_only_objects':context,'preview_input_sha256':{str(source.relative_to(R)):hashlib.sha256(source.read_bytes()).hexdigest(),str(water_source.relative_to(R)):hashlib.sha256(water_source.read_bytes()).hexdigest()},'native_resaved':False,'presentation':'Actual saved proposed console and exact registered cascade source in original shoulder/hood context. Original compiler floor/water-face previews are render-only and never saved or exported. Neutral studio/base-color geometry; no connected network, acoustic/fluid operation, ordinary lighting, engineering or final-art acceptance.'},indent=2)+'\n')
