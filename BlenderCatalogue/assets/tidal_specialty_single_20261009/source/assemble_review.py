from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector
O=Path(__file__).resolve().parents[1];R=O.parents[2];p=json.load(open(O/'PLAN.json'));bpy.ops.wm.read_factory_settings(use_empty=True)
def model(path,label,pos=(0,0,0),yaw=0):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));new=set(bpy.context.scene.objects)-before
 parent=bpy.data.objects.new(label,None);bpy.context.collection.objects.link(parent)
 for ob in new:
  if ob.parent not in new:ob.parent=parent
 parent.location=(pos[0],-pos[2],pos[1]);parent.rotation_euler.z=yaw
 return parent
model(O/'exports/TidalSpecialty102.glb','AuthoredShell')
model(R/'BlenderCatalogue/assets/quiet_cocoon_support_20261009/AST-RST-QC-001.glb','CocoonSupport',p['component']['world_origin'],p['component']['godot_yaw'])
for item in p['source_fixtures']:model(R/'Game/assets/models'/(item['catalogue_id']+'.glb'),item['catalogue_id'],item['origin'],item['yaw'])
for item in p['doors']:model(R/'Game/assets/models'/(item['source']+'.glb'),item['name'],item['world_origin'],item['godot_yaw'])
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
# Source-composition view only: no claim this is a Godot frame or final CRT presentation.
for i,item in enumerate(p['lights']):
 li=bpy.data.lights.new('ReviewFixture_'+str(i),'AREA');li.energy=100;li.shape='DISK';li.size=.8;ob=bpy.data.objects.new(li.name,li);bpy.context.collection.objects.link(ob);v=item['position'];ob.location=(v[0],-v[2],v[1]);li.color=(1,.82,.6)
li=bpy.data.lights.new('CourtAmbientReview','AREA');li.energy=300;li.size=5;ob=bpy.data.objects.new(li.name,li);bpy.context.collection.objects.link(ob);ob.location=(-59.1,298.4,85.8);ob.rotation_euler=(Vector((-55.5,298.4,85))-ob.location).to_track_quat('-Z','Y').to_euler();li.color=(.65,.83,1)
cam=bpy.data.cameras.new('CompositionReviewCamera');ob=bpy.data.objects.new(cam.name,cam);bpy.context.collection.objects.link(ob);ob.location=(-48.2,298.1,85.62);ob.rotation_euler=(Vector((-55.3,298.8,85.05))-ob.location).to_track_quat('-Z','Y').to_euler();cam.lens=20;bpy.context.scene.camera=ob
sc=bpy.context.scene;sc.world=bpy.data.worlds.new('ReviewWorld');sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=False;sc.render.resolution_x=800;sc.render.resolution_y=600;sc.render.resolution_percentage=100;sc.world.color=(.08,.08,.08);sc.render.image_settings.file_format='PNG';sc.render.filepath=str(O/'SOURCE_COMPOSITION_REVIEW.png')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'source/TidalSpecialty102Assembly.blend'),compress=True)
bpy.ops.render.render(write_still=True)
print('SOURCE_COMPOSITION_REVIEW_SAVED',flush=True)
