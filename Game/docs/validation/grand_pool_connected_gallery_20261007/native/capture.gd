extends SceneTree
# Actual installed scene only. No candidate import, geometry edits or acceptance gate.
const PREP := "/workspace/scratch/375c2e438292/pool-connected-gallery-curved001/native_capture001/"
const OUT := PREP+"output"
var ship: Node3D
var actor: CharacterBody3D
var budget: Node
var feature_root: Node3D
var lights: Array[SpotLight3D]=[]
var captures: Array=[]
var focused_sha: String
func vec(p: Vector3) -> Array:return [p.x,p.y,p.z]
func _initialize() -> void:call_deferred("run")
func save_json(path: String,value: Dictionary) -> void:
	value["installed"]=true;value["production_changes"]=false;value["visual_acceptance"]=false;value["visual_first_pass_complete"]=false;value["final_acceptance"]=false
	var file:=FileAccess.open(path,FileAccess.WRITE);assert(file!=null);file.store_string(JSON.stringify(value,"  ",true,true));file.close()
func selection() -> Dictionary:
	var selected: Array=[];var proposed: Array=[]
	for light in budget.sources:
		if budget.requested_shadow.get(light.get_instance_id(),false) and light.visible:
			selected.append({"path":str(light.get_path()),"shadow_enabled":light.shadow_enabled,"position":vec(light.global_position),"energy":light.light_energy})
	for light in lights:
		proposed.append({"name":str(light.name),"path":str(light.get_path()),"selected":light.visible,"shadow_enabled":light.shadow_enabled,"receiver_visible":budget._has_visible_sample(light),"position":vec(light.global_position),"direction":vec(-light.global_basis.z),"energy":light.light_energy,"range":light.spot_range,"angle":light.spot_angle,"source_marker":str(light.get_meta("source_marker","")),"fixture_powered":light.get_meta("fixture_powered",true),"observer_distance":actor.global_position.distance_to(light.global_position)})
	return {"selected":selected,"active_count":selected.size(),"feature_sources":proposed,"budget":budget.shadow_source_budget,"candidate_limit":budget.MAX_VISIBILITY_CANDIDATES,"natural_selector":true}
func required_selected(samples: Array,names: Array) -> bool:
	for sample in samples:
		for name in names:
			var found: bool=false
			for row in sample.feature_sources:
				if row.name==name and row.selected:found=true
			if not found:return false
	return true
