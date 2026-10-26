extends SceneTree
const P:="res://aquatic_tram_interior_20261026/integration/"
var checks:=0
var failures:Array[String]=[]
func _initialize()->void:call_deferred("run")
func require(value:bool,message:String)->bool:
	checks+=1
	if not value:failures.append(message);push_error("AQUATIC_BINDING_HOLD: "+message)
	return value
func run()->void:
	var ship:=Node3D.new();ship.name="AquaticLocalBindingFixture_NOT_INSTALLED";root.add_child(ship)
	var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
	var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
	var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PIT_AND_BINDING.json"))
	var material:=StandardMaterial3D.new()
	load("res://scripts/structural_floor_builder.gd").build_regions(space,material,material,[proof.before],{"guest_floor":material})
	if not require(load(P+"floor.gd").apply(ship),"Exact named floor and retired original-overlap infill"):finish();return
	var assembly:Node3D=load(P+"assembly.gd").create(districts,"AFT_MIDSHIP")
	if not require(assembly!=null,"Single original assembly created"):finish();return
	var lift:Node3D=assembly.get_node("Group4Lift_AFT_MIDSHIP")
	require(str(lift.persistent_id)=="group4_aft_midship_boarding_lift_001","Original lift identity")
	require(lift.stop_ids==["G4_AFT_MIDSHIP_LOWER","G4_AFT_MIDSHIP_BOARDING"],"Original stop identities")
	require(lift.global_position.distance_to(Vector3(23.3,0,187.7))<.00001,"Relocated lift root")
	require(absf(lift.rotation.y-PI/2)<.00001,"Original cabin orientation received")
	var fore:Node3D=assembly.get_node("Group4Lift_FORE_MIDSHIP")
	require(fore.global_position.distance_to(Vector3(13,0,-231.8))<.00001,"Selected Orchard lift preserved")
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var safety:Node3D=assembly.get_node("Group4BoardingSafety")
	require(safety.expected_dock("AFT_MIDSHIP").origin.distance_to(Vector3(18.5,56.1,192))<.00001,"Expected original vehicle pose")
	require(safety.expected_dock("FORE_MIDSHIP").origin.distance_to(Vector3(17.3,56.1,-236.1))<.00001,"Orchard physical stop preserved")
	var bridge:Node3D=assembly.get_node("Group4Bridge_AFT_MIDSHIP")
	require(bridge.global_position.distance_to(Vector3(20.7,56.1,192))<.00001,"One original bridge received")
	require(body.transform.is_equal_approx(body.get_meta("initial_pose_before_tree")),"Initial pose set before tree")
	var receiving:Node3D=assembly.get_node("AquaticInteriorReceiving")
	require(receiving.get_meta("authored_meshes")==421 and receiving.get_meta("retained_plant_placements")==35 and receiving.get_meta("retained_benches")==3,"Guest planting/seating and full architecture present")
	require(not assembly.has_node("AST-TRM-G4-012_aft_midship_source") and not assembly.has_node("AST-TRM-G4-030_aftmid_upper_receiving_r002"),"No duplicate retired station")
	for i in range(3):await physics_frame
	var state:=ship.get_world_3d().direct_space_state
	var excluded:Array[RID]=[]
	for collider:CollisionObject3D in lift.find_children("*","CollisionObject3D",true,false):excluded.append(collider.get_rid())
	for x in [21.4,23.3,25.2]:
		for z in [184.2,185.8,187.5]:
			var q:=PhysicsRayQueryParameters3D.create(Vector3(x,52.55,z),Vector3(x,52.29,z));q.exclude=excluded
			require(state.intersect_ray(q).is_empty(),"No original floor through received cabin pit "+str(Vector2(x,z)))
	for z in [228.7,230.4,232.1]:
		var hit:=state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(3.6,52.7,z),Vector3(3.6,52.4,z)))
		require(not hit.is_empty() and absf(hit.position.y-52.5)<.00002,"Only real retired route overlap restored")
	finish()
func finish()->void:
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--result="):output=arg.substr(9)
	assert(not output.is_empty() and not FileAccess.file_exists(output))
	var report:={"scope":"Local exact floor receiving and original five-station bindings; not installed ship, operation or visual acceptance","checks":checks,"failures":failures}
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close();print(JSON.stringify(report));quit(0 if failures.is_empty() else 2)
