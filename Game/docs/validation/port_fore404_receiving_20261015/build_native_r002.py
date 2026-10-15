from pathlib import Path
import bpy,json,hashlib
D=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((D/'NATIVE_VERIFICATION_r001.json').read_text());old=D/'native/PORT_FORE404_RECEIVER_r001.blend';oldglb=D/'import/Game/assets/port_fore404_receiving_20261015/PORT_FORE404_RECEIVER_r001.glb';assert sha(old)==r['native_sha256']and sha(oldglb)==r['model_sha256'];bpy.ops.wm.open_mainfile(filepath=str(old));bpy.context.preferences.filepaths.save_version=0;part=bpy.data.objects['PFR_StaffEmbeddedTie2'];part.location.y+=2.1;bpy.context.view_layer.update();row=next(x for x in r['batches']if part.name in x['members']);batch=bpy.data.objects[row['name']];vs=[];fs=[];uvs=[]
for name in row['members']:
 o=bpy.data.objects[name]
 for polygon in o.data.polygons:
  material=o.data.materials[polygon.material_index]
  if material.name!=row['material']:continue
  ids=[]
  for li in polygon.loop_indices:ids.append(len(vs));vs.append(tuple(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co));uvs.append(tuple(o.data.uv_layers.active.data[li].uv))
  fs.append(ids)
mesh=bpy.data.meshes.new(batch.name+'_exact_root_relocation_r002');mesh.from_pydata(vs,[],fs);mesh.update();mesh.materials.append(bpy.data.materials[row['material']]);uv=mesh.uv_layers.new(name='UVMap')
for i in range(len(mesh.loops)):uv.data[i].uv=uvs[mesh.loops[i].vertex_index]
batch.data=mesh
GV=lambda v:[v.x,v.z,-v.y]
for entry,o in[(row,batch),(next(x for x in r['bounds']if x['name']==part.name),part)]:
 ps=[GV(o.matrix_world@v)for v in[__import__('mathutils').Vector(x)for x in o.bound_box]];entry['min']=[min(p[i]for p in ps)for i in range(3)];entry['max']=[max(p[i]for p in ps)for i in range(3)]
next(x for x in r['source_bearings']if x['name']==part.name)['point'][2]=-404.;native=D/'native/PORT_FORE404_RECEIVER_r002.blend';export=D/'import/Game/assets/port_fore404_receiving_20261015/PORT_FORE404_RECEIVER_r002.glb';assert not native.exists()and not export.exists();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);nsha=sha(native);esha=sha(export);bpy.ops.wm.open_mainfile(filepath=str(native));fresh=D/'FRESH_REEXPORT_r002.glb';bpy.ops.export_scene.gltf(filepath=str(fresh),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);assert sha(fresh)==esha and sha(native)==nsha and sha(old)==r['native_sha256']and sha(oldglb)==r['model_sha256'];r.update(file=export.name,native_sha256=nsha,model_sha256=esha,revision='r002',source_root_correction_plan='EXACT_ROOT_PREIMAGE_CORRECTION_PLAN.json');(D/'NATIVE_VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS_PORT_R002_EXACT_SINGLE_NEW_ROOT_RELOCATION',esha)
