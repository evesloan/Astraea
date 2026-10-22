import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
from datetime import datetime,timezone
P=Path(__file__).resolve().parents[1];G=P.parent
original=P/'evidence/ActualBoundedGalleryContext.glb'
source=P/'evidence/BlenderReviewContext.glb'
# Blender4.3 predates KHR_node_visibility. Translate only its16 hidden light
# nodes by removing their light binding; preserve every geometry buffer byte.
assert not source.exists()
blob=original.read_bytes();length,kind=struct.unpack_from('<II',blob,12);data=json.loads(blob[20:20+length]);hidden=[]
for node in data['nodes']:
 ext=node.get('extensions',{})
 if 'KHR_node_visibility' not in ext:continue
 assert ext['KHR_node_visibility']['visible']==False and 'mesh' not in node and 'KHR_lights_punctual' in ext
 hidden.append(node['name']);del ext['KHR_node_visibility'];del ext['KHR_lights_punctual']
assert len(hidden)==16
for field in ['extensionsRequired','extensionsUsed']:data[field]=[v for v in data[field]if v!='KHR_node_visibility']
encoded=json.dumps(data,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);tail=blob[20+length:]
source.write_bytes(struct.pack('<III',0x46546c67,2,20+len(encoded)+len(tail))+struct.pack('<II',len(encoded),kind)+encoded+tail)
(P/'evidence/REVIEW_FORMAT_TRANSLATION.json').write_text(json.dumps({'original_sha256':hashlib.sha256(blob).hexdigest(),'review_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'unchanged_binary_geometry_sha256':hashlib.sha256(tail).hexdigest(),'hidden_light_bindings_removed':hidden,'source_modified':False},indent=2)+'\n')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
sources={str(source.relative_to(G)):hashlib.sha256(source.read_bytes()).hexdigest()}
for name in ['G7_Completion_R003_Body_1_03.glb','G7_Completion_R005B_Body_1_04.glb','G7_Completion_R003_Body_1_05.glb']:
 p=G/'assets/models'/name;assert p.exists();sources[str(p.relative_to(G))]=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.import_scene.gltf(filepath=str(p))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=False
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('ReviewWorld');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.35,.4,.5,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45
# Review-only illumination at actual authored fixture locations, not engine-light acceptance.
for x,z in [(100.8,-42),(100.8,-56),(100.8,-72),(100.8,-87),(96,-42)]:
 d=bpy.data.lights.new('ReviewFixture','AREA');d.energy=180;d.shape='DISK';d.size=3;o=bpy.data.objects.new('ReviewFixture',d);scene.collection.objects.link(o);o.location=(x,-z,96.3)
cam=bpy.data.cameras.new('ResidentReview');obj=bpy.data.objects.new('ResidentReview',cam);scene.collection.objects.link(obj);scene.camera=obj;cam.lens=23;cam.clip_start=.05;cam.clip_end=500
receipts=[]
for label,eye,target in [('RESIDENT_404_UNFINISHED',(97.0,94.6,-40.2),(104,94.8,-45.5)),('OUTER_GALLERY_UNFINISHED',(100.5,94.7,-99),(101,94.8,-44))]:
 out=P/'evidence'/(label+'.png');assert not out.exists()
 obj.location=(eye[0],-eye[2],eye[1]);t=Vector((target[0],-target[2],target[1]));obj.rotation_euler=(t-obj.location).to_track_quat('-Z','Y').to_euler()
 count=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  name=o.name
  if not any(w in name for w in ['PrivateViewPane','OvalAtriumGlass','ScreenedStreetGlass']):continue
  points=[o.matrix_world@Vector(v)for v in o.bound_box];plane=(min(v.x for v in points)+max(v.x for v in points))/2;inside=(eye[0]-plane)*(-1 if 'PrivateViewPane'in name else 1)>0
  mat=bpy.data.materials.new('CameraSidePrivacy');mat.use_nodes=True;mat.surface_render_method='DITHERED';bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.24,.38,.33,1)if inside else(.055,.09,.08,1);bs.inputs['Alpha'].default_value=.12 if inside else 1;bs.inputs['Roughness'].default_value=.16 if inside else .42;o.data.materials.clear();o.data.materials.append(mat);count+=1
 scene.render.filepath=str(out);scene.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
 receipts.append({'file':out.name,'created_utc':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'camera_godot':eye,'target_godot':target,'privacy_panes':count,'scope':'Actual bounded Godot gallery fixture export with404 private details and retained hull context, rendered in Blender; candidate not full main','unfinished':True,'final_visual_acceptance':False,'lighting':'diagnostic fixture-position illumination; not runtime lighting acceptance'})
(P/'evidence/VIEWS.json').write_text(json.dumps({'sources':sources,'views':receipts},indent=2)+'\n')
