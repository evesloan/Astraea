"""Root-serialized Blender builder, deliberately not executed during preparation.
blender -b --python build_candidate_blender.py
Writes NEW scratch outputs only; refuses existing outputs or changed pins.
"""
import bpy,json,pathlib,hashlib
D=pathlib.Path(__file__).resolve().parent
O=D/'root_build'
if O.exists():raise RuntimeError('Output exists: preserve it; create an explicitly versioned successor')
for p in json.loads((D/'SOURCE_PINS.json').read_text()):
 actual=hashlib.sha256(pathlib.Path(p['path']).read_bytes()).hexdigest()
 if actual!=p['current_sha256']:raise RuntimeError('Source drift, root revalidation required: '+p['path'])
for c in json.loads((D/'ROOM_CONTACTS.json').read_text()):
 if hashlib.sha256(pathlib.Path(c['shell_path']).read_bytes()).hexdigest()!=c['shell_sha256']:raise RuntimeError('Room shell drift: '+c['shell_path'])
data=json.loads((D/'GEOMETRY_PROPOSAL.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('Diagnostic_receiver_neutral_NOT_FINAL_ART');mat.diffuse_color=(.48,.53,.55,1)
mat2=bpy.data.materials.new('Diagnostic_bearing_NOT_FINAL_ART');mat2.diffuse_color=(.36,.27,.13,1)
faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
for p in data['parts']:
 x,y,z,X,Y,Z=p['bounds']
 # Author actual world geometry: Blender Z-up conversion, GLTF restores game Y-up.
 world=[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)]
 mesh=bpy.data.meshes.new(p['id']);mesh.from_pydata([(a,-c,b) for a,b,c in world],[],faces);mesh.update()
 obj=bpy.data.objects.new(p['id'],mesh);bpy.context.collection.objects.link(obj)
 obj.data.materials.append(mat2 if p['kind']=='bearing_node' else mat)
 obj['owner']='Root isolated Quiet Grove upper receiving candidate';obj['status']='SOURCE_ONLY_NOT_ADOPTED';obj['source_bounds_world_xyz']=p['bounds'];obj['counterparts_pending']=True
bpy.context.scene.unit_settings.system='METRIC';O.mkdir()
bpy.ops.wm.save_as_mainfile(filepath=str(O/'quiet_grove_upper_receiver.blend'))
bpy.ops.export_scene.gltf(filepath=str(O/'quiet_grove_upper_receiver.glb'),export_format='GLB',export_yup=True,export_apply=True)
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in O.iterdir() if p.is_file()}
(O/'BUILD_RECEIPT.json').write_text(json.dumps({'status':'source candidate built; root must inspect normals, source composition and export contacts before acceptance','meshes':len(data['parts']),'files':files,'runtime_installed':False,'art_accepted':False},indent=2))
