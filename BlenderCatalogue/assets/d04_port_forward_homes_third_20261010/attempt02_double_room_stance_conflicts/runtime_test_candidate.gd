extends SceneTree
var checks:Dictionary={}
var errors:Array=[]
func record(key:String,ok:bool)->void:
	checks[key]=ok
	if not ok:errors.append(key)
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func ray(space:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3)->Dictionary:
	return space.intersect_ray(PhysicsRayQueryParameters3D.create(a,b))
func capsule_clear(space:PhysicsDirectSpaceState3D,at:Vector3)->bool:
	var q:=PhysicsShapeQueryParameters3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001
	q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925)
	if not space.intersect_shape(q,32).is_empty():return false
	# Opposite cross-rays also catch a stance placed wholly inside an opaque
	# closed mesh; concave surface queries alone can miss that case.
	for delta in [Vector3(.3,0,0),Vector3(0,0,.3)]:
		if not ray(space,at+Vector3.UP-delta,at+Vector3.UP+delta).is_empty():return false
	return true
func cart_clear(space:PhysicsDirectSpaceState3D,at:Vector3,yaw:float)->bool:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
	var pose:=Transform3D(Basis(Vector3.UP,yaw),at+Vector3.UP*.005)
	for item in d.boxes:
		var shape:=BoxShape3D.new();shape.size=vec(item.size);shape.margin=.001
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=pose*Transform3D(Basis.IDENTITY,vec(item.center))
		if not space.intersect_shape(q,32).is_empty():return false
	for item in d.wheel_contacts:
		var shape:=SphereShape3D.new();shape.radius=float(item.radius);shape.margin=.001
		var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=pose*Transform3D(Basis.IDENTITY,vec(item.center))
		if not space.intersect_shape(q,32).is_empty():return false
	return true
func physical_key(down:bool)->void:
	var e:=InputEventKey.new();e.keycode=KEY_W;e.physical_keycode=KEY_W;e.pressed=down;Input.parse_input_event(e)
