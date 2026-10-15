extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/dining_public_core_20261015/CANDIDATE_OVERLAY.zip",true));call_deferred("run")
func run()->void:
 var ship:=Node3D.new();root.add_child(ship);var parent:Node3D=ship
 for key in["ShipSpace","Districts","ForwardPublicCore_WIP"]:
  var child:=Node3D.new();child.name=key;parent.add_child(child);parent=child
 var source:Node3D=(load("res://assets/models/AST-CIR-005_forward_breakroom_d03.glb")as PackedScene).instantiate();source.name="PrimaryCoreEnclosure";source.position=Vector3(0,0,-432);parent.add_child(source)
 for mesh:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 for i in range(2):await physics_frame
 var fitted:Node3D=load("res://scripts/dining_public_core_20261015/package.gd").build(ship);assert(fitted.get_meta("exact_selected_wall_preimages").size()==4);print("PASS_FOUR_DINING_WALL_PREIMAGES_AND_ACTUAL_REPLACEMENTS");quit(0)
