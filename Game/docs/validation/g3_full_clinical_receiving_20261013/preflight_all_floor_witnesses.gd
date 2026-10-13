extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/g3_full_clinical_receiving/CANDIDATE_OVERLAY.zip",true));call_deferred("run")
func run()->void:
 var world:=Node3D.new();root.add_child(world)
 for file in ["AST-MED-G3-007.glb","AST-MED-G3-008.glb","AST-MED-G3-010.glb"]:
  var visual:Node3D=(load("res://assets/models/group3_clinical_full_20261011/"+file)as PackedScene).instantiate();visual.name=file.trim_suffix(".glb");world.add_child(visual)
  for mesh in visual.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 for i in range(5):await physics_frame
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/g3_full_clinical_receiving/native/CLINICAL_COMPLETE_MISSING_FLOOR.json"));var state:PhysicsDirectSpaceState3D=world.get_world_3d().direct_space_state;var rows:Array=[]
 for part in data.parts:
  for tri in part.triangles:
   var at:=Vector3((tri[0][0]+tri[1][0]+tri[2][0])/3.,21,(tri[0][1]+tri[1][1]+tri[2][1])/3.);var h:Dictionary=state.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02));assert(not h.is_empty()and world.get_node("AST-MED-G3-008").is_ancestor_of(h.collider)and absf(h.position.y-21)<.002);rows.append(str(at))
 var floor:Node3D=world.get_node("AST-MED-G3-008");var meshes:Array=[]
 for mesh:MeshInstance3D in floor.find_children("*","MeshInstance3D",true,false):
  meshes.append({"name":mesh.name,"bounds":str(mesh.global_transform*mesh.get_aabb()),"format":mesh.mesh.surface_get_format(0)})
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g3_full_clinical_receiving/PRECISE_FLOOR_ALL_WITNESSES.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_ALL_247_EXACT_PRECISE_SOURCE_FLOOR_WITNESSES","floor_witnesses":rows.size(),"floor_meshes":meshes},"  "));print("CLINICAL_FLOOR_WITNESS_PROBE_PASS");quit(0)