func run() -> void:
	assert(OS.get_environment("ASTRAEA_INSTALLED_EAST_GALLERY_CAPTURE")=="parent_approved")
	var freeze: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PREP+"FINAL_CURRENT_FREEZE.json"))
	assert(FileAccess.get_sha256(PREP+"capture.gd")==str(freeze.prepared_files["capture.gd"]))
	focused_sha=str(freeze.focused_receipt_sha256)
	assert(not DirAccess.dir_exists_absolute(OUT));assert(DirAccess.make_dir_recursive_absolute(OUT)==OK)
	var main: Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(30):await physics_frame
	ship=main.get_node("World360/Astraea");actor=ship.get_node("ShipSpace/PersistentActors/Player");budget=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	feature_root=ship.get_node("ShipSpace/Districts/GrandPoolEastGallery_WIP")
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GRAND_POOL_EAST_GALLERY_RUNTIME.json"))
	for fixture in data.fixtures:
		lights.append(feature_root.get_node(NodePath(str(fixture.name)))as SpotLight3D)
	actor.set_physics_process(false);actor.set_controls_enabled(false)
	var views: Array=[
		{"id":"connected_gallery_original_arrival","eye":Vector3(-14,54.15,-443.2),"target":Vector3(-9.4,54.3,-449.4),"feet_y":52.5,"required":[],"scope":"Same standing pose as the user-flagged canopy view; restored curvature, mounts and whole-gallery connection require visual review"},
		{"id":"connected_gallery_market_receiving","eye":Vector3(-14.6,54.15,-435.65),"target":Vector3(-9.8,55.7,-451.8),"feet_y":52.5,"required":[],"scope":"Actual public apron looking through the counter, service bench and curved gallery; native light balance pending"},
		{"id":"connected_gallery_fore_directory","eye":Vector3(-14.4,54.15,-460.5),"target":Vector3(-9.8,55.2,-446.5),"feet_y":52.5,"required":[],"scope":"Fore directory and mounted crown/collar junction looking along the full inhabited gallery; all existing routes retained"},
	]
	for view in views:
		actor.global_position=Vector3(view.eye.x,view.feet_y,view.eye.z);actor.camera.position.y=view.eye.y-view.feet_y;actor.velocity=Vector3.ZERO
		var direction: Vector3=view.target-view.eye;actor.rotation.y=atan2(-direction.x,-direction.z);actor.pitch=atan2(direction.y,Vector2(direction.x,direction.z).length());actor.camera.rotation.x=actor.pitch
		for frame in range(3):await physics_frame
		for frame in range(12):await process_frame
		for effects in [true,false]:
			main.set_world_resolution(0 if effects else 2);main.effects=effects;main.post_pass.material.set_shader_parameter("enabled",effects);ship.set_display_effects(effects)
			for frame in range(8):await process_frame
			var samples: Array=[]
			for sample in range(3):
				for frame in range(4):await process_frame
				budget.refresh();samples.append(selection())
			await RenderingServer.frame_post_draw
			var name: String=str(view.id)+"_installed"+("_normal"if effects else"_effects_off")+".png"
			var path: String=OUT+"/"+name;var photo: Image=main.post_view.get_texture().get_image();assert(photo.save_png(path)==OK)
			var row: Dictionary={"view":view.id,"file":name,"sha256":FileAccess.get_sha256(path),"effects":effects,"installed":true,"feature_root_path":str(feature_root.get_path()),"requested_eye":vec(view.eye),"requested_target":vec(view.target),"actual_eye":vec(actor.camera.global_position),"actual_camera_forward":vec(-actor.camera.global_basis.z),"actual_actor_position":vec(actor.global_position),"actor_yaw":actor.rotation.y,"camera_pitch":actor.camera.rotation.x,"fov":actor.camera.fov,"eye_delta_m":actor.camera.global_position.distance_to(view.eye),"selection_samples":samples,"capture_selection":selection(),"required_primary_names":view.required,"primary_selection_satisfied":required_selected(samples,view.required),"render_adapter":RenderingServer.get_video_adapter_name(),"world_resolution":[main.world_view.size.x,main.world_view.size.y],"image_resolution":[photo.get_width(),photo.get_height()],"focused_gallery_receipt_sha256":focused_sha,"external_focused_physical_and_source_check":true,"geometry_checks_run_here":false,"visual_first_pass_complete":false,"visual_acceptance":false,"final_acceptance":false,"scene_saved":false,"view_scope":view.scope}
			captures.append(row);save_json(path+".caption.json",row);save_json(OUT+"/CAPTURES.json",{"status":"ACTUAL_INSTALLED_CAPTURE_IN_PROGRESS","captures":captures,"focused_gallery_receipt_sha256":focused_sha})
	save_json(OUT+"/RESULT.json",{"status":"INSTALLED_NATIVE_CAPTURE_COMPLETE_PENDING_VISUAL_REVIEW","captures":captures,"capture_count":captures.size(),"focused_gallery_receipt_sha256":focused_sha,"feature_root_path":str(feature_root.get_path()),"budget":budget.shadow_source_budget,"candidate_limit":budget.MAX_VISIBILITY_CANDIDATES,"candidate_models_created":false,"imports_run":false,"geometry_checks_run_here":false,"baseline_replacement_toggles":false,"full_suite":false,"scene_saved":false})
	print("INSTALLED_POOL_CONNECTED_GALLERY_CAPTURE_COMPLETE: six actual installed images; visual first pass remains incomplete")
	main.queue_free();await process_frame;quit(0)
