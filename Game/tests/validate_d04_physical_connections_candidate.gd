extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var fitting_samples:=0
func give_visit(gate:Node3D,player:CharacterBody3D)->RefCounted:
	var visit:RefCounted=load("res://scripts/d04_court_service_visit.gd").new();visit.actor=weakref(player);visit.request_id=&"bounded_physical_visit";visit.court_ids.assign([gate.persistent_id]);visit.active=true;visit.consent_known=true;visit.consent_allowed=true;gate.visit=visit;return visit
func clear_pose(space:PhysicsDirectSpaceState3D,gate:Node3D,spec:Dictionary,parts:Array,label:String)->void:
	record(label+"_hinge",gate.leaves[0].global_position.distance_to(vec(spec.pivot))<.00004)
	for part in parts:
		if part.name not in spec.members:continue
		var lo:=Vector3(INF,INF,INF);var hi:=-lo
		for point in part.verts:lo=lo.min(vec(point));hi=hi.max(vec(point))
		var shape:=BoxShape3D.new();shape.size=hi-lo-Vector3.ONE*.004;shape.margin=.0001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=gate.leaves[0].global_transform*Transform3D(Basis.IDENTITY,(lo+hi)/2-vec(spec.pivot));q.exclude=[gate.leaves[0].get_rid()]
		var hits:=space.intersect_shape(q,64);record(label+"_clear_"+str(part.name),hits.is_empty())
		if not hits.is_empty():print("FIT_CONTACT ",label," ",part.name," ",hits.map(func(h):return str(h.collider.get_path())))
	fitting_samples+=1
func route(player:CharacterBody3D,goals:Array,label:String)->Array:
	var results:Array=[]
	for goal in goals:
		var w:Dictionary=await walk_to(player,vec(goal));results.append(w);record(label+"_"+str(results.size()),w.reached and w.floor_contact)
	return results
func carry_route(player:CharacterBody3D,item:RigidBody3D,goals:Array,label:String)->Array:
	var results:Array=[]
	for goal in goals:
		var w:Dictionary=await walk_to(player,vec(goal))
		for i in range(45):await physics_frame
		w["original_physics_tether_held"]=item.driver==player and player.held_interaction==item;w["actual_item_position"]=str(item.global_position);w["no_item_pose_or_velocity_write_during_leg"]=true;results.append(w);record(label+"_"+str(results.size()),w.reached and w.floor_contact and w.original_physics_tether_held)
	return results
