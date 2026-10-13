extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/g3_full_clinical_receiving/CANDIDATE_OVERLAY.zip",true));call_deferred("run")
func run()->void:
 var script:Script=load("res://scripts/group3_clinical_full_20261011/physical_package.gd");assert(script!=null and script.can_instantiate())
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_clinical_full_20261011/CLINICAL.json"));var old:Node3D=(load("res://assets/models/group3_port2_clinical_20261011/AST-MED-G3-006.glb")as PackedScene).instantiate();root.add_child(old)
 var pre:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_clinical_full_20261011/CURRENT_BOUNDED_PREFLIGHT.json"))
 for row in pre.mesh_preimages:
  var mesh:MeshInstance3D=old.find_child(str(row.name).validate_node_name(),true,false);assert(mesh!=null);var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(Vector3(row.min[0],row.min[1],row.min[2]))<.0001 and b.end.distance_to(Vector3(row.max[0],row.max[1],row.max[2]))<.0001)
 for file in p.model_pins:assert(load("res://assets/models/group3_clinical_full_20261011/"+str(file)) is PackedScene)
 print("FULL_CLINICAL_RESOURCES_AND_BOUNDED_PREIMAGE_PASS");quit(0)
