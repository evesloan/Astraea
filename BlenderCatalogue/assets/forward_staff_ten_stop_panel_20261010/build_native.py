from pathlib import Path
import bpy,bmesh,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'INTERFACE_SURVEY.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=R/'BlenderCatalogue/assets/commons_lift_cabin/source/AST-CIR-003_five_stop.blend';assert sha(source)==P['source_pins'][str(source.relative_to(R))]
assert next(q for q in json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'))['assets']if q['catalogue_id']=='AST-CIR-003')['family']=='commons_lift_cabin'
bpy.ops.wm.open_mainfile(filepath=str(source))
def fingerprint(o):
 return {'matrix':[list(v)for v in o.matrix_world],'vertices':[list(v.co)for v in o.data.vertices],'faces':[list(p.vertices)for p in o.data.polygons],'uv':[[list(v.uv)for v in u.data]for u in o.data.uv_layers],'materials':[m.name for m in o.data.materials]}
old=bpy.data.objects['CAB_FiveStopControlPanel'];unchanged={o.name:fingerprint(o)for o in bpy.context.scene.objects if o.type=='MESH'and o!=old};markers={str(i):list(bpy.data.objects['DATUM_floor_button_'+str(i)].location)for i in range(5)};material=old.data.materials[0];bpy.data.objects.remove(old,do_unlink=True)
vs=[(x,y,z)for z in [1.10,1.90]for x,y in [(1.75,.32),(1.88,.32),(1.88,1.72),(1.75,1.72)]];fs=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4)for i in range(4)]
me=bpy.data.meshes.new('CAB_TenStopControlPanel');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(material);uv=me.uv_layers.new(name='MetreScaled')
for p in me.polygons:
 for li in p.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.y,v.z)
o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
for i in range(5):
 marker=bpy.data.objects.new('DATUM_floor_button_'+str(i+5),None);marker.location=(1.73,.46+.28*i,1.73);bpy.context.collection.objects.link(marker)
assert all(fingerprint(bpy.data.objects[n])==f for n,f in unchanged.items())
assert all(list(bpy.data.objects['DATUM_floor_button_'+i].location)==p for i,p in markers.items())
blend=W/'AST-CIR-003_ten_stop.blend';export=W/'AST-CIR-003_ten_stop.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_extras=True);h=sha(export)
bpy.ops.wm.open_mainfile(filepath=str(blend));assert all(fingerprint(bpy.data.objects[n])==f for n,f in unchanged.items());bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_extras=True);assert sha(export)==h
result={'status':'PASS','blender_version':bpy.app.version_string,'catalogue_id':'AST-CIR-003','retained_predecessor_source_sha256':sha(source),'native_sha256':sha(blend),'export_sha256':h,'fresh_native_repeat_identical':True,'unchanged_native_meshes':len(unchanged),'first_five_native_marker_positions_unchanged':markers,'panel_bounds_godot':{'min':[1.75,1.10,-1.72],'max':[1.88,1.90,-.32]},'backing_center_godot':[1.815,1.50,-1.02],'backing_size':[.13,.80,1.40],'new_markers_godot':[[1.73,1.73,-(.46+.28*i)]for i in range(5)],'upper_operation_enabled':False}
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print('TEN_STOP_NATIVE_PASS',json.dumps(result))