func run()->void:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PHYSICAL_CONNECTIONS_CANDIDATE.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.global_position=Vector3(-57,12.03,-449);player.velocity=Vector3.ZERO;player.set_controls_enabled(true)
	ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
	for i in range(15):await physics_frame
	var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
	for f in p.source_pins:record("protected_pin_"+str(f),FileAccess.get_sha256("res://../"+str(f))==p.source_pins[f])
	for f in p.model_pins:record("model_pin_"+str(f),FileAccess.get_sha256("res://assets/models/"+str(f))==p.model_pins[f])
	record("production_candidate_inactive",ship.find_child("D04PhysicalConnectionsCandidateTestOnly",true,false)==null and not p.production_active)
	var built:Dictionary=load("res://scripts/d04_physical_connections_candidate.gd").build(ship,player,p)
	for i in range(10):await physics_frame
	var operations:Array=[];var hatches:Array=[]
	for j in range(built.controls.size()):
		var gate:Node3D=built.controls[j];var spec:Dictionary=p.gates[j];var stance:=Vector3.ZERO
		if j<2:stance=Vector3(-57.3,12,float(spec.closed_center[2]))
		elif j==2:stance=Vector3(-28.1,16.5,-447.05)
		else:
			var zs:Array=spec.service_opening_z;var found:=false
			for x in [-57.95,-57.55,-57.15]:
				for z in [float(zs[0])-.65,float(zs[1])+.65,float(zs[0])-1,float(zs[1])+1]:
					var at:=Vector3(x,16.5,z);var floor:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
					if not found and capsule_clear(space,at) and not floor.is_empty() and at.distance_to(vec(spec.control_at)-Vector3.UP*1.35)<2.3:stance=at;found=true
			if not found:record("hatch_safe_stance_"+str(j),false);continue
			else:record("hatch_safe_stance_"+str(j),true)
		player.global_position=stance+Vector3.UP*.03;player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
		for i in range(15):await physics_frame
		await aim(player,vec(spec.control_at));record("normal_control_target_"+str(j),player.interaction_target==gate)
		if spec.requires_visit:
			await key_e();record("unknown_private_visit_denied_"+str(j),not gate.desired_open and gate.open_fraction==0);var visit:=give_visit(gate,player);visit.consent_allowed=false;await key_e();record("refused_private_visit_denied_"+str(j),not gate.desired_open);visit.consent_allowed=true
		var stranger:=CharacterBody3D.new();built.owner.add_child(stranger);gate.interact(stranger);record("other_actor_denied_"+str(j),not gate.desired_open);stranger.free()
		if j==0:
			var crowded:Array=[]
			for i in range(64):
				var body:=StaticBody3D.new();var c:=CollisionShape3D.new();var s:=BoxShape3D.new();s.size=Vector3.ONE*.01;c.shape=s;body.add_child(c);built.owner.add_child(body);body.global_position=(vec(spec.sweep_min)+vec(spec.sweep_max))/2;crowded.append(body)
			for i in range(3):await physics_frame
			await key_e();record("saturated_new_fitting_guard_denies_motion",gate.obstructed and not gate.desired_open)
			for body in crowded:body.free()
			for i in range(3):await physics_frame
		var blocker:=RigidBody3D.new();blocker.freeze=true;var col:=CollisionShape3D.new();var box:=BoxShape3D.new();box.size=Vector3(.15,.15,.15);col.shape=box;blocker.add_child(col);built.owner.add_child(blocker);blocker.global_position=(vec(spec.sweep_min)+vec(spec.sweep_max))/2
		for i in range(3):await physics_frame
		await key_e();record("load_guard_"+str(j),gate.obstructed and not gate.desired_open);blocker.free()
		for i in range(3):await physics_frame
		if j==2:
			var worker:=CharacterBody3D.new();var wc:=CollisionShape3D.new();var ws:=CapsuleShape3D.new();ws.radius=.3;ws.height=1.8;wc.shape=ws;worker.add_child(wc);built.owner.add_child(worker);worker.global_position=(vec(spec.sweep_min)+vec(spec.sweep_max))/2
			for i in range(3):await physics_frame
			await key_e();record("fourth_gate_worker_guard",gate.obstructed and not gate.desired_open);worker.free()
			for i in range(3):await physics_frame
		await key_e()
		for i in range(100):
			await physics_frame
			if i%10==0:clear_pose(space,gate,spec,p.parts,"open_"+str(j)+"_"+str(i))
		record("fully_open_"+str(j),gate.desired_open and gate.open_fraction>.999)
		if j>2:
			hatches.append({"gate":gate,"spec":spec,"stance":stance})
			# Fixed glazing above the low hatch still blocks a standing person.
			var z:float=(spec.service_opening_z[0]+spec.service_opening_z[1])/2;var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,Vector3(-58.86,17.425,z));var hits:=space.intersect_shape(q,64);record("fixed_window_blocks_person_"+str(j),not hits.is_empty())
		await aim(player,vec(spec.control_at));await key_e()
		for i in range(100):
			await physics_frame
			if i%10==0:clear_pose(space,gate,spec,p.parts,"close_"+str(j)+"_"+str(i))
		record("fully_closed_"+str(j),not gate.desired_open and gate.open_fraction<.001);operations.append({"fitting":spec.name,"stance":str(stance),"unknown_state_closed":spec.requires_visit,"normal_target":checks["normal_control_target_"+str(j)]})
	# Open only explicit temporary visits for the complete real-controller route.
	player.global_position=Vector3(-57.3,12.03,-447);player.velocity=Vector3.ZERO
	for i in range(15):await physics_frame
	await aim(player,vec(p.gates[1].control_at));await key_e()
	for i in range(100):await physics_frame
	for gate in built.old_controls:
		give_visit(gate,player);gate.interact(player)
	for i in range(100):await physics_frame
	var incoming:Array=await route(player,[[-53,12,-447],[-34,12,-447],[-31.75,12,-446.8],[-31.75,14.25,-455.4],[-31.75,14.25,-456.3],[-28.25,14.25,-456.3],[-28.25,16.5,-447.35]],"whole_staff_incoming")
	await aim(player,vec(p.gates[2].control_at));await key_e()
	for i in range(100):await physics_frame
	record("full_route_fourth_gate_open",built.controls[2].open_fraction>.999)
	var courts:Array=await route(player,[[-28.1,16.5,-439.5],[-28.1,16.5,-424.5],[-28.1,16.5,-410.5],[-28.1,16.5,-424.5],[-28.1,16.5,-439.5],[-28.1,16.5,-443.1]],"whole_court_out_back")
	var fourth:Node3D=built.controls[2];fourth.visit.active=false;await aim(player,vec(p.gates[2].control_at));record("fourth_gate_inside_target",player.interaction_target==fourth);await key_e()
	for i in range(100):await physics_frame
	record("revoked_inside_worker_can_close_fourth",not fourth.desired_open and fourth.open_fraction<.001);await key_e()
	for i in range(100):await physics_frame
	record("revoked_inside_worker_can_open_for_exit",fourth.desired_open and fourth.open_fraction>.999)
	var egress:Dictionary=await walk_to(player,Vector3(-28.25,16.5,-447.35));record("actual_revoked_fourth_egress",egress.reached and egress.floor_contact);await aim(player,vec(p.gates[2].control_at));await key_e()
	for i in range(100):await physics_frame
	await key_e();record("revoked_outside_fourth_reentry_denied",not fourth.desired_open and fourth.open_fraction<.001);fourth.visit.active=true
	var returning:Array=await route(player,[[-28.25,14.25,-456.3],[-31.75,14.25,-456.3],[-31.75,14.25,-455.4],[-31.75,12,-446.8],[-34,12,-447],[-53,12,-447],[-57.3,12,-447]],"whole_staff_return")
	# Unbroken original staff corridor remains clear; the old -370 derivative
	# and protected crew doorway remain untouched through the source pins.
	player.global_position=Vector3(-43.8,16.53,-331.7);player.velocity=Vector3.ZERO
	for i in range(10):await physics_frame
	for z in range(-4590,-4409,5):record("staff_original_corridor_"+str(z),capsule_clear(space,Vector3(-57,12,float(z)/10)))
	for at in [p.clean_bay_approach,p.used_bay_approach]:record("local_bay_worker_"+str(at),capsule_clear(space,vec(at)))
	# Gate motions are proved separately. These carrying legs use the prepared
	# open fittings and original force tether, with one initial actor/item fixture.
	for gate in built.controls:
		if not gate.desired_open:gate.interact(player)
	for i in range(100):await physics_frame
	player.global_position=Vector3(-34.7,12.03,-445.7);player.velocity=Vector3.ZERO
	var bottle:RigidBody3D=load("res://scripts/cleaning_bottle.gd").new();bottle.persistent_id=&"D04PC_clean_supply_validation";bottle.contact_monitor=true;bottle.max_contacts_reported=16;built.owner.add_child(bottle);bottle.global_position=Vector3(-34.7,12.94,-444.9)
	for i in range(25):await physics_frame
	await aim(player,bottle.global_position+Vector3.UP*.13);record("normal_clean_product_target",player.interaction_target==bottle);await key_e();record("normal_clean_product_pickup",bottle.driver==player);player.camera.rotation.x=0
	for i in range(30):await physics_frame
	var carry_goals:Array=[[-34.4,12,-447],[-31.75,12,-446.8],[-31.75,14.25,-455.4],[-31.75,14.25,-456.3],[-28.25,14.25,-456.3],[-28.25,16.5,-447.35],[-28.1,16.5,-439.5],[-28.25,16.5,-447.35],[-28.25,14.25,-456.3],[-31.75,14.25,-456.3],[-31.75,14.25,-455.4],[-31.75,12,-446.8],[-34.4,12,-447],[-34.7,12,-446.3]]
	var clean_carry:Array=await carry_route(player,bottle,carry_goals,"clean_supply_actual_carry")
	await aim(player,Vector3(-34.7,13.065,-444.9))
	for i in range(90):await physics_frame
	await key_e()
	for i in range(90):await physics_frame
	record("clean_product_release",bottle.driver==null);var clean_support:=false;var clean_support_names:Array=[]
	for body in bottle.get_colliding_bodies():
		var n:=str(body.get_parent().name);clean_support_names.append(n)
		if n.begins_with("D04PC_CleanTray") or n=="D03_protected_crew_cover":clean_support=true
	record("clean_product_return_supported",clean_support);bottle.free()
	player.global_position=vec(p.used_bay_approach)+Vector3.UP*.03;player.velocity=Vector3.ZERO
	var used:RigidBody3D=load("res://scripts/d04_closed_used_container.gd").new();used.persistent_id=&"D04PC_closed_used_validation";used.authored_visual=built.owned;used.authored_prefix="D04PC_ClosedUsed_1_";used.position=Vector3(-34.3,12,-451);built.owner.add_child(used)
	for i in range(20):await physics_frame
	await aim(player,used.global_position+Vector3.UP*.6);record("normal_closed_used_target",player.interaction_target==used);await key_e();record("normal_closed_used_pickup",used.driver==player);player.camera.rotation.x=0
	for i in range(40):await physics_frame
	var used_carry:Array=await carry_route(player,used,[[-34.4,12,-449],[-53,12,-449],[-57.3,12,-449],[-53,12,-449],[-34.4,12,-449],[-34.4,12,-450.25]],"closed_used_actual_carry")
	await aim(player,Vector3(-34.3,12.6,-451))
	for i in range(120):await physics_frame
	await key_e()
	for i in range(180):await physics_frame
	record("closed_used_release",used.driver==null);var supported:=false;var used_support_names:Array=[]
	for body in used.get_colliding_bodies():
		var support_name:=str(body.get_parent().name);used_support_names.append(support_name)
		if support_name=="D03_protected_crew_cover":supported=true
	record("closed_used_destination_floor",supported);used.free()
	player.global_position=Vector3(-43.8,16.53,-331.7);player.velocity=Vector3.ZERO
	for i in range(10):await physics_frame
	# Maintenance reach uses the rigid native three-stage tube: hand origin from
	# a full worker stance, no scale and <=1.1m slide per joint. Contact may occur
	# only on the intended native foliage, never through glass/walls/furniture.
	var reaches:Array=[];var reach_blockers:Dictionary={};var stance_cache:Dictionary={}
	var tool:Node3D=load("res://assets/models/"+str(p.reach_tool.model)).instantiate();built.owner.add_child(tool);tool.visible=false;var tool_parts:Array=[]
	for member in p.reach_tool.members:
		var mesh:MeshInstance3D=tool.find_child(str(member.name),true,false);var shape:=mesh.mesh.create_convex_shape();shape.margin=.0001;tool_parts.append({"shape":shape,"native_pose":mesh.global_transform})
	# Foliage is deliberately visual-only in production. Exact native mesh
	# contacts below exist solely as reach-test terminals and are never installed.
	for planter in range(3):
		for leaf in range(3):load("res://scripts/static_contact_cache.gd").attach(ship.find_child("D04HC2_west_LeafMass_"+str(planter)+"_"+str(leaf),true,false))
	for i in range(3):await physics_frame
	for hatch in hatches:
		var gate:Node3D=hatch.gate
		if not gate.desired_open:gate.interact(player)
	for i in range(100):await physics_frame
	var person_barrier_samples:=0
	for hatch in hatches:
		var zs:Array=hatch.spec.service_opening_z;var z:float=float(zs[0])+.25
		while z<float(zs[1])-.24:
			var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001;var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,Vector3(-58.98,17.425,z));var fixed_block:=false
			for hit in space.intersect_shape(query,64):
				var name:=str(hit.collider.get_parent().name)
				if name.begins_with("D04PC_FixedToolBarrier_") or name.begins_with("D04PC_FixedEndToolBarrier_") or name.ends_with("_FixedHead") or (name.begins_with("D04PC_Successor_D04H") and (name.ends_with("_GardenGlass") or name.ends_with("_GardenDado"))):fixed_block=true
			record("fixed_person_barrier_"+str(person_barrier_samples),fixed_block);person_barrier_samples+=1;z+=.1
	for planter in range(3):
		var centres:Array=[-436.3,-430.5,-424.7];var cz:float=centres[planter]
		for leaf in range(3):
			var name:="D04HC2_west_LeafMass_"+str(planter)+"_"+str(leaf);var mesh:MeshInstance3D=ship.find_child(name,true,false);var bounds:AABB=mesh.global_transform*mesh.get_aabb();var z:float=cz+[-.5,.15,.6][leaf]
			for height in [bounds.position.y+.04,bounds.get_center().y,bounds.end.y-.02]:
				var found:=false;var evidence:Dictionary={};var blocked:Dictionary={}
				var target_zs:Array=[z,bounds.position.z+.04,bounds.end.z-.04,bounds.get_center().z]
				for target_z in target_zs:
					if found:continue
					var target:=Vector3(bounds.end.x-.025,height,target_z)
					for hatch in hatches:
						var hs:Dictionary=hatch.spec;var zs:Array=hs.service_opening_z
						if (planter==0 and int(hs.home_index)!=952) or (planter==2 and int(hs.home_index)!=928):continue
						for x in [-58.25,-57.95,-57.55,-57.15]:
							if found:continue
							var sampled_z:Array=[];var next_z:float=float(zs[0])-1
							while next_z<float(zs[1])+1.401:sampled_z.append(next_z);next_z+=.15
							for Z in sampled_z:
								if found:continue
								var at:=Vector3(x,16.5,Z)
								var stance_key:=str(at)
								if not stance_cache.has(stance_key):stance_cache[stance_key]=capsule_clear(space,at) and not ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02).is_empty()
								if not stance_cache[stance_key]:continue
								for hand_y in [17.05,17.2,17.35,17.5,17.65,17.75,17.9,18.05]:
									if found:continue
									var hand:=Vector3(x-.45,hand_y,Z);var length:float=hand.distance_to(target)
									if length>3.4 or length<1.2:continue
									var hit:=ray(space,hand,target)
									if not hit.is_empty():
										var blocker:=str(hit.collider.get_parent().name);blocked[blocker]=int(blocked.get(blocker,0))+1
									if not hit.is_empty() and str(hit.collider.get_parent().name)==name and hand.distance_to(hit.position)>=1.2:
										var tube_clear:=true;var direction:Vector3=(hit.position-hand).normalized();var axis:=direction.cross(Vector3.UP).normalized();var vertical:=direction.cross(axis).normalized()
										for offset in [axis*.012,-axis*.012,vertical*.012,-vertical*.012]:
											var side:=ray(space,hand+offset,hit.position+offset-direction*.015)
											if not side.is_empty() and str(side.collider.get_parent().name)!=name:
												var bn:="shaft_ray_"+str(side.collider.get_parent().name);blocked[bn]=int(blocked.get(bn,0))+1;tube_clear=false
										length=hand.distance_to(hit.position);var slide:float=maxf(0,(length-1.2)/2)
										if tube_clear and not found:
											var pose:=Transform3D(Basis.looking_at(-direction,Vector3.UP),hand)
											for k in range(tool_parts.size()):
												var query:=PhysicsShapeQueryParameters3D.new();query.shape=tool_parts[k].shape;query.transform=pose*Transform3D(Basis.IDENTITY,Vector3(0,0,k*slide))*tool_parts[k].native_pose;var contacts:=space.intersect_shape(query,64)
												if contacts.size()>=64:tube_clear=false
												for tool_contact in contacts:
													if str(tool_contact.collider.get_parent().name)!=name or absf(1.2+k*slide-length)>.02:
														var bn:="native_tube_"+str(k)+"_"+str(tool_contact.collider.get_parent().name);blocked[bn]=int(blocked.get(bn,0))+1;tube_clear=false
										if tube_clear and not found:
											found=true;var wall_points:Array=[];var actual_openings:Array=[]
											for X in [-58.77,-58.95]:
												var point:Vector3=hand+(hit.position-hand)*((X-hand.x)/(hit.position.x-hand.x));wall_points.append(str(point))
											for opening in p.gates:
												if not opening.has("home_index"):continue
												var contains:=true
												for X in [-58.77,-58.95]:
													var point:Vector3=hand+(hit.position-hand)*((X-hand.x)/(hit.position.x-hand.x))
													if point.y<opening.leaf_min[1]-.03 or point.y>opening.leaf_max[1]+.03 or point.z<opening.service_opening_z[0] or point.z>opening.service_opening_z[1]:contains=false
												if contains:actual_openings.append(opening.name)
											evidence={"plant":name,"height":height,"requested_native_target":str(target),"worker_stance":str(at),"hand":str(hand),"first_contact":str(hit.position),"length":length,"fixture_generator":hs.name,"actual_opening_gates":actual_openings,"source_wall_entry_exit":wall_points,"native_rigid_tubes":3,"exact_native_tool_convex_shapes_checked":3,"joint_slide":slide,"person_access":false,"hand_extension_m":.45,"terminal_native_foliage_contact_test_only":true}
				var key:="maintenance_reach_"+str(planter)+"_"+str(leaf)+"_"+str(height);record(key,found);reaches.append(evidence);reach_blockers[key]=blocked if not found else {}
	var result:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks,"check_count":checks.size(),"errors":errors,"operations":operations,"fitting_pose_samples":fitting_samples,"whole_staff_incoming":incoming,"whole_court_out_back":courts,"whole_staff_return":returning,"clean_product_carry":clean_carry,"clean_product_support_contacts":clean_support_names,"closed_used_carry":used_carry,"closed_used_support_contacts":used_support_names,"maintenance_reach":reaches,"reach_blockers":reach_blockers,"fixed_person_barrier_samples":person_barrier_samples,"production_active":false,"temporary_visit_only":true,"provider_available":false,"physical_carry_transfer_proved":errors.is_empty(),"full_commons_stock_return_network":false,"cart_safe_vertical":false,"model_pins":p.model_pins,"runtime_plan_sha256":FileAccess.get_sha256("res://data/architecture/D04_PHYSICAL_CONNECTIONS_CANDIDATE.json"),"test_source_sha256":FileAccess.get_sha256("res://tests/validate_d04_physical_connections_candidate.gd")}
	FileAccess.open("res://artifacts/d04_physical_connections_candidate.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
