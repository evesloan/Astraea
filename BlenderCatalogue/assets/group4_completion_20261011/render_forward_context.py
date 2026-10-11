"""Wide real-source review; unsaved assembly of pinned production assets and floors."""
from pathlib import Path
import bpy,json,hashlib,math,numpy as np
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2]
T=R/'Game/source_derivatives/group4_completion_20261011'
B=lambda p:(p[0],-p[2],p[1])
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [W/'Group4_Completion_Receiving_r002.blend',W/'AST-TRM-G4-023_station_receiving_r002.glb']}
bpy.ops.wm.open_mainfile(filepath=str(W/'Group4_Completion_Receiving_r002.blend'))
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD'
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.world.color=(.22,.22,.22);scene.view_settings.view_transform='Standard'
def import_source(path,at=(0,0,0),yaw=0):
 old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));obs=set(bpy.data.objects)-old
 wrap=bpy.data.objects.new('REVIEW_'+path.stem,None);scene.collection.objects.link(wrap)
 for o in obs:
  if o.parent not in obs:m=o.matrix_world.copy();o.parent=wrap;o.matrix_world=m
 wrap.location=B(at);wrap.rotation_euler.z=yaw
 return obs
for name in ['AST-TRM-G4-013_forward_source.glb','AST-TRM-G4-017_receiving_module.glb','AST-TRM-G4-016_continuous_guideway.glb']:
 import_source(T/name)
import_source(T/'AST-TRM-G4-011_cart_tram_component.glb',(-5.6,56.1,-432))
import_source(R/'Game/assets/models/AST-CIR-003.glb',(5.6,52.5,-449.2),0)
import_source(R/'Game/assets/models/AST-CIR-005_forward_breakroom_d03.glb',(0,0,-432))

regions=json.loads((T/'CANDIDATE_FLOOR_FIXTURE.json').read_text())
vs=[];fs=[]
for q in regions:
 for t in q['triangles']:
  # Retain actual complete triangles overlapping the review vicinity; no fabricated floor.
  if max(p[0] for p in t)<-22 or min(p[0] for p in t)>20 or max(p[1] for p in t)<-470 or min(p[1] for p in t)>-410:continue
  idx=len(vs);vs.extend(B((x,52.5,z)) for x,z in t);fs.append((idx,idx+1,idx+2))
me=bpy.data.meshes.new('Actual D09 compiled floor context');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['warm_stone'])
ob=bpy.data.objects.new(me.name,me);scene.collection.objects.link(ob)
def look(o,target):o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler()
target=(1.0,54.8,-448)
for i,(pos,power,size) in enumerate([((-19,73,-237),11000,24),((12,70,-250),14000,24),((-10,63,-276),7500,18)]):
 bpy.ops.object.light_add(type='AREA');o=bpy.context.object;o.data.energy=power;o.data.size=size;o.location=B(pos);look(o,target)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.location=B((24,65,-480));look(cam,target);cam.data.lens=36;cam.data.clip_end=2000;scene.camera=cam
for m in bpy.data.materials:
 if m.use_nodes:
  bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if bs:m.diffuse_color=bs.inputs['Base Color'].default_value
  tex=next((n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image is not None and n.image.size[0]>0),None)
  if tex:
   pixels=np.empty(len(tex.pixels),dtype=np.float32);tex.pixels.foreach_get(pixels)
   m.diffuse_color=(*pixels.reshape(-1,4)[:,:3].mean(axis=0),1)
scene.render.filepath=str(W/'SOURCE_GROUP4_FORWARD_RECEIVING_WIDE001.png');bpy.ops.render.render(write_still=True)
for p,h in before.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
receipt=dict(source_image='SOURCE_GROUP4_FORWARD_RECEIVING_WIDE001.png',sha256=hashlib.sha256((W/'SOURCE_GROUP4_FORWARD_RECEIVING_WIDE001.png').read_bytes()).hexdigest(),pixels=[1920,1080],real_source=True,native_and_export_unchanged=True,source_view_only=True,
    scene='Retained forward station 002, new r002 annex floor/ledgers/sill tongue and lenses, guideway and receiver003, original car and two-stop lift cabin, actual current forward public core and compiled D09 floor',
    limits='Unsaved contextual source assembly, neutral Workbench packed material-average-color review; texture detail omitted and stationary car/cabin poses. No Godot, ordinary-world lighting, CRT, gameplay, engineering or final-art acceptance.')
(W/'FORWARD_SOURCE_PHOTO_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print('REAL_SOURCE_WIDE_RENDER_COMPLETE')
