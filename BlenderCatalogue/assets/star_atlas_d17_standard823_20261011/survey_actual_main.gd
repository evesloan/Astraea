extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);player.global_position=Vector3(-61.5,102.03,35.6);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
	for i in range(10):await physics_frame
	var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state;var floors:Array=[];var volumes:Array=[]
	for y in [97.5,102.0]:
		for x in [-75.5,-73.5,-71.5,-69.5,-67.5,-65.5,-63.5,-62.75,-60.25]:
			for z in [32.2,33.8,35.6,37.4,39.0]:
				var at:=Vector3(x,y,z);var hit:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.04,at-Vector3.UP*.04));floors.append({"at":[x,y,z],"hit":not hit.is_empty(),"height":hit.get("position",Vector3.ZERO).y,"owner":str(hit.collider.get_parent().get_path())if not hit.is_empty()else"none"})
	# Candidate support volumes are observations only; no geometry is authored here.
	for x in [-62.75,-60.25]:
		for z in [32.4,38.6]:
			var query:=PhysicsShapeQueryParameters3D.new();var box:=BoxShape3D.new();box.size=Vector3(.44,4.12,.44);box.margin=.001;query.shape=box;query.transform.origin=Vector3(x,99.59,z);var hits:=space.intersect_shape(query,64);var owners:Array=[]
			for hit in hits:owners.append(str(hit.collider.get_parent().get_path()))
			volumes.append({"kind":"lower_pier","at":[x,99.59,z],"size":[.44,4.12,.44],"owners":owners})
	for z in [32.4,35.6,38.6]:
		var query:=PhysicsShapeQueryParameters3D.new();var box:=BoxShape3D.new();box.size=Vector3(15.96,.3,.26);box.margin=.001;query.shape=box;query.transform.origin=Vector3(-68.03,101.78,z);var hits:=space.intersect_shape(query,64);var owners:Array=[]
		for hit in hits:owners.append(str(hit.collider.get_parent().get_path()))
		volumes.append({"kind":"underfloor_transverse","at":[-68.03,101.78,z],"size":[15.96,.3,.26],"owners":owners})
	var out:Dictionary={"status":"SURVEY_COMPLETE_NO_CONSTRUCTION_ACCEPTANCE","baseline":"9c301f656257ddb2d420e6680e8ed9c1f7af9337","floor_queries":floors,"candidate_volume_queries":volumes,"unrestricted_source_queries":true,"new_geometry":false,"original_room823_and_two_reservations_unchanged":true}
	FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/star_atlas_d17_standard823_20261011/ACTUAL_MAIN_SUPPORT_SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  "));print("D17 ROOM823 SUPPORT SURVEY COMPLETE ",floors.size()," floor rays, ",volumes.size()," source volume queries");quit()
