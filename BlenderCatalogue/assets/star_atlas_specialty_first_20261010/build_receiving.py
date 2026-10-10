from pathlib import Path
import bpy,json,hashlib,shutil
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.loads((W/'RECEIVING_PLAN.json').read_text());B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def add(part):
 mesh=bpy.data.meshes.new(part['name']);mesh.from_pydata([B(v)for v in part['verts']],[],part['faces']);mesh.update()
 role=part['role'];mat=bpy.data.materials.get('SpecialtyReceiving_'+role)
 if not mat:
  mat=bpy.data.materials.new('SpecialtyReceiving_'+role);mat.diffuse_color=(.58,.54,.45,1)if role=='warm_stone'else(.46,.4,.27,1);mat.use_nodes=True
  bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color
  path=R/'Game/assets/models'/('AST-LIB-011_'+role+'.png')
  if path.exists():
   n=mat.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(path),check_existing=True);n.image.pack();mat.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 mesh.materials.append(mat);uv=mesh.uv_layers.new(name='MetreScaled')
 for face in mesh.polygons:
  normal=face.normal;u=Vector((1,0,0))if abs(normal.z)>.7 else Vector((-normal.y,normal.x,0)).normalized();v=normal.cross(u)
  for li in face.loop_indices:co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(co.dot(u),co.dot(v))
 ob=bpy.data.objects.new(part['name'],mesh);bpy.context.collection.objects.link(ob);ob['runtime_collision']=True;ob['material_role']=role;return ob
records=[]
def save_export(native,out,selected=False):
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(W/native));bpy.ops.export_scene.gltf(filepath=str(W/out),export_format='GLB',export_extras=True,export_yup=True,export_apply=True,use_selection=selected);s=sha(W/out)
 bpy.ops.wm.open_mainfile(filepath=str(W/native));bpy.ops.export_scene.gltf(filepath=str(W/out),export_format='GLB',export_extras=True,export_yup=True,export_apply=True,use_selection=selected);assert sha(W/out)==s
 shutil.copy2(W/out,R/'Game/assets/models'/out);records.append({'native':native,'native_sha256':sha(W/native),'export':out,'export_sha256':s,'fresh_native_repeat_identical':True})
bpy.ops.wm.read_factory_settings(use_empty=True)
for p in P['parts']:add(p)
save_export('StarAtlasSpecialtyFirstReceiving.blend',P['model_file'])
bpy.ops.wm.open_mainfile(filepath=str(R/'BlenderCatalogue/assets/star_atlas_upper_commons_20261009/source/StarAtlasUpperCommons.blend'))
def fingerprint(o):
 return hashlib.sha256(repr((str(o.matrix_world),[(tuple(v.co))for v in o.data.vertices]if o.type=='MESH'else[],[tuple(p.vertices)for p in o.data.polygons]if o.type=='MESH'else[],[m.name for m in o.data.materials]if o.type=='MESH'else[])).encode()).hexdigest()
changed=[p['name']for p in P['commons_patches']];before={o.name:fingerprint(o)for o in bpy.data.objects if o.name not in changed};bpy.ops.object.select_all(action='DESELECT')
for patch in P['commons_patches']:
 old=bpy.data.objects[patch['name']];verts=[];faces=[]
 for p in patch['replacement_parts']:
  off=len(verts);verts.extend([B(v)for v in p['verts']]);faces.extend([[off+i for i in f]for f in p['faces']])
 mesh=bpy.data.meshes.new(old.name+'_DoorMouth');mesh.from_pydata(verts,[],faces);mesh.update()
 for m in old.data.materials:mesh.materials.append(m)
 uv=mesh.uv_layers.new(name='MetreScaled')
 for face in mesh.polygons:
  for li in face.loop_indices:co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(co.x,co.z)
 old.data=mesh;old.select_set(True)
assert before=={o.name:fingerprint(o)for o in bpy.data.objects if o.name not in changed}
save_export('StarAtlasUpperCommonsSpecialtyFirst.blend',P['commons_patch_file'],True)
P['exports']=records;P['unchanged_original_objects']=len(before);assert len(before)==512
(W/'RECEIVING_NATIVE_CHECK.json').write_text(json.dumps({'status':'PASS','unchanged_original_objects':len(before),'exports':records},indent=2)+'\n')
(W/'RUNTIME_RECEIVING.json').write_text(json.dumps(P,indent=2)+'\n')
