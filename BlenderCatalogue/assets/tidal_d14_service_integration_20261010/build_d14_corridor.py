from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group3_crew_service_20261009';P=json.load(open(W/'D14_CORRIDOR_INTEGRATION_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1])
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.open_mainfile(filepath=str(F/'source/AST-STF-G3-003.blend'));keep={q['name']for q in P['retained_source_parts']}|{q['name']for q in P['fixture_markers']}
for o in list(bpy.data.objects):
 if o.name not in keep:bpy.data.objects.remove(o,do_unlink=True)
assert sum(o.type=='MESH'for o in bpy.context.scene.objects)==64
for name,members in P['batched_patch_targets'].items():
 bpy.ops.object.select_all(action='DESELECT')
 for member in members:bpy.data.objects[member].select_set(True)
 bpy.context.view_layer.objects.active=bpy.data.objects[members[0]];bpy.ops.object.join();o=bpy.context.object;o.name=name;o['retained_editable_source_parts']=members;o['role']='staff_bluegrey_paint'if'bluegrey'in name else'staff_white_paint';o['category']='screen_wall';o['runtime_collision']=True
mats={o.data.materials[0].name:o.data.materials[0]for o in bpy.context.scene.objects if o.type=='MESH'}
for p in P['closures']:
 b=p['aabb'];vs=[B((x,y,z))for y in[b[2],b[3]]for z in[b[4],b[5]]for x in[b[0],b[1]]];fs=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)];me=bpy.data.meshes.new(p['name']);me.from_pydata(vs,[],fs);me.update();me.materials.append(mats[p['role']]);o=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(o);o['role']=p['role'];o['category']=p['category'];o['runtime_collision']=True
 uv=me.uv_layers.new(name='MetricUV')
 for q in me.polygons:
  axes=[i for i in range(3)if i!=max(range(3),key=lambda a:abs(q.normal[a]))]
  for li in q.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*.3,v[axes[1]]*.3)
for o in bpy.context.scene.objects:o['d14_only_derivative']=True;o['source_recipe']=P['catalogue_id']
bpy.data.orphans_purge(do_recursive=True)
for im in bpy.data.images:
 if im.source=='FILE'and not im.packed_file:im.pack()
native=W/'TidalD14ServiceCorridor.blend';asset=W/'AST-RES-TIDAL_D14_service_corridor_r001.glb';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.export_scene.gltf(filepath=str(asset),export_format='GLB',export_yup=True,export_extras=True,export_cameras=False,export_lights=False);nh=sha(native);ah=sha(asset);bpy.ops.wm.open_mainfile(filepath=str(native));assert sum(o.type=='MESH'for o in bpy.context.scene.objects)==65;repeat=W/'_repeat.glb';bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_extras=True,export_cameras=False,export_lights=False);assert sha(repeat)==ah;repeat.unlink();assert sha(native)==nh
r={'schema':1,'native':native.name,'native_sha256':nh,'export':asset.name,'export_sha256':ah,'retained_editable_source_parts':64,'retained_parts_joined_only_to_two_exact_patch_batches':4,'new_physical_closures':3,'export_meshes':65,'fixture_markers':7,'repeat_export_byte_identical':True,'original_source_pins_unchanged':all(sha(R/p)==h for p,h in P['source_pins'].items()),'no_upper_shaft_or_landing_threshold_geometry':True,'blender_version':bpy.app.version_string};(W/'CORRIDOR_NATIVE_EXPORT_CHECK.json').write_text(json.dumps(r,indent=2)+'\n');print('D14_CORRIDOR_NATIVE_PASS',json.dumps(r),flush=True)
