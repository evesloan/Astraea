extends SceneTree
const PREP: String="/workspace/scratch/375c2e438292/medical-receiving-runtime-20261006-2241/native_capture001/"
const OUT: String=PREP+"output"
var main: Node
var ship: Node3D
var actor: CharacterBody3D
var budget: Node
var medical: Node3D
var captures: Array=[]
func _initialize() -> void:call_deferred("run")
func vec(p: Vector3) -> Array:return [p.x,p.y,p.z]
func save_json(path: String, value: Dictionary) -> void:
	var f:FileAccess=FileAccess.open(path,FileAccess.WRITE);assert(f!=null);f.store_string(JSON.stringify(value,"  ")+"\n")
func selection() -> Dictionary:
	var selected: Array=[];var local: Array=[]
	for light in budget.sources:
		if budget.requested_shadow.get(light.get_instance_id(),false) and light.visible:selected.append({"path":str(light.get_path()),"shadow":light.shadow_enabled,"position":vec(light.global_position),"energy":light.light_energy})
	for light in medical.find_children("MedicalSource_*","SpotLight3D",true,false):local.append({"name":str(light.name),"selected":light.visible,"shadow":light.shadow_enabled,"position":vec(light.global_position),"energy":light.light_energy,"range":light.spot_range,"angle":light.spot_angle,"source_node":str(light.get_meta("source_node",""))})
	return {"selected_sources":selected,"active_count":selected.size(),"medical_sources":local,"budget":budget.shadow_source_budget,"candidate_limit":budget.MAX_VISIBILITY_CANDIDATES,"natural_selector":true}
func supported(feet: Vector3) -> bool:
	var q: PhysicsRayQueryParameters3D=PhysicsRayQueryParameters3D.create(feet+Vector3.UP*.2,feet-Vector3.UP*.2,1);q.exclude=[actor.get_rid()]
	var hit:Dictionary=ship.get_world_3d().direct_space_state.intersect_ray(q)
	var floors:Node=ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false)
	return not hit.is_empty() and floors.is_ancestor_of(hit.collider) and absf(float(hit.position.y)-21)<.015
func run() -> void:
	assert(OS.get_environment("ASTRAEA_MEDICAL_INSTALLED_CAPTURE")=="root_approved")
	var freeze: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PREP+"FREEZE.json"))
	assert(FileAccess.get_sha256(PREP+"capture.gd")==str(freeze.prepared_sha256["capture.gd"]))
	assert(not DirAccess.dir_exists_absolute(OUT));assert(DirAccess.make_dir_recursive_absolute(OUT)==OK)
	main=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(45):await physics_frame
	ship=main.get_node("World360/Astraea");actor=ship.get_node("ShipSpace/PersistentActors/Player");budget=ship.get_node("ShipSystems/LocalShadowSourceBudget");medical=ship.get_node("ShipSpace/Districts/D05MedicalWelcome_WIP")
	actor.set_physics_process(false);actor.set_controls_enabled(false)
	var views: Array=[
		{"id":"core_receiving","eye":Vector3(-5.4,22.65,-432),"target":Vector3(-13.5,22.45,-432),"scope":"Actual D05 port receiving aperture, shoulder/lintel closure and continuous level floor"},
		{"id":"admission_bend","eye":Vector3(-11,22.65,-440.5),"target":Vector3(-18,22.45,-446),"scope":"Actual admission bend, deeper screened threshold and waiting canopy transition"},
		{"id":"waiting_group","eye":Vector3(-16,22.65,-446),"target":Vector3(-26.5,22.45,-446),"scope":"Actual waiting focal grouping, welcome ledge, seating pockets, fitted ceiling and real sources"},
		{"id":"diagnostic_support","eye":Vector3(-33,22.65,-446.5),"target":Vector3(-39.5,22.1,-444.4),"scope":"Actual static diagnostic-support fixtures and screened support edge; no clinical operation claim"}
	]
	for view in views:
		var feet:Vector3=Vector3(view.eye.x,21,view.eye.z);assert(supported(feet),"Supported D05 image stance required")
		actor.global_position=feet;actor.camera.position.y=view.eye.y-21;actor.velocity=Vector3.ZERO
		var direction:Vector3=view.target-view.eye;actor.rotation.y=atan2(-direction.x,-direction.z);actor.pitch=atan2(direction.y,Vector2(direction.x,direction.z).length());actor.camera.rotation.x=actor.pitch
		for frame in range(3):await physics_frame
		for frame in range(12):await process_frame
		for effects in [true,false]:
			main.set_world_resolution(0 if effects else 2);main.effects=effects;main.post_pass.material.set_shader_parameter("enabled",effects);ship.set_display_effects(effects)
			for frame in range(12):await process_frame
			var samples:Array=[]
			for i in range(3):
				for frame in range(4):await process_frame
				budget.refresh();samples.append(selection())
			await RenderingServer.frame_post_draw
			var filename:String=str(view.id)+( "_normal.png" if effects else "_effects_off.png")
			var photo:Image=main.post_view.get_texture().get_image();assert(photo.save_png(OUT+"/"+filename)==OK)
			var row:Dictionary={"view":view.id,"file":filename,"sha256":FileAccess.get_sha256(OUT+"/"+filename),"effects":effects,"eye":vec(actor.camera.global_position),"target":vec(view.target),"feet":vec(feet),"fov":actor.camera.fov,"eye_error_m":actor.camera.global_position.distance_to(view.eye),"supported_stance":true,"light_samples":samples,"render_adapter":RenderingServer.get_video_adapter_name(),"world_resolution":[main.world_view.size.x,main.world_view.size.y],"image_resolution":[photo.get_width(),photo.get_height()],"scope":view.scope,"installed":true,"scene_saved":false,"visual_acceptance":false,"clinical_operation":false}
			captures.append(row);save_json(OUT+"/"+filename+".caption.json",row);save_json(OUT+"/CAPTURES.json",{"status":"CAPTURING_INSTALLED_MEDICAL","captures":captures})
	save_json(OUT+"/RESULT.json",{"status":"ACTUAL_INSTALLED_VIEWS_COMPLETE_PENDING_REVIEW","captures":captures,"capture_count":captures.size(),"budget":budget.shadow_source_budget,"candidate_limit":budget.MAX_VISIBILITY_CANDIDATES,"installed":true,"candidate_models_created":false,"imports_run":false,"scene_saved":false,"visual_acceptance":false,"medical_or_repair_gameplay":false})
	print("INSTALLED_MEDICAL_CAPTURE_COMPLETE: eight actual main-scene images, awaiting visual review")
	main.queue_free();await process_frame;quit()
