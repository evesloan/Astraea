extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for f in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	actor.position=Vector3(54.5,61.06,0);actor.velocity=Vector3.ZERO
	for f in range(20):actor.velocity.y=-.1;actor.move_and_slide();await physics_frame
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var entries:Array=[];var lamps:Array=[];var roots:Array=[]
	for entry in residency.entries:
		if str(entry.room.get_meta("programme_key",""))in["D10_directory_06","D10_directory_10"]:
			entries.append(entry);var room:Node3D=entry.room
			assert(room.has_node("Group8DiningFixtureSources_WIP"),"Two-key receiving hook missing")
			var n:Node3D=room.get_node("Group8DiningFixtureSources_WIP");roots.append(n)
			for light in n.find_children("*","SpotLight3D",true,false):
				assert(budget.sources.has(light)and budget.requested_shadow[light.get_instance_id()],"Pre-configure source lost its requested shadow")
				lamps.append({"node":light,"id":light.get_instance_id()})
	assert(entries.size()==2 and lamps.size()==39)
	var pose:=actor.global_transform;var saved:Node3D=residency.actor;var fixture:=Node3D.new();root.add_child(fixture);fixture.position=Vector3(0,61,-650);residency.set_physics_process(false);residency.actor=fixture;residency.refresh(9);budget.refresh()
	for entry in entries:assert(not entry.attached and not entry.room.is_inside_tree(),"Actual cached-room detach failed")
	for row in lamps:assert(is_instance_valid(row.node)and row.node.get_instance_id()==row.id and not row.node.is_inside_tree()and not row.node.visible and not row.node.shadow_enabled,"Cached source was freed, replaced or active outside the tree")
	residency.prepare_position(Vector3(63,61,0));residency.prepare_position(Vector3(19,61,432))
	for entry in entries:
		assert(entry.attached and entry.room.is_inside_tree())
		assert(entry.room.get_node("Group8DiningFixtureSources_WIP")in roots,"Cached restoration duplicated the owned source root")
	for row in lamps:assert(row.node.get_instance_id()==row.id and row.node.is_inside_tree(),"Restored source identity changed")
	residency.actor=saved;residency.set_physics_process(true);fixture.free();budget.refresh()
	assert(actor.global_transform.is_equal_approx(pose),"Range fixture moved the actual player")
	var active:=0
	for row in lamps:
		if row.node.visible and row.node.shadow_enabled:active+=1
	assert(active>0 and active<=8,"Restored housed dining source not admitted by original budget")
	var r:={"status":"PASS","two_key_scoped_received_hook":true,"cached_detach_attach_same_source_objects":39,"rooms":2,"original_actor_pose_and_identity_unchanged":true,"existing_budget_limit":8,"actual_restored_active_sources":active,"resources_freed":false,"walked_external_receiving_or_gameplay_acceptance":false}
	FileAccess.open("res://data/architecture/group8/DINING_FIXTURE_RESIDENCY_VALIDATION.json",FileAccess.WRITE).store_string(JSON.stringify(r,"  ")+"\n");print("GROUP8 DINING FIXTURE PASS: ",JSON.stringify(r))
	main.queue_free();for f in range(4):await process_frame
	quit(0)
