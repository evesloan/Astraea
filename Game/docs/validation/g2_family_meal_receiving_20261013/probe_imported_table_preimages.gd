extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/g2_family_meal_receiving/CANDIDATE_OVERLAY.zip",true));call_deferred("run")
func run()->void:
 var visual:Node3D=(load("res://assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb")as PackedScene).instantiate();root.add_child(visual)
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_family_meal/CURRENT_TABLE_PREFLIGHT.json"));var rows:Array=[]
 for row in data.table_parts:
  var batch:MeshInstance3D=visual.find_child(str(row.batch_node),true,false);var vertices:PackedVector3Array=batch.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX];var floats:=PackedFloat32Array();var samples:Array=[];var full_vertices:Array=[];var lo:=Vector3(INF,INF,INF);var hi:=Vector3(-INF,-INF,-INF)
  for i in range(int(row.vertex_start),int(row.vertex_start)+int(row.vertex_count)):
   var v:Vector3=vertices[i];full_vertices.append([v.x,v.y,v.z]);floats.append(v.x);floats.append(v.y);floats.append(v.z);lo=lo.min(v);hi=hi.max(v)
   if samples.size()<4:samples.append([v.x,v.y,v.z])
  var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(floats.to_byte_array());rows.append({"table":row.name,"batch":row.batch_node,"actual_vertex_count":vertices.size(),"source_range_start":row.vertex_start,"source_range_count":row.vertex_count,"source_sha":row.source_vertex_sha256,"actual_sha":h.finish().hex_encode(),"actual_min":[lo.x,lo.y,lo.z],"actual_max":[hi.x,hi.y,hi.z],"expected_min":row.min,"expected_max":row.max,"samples":samples,"vertices":full_vertices,"surface_format":batch.mesh.surface_get_format(0),"compress_attributes_flag":Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES,"indices":Array(batch.mesh.surface_get_arrays(0)[Mesh.ARRAY_INDEX])})
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_family_meal_receiving/IMPORTED_TABLE_CODEC_VERIFICATION_INPUT.json",FileAccess.WRITE).store_string(JSON.stringify(rows,"  "));print("IMPORTED_TABLE_PREIMAGE_PROBE_PASS");quit(0)
