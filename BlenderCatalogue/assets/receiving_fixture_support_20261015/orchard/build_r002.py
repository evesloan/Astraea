from pathlib import Path
import bpy,json,hashlib,math,struct,copy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
D=Path(__file__).parent;V=D.parent.parent/'orchard_external_receiving_20261015';R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';oldnative=V/'native/ORCHARD_SERVICE_GATEWAY_r001.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=json.loads((V/'NATIVE_VERIFICATION.json').read_text());assert sha(oldnative)==old['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(oldnative));bpy.context.preferences.filepaths.save_version=0
col=bpy.data.collections['ORCHARD_EXTERNAL_RECEIVING_AUTHORING_R001'];runtime=bpy.data.collections['ORCHARD_EXTERNAL_RECEIVING_RUNTIME_R001'];parts=list(col.objects);extras=[bpy.data.objects[r['replacement_name']]for r in old['walls']];B=lambda p:Vector((p[0],-p[2],p[1]));GV=lambda p:Vector((p.x,p.z,-p.y))
def geometry(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
 for p in o.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 for l in o.data.uv_layers:
  for x in l.data:h.update(struct.pack('<2f',*x.uv))
 return h.hexdigest()
before={o.name:{'geometry':geometry(o),'matrix':o.matrix_world.copy()}for o in parts+extras};referenced={sha for o in parts for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image and n.image.packed_file for sha in [hashlib.sha256(bytes(n.image.packed_file.data)).hexdigest()]}
deltas={i:Matrix.Translation(B(t))@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation(-B(p))for i,p,t in[(0,(62,64.1,-214),(62,64.1,-214)),(1,(62,64.1,-194),(62,64.1,-194))]};changed=[]
for o in parts:
 for i,delta in deltas.items():
  if o.name.startswith(f'ORX_Hood{i}__'):o.matrix_world=delta@o.matrix_world;changed.append(o.name)
assert len(changed)==14
clones=copy.deepcopy(old['rigid_clones']);lights=copy.deepcopy(old['lights'])
for row in clones:
 for i,delta in deltas.items():
  if row['name'].startswith(f'ORX_Hood{i}__'):row['rigid_matrix_blender']=[list(r)for r in delta@Matrix(row['rigid_matrix_blender'])]
for row in lights:
 for i,delta in deltas.items():
  if row['name'].startswith(f'ORX_LIGHT_{i}_'):row['at']=list(GV(delta@B(row['at'])))
roof=bpy.data.objects['ORX_SourceJoinedRoof'];bvh=BVHTree.FromPolygons([roof.matrix_world@v.co for v in roof.data.vertices],[list(p.vertices)for p in roof.data.polygons],all_triangles=False);mounts=[]
for o in parts:
 if 'CanopyTie'not in o.name:continue
 ps=[o.matrix_world@Vector(v)for v in o.bound_box];x=(min(p.x for p in ps)+max(p.x for p in ps))/2;y=(min(p.y for p in ps)+max(p.y for p in ps))/2;top=max(p.z for p in ps);hit=bvh.ray_cast(Vector((x,y,64.79)),Vector((0,0,1)),.05)[0];assert hit is not None and abs(hit.z-64.8)<.00005 and top-hit.z>.0049 and top<64.98,o.name;mounts.append({'name':o.name,'roof_contact_xyz':[x,hit.z,-y],'stem_top_y':top,'positive_embed_m':top-hit.z})
assert len(mounts)==8
for o in parts+extras:
 assert geometry(o)==before[o.name]['geometry']
 if o.name not in changed:assert o.matrix_world==before[o.name]['matrix']
for o in list(runtime.objects):bpy.data.objects.remove(o,do_unlink=True)
bounds=[]
for o in parts:
 o.data.calc_loop_triangles();ps=[GV(o.matrix_world@Vector(v))for v in o.bound_box];bounds.append({'name':o.name,'min':[min(p[i]for p in ps)for i in range(3)],'max':[max(p[i]for p in ps)for i in range(3)],'triangles':len(o.data.loop_triangles)})
groups={};batchrows=[]
for o in parts:
 for polygon in o.data.polygons:
  material=o.data.materials[polygon.material_index];key=(material.name,'Lens'not in o.name);g=groups.setdefault(key,{'vs':[],'fs':[],'uvs':[],'members':set()});g['members'].add(o.name);ix=[]
  for li in polygon.loop_indices:ix.append(len(g['vs']));g['vs'].append(tuple(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co));g['uvs'].append(tuple(o.data.uv_layers.active.data[li].uv))
  g['fs'].append(ix)
for i,(key,g)in enumerate(sorted(groups.items())):
 name=f'ORX_BATCH_{i:03d}';data=bpy.data.meshes.new(name);data.from_pydata(g['vs'],[],g['fs']);data.update();data.materials.append(bpy.data.materials[key[0]]);uv=data.uv_layers.new(name='UVMap')
 for li in range(len(data.loops)):uv.data[li].uv=g['uvs'][data.loops[li].vertex_index]
 o=bpy.data.objects.new(name,data);runtime.objects.link(o);ps=[GV(Vector(v))for v in o.bound_box];batchrows.append({'name':name,'material':key[0],'collide':key[1],'members':sorted(g['members']),'min':[min(p[j]for p in ps)for j in range(3)],'max':[max(p[j]for p in ps)for j in range(3)]})
for row in lights:row['lens_batch']=next(b['name']for b in batchrows if row['lens']in b['members'])
I=D/'import/Game/assets/orchard_external_receiving_20261015';I.mkdir(parents=True,exist_ok=True);model=I/'ORCHARD_SERVICE_GATEWAY_r002.glb';bpy.ops.object.select_all(action='DESELECT')
for o in list(runtime.objects)+extras:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(model),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);N=D/'native';N.mkdir(exist_ok=True);native=N/'ORCHARD_SERVICE_GATEWAY_r002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.wm.open_mainfile(filepath=str(native));fresh=D/'FRESH_REEXPORT_r002.glb';bpy.ops.export_scene.gltf(filepath=str(fresh),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);assert sha(fresh)==sha(model)and sha(oldnative)==old['native_sha256'];newrefs={hashlib.sha256(bytes(n.image.packed_file.data)).hexdigest()for o in bpy.data.collections['ORCHARD_EXTERNAL_RECEIVING_AUTHORING_R001'].objects for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image and n.image.packed_file};assert newrefs==referenced
receipt={**old,'file':model.name,'native_file':native.name,'native_sha256':sha(native),'model_sha256':sha(model),'batches':batchrows,'bounds':bounds,'lights':lights,'rigid_clones':clones,'revision':'r002','predecessor_native_sha256':old['native_sha256'],'fixture_support_correction':True};(D/'NATIVE_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(D/'NATIVE_PLAN.json').write_text((V/'NATIVE_PLAN.json').read_text());(D/'NATIVE_FIXTURE_SUPPORT_VERIFICATION.json').write_text(json.dumps({'status':'PASS_EXACT_COMPONENT_GEOMETRY_UV_AND_UNCHANGED_POSES_EXCEPT14_FIXTURE_POSES','changed_pose_names':changed,'unchanged_mesh_data':len(parts)+len(extras),'unchanged_other_poses':len(parts)+len(extras)-14,'all8_actual_roof_mounts':mounts,'referenced_image_payloads_identical':True,'referenced_payload_count':len(referenced),'fresh_export_exact':True,'native_sha256':sha(native),'source_r001_retained':True,'floor_wall_frame_meshes_and_poses_unchanged':True},indent=2)+'\n');print('PASS_ORCHARD_R002_ACTUAL_ROOF_SUPPORT',len(parts),len(mounts))