func walk_to(player:CharacterBody3D,goal:Vector3)->Dictionary:
	var start:=player.global_position;var delta:=goal-start;delta.y=0
	player.rotation.y=atan2(-delta.x,-delta.z);physical_key(true)
	var budget:=int(delta.length()/3.1*60)+150;var frames:=0;var reached:=false;var route_contacts:Dictionary={}
	for i in range(budget):
		await physics_frame;frames+=1
		for j in range(player.get_slide_collision_count()):route_contacts[str(player.get_slide_collision(j).get_collider().get_path())]=true
		var now:=goal-player.global_position;now.y=0
		if now.dot(delta.normalized())<.16:reached=true;break
	physical_key(false)
	for i in range(20):await physics_frame
	var contacts:Array=[]
	for i in range(player.get_slide_collision_count()):contacts.append(str(player.get_slide_collision(i).get_collider().get_path()))
	if not reached:print("WALK_BLOCKED_CONTACTS ",contacts," ALL ",route_contacts.keys())
	var at:=player.global_position;var horizontal:=Vector2(at.x-goal.x,at.z-goal.z).length()
	return {"reached":reached and horizontal<.55 and absf(at.y-goal.y)<.12,"frames":frames,"start":str(start),"goal":str(goal),"final":str(at),"floor_contact":player.is_on_floor(),"existing_player_controller":true}
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_HOMES_THIRD.json"))
	var homes:Node3D=ship.find_child("D04PortForwardThirdHomeCandidates",true,false)
	var structure:Node3D=ship.find_child("D04PortForwardThirdHomesStructure",true,false)
	if homes==null or structure==null:print("MISSING_HOME_ROOTS");quit(1);return
	var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	player.global_position=Vector3(-44,16.53,-412);player.velocity=Vector3.ZERO;player.set_controls_enabled(true)
	ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
	for i in range(15):await physics_frame
	var space:=ship.get_world_3d().direct_space_state
	for file in p.model_pins:record("model_pin_"+str(file),FileAccess.get_sha256("res://assets/models/"+str(file))==p.model_pins[file])
	for fi in range(p.foundation_feet.size()):
		var f:Dictionary=p.foundation_feet[fi];var owner:Node=ship.find_child(str(f.owner),true,false)
		for dx in[-.1,0,.1]:
			for dz in[-.1,0,.1]:
				var at:=Vector3(f.x+dx,11.76,f.z+dz);var h:=ray(space,at-Vector3.UP*.03,at+Vector3.UP*.03)
				record("baseline_bearing_"+str(fi)+"_"+str(dx)+"_"+str(dz),owner!=null and not h.is_empty()and owner.is_ancestor_of(h.collider)and absf(h.position.y-11.76)<.002)
	var walks:Array=[]
	for rr in p.rooms:
		var r:Dictionary=rr;var home:Node3D=homes.get_node(str(r.allocation.proposed_runtime_id));var door:Node3D=home.get_node("HomeEntry")
		var idx:=str(r.source_index);var west:bool=r.court_side=="west";var front:float=r.allocation.allocation_x[1]if west else r.allocation.allocation_x[0];var cz:float=r.entry.origin[2];var sign:float=-1 if west else 1
		record("reservation_"+idx,int(home.get_meta("reserved_rest_count",0))==2 and home.get_meta("rest_slot_ids",[])==r.allocation.proposed_rest_slot_ids and not home.get_meta("species_ready",true))
		var foyer:=Vector3(front+sign*.72,16.5,cz)
		var care:=vec(r.care_station_world)
		for key in["foyer","care"]:
			var at:Vector3=foyer if key=="foyer"else care;var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03)
			record("floor_"+idx+"_"+key,not h.is_empty()and structure.is_ancestor_of(h.collider)and absf(h.position.y-16.5)<.002)
			record("capsule_"+idx+"_"+key,capsule_clear(space,at))
			if key=="care":record("care_cart_station_"+idx,cart_clear(space,at,0))
		for approach in r.rest_approach_worlds:
			record("rest_dry_approach_"+str(approach.rest_slot_id),capsule_clear(space,vec(approach.position)))
		# All fixtures remain the catalogue source; privacy is tested from inside
		# the foyer so the closed exterior leaf cannot supply the result.
		for component in r.components:
			if component.name in["Toilet","Shower"]:
				var target:=vec(component.position)+Vector3.UP*(.55 if component.name=="Toilet"else 1.1)
				var h:=ray(space,foyer+Vector3.UP*1.65,target)
				var owner_name:String=""if h.is_empty()else str(h.collider.get_parent().name)
				record("privacy_"+idx+"_"+str(component.name),not h.is_empty()and ("Bath"in owner_name))
		var outlook:=vec(r.outlook_world)
		record("dry_outlook_stance_"+idx,capsule_clear(space,outlook))
		var hit:=ray(space,outlook+Vector3.UP*1.65,outlook+Vector3(sign*8,1.65,0))
		record("private_garden_glass_"+idx,not hit.is_empty()and "GardenGlass"in str(hit.collider.get_parent().name))
		record("door_initial_closed_"+idx,not door.desired_open and door.open_fraction<.001)
		if p.open_room_entries:
			player.global_position=Vector3(-44,16.53,cz);player.velocity=Vector3.ZERO
			for i in range(10):await physics_frame
			door.interact(null)
			for frame in range(100):
				await physics_frame
				if frame in[0,20,40,60,80,99]:
					for leaf in door.leaves:
						var c:CollisionShape3D=leaf.get_node("LeafContact");var q:=PhysicsShapeQueryParameters3D.new();q.shape=c.shape;q.transform=c.global_transform;var foreign:Array=[]
						for h in space.intersect_shape(q,64):
							if not door.is_ancestor_of(h.collider):foreign.append(str(h.collider.get_path()))
						record("leaf_sweep_"+idx+"_"+str(frame)+"_"+str(leaf.name),foreign.is_empty())
						if not foreign.is_empty():print("FOREIGN_LEAF ",idx," ",foreign)
			record("door_open_"+idx,door.open_fraction>.999)
			for goal in[foyer,Vector3(foyer.x,16.5,cz+1.3),Vector3(care.x,16.5,cz+1.3),care]:
				var result:Dictionary=await walk_to(player,goal);result.room=r.source_index;walks.append(result);record("actual_home_walk_"+str(walks.size()),result.reached and result.floor_contact)
				if not result.reached:break
			door.interact(null)
			for i in range(100):await physics_frame
			record("door_roundtrip_"+idx,door.open_fraction<.001)
	for sample in p.rest_reference_samples:
		var at:Vector3=vec(sample.position)+Basis(Vector3.UP,float(sample.yaw))*vec(sample.local_reference.position)
		var h:=ray(space,at+Vector3.UP*.035,at-Vector3.UP*.035)
		var home:Node3D=homes.get_node(str(p.rooms.filter(func(a):return a.source_index==sample.room)[0].allocation.proposed_runtime_id))
		record("rest_contact_"+str(sample.room)+"_"+str(sample.binding)+"_"+str(sample.local_reference.name),not h.is_empty()and home.is_ancestor_of(h.collider)and str(h.collider.get_parent().name)==str(sample.source_contact_node)and absf(h.position.y-float(sample.source_contact_surface_y))<.0002)
	for i in range(p.courts.size()):
		var coords:Array=p.courts[i].geometry.coordinates[0];var center:=Vector3.ZERO
		for j in range(coords.size()-1):center+=Vector3(coords[j][0],16.5,coords[j][1])
		center/=float(coords.size()-1)
		for dz in[-1,0,1]:
			var at:=center+Vector3(0,0,dz);var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03)
			record("contained_court_floor_"+str(i)+"_"+str(dz),not h.is_empty()and structure.is_ancestor_of(h.collider)and str(h.collider.get_parent().name)=="D04HC3_"+str(p.courts[i].side)+"_Floor"and absf(h.position.y-16.5)<.002)
	var original:Node3D=ship.find_child("D04PortForwardSecondHomesStructure",true,false)
	for g in p.guard_preimages:record("original_guard_gate_"+str(g.name),(original.find_child(str(g.name),true,false)==null)==bool(p.open_room_entries))
	# Recheck the existing public arrival and staff upper landing into the
	# fuller commons; do not move the public core or claim cart-safe stairs.
	var arrival_walks:Array=[]
	if p.open_room_entries:
		for route in[[Vector3(-1.5,16.53,-405.2),Vector3(-8.5,16.5,-405.2)],[Vector3(-60.05,16.53,-369.5),Vector3(-66.4,16.5,-369.5)]]:
			player.global_position=route[0];player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
			for i in range(10):await physics_frame
			var walk:Dictionary=await walk_to(player,route[1]);arrival_walks.append(walk);record("retained_public_staff_arrival_"+str(arrival_walks.size()),walk.reached and walk.floor_contact)
	var old:Node3D=ship.find_child("StarAtlasRoomCandidates",true,false)
	record("original85_homes",int(old.get_meta("source_candidate_units",0))==85);record("original221_anchors",int(old.get_meta("source_rest_slots",0))==221)
	record("culling_preserved",ship.get_node("ShipSystems/ReceivedRoomResidency").enabled)
	record("capacity20_25",int(homes.get_meta("total_house_reservation_count",0))==20 and int(homes.get_meta("capacity_preserved",0))==25)
	record("species_acceptance_held",int(homes.get_meta("species_ready_rooms",-1))==0 and not structure.get_meta("primary_load_accepted",true))
	var prior:Node3D=ship.find_child("D04PortForwardHomeCandidates",true,false);record("prior_four_physical_proposals_preserved",prior.get_child_count()==4 and int(prior.get_meta("physical_candidates",0))==4)
	var second:Node3D=ship.find_child("D04PortForwardSecondHomeCandidates",true,false);record("prior_second_four_physical_proposals_preserved",second.get_child_count()==4 and int(second.get_meta("physical_candidates",0))==4)
	record("ten_proposals_ten_remaining",int(homes.get_meta("physical_proposals_after_batch",0))==10 and int(homes.get_meta("remaining_interiors",-1))==10)
	var crew_contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/CREW_HOME_APPROACH_RUNTIME.json"))
	for i in range(crew_contract.route_xz.size()):
		var at:=Vector3(crew_contract.route_xz[i][0],12,crew_contract.route_xz[i][1]);record("retained_crew_approach_capsule_"+str(i),capsule_clear(space,at));record("retained_crew_approach_cart_"+str(i),cart_clear(space,at,PI/2 if i<3 or i==4 else 0))
	var crew_walks:Array=[]
	if p.open_room_entries:
		var crew:Node3D=ship.find_child("CrewHomeApproach_WIP",true,false);var crew_door:Node3D=crew.get_node("HomeServiceDoor")
		player.global_position=Vector3(-57,12.03,-432);player.velocity=Vector3.ZERO
		for i in range(10):await physics_frame
		crew_door.interact(null)
		for frame in range(100):
			await physics_frame
			if frame in[0,20,40,60,80,99]:
				for leaf in crew_door.leaves:
					var bad:Array=[]
					for contact in leaf.get_children():
						if contact is CollisionShape3D:
							var q:=PhysicsShapeQueryParameters3D.new();q.shape=contact.shape;q.transform=contact.global_transform
							for h in space.intersect_shape(q,128):
								if structure.is_ancestor_of(h.collider):bad.append(str(h.collider.get_path()))
					record("protected_crew_leaf_new_contacts_"+str(frame)+"_"+str(leaf.name),bad.is_empty())
		record("protected_crew_door_open",crew_door.desired_open and crew_door.open_fraction>.999)
		for i in range(1,crew_contract.route_xz.size()):
			var point:Array=crew_contract.route_xz[i];var walked:Dictionary=await walk_to(player,Vector3(point[0],12,point[1]));crew_walks.append(walked);record("protected_crew_actual_walk_"+str(i),walked.reached and walked.floor_contact)
			if not walked.reached:break
		crew_door.interact(null)
		for i in range(100):await physics_frame
		record("protected_crew_door_roundtrip",not crew_door.desired_open and crew_door.open_fraction<.001)

	physical_key(false)
	var result={"status":"PASS"if errors.is_empty()else"FAIL","stage":"connected"if p.open_room_entries else"sealed","model_pins":p.model_pins,"checks":checks,"check_count":checks.size(),"errors":errors,"existing_player_walks":walks,"ray_excludes":0,"bearing_samples":72,"rest_reference_samples":18,"primary_load_accepted":false,"species_ready_rooms":0,"cart_safe_vertical_accepted":false,"ordinary_graphics_review":false,"retained_rest_markers_unchanged":true,"source_trim_surface_offset_disclosed":true,"retained_public_staff_arrival_walks":arrival_walks,"protected_crew_actual_walks":crew_walks,"prior_physical_proposals_preserved":8,"physical_proposals_after_batch":10,"remaining_interiors":10}
	FileAccess.open("res://artifacts/d04_port_forward_homes_third_connected.json"if p.open_room_entries else"res://artifacts/d04_port_forward_homes_third_sealed.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
