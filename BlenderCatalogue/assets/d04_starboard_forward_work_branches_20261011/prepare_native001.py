from pathlib import Path
import json,struct
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_starboard_forward_work_branches_20261011';P=json.load(open(W/'PLAN.json'));raw={};file=P['moves'][0]['source_model'];b=(R/'Game/assets/models'/file).read_bytes();n=struct.unpack_from('<I',b,12)[0];doc=json.loads(b[20:20+n]);off=20+n;length=struct.unpack_from('<I',b,off)[0];data=b[off+8:off+8+length]
for row in P['moves']:
 node=next(q for q in doc['nodes']if q['name']==row['name']);assert not any(k in node for k in ['matrix','translation','rotation','scale']);vs=[]
 for prim in doc['meshes'][node['mesh']]['primitives']:
  a=doc['accessors'][prim['attributes']['POSITION']];v=doc['bufferViews'][a['bufferView']];assert a['componentType']==5126 and a['type']=='VEC3';begin=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12);vs += [list(struct.unpack_from('<3f',data,begin+i*stride))for i in range(a['count'])]
 raw[row['name']]=vs
(W/'RAW_SOURCE_VERTICES.json').write_text(json.dumps(raw,indent=2)+'\n')
s='''extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("PLANPATH"))
 var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file("res://assets/models/FILE",state,8)==OK);var fresh:Node3D=doc.generate_scene(state);root.add_child(fresh);var faces:Dictionary={}
 for row in p.moves:
  var mesh:MeshInstance3D=fresh.find_child(row.name,true,false);var vs:Array=[]
  for at in mesh.mesh.get_faces():var q:Vector3=mesh.global_transform*at;vs.append([q.x,q.y,q.z])
  faces[row.name]=vs
 FileAccess.open("OUTPUT",FileAccess.WRITE).store_string(JSON.stringify({"selected_flags":8,"source_sha256":FileAccess.get_sha256("res://assets/models/FILE"),"faces":faces},"  "));print("Fresh unchanged source import triangles retained");quit()
'''.replace('PLANPATH',str(W/'PLAN.json')).replace('FILE',file).replace('OUTPUT',str(W/'FRESH_IMPORT_FACES001.json'));(W/'probe_fresh_import001.gd').write_text(s)
s=(R/'BlenderCatalogue/assets/d04_port_central_west_staff_circuit_20261011/author_circuit002.py').read_text().replace('FRESH_IMPORT_FACES_r002.json','FRESH_IMPORT_FACES001.json').replace('D04PortCentralWestStaffPatch_r002','D04StarboardForwardWorkPatch_r001').replace('D04PortCentralWestStaffCircuit_r002','D04StarboardForwardWorkBranches_r001').replace('D04_PORT_CENTRAL_WEST_STAFF_CIRCUIT','D04_STARBOARD_FORWARD_WORK_BRANCHES').replace("'PCW_'","'SFW_'").replace("'PCW_G'","'SFW_G'").replace('4327','4351')
s=s.replace("@Matrix.Rotation(-math.pi/2,4,'Z')", "@Matrix.Rotation(math.radians(g['source_rotation_y_degrees']),4,'Z')")
s=s.replace("ob.matrix_world=T@old.matrix_world;mapping_records.append", "ob.matrix_world=T@old.matrix_world\n  if name.endswith('_Control')and i>=4:\n   d=g['fixed_control_delta'];ob.location+=Vector((d[0],-d[2],d[1]))\n  mapping_records.append")
s=s.replace("'rotation_godot_y_degrees':-90", "'rotation_godot_y_degrees':g['source_rotation_y_degrees']")
a=s.index('for ob in dst.objects:\n if ob:bpy.data.objects.remove');s=s[:a]+'''for name in P['closed_staging_source_members']:
 old=source_objects[name];ob=old.copy();ob.data=old.data.copy();ob.name='SFW_ClosedDock_'+name;bpy.context.collection.objects.link(ob);ob.parent=None;d=P['closed_staging_translation'];ob.matrix_world=Matrix.Translation(Vector((d[0],-d[2],d[1])))@old.matrix_world
'''+s[a:]
s=s.replace("'original_native_exports_unchanged':4327","'original_native_exports_unchanged':4351")
(W/'author_native001.py').write_text(s);(W/'prepare_native001.py').write_bytes(Path(__file__).read_bytes());print('Reviewed fresh proof and immutable authoring scripts prepared')
