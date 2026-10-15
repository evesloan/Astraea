from pathlib import Path
import bpy,json,hashlib,struct
from mathutils import Matrix,Vector
D=Path(__file__).resolve().parent;R=Path('/workspace/astraea-protected-integration-20261012');r=json.loads((D/'NATIVE_RECEIVER_VERIFICATION.json').read_text());plan=json.loads((D/'NATIVE_PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();donor=R/plan['source_native'];assert sha(donor)==plan['source_native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(donor));source={}
def geometry(data):
 h=hashlib.sha256()
 for v in data.vertices:h.update(struct.pack('<3f',*v.co))
 for p in data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 for layer in data.uv_layers:
  h.update(layer.name.encode()+b'\0')
  for point in layer.data:h.update(struct.pack('<2f',*point.uv))
 return h.hexdigest()
for row in r['rigid_source_clones']:
 name=row['source']
 if name not in source:
  o=bpy.data.objects[name];source[name]={'mesh_sha256':geometry(o.data),'matrix':o.matrix_world.copy()}
native1=D/'native/D10_CONNECTED_SERVICE_RECEIVERS_r003.blend';assert sha(native1)==r['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(native1));maxerror=0
for row in r['rigid_source_clones']:
 o=bpy.data.objects[row['name']];pin=source[row['source']];assert geometry(o.data)==pin['mesh_sha256'];expected=Matrix(row['rigid_matrix_blender'])@pin['matrix'];error=max(abs(o.matrix_world[i][j]-expected[i][j])for i in range(4)for j in range(4));maxerror=max(maxerror,error);assert error<.0001
cloneproof={'status':'PASS_772_RIGID_SOURCE_NATIVE_MESH_UV_AND_TRANSFORMS','clones':len(r['rigid_source_clones']),'source_unique_meshes':len(source),'max_transform_element_error':maxerror,'source_native_sha256':sha(donor),'new_native_r003_sha256':sha(native1)};(D/'RIGID_SOURCE_GEOMETRY_VERIFICATION.json').write_text(json.dumps(cloneproof,indent=2)+'\n')
col=bpy.data.collections['D10_CONNECTED_SERVICE_RECEIVERS_R003'];col.hide_render=True;runtime=bpy.data.collections.new('D10_CONNECTED_SERVICE_RUNTIME_R004');bpy.context.scene.collection.children.link(runtime);groups={};noncollision={row['name']for row in r['rigid_source_clones']if 'Lens'in row['source']};batchrows=[]
for o in col.objects:
 if o.type!='MESH':continue
 for polygon in o.data.polygons:
  material=o.data.materials[polygon.material_index];key=(o.name.split('_')[1],material.name,o.name not in noncollision);group=groups.setdefault(key,{'verts':[],'faces':[],'uvs':[],'members':set(),'smooth':[]});group['members'].add(o.name);indices=[]
  for loopindex in polygon.loop_indices:
   loop=o.data.loops[loopindex];point=o.matrix_world@o.data.vertices[loop.vertex_index].co;indices.append(len(group['verts']));group['verts'].append(tuple(point));group['uvs'].append(tuple(o.data.uv_layers.active.data[loopindex].uv))
  group['faces'].append(indices);group['smooth'].append(polygon.use_smooth)
for i,(key,g)in enumerate(sorted(groups.items())):
 name=f'D10_SERVICE_BATCH_{i:03d}_{key[0]}';data=bpy.data.meshes.new(name);data.from_pydata(g['verts'],[],g['faces']);data.materials.append(bpy.data.materials[key[1]]);data.update();uv=data.uv_layers.new(name='AuthoredMetreUV')
 for polygon,smooth in zip(data.polygons,g['smooth']):
  polygon.use_smooth=smooth
  for loopindex in polygon.loop_indices:uv.data[loopindex].uv=g['uvs'][data.loops[loopindex].vertex_index]
 o=bpy.data.objects.new(name,data);runtime.objects.link(o);ps=[o.matrix_world@Vector(v)for v in o.bound_box];gv=lambda p:Vector((p.x,p.z,-p.y));ps=list(map(gv,ps));batchrows.append({'name':name,'material':key[1],'collide':key[2],'members':sorted(g['members']),'min':[min(p[j]for p in ps)for j in range(3)],'max':[max(p[j]for p in ps)for j in range(3)]})
I=D/'native_import/Game/assets/dining_service_receiving_20261015';file=I/'D10_CONNECTED_SERVICE_RECEIVERS_r004.glb';bpy.ops.object.select_all(action='DESELECT')
for o in runtime.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(file),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);native=D/'native/D10_CONNECTED_SERVICE_RECEIVERS_r004.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.wm.open_mainfile(filepath=str(native));bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.collections['D10_CONNECTED_SERVICE_RUNTIME_R004'].objects:o.select_set(True)
fresh=D/'D10_FRESH_REEXPORT_r004.glb';bpy.ops.export_scene.gltf(filepath=str(fresh),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);assert sha(fresh)==sha(file)and sha(donor)==plan['source_native_sha256'];(D/'NATIVE_RECEIVER_VERIFICATION_r003.json').write_text(json.dumps(r,indent=2)+'\n');r.update(native_file=native.name,native_sha256=sha(native),authoring_meshes=r['meshes'],meshes=len(batchrows),batches=batchrows,file=file.name,model_sha256=sha(file),raw_authoring_file='D10_CONNECTED_SERVICE_RECEIVERS_r003.glb',raw_authoring_sha256=sha(I/'D10_CONNECTED_SERVICE_RECEIVERS_r003.glb'))
for light in r['lights']:
 light['lens_batch']=next(b['name']for b in batchrows if light['lens']in b['members'])
(D/'NATIVE_RECEIVER_VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS_D10_EDITABLE_NATIVE_AND_RUNTIME_BATCHES',r['authoring_meshes'],r['meshes'],len(r['lights']))
