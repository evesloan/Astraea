from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files=[W/'StarAtlasSpecialtyTenthReceiving.blend']+[W/f'StarAtlasSpecialty_{i}.blend'for i in [121,127,133,139]];pins={str(p.relative_to(R)):sha(p)for p in files};bpy.ops.wm.open_mainfile(filepath=str(files[0]))
for p in files[1:]:
 with bpy.data.libraries.load(str(p),link=False)as(a,b):b.objects=a.objects
 for o in b.objects:
  if o:bpy.context.collection.objects.link(o)
p=W.parent/'star_atlas_specialty_ninth_20261010/StarAtlasSpecialtyNinthReceiving.blend';pins[str(p.relative_to(R))]=sha(p)
with bpy.data.libraries.load(str(p),link=False)as(a,b):b.objects=[n for n in a.objects if n!='SA_D13_NinthSouthTerminalGuard']
for o in b.objects:
 if o:bpy.context.collection.objects.link(o)
# Visualize exactly the retained southern slab owner, not an invented D12 floor.
owner=next(r for r in json.load(open(R/'Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json'))['regions']if r['id']=='D13_STAR_ATLAS_MISSING_STREET_0');verts=[];faces=[]
for triangle in owner['triangles']:
 start=len(verts);verts += [B([x,y,z])for y in [83.76,84]for x,z in triangle];faces.extend([[start,start+2,start+1],[start+3,start+4,start+5]])
for ring in owner['rings']:
 for i,a in enumerate(ring):
  b=ring[(i+1)%len(ring)];start=len(verts);verts += [B([x,y,z])for x,z,y in [(a[0],a[1],83.76),(b[0],b[1],83.76),(b[0],b[1],84),(a[0],a[1],84)]];faces.append([start,start+1,start+2,start+3])
mesh=bpy.data.meshes.new(owner['id']);mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(owner['id'],mesh);bpy.context.collection.objects.link(ob);mat=bpy.data.materials.new('DiagnosticRetainedSlab');mat.diffuse_color=(.42,.38,.3,1);mesh.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.world=bpy.data.worlds.new('DiagnosticContextWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.24,.26,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
for p in [(-84,87,-79),(-84,82,-79),(-94,81,-78),(-84,87,79),(-84,82,79)]:
 bpy.ops.object.light_add(type='AREA',location=B(p));bpy.context.object.data.energy=180;bpy.context.object.data.size=3
images=[]
for name,p,target,lens in [('SOURCE_CONTEXT_NORTH_STREET.png',(-84,85.6,-73.8),(-84,85,-79),18),('SOURCE_CONTEXT_NORTH_RAKERS.png',(-101,81.5,-85),(-84,83.5,-78),23),('SOURCE_CONTEXT_SOUTH_RAKERS.png',(-101,81.5,85),(-84,83.5,78),23)]:
 bpy.ops.object.camera_add(location=B(p));camera=bpy.context.object;camera.data.lens=lens;camera.rotation_euler=(Vector(B(target))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera;scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
for p,h in pins.items():assert sha(R/p)==h
(W/'SOURCE_CONTEXT_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'source_only':True,'native_pins_unchanged':pins,'retained_slab_owner':owner['id'],'D12_foundation_invented':False,'unsaved_source_views':True,'diagnostic_fill_lighting':True},indent=2)+'\n')
