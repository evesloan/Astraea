"""Unsaved fresh-native/source context view; no source or export rewriting."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];G=R/'Game';P=json.load(open(W/'D17_RECEIVING_PLAN.json'));N=json.load(open(W/'NATIVE_EXPORT_CHECK.json'))
B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins={W/N[k][t]:N[k][t+'_sha256'] for k in ['corridor','patch'] for t in ['native','export']}
bpy.ops.wm.open_mainfile(filepath=str(W/N['corridor']['native']))
for o in bpy.context.scene.objects:
 if o.type=='MESH' and ('Roof' in o.name or o.name in ['D17_LinkSouthWall','D17_LinkWestStemWall']):o.hide_render=True
mat=next(o.data.materials[0] for o in bpy.context.scene.objects if o.type=='MESH')
for q in P['floor_regions']:
 vs=[];faces=[]
 for t in q['triangles']:
  pts=[B((x,102,z)) for x,z in t]
  if (Vector(pts[1])-Vector(pts[0])).cross(Vector(pts[2])-Vector(pts[0])).z<0:pts.reverse()
  k=len(vs);vs.extend(pts);faces.append((k,k+1,k+2))
 me=bpy.data.meshes.new(q['id']);me.from_pydata(vs,[],faces);me.materials.append(mat);o=bpy.data.objects.new('UNSAVED_'+q['id'],me);bpy.context.collection.objects.link(o)
for file in ['AST-RES-TIDAL_D16_service_receiving_r001.glb']:
 bpy.ops.import_scene.gltf(filepath=str(G/'assets/models'/file))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=640;s.render.resolution_y=480;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world.color=(.04,.04,.04)
bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=23;s.camera=camera
camera.location=B((-31,115,-505));camera.rotation_euler=(Vector(B((-14,102,-485)))-camera.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='AREA');light=bpy.context.object;light.location=B((-17,119,-486));light.data.energy=3500;light.data.size=15
light.rotation_euler=(Vector(B((-14,102,-485)))-light.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(W/'SOURCE_D17_LINK_RECEIVING_CUTAWAY.png');bpy.ops.render.render(write_still=True)
assert all(sha(p)==h for p,h in pins.items())
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'fresh_native_opened':N['corridor']['native'],'status':'rendered_for_review','native_exports_unchanged':True,'view':'SOURCE_D17_LINK_RECEIVING_CUTAWAY.png','diagnostic_cutaway_hidden_parts':['roof meshes','south link wall and west stem wall'],'temporary_floor_geometry':'exact runtime region triangles','D16_context':'exact retained service receiving export; roof and walls are lower receiving surfaces','ordinary_Godot_CRT_capture':False},indent=2)+'\n')
