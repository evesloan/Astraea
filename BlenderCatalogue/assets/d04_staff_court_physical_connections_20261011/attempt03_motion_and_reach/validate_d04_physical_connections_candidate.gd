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
		if not hits.is_empty():print("FIT_CONTACT ",label," ",part.name," ",hits)
	fitting_samples+=1
func route(player:CharacterBody3D,goals:Array,label:String)->Array:
	var results:Array=[]
	for goal in goals:
		var w:Dictionary=await walk_to(player,vec(goal));results.append(w);record(label+"_"+str(results.size()),w.reached and w.floor_contact)
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
		var blocker:=RigidBody3D.new();blocker.freeze=true;var col:=CollisionShape3D.new();var box:=BoxShape3D.new();box.size=Vector3(.15,.15,.15);col.shape=box;blocker.add_child(col);built.owner.add_child(blocker);blocker.global_position=(vec(spec.sweep_min)+vec(spec.sweep_max))/2
		for i in range(3):await physics_frame
		await key_e();record("load_guard_"+str(j),gate.obstructed and not gate.desired_open);blocker.free()
		for i in range(3):await physics_frame
		await key_e()
		for i in range(100):
			await physics_frame
			if i%10==0:clear_pose(space,gate,spec,p.parts,"open_"+str(j)+"_"+str(i))
		record("fully_open_"+str(j),gate.desired_open and gate.open_fraction>.999)
		if j>2:
			hatches.append({"gate":gate,"spec":spec,"stance":stance})
			# Fixed glazing above the low hatch still blocks a standing person.
			var z:float=(spec.service_opening_z[0]+spec.service_opening_z[1])/2;var hit:=ray(space,Vector3(-58.4,18.1,z),Vector3(-59.1,18.1,z));record("fixed_upper_glass_blocks_person_"+str(j),not hit.is_empty() and str(hit.collider.get_parent().name)=="D04H"+str(spec.home_index)+"_GardenGlass")
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
	var incoming:Array=await route(player,[[-53,12,-447],[-34,12,-447],[-31.75,12,-446.8],[-31.75,14.25,-455.4],[-31.75,14.25,-456.3],[-28.25,14.25,-456.3],[-28.25,16.5,-447.05]],"whole_staff_incoming")
	await aim(player,vec(p.gates[2].control_at));await key_e()
	for i in range(100):await physics_frame
	var courts:Array=await route(player,[[-28.1,16.5,-439.5],[-28.1,16.5,-424.5],[-28.1,16.5,-410.5],[-28.1,16.5,-424.5],[-28.1,16.5,-439.5],[-28.25,16.5,-447.05]],"whole_court_out_back")
	var returning:Array=await route(player,[[-28.25,14.25,-456.3],[-31.75,14.25,-456.3],[-31.75,14.25,-455.4],[-31.75,12,-446.8],[-34,12,-447],[-53,12,-447],[-57.3,12,-447]],"whole_staff_return")
	# Unbroken original staff corridor remains clear; the old -370 derivative
	# and protected crew doorway remain untouched through the source pins.
	for z in range(-4590,-4409,5):record("staff_original_corridor_"+str(z),capsule_clear(space,Vector3(-57,12,float(z)/10)))
	for at in [p.clean_bay_approach,p.used_bay_approach]:record("local_bay_worker_"+str(at),capsule_clear(space,vec(at)))
	# Maintenance reach uses the rigid native three-stage tube: hand origin from
	# a full worker stance, no scale and <=1.1m slide per joint. Contact may occur
	# only on the intended native foliage, never through glass/walls/furniture.
	var reaches:Array=[]
	for hatch in hatches:
		var gate:Node3D=hatch.gate;gate.interact(player)
	for i in range(100):await physics_frame
	for planter in range(3):
		var centres:Array=[-436.3,-430.5,-424.7];var cz:float=centres[planter]
		for leaf in range(3):
			var name:="D04HC2_west_LeafMass_"+str(planter)+"_"+str(leaf);var mesh:MeshInstance3D=ship.find_child(name,true,false);var bounds:AABB=mesh.global_transform*mesh.get_aabb();var z:float=cz+[-.5,.15,.6][leaf]
			for height in [bounds.position.y+.04,bounds.get_center().y,bounds.end.y-.02]:
				var target:=Vector3(bounds.end.x-.025,height,z);var found:=false;var evidence:Dictionary={}
				for hatch in hatches:
					var hs:Dictionary=hatch.spec;var zs:Array=hs.service_opening_z
					for x in [-57.95,-57.55,-57.15]:
						for Z in [float(zs[0])+.35,(float(zs[0])+float(zs[1]))/2,float(zs[1])-.35]:
							var at:=Vector3(x,16.5,Z)
							if not capsule_clear(space,at):continue
							for hand_y in [16.85,17.05,17.25]:
								var hand:=Vector3(x,hand_y,Z);var length:float=hand.distance_to(target)
								if length>3.4 or length<1.2:continue
								var hit:=ray(space,hand,target)
								if not hit.is_empty() and str(hit.collider.get_parent().name)==name and hit.position.distance_to(target)<.08:
									var tube_clear:=true;var direction:Vector3=(hit.position-hand).normalized();var axis:=direction.cross(Vector3.UP).normalized();var vertical:=direction.cross(axis).normalized()
									for offset in [axis*.008,-axis*.008,vertical*.008,-vertical*.008]:
										var side:=ray(space,hand+offset,hit.position+offset-direction*.015)
										if not side.is_empty() and str(side.collider.get_parent().name)!=name:tube_clear=false
									if tube_clear and not found:found=true;evidence={"plant":name,"height":height,"worker_stance":str(at),"hand":str(hand),"first_contact":str(hit.position),"length":length,"hatch":hs.name,"native_rigid_tubes":3,"joint_slide":maxf(0,(length-1.2)/2),"person_access":false}
				var key:="maintenance_reach_"+str(planter)+"_"+str(leaf)+"_"+str(height);record(key,found);reaches.append(evidence)
	var result:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks,"check_count":checks.size(),"errors":errors,"operations":operations,"fitting_pose_samples":fitting_samples,"whole_staff_incoming":incoming,"whole_court_out_back":courts,"whole_staff_return":returning,"maintenance_reach":reaches,"production_active":false,"temporary_visit_only":true,"provider_available":false,"physical_carry_transfer_proved":false,"cart_safe_vertical":false}
	FileAccess.open("res://artifacts/d04_physical_connections_candidate.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
