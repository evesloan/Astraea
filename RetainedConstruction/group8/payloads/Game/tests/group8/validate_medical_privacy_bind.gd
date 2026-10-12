extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var old:Node3D=ship.get_node("ShipSpace/Districts/D05MedicalWelcome_WIP");var arch:Node3D=old.get_node("AuthoredMedicalWelcome")
	var meshes:Array=arch.find_children("*","MeshInstance3D",true,false);var poses:Dictionary={}
	for mesh:MeshInstance3D in meshes:poses[mesh.get_instance_id()]={"node":mesh,"pose":mesh.global_transform,"resource":mesh.mesh.get_instance_id()}
	var g8:Node3D=load("res://scripts/group8/medical_privacy.gd").build(ship)
	for frame in range(8):await physics_frame
	assert(arch.find_children("*","MeshInstance3D",true,false).size()==meshes.size(),"Original medical source mesh count must survive fitting")
	var checks:=0
	for row in poses.values():
		assert(row.node.global_transform.is_equal_approx(row.pose)and row.node.mesh.get_instance_id()==row.resource,"Initial original source geometry/pose must be exact");checks+=1
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/medical_privacy.json"));var bound:=0
	for row in plan.doors:
		var driver:Node3D=arch.get_node(str(row.name));assert(driver.hinge_nodes.size()==2 and driver.bound_meshes.size()==10 and driver.open_fraction==1 and driver.desired_open);bound+=driver.bound_meshes.size()
		for mesh:MeshInstance3D in driver.bound_meshes:
			var body:AnimatableBody3D=mesh.get_node("StaticContact");var contact:CollisionShape3D=body.get_child(0);assert(contact.shape is ConcavePolygonShape3D and not contact.disabled and body.collision_layer==1);checks+=1
	assert(bound==80 and g8.get_meta("new_capacity")==0 and g8.get_meta("new_floor_owners")==0)
	print("GROUP8 MEDICAL INITIAL BIND PASS: ",JSON.stringify({"checks":checks,"original_medical_meshes":meshes.size(),"source_elements_fitted":bound,"default_source_open_poses_exact":true,"motion_and_shared_static_successor_acceptance":false}))
	main.queue_free();for frame in range(4):await process_frame
	quit(0)
