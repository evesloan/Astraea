extends SceneTree
# Focused structural/contact test candidate. Not executed in isolated preparation.
var failed := false
var main: Node
var ship: Node3D
var actor: CharacterBody3D
var data: Dictionary
var checks := 0
func _initialize() -> void: call_deferred("run")
func require(ok: bool, message: String) -> bool:
	checks += 1
	if ok: return true
	failed = true
	push_error("MOVEMENT RECEIVING: " + message)
	quit(1)
	return false
func xyz(a: Array) -> Vector3: return Vector3(float(a[0]),float(a[1]),float(a[2]))
func ray(a: Vector3,b: Vector3) -> Dictionary:
	var q := PhysicsRayQueryParameters3D.create(a,b,1)
	q.exclude = [actor.get_rid()]
	q.hit_back_faces = true
	return ship.get_world_3d().direct_space_state.intersect_ray(q)
func run() -> void:
	data = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D07_MOVEMENT_STUDIO_RECEIVING.json"))
	main = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for i in range(120): await physics_frame
	ship = main.get_node("World360/Astraea") as Node3D
	actor = ship.get_node("ShipSpace/PersistentActors/Player") as CharacterBody3D
	var built := ship.find_child(str(data.root_name),true,false) as Node3D
	if not require(built != null,"Whole main-scene room must exist"): return
	var floor_group := ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false)
	for id in data.floor_owners:
		var owner := floor_group.get_node(str(id))
		if not require(owner.find_children("*","CollisionShape3D",true,false).size()==1,"One floor collision owner required"): return
	var room := built.get_node("WholeRetainedMovementStudio")
	if not require(room.find_children("*","MeshInstance3D",true,false).size()==1290,"All retained source mesh instances required"): return
	if not require(room.find_children("*","StaticBody3D",true,false).size()==1290,"One cached source-faithful triangle contact per source mesh required"): return
	for seat in data.seats:
		var marker := room.find_child(str(seat.runtime_name),true,false) as Node3D
		if not require(marker!=null and marker.global_position.distance_to(xyz(seat.world))<0.0001,"Source seat datum moved"): return
	# Supported branch, actual offset mouth and inward continuation; no8m-clear-mouth assumption.
	for p in [[2,35.5,-458],[4,35.5,-458],[6,35.5,-458],[8,35.5,-458],[10,35.5,-458],[13,35.5,-458],[13,35.5,-456],[22,35.5,-456]]:
		var position := xyz(p)
		var hit := ray(position+Vector3.UP*.15,position-Vector3.UP*.15)
		if not require(not hit.is_empty() and floor_group.is_ancestor_of(hit.collider) and absf(hit.position.y-35.5)<0.001,"Missing exact receiving support"): return
	# Both real guarded drop edges, below rail and across glass. Return-wall geometry is untouched.
	for z in [-460.0,-452.0]:
		for x in [4.25,5.0,6.0,7.0,7.75]:
			var inward := 1.0 if z < -456.0 else -1.0
			var hit := ray(Vector3(x,36.1,z+inward*.8),Vector3(x,36.1,z-inward*.2))
			if not require(not hit.is_empty() and built.get_node("SourceDerivedReceivingGuards").is_ancestor_of(hit.collider),"Receiving guard gap"): return
	for spec in data.lights:
		var lamp := built.get_node(str(spec.id)) as SpotLight3D
		if not require(lamp!=null and lamp.global_position.distance_to(xyz(spec.world))<.0001,"Source fixture datum changed"): return
		var exit_ray := ray(lamp.global_position,lamp.global_position+Vector3.DOWN*.12)
		if not require(exit_ray.is_empty(),"Fixture self-occludes its light exit"): return
	var budget := ship.find_child("LocalShadowSourceBudget",true,false)
	if not require(budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32,"Shared light budget changed"): return
	var active := 0
	for lamp in ship.find_children("*","Light3D",true,false):
		if lamp.visible and lamp.shadow_enabled: active += 1
	if not require(active<=8,"Global eight-shadow budget exceeded"): return
	print("MOVEMENT RECEIVING STRUCTURE PASS ",checks," scoped checks; ordinary walking, actual loaded cart, visual review and final acceptance remain separate")
	main.queue_free()
	await process_frame
	quit(0)
