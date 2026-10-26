extends SceneTree
const P:="res://orchard_tram_interior_20261025/integration/"
var checks:=0
var failures:Array[String]=[]
func _initialize()->void:call_deferred("run")
func require(value:bool,message:String)->bool:
	checks+=1
	if not value:failures.append(message);push_error("ORCHARD_BINDING_HOLD: "+message)
	return value
func run()->void:
	var ship:Node3D=load(P+"fixture_ship.gd").new();ship.name="OrchardLocalBindingFixture_NOT_INSTALLED";root.add_child(ship)
	var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
	var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
	var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PIT_AND_BINDING.json"))
	var material:=StandardMaterial3D.new()
	load("res://scripts/structural_floor_builder.gd").build_regions(space,material,material,[proof.before],{"guest_floor":material})
	load("res://scripts/orchard_exchange.gd").build(districts,ship)
	load("res://scripts/thread_shell.gd").build(districts,ship)
	var existing_lift:Node3D=districts.get_node("D09_D10_OrchardExchange_WIP/OrchardExchangeLift")
	var prior_id:=existing_lift.get_instance_id()
	if not require(load(P+"floor.gd").apply(ship),"Exact pit receiving"):finish();return
	if not require(load(P+"rooms.gd").apply(ship),"Room and fixture binding"):finish();return
	var assembly:Node3D=load(P+"assembly.gd").create(districts)
	if not require(assembly!=null,"Single original assembly created"):finish();return
	var lift:Node3D=assembly.get_node("Group4Lift_FORE_MIDSHIP")
	require(str(lift.persistent_id)=="group4_fore_midship_boarding_lift_001","Original lift persistent identity")
	require(lift.stop_ids==["G4_FORE_MIDSHIP_LOWER","G4_FORE_MIDSHIP_BOARDING"],"Original two stop identities")
	require(lift.global_position.distance_to(Vector3(13,0,-231.8))<.00001,"Lift bound before first physics")
	require(existing_lift.get_instance_id()==prior_id,"Existing Orchard D09/D10 lift preserved")
	var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var safety:Node3D=assembly.get_node("Group4BoardingSafety")
	require(safety.expected_dock("FORE_MIDSHIP").origin.distance_to(Vector3(17.3,56.1,-236.1))<.00001,"FORE_MIDSHIP expected physical docking pose")
	var bridge:Node3D=assembly.get_node("Group4Bridge_FORE_MIDSHIP")
	require(bridge.global_position.distance_to(Vector3(14.9,56.1,-236.1))<.00001,"One original bridge binding")
	require(absf(bridge.panel_reach-1.292592592592593)<.000001,"Authored exact bridge reach")
	require(body.transform.is_equal_approx(body.get_meta("initial_pose_before_tree")),"Vehicle initial pose before tree retained")
	await physics_frame
	await physics_frame
	var state:=ship.get_world_3d().direct_space_state
	var lift_contacts:Array[RID]=[]
	for collision:CollisionObject3D in lift.find_children("*","CollisionObject3D",true,false):lift_contacts.append(collision.get_rid())
	for x in [11.1,13.,14.9]:
		for z in [-231.6,-230.,-228.3]:
			var q:=PhysicsRayQueryParameters3D.create(Vector3(x,52.55,z),Vector3(x,52.29,z))
			# This checks floor receiving only; cabin/gate operation is a separate gate.
			q.exclude=lift_contacts
			var hit:=state.intersect_ray(q)
			require(hit.is_empty(),"No fixed slab through relocated cabin pit "+str(Vector2(x,z)))
	for point in [Vector2(-13.1,-224.9),Vector2(-11.2,-223.2),Vector2(-9.3,-221.5)]:
		var hit:=state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(point.x,52.7,point.y),Vector3(point.x,52.4,point.y)))
		require(not hit.is_empty() and absf(hit.position.y-52.5)<.00002,"Retired pit closed at real floor height")
	finish()
func finish()->void:
	var result:={"scope":"Original local Orchard/retail room constructors, floor receiving and five-station factory binding; not full ship or movement acceptance","checks":checks,"failures":failures}
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--result="):output=arg.substr(9)
	assert(not output.is_empty() and not FileAccess.file_exists(output))
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t")+"\n");file.close()
	print(JSON.stringify(result));quit(0 if failures.is_empty() else 2)
