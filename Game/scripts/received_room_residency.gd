extends Node
# First residency layer: keep exact room state cached, detach hidden distant
# source rooms from the live render/physics tree. Cached doors retain state. This does not free RAM.
# Engine occlusion-aware notifiers preserve distant views through real openings.
const ENTER_MARGIN := 45.0
const KEEP_MARGIN := 65.0
const HIDDEN_GRACE_SECONDS := 8.0
var host:Node3D
var actor:Node3D
var rooms_root:Node3D
var entries:Array[Dictionary]=[]
var elapsed:=0.0
var changes:=0
var enabled:=true
func setup(ship:Node3D)->void:
	host=ship
	actor=ship.get_node("ShipSpace/PersistentActors/Player")
	rooms_root=ship.get_node("ShipSpace/Districts/ReceivedSections")
	process_physics_priority=-150
	enabled=OS.get_environment("ASTRAEA_FORCE_ALL_RECEIVED_ROOMS")!="1"
	var candidates:Array[Node]=rooms_root.get_children()
	for name in ["ListeningSalonReceiving_WIP","StillroomReceiving_WIP","Cinema5Receiving_WIP","CustodialDepotReceiving_WIP","EquipmentDepotReceiving_WIP"]:
		var room:=ship.get_node_or_null("ShipSpace/Districts/"+name)
		if room!=null:candidates.append(room)
	for home_root in ["TidalRoomCandidates","QuietGroveRoomCandidates","FamilyTerraceRoomCandidates","SunsetRoomCandidates","StarAtlasRoomCandidates","NightGardenRoomCandidates","ShoppingPromenadeChunks","SpecialtyHomeCandidates","AtriumGalleryFittings","D04PortForwardHomeCandidates","D04PortForwardSecondHomeCandidates","D04PortForwardThirdHomeCandidates"]:
		var homes:=ship.get_node_or_null("ShipSpace/Districts/"+home_root)
		if homes!=null:candidates.append_array(homes.get_children())
	for room:Node3D in candidates:
		var bounds:=AABB()
		var initialized:=false
		for mesh:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):
			var box: AABB=mesh.global_transform*mesh.get_aabb()
			bounds=bounds.merge(box) if initialized else box
			initialized=true
		if room.has_meta("deferred_visual_bounds"):
			var authored_bounds:AABB=room.global_transform*room.get_meta("deferred_visual_bounds")
			bounds=bounds.merge(authored_bounds) if initialized else authored_bounds
			initialized=true
		if not initialized:continue
		var witness:=VisibleOnScreenNotifier3D.new()
		witness.name=str(room.name)+"_VisibilityWitness"
		# Conservative expansion admits rooms before their real edges enter view.
		witness.aabb=bounds.grow(3.0)
		host.add_child(witness)
		var entry:Dictionary={"room":room,"parent":room.get_parent(),"bounds":bounds,"witness":witness,"attached":true,"hidden_seconds":0.0,"meshes":room.find_children("*","MeshInstance3D",true,false).size()+int(room.get_meta("deferred_visual_meshes",0))}
		entries.append(entry)
		witness.screen_entered.connect(_on_screen_entered.bind(entry))
	set_meta("scope","Received sources, Tidal, Quiet, Family, Sunset, Star Atlas and Night Garden homes; exact nodes and door states cached, not destroyed; independent floors/occluders remain resident; no RAM-unload claim")
	# Avoid registering the entire distant ship in the first physics/render frame.
	set_meta("startup_live_nodes",get_tree().get_node_count())
	if enabled:refresh(HIDDEN_GRACE_SECONDS)
	else:
		for entry in entries:load("res://scripts/deferred_home_visual.gd").ensure(entry.room)

func _on_screen_entered(entry:Dictionary)->void:
	# React at the next safe main-thread point, not the 0.2 second polling boundary.
	_attach_visible_room.call_deferred(entry)
func _attach_visible_room(entry:Dictionary)->void:
	if not is_inside_tree() or entry.attached:return
	entry.parent.add_child(entry.room)
	entry.attached=true
	load("res://scripts/deferred_home_visual.gd").ensure(entry.room)
	entry.hidden_seconds=0.0
	changes+=1
func _physics_process(delta:float)->void:
	if not enabled:return
	elapsed+=delta
	if elapsed<.2:return
	var step:=elapsed
	elapsed=0.0
	refresh(step)
func near_bounds(position:Vector3,bounds:AABB,margin:float)->bool:
	# Preserve neighboring levels around shafts and stairs; full AABB distance.
	var nearest:Vector3=position.clamp(bounds.position,bounds.end)
	return position.distance_to(nearest)<=margin
func refresh(delta:float=0.0)->void:
	if not is_instance_valid(actor):return
	var persistent_bodies:Array[Node]=host.get_node("ShipSpace/PersistentActors").find_children("*","RigidBody3D",true,false)
	for entry in entries:
		var room:Node3D=entry.room
		var witness:VisibleOnScreenNotifier3D=entry.witness
		var near:=near_bounds(actor.global_position,entry.bounds,KEEP_MARGIN if entry.attached else ENTER_MARGIN)
		# Loose carts/bottles keep their supporting room contacts even without Player.
		for persistent_body:Node3D in persistent_bodies:
			if near_bounds(persistent_body.global_position,entry.bounds,8.0):
				near=true
				break
		var wanted:bool=near or witness.is_on_screen()
		if wanted:
			entry.hidden_seconds=0.0
			if not entry.attached:
				entry.parent.add_child(room)
				entry.attached=true
				changes+=1
			load("res://scripts/deferred_home_visual.gd").ensure(room)
		else:
			entry.hidden_seconds+=delta
			if entry.attached and entry.hidden_seconds>=HIDDEN_GRACE_SECONDS:
				entry.parent.remove_child(room)
				entry.attached=false
				load("res://scripts/deferred_home_visual.gd").release(room)
				changes+=1
func prepare_position(position:Vector3)->void:
	# Explicit arrivals call this before collision validation and control release.
	for entry in entries:
		if not entry.attached and near_bounds(position,entry.bounds,ENTER_MARGIN):
			entry.parent.add_child(entry.room)
			entry.attached=true
			load("res://scripts/deferred_home_visual.gd").ensure(entry.room)
			entry.hidden_seconds=0.0
			changes+=1
func statistics()->Dictionary:
	var live:=0
	var resident_meshes:=0
	var cached_meshes:=0
	var deferred_meshes:=0
	var deferred_rooms:=0
	for entry in entries:
		if entry.attached:
			live+=1
			resident_meshes+=int(entry.meshes)
		else:
			var unloaded:int=int(entry.room.get_meta("deferred_visual_meshes",0)) if not entry.room.has_meta("resident_visual") else 0
			cached_meshes+=int(entry.meshes)-unloaded
			deferred_meshes+=unloaded
			if unloaded>0:deferred_rooms+=1
	return {"registered_rooms":entries.size(),"active_rooms":live,"active_meshes":resident_meshes,"cached_detached_meshes":cached_meshes,"transitions":changes,"resources_freed":false,"uninstantiated_meshes":deferred_meshes,"deferred_visual_rooms":deferred_rooms}
func _notification(what:int)->void:
	if what==NOTIFICATION_PREDELETE:
		for entry in entries:
			if is_instance_valid(entry.room) and not entry.attached:entry.room.free()
