extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(50):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false)
	var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state;var floors:Array=[];var columns:Array=[];var beams:Array=[]
	for z in [-67.8,-60.6,-53.4,-46.2,-39.0,-32.2,39.4,46.6,53.8,61.0,67.8]:
		player.global_position=Vector3(-84,97.53,z);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
		for i in range(10):await physics_frame
		for dx in [-.16,0,.16]:
			for dz in [-.16,0,.16]:
				var at:=Vector3(-85.82+dx,97.5,z+dz);var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.035,at-Vector3.UP*.035));floors.append({"at":[at.x,at.y,at.z],"owner":str(h.collider.get_parent().get_path())if not h.is_empty()else"none","height":h.get("position",Vector3.ZERO).y})
		var q:=PhysicsShapeQueryParameters3D.new();var box:=BoxShape3D.new();box.size=Vector3(.32,4.02,.32);box.margin=.0001;q.shape=box;q.transform.origin=Vector3(-85.82,99.545,z);var hits:=space.intersect_shape(q,64);var owners:Array=[]
		for h in hits:owners.append(str(h.collider.get_parent().get_path()))
		columns.append({"at":[-85.82,99.545,z],"size":[.32,4.02,.32],"foreign_owners":owners})
		box=BoxShape3D.new();box.size=Vector3(25.72,.18,.24);box.margin=.0001;q.shape=box;q.transform.origin=Vector3(-72.96,101.68,z);hits=space.intersect_shape(q,64);owners=[]
		for h in hits:owners.append(str(h.collider.get_parent().get_path()))
		beams.append({"at":[-72.96,101.68,z],"size":[25.72,.18,.24],"contact_owners":owners})
	var north:Array=[]
	player.global_position=Vector3(-61.5,97.53,-32);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
	for i in range(10):await physics_frame
	for x in [-62.75,-60.25]:
		for z in [-31.2,-33.0]:
			var at:=Vector3(x,97.5,z);var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.035,at-Vector3.UP*.035));north.append({"at":[x,97.5,z],"owner":str(h.collider.get_parent().get_path())if not h.is_empty()else"none","height":h.get("position",Vector3.ZERO).y})
	var report:Dictionary={"status":"SURVEY_COMPLETE_NO_SOURCE_CHANGED","baseline":"bc731d6d6d54bb2595331ee2f4368558d4d24fda","lower_street_footprint_rays":floors,"proposed_column_volumes":columns,"proposed_cross_beam_volumes":beams,"north_source_pier_candidates":north,"original_routes_and_assets_unchanged":true}
	FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/star_atlas_d17_standard_batch_20261011/ACTUAL_SUPPORT_SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("NINE STANDARD BATCH SUPPORT SURVEY COMPLETE ",floors.size()," lower-floor rays, ",columns.size()," column and crossbeam volumes");quit()
