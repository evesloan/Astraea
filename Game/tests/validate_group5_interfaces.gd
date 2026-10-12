extends SceneTree
var errors:Array=[]
var counts:Dictionary={"control_source_pins":0,"physical_control_rays":0,"guide_instances":0,"guide_source_pins":0,"cached_state_returns":0,"fitout_source_pins":0,"care_back_contacts":0}
func _initialize()->void:call_deferred("run")
func check(label:String,condition:bool)->void:
	if not condition:errors.append(label)
func contains(ancestor:Node,child:Node)->bool:
	while child!=null:
		if child==ancestor:return true
		child=child.get_parent()
	return false
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(12):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	manager.enabled=false
	actor.set_controls_enabled(false)
	var startup_attached:bool=ship.get_node("ShipSpace/Districts/ShoppingPromenadeChunks").has_meta("group5_completion_attached")
	if not startup_attached:load("res://scripts/group5_completion.gd").build(ship)
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/CONSTRUCTION.json"))
	var shopping:Node3D=ship.get_node("ShipSpace/Districts/ShoppingPromenadeChunks")
	var state:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
	for row in definition.doors:
		var chunk:Node3D=load("res://scripts/group5_completion.gd")._chunk(ship,shopping,str(row.chunk_id))
		actor.global_position=chunk.position+Vector3(0,.03,0)
		manager.prepare_position(actor.global_position)
		manager.refresh(9.0)
		for i in range(3):await physics_frame
		var door:Node3D=chunk.get_node(str(row.local_name))
		check(str(row.physical_id)+" control source pin",FileAccess.get_sha256(definition.control_model)==str(row.control_model_sha256))
		counts.control_source_pins+=1
		for spec in row.controls:
			var pod:Node3D=door.get_node(str(spec.id))
			var normal:Vector3=pod.global_basis.z
			var ray:=PhysicsRayQueryParameters3D.create(pod.global_position+normal*.25,pod.global_position+normal*.01)
			ray.exclude=[actor.get_rid()]
			var hit:Dictionary=state.intersect_ray(ray)
			check(str(row.physical_id)+" "+str(spec.id)+" actual contact/ancestor",not hit.is_empty() and contains(pod,hit.collider) and contains(door,hit.collider))
			counts.physical_control_rays+=1
	for revision in definition.get("fitout_revisions",[]):
		var chunk:Node3D=load("res://scripts/group5_completion.gd")._chunk(ship,shopping,str(revision.chunk_id))
		actor.global_position=chunk.position+Vector3(0,.03,0)
		manager.prepare_position(actor.global_position)
		manager.refresh(9.0)
		for i in range(3):await physics_frame
		check(str(revision.chunk_id)+" pinned adopted revision",str(chunk.get_meta("group5_fitout_revision"))==str(revision.model_sha256) and FileAccess.get_sha256(str(revision.model_path))==str(revision.model_sha256) and FileAccess.get_sha256(str(revision.scene_path))==str(revision.scene_sha256))
		counts.fitout_source_pins+=1
		var s:float=1.0 if float(revision.godot_matrix_rows[0][2])<0 else -1.0
		var from:Vector3=chunk.to_global(Vector3(-s*1.1,1.0,-5.25))
		var to:Vector3=chunk.to_global(Vector3(-s*1.1,1.0,-5.6))
		var hit:Dictionary=state.intersect_ray(PhysicsRayQueryParameters3D.create(from,to))
		check(str(revision.chunk_id)+" actual rotated care back",not hit.is_empty() and absf(chunk.to_local(hit.position).z+5.52)<.002)
		counts.care_back_contacts+=1
	for spec in definition.wayfinding:
		var chunk:Node3D=load("res://scripts/group5_completion.gd")._chunk(ship,shopping,str(spec.chunk_id))
		manager.prepare_position(chunk.position)
		check(str(spec.id)+" exact instance",chunk.has_node(str(spec.id)))
		check(str(spec.id)+" guide source/two faces",FileAccess.get_sha256(str(spec.model_path))==str(spec.model_sha256) and spec.readable_faces==2)
		counts.guide_instances+=1
		counts.guide_source_pins+=1
	# Exercise the existing cached residency owner with one actual opened public
	# door in each bank. This fixture relocation tests caching, not a walking route.
	for key in ["SHOP_D09_P72_F340","SHOP_D09_P100_F210","SHOP_D09_S72_F340","SHOP_D09_S100_F210"]:
		var chunk:Node3D=load("res://scripts/group5_completion.gd")._chunk(ship,shopping,key)
		actor.global_position=chunk.position+Vector3(0,.03,0)
		manager.prepare_position(actor.global_position)
		manager.refresh(9.0)
		for i in range(3):await physics_frame
		var door:Node3D=chunk.get_node("PublicDoors")
		var original_instance:int=door.get_instance_id()
		door.interact(actor)
		for i in range(82):await physics_frame
		check(key+" opened before cache",door.desired_open and door.fraction==1)
		actor.global_position=Vector3(1000,1000,1000)
		manager.refresh(9.0)
		check(key+" cached detached",not chunk.is_inside_tree())
		check(key+" retained state detached",door.get_instance_id()==original_instance and door.desired_open and door.fraction==1)
		actor.global_position=chunk.position+Vector3(0,.03,0)
		manager.prepare_position(actor.global_position)
		for i in range(3):await physics_frame
		check(key+" same state returned",chunk.is_inside_tree() and door.get_instance_id()==original_instance and door.desired_open and door.fraction==1)
		counts.cached_state_returns+=1
	var result:Dictionary={"builder_attached_during_main_startup":startup_attached,"status":"PASS" if errors.is_empty() else "HOLD","counts":counts,"errors":errors,"fixture":"actual production main.tscn plus scoped builder and original cached residency manager","scope":"All fixed control contact rays/source pins, guide instances,ten rotated care-back contacts/revision pins and four garden-shop public-door state returns through actual residency detach/release/prepare. Fixture relocations are explicit; no walking, save/load, graphical lighting or combined shared-integration acceptance.","whole_group_accepted":false}
	FileAccess.open("res://artifacts/group5_interfaces_integrated001.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("GROUP5_INTERFACES ",JSON.stringify(result))
	quit(0 if errors.is_empty() else 1)
