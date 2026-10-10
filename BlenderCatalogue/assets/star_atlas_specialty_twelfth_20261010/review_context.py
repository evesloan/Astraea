from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files=[W/'StarAtlasSpecialtyTwelfthReceiving.blend']+[W/f'StarAtlasSpecialty_{i}.blend'for i in [365,371,377,383,389,395]];pins={str(p.relative_to(R)):sha(p)for p in files};bpy.ops.wm.open_mainfile(filepath=str(files[0]))
for p in files[1:]:
 with bpy.data.libraries.load(str(p),link=False)as(a,b):b.objects=a.objects
 for o in b.objects:
  if o:bpy.context.collection.objects.link(o)
# Reconstruct only exact original retained D14 street slabs for diagnostic source context.
slab_owners=[]
for owner in json.load(open(R/'Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json'))['regions']:
 if owner['id']not in ['D14_STAR_ATLAS_MISSING_STREET_0','D14_STAR_ATLAS_MISSING_STREET_1']:continue
 slab_owners.append(owner['id']);verts=[];faces=[]
 for triangle in owner['triangles']:
  start=len(verts);verts += [B([x,y,z])for y in [88.26,88.5]for x,z in triangle];faces.extend([[start,start+2,start+1],[start+3,start+4,start+5]])
 for ring in owner['rings']:
  for i,a in enumerate(ring):
   b=ring[(i+1)%len(ring)];start=len(verts);verts += [B([x,y,z])for x,z,y in [(a[0],a[1],88.26),(b[0],b[1],88.26),(b[0],b[1],88.5),(a[0],a[1],88.5)]];faces.append([start,start+1,start+2,start+3])
 mesh=bpy.data.meshes.new(owner['id']);mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(owner['id'],mesh);bpy.context.collection.objects.link(ob);mat=bpy.data.materials.new('DiagnosticRetainedSlab');mat.diffuse_color=(.42,.38,.3,1);mesh.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.world=bpy.data.worlds.new('DiagnosticContextWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.24,.26,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
for p in [(-84,91.5,-108.6),(-84,86.5,-108.6),(-94,86,-107.6),(-84,91.5,108.6),(-84,86.5,108.6)]:
 bpy.ops.object.light_add(type='AREA',location=B(p));bpy.context.object.data.energy=180;bpy.context.object.data.size=3
images=[]
for name,p,target,lens in [('SOURCE_CONTEXT_NORTH_STREET.png',(-84,90.1,-98.5),(-84,89.5,-108.6),18),('SOURCE_CONTEXT_NORTH_RAKERS.png',(-101,86,-115),(-84,88,-104.5),23),('SOURCE_CONTEXT_SOUTH_RAKERS.png',(-101,86,115),(-84,88,104.5),23)]:
 bpy.ops.object.camera_add(location=B(p));camera=bpy.context.object;camera.data.lens=lens;camera.rotation_euler=(Vector(B(target))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera;scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
for p,h in pins.items():assert sha(R/p)==h
(W/'SOURCE_CONTEXT_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'source_only':True,'native_pins_unchanged':pins,'retained_slab_owners':slab_owners,'D13_foundation_invented':False,'unsaved_source_views':True,'diagnostic_fill_lighting':True},indent=2)+'\n')

# Unsaved top cutaways expose retained programme geometry for layout review.
layout_images=[];hidden={};plan=json.load(open(W/'RUNTIME_PLAN.json'))
for room in plan['rooms']:
 idx=room['allocation']['source_envelope_index'];native=W/f'StarAtlasSpecialty_{idx}.blend';bpy.ops.wm.open_mainfile(filepath=str(native));hidden[str(idx)]=[]
 for part in room['parts']:
  if 'Ceiling'in part['name']or '_Roof'in part['name']:
   ob=bpy.data.objects.get(part['name']);assert ob is not None;ob.hide_render=True;hidden[str(idx)].append(part['name'])
 assert len(hidden[str(idx)])==(3 if idx==395 else 2)
 a=room['allocation'];x=sum(a['allocation_x'])/2;z=sum(a['allocation_z'])/2
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.world=bpy.data.worlds.new('DiagnosticPlanWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.24,.26,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
 for px in [x-4,x,x+4]:
  bpy.ops.object.light_add(type='AREA',location=B([px,94.5,z]));bpy.context.object.data.energy=140;bpy.context.object.data.size=3
 bpy.ops.object.camera_add(location=B([x,103.5,z+.001]));camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=16;camera.rotation_euler=(Vector(B([x,88.5,z]))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera;name=f'SOURCE_PLAN_CUTAWAY_{idx}.png';scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);layout_images.append(name)
for p,h in pins.items():assert sha(R/p)==h
(W/'SOURCE_LAYOUT_RUN.json').write_text(json.dumps({'status':'PASS','images':layout_images,'source_only':True,'unsaved_cutaway_views':True,'hidden_for_diagnostic_only':hidden,'native_pins_unchanged':pins},indent=2)+'\n')
