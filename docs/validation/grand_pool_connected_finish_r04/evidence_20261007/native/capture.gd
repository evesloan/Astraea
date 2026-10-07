extends SceneTree
# Actual installed scene only. No candidate import, geometry edits or acceptance gate.
var PREP: String
var OUT: String
var ship: Node3D
var actor: CharacterBody3D
var budget: Node
var feature_root: Node3D
var lights: Array[SpotLight3D]=[]
var captures: Array=[]
var focused_sha: String
func vec(p: Vector3) -> Array:return [p.x,p.y,p.z]
func _initialize() -> void:
	PREP=OS.get_environment("ASTRAEA_POOL_CAPTURE_PREP").trim_suffix("/")+"/"
	assert(PREP.begins_with("/workspace/"))
	OUT=PREP+"output"
	call_deferred("run")
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
	assert(OS.get_environment("ASTRAEA_INSTALLED_GALLERY_FINISH_CAPTURE")=="parent_approved")
	var freeze: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PREP+"FINAL_CURRENT_FREEZE.json"))
	for input in freeze.game_inputs:
		assert(FileAccess.get_sha256("res://"+str(input))==str(freeze.game_inputs[input]),"Capture input differs: "+str(input))
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
			var name: String=str(view.id)+"_finish_r04"+("_normal"if effects else"_effects_off")+".png"
			var path: String=OUT+"/"+name;var photo: Image=main.post_view.get_texture().get_image();assert(photo.save_png(path)==OK)
			var row: Dictionary={"view":view.id,"file":name,"sha256":FileAccess.get_sha256(path),"effects":effects,"installed":true,"feature_root_path":str(feature_root.get_path()),"requested_eye":vec(view.eye),"requested_target":vec(view.target),"actual_eye":vec(actor.camera.global_position),"actual_camera_forward":vec(-actor.camera.global_basis.z),"actual_actor_position":vec(actor.global_position),"actor_yaw":actor.rotation.y,"camera_pitch":actor.camera.rotation.x,"fov":actor.camera.fov,"eye_delta_m":actor.camera.global_position.distance_to(view.eye),"selection_samples":samples,"capture_selection":selection(),"required_primary_names":view.required,"primary_selection_satisfied":required_selected(samples,view.required),"render_adapter":RenderingServer.get_video_adapter_name(),"world_resolution":[main.world_view.size.x,main.world_view.size.y],"image_resolution":[photo.get_width(),photo.get_height()],"focused_gallery_receipt_sha256":focused_sha,"external_focused_physical_and_source_check":true,"geometry_checks_run_here":false,"visual_first_pass_complete":false,"visual_acceptance":false,"final_acceptance":false,"scene_saved":false,"view_scope":view.scope}
			captures.append(row);save_json(path+".caption.json",row);save_json(OUT+"/CAPTURES.json",{"status":"ACTUAL_INSTALLED_CAPTURE_IN_PROGRESS","captures":captures,"focused_gallery_receipt_sha256":focused_sha})
	var outside: Dictionary=await capture_outside_floor(main)
	for input in freeze.game_inputs:
		assert(FileAccess.get_sha256("res://"+str(input))==str(freeze.game_inputs[input]),"Capture changed source: "+str(input))
	save_json(OUT+"/RESULT.json",{"status":"INSTALLED_NATIVE_CAPTURE_COMPLETE_PENDING_VISUAL_REVIEW","outside_floor_comparison":outside,"captures":captures,"capture_count":captures.size(),"focused_gallery_receipt_sha256":focused_sha,"feature_root_path":str(feature_root.get_path()),"budget":budget.shadow_source_budget,"candidate_limit":budget.MAX_VISIBILITY_CANDIDATES,"candidate_models_created":false,"imports_run":false,"geometry_checks_run_here":false,"baseline_replacement_toggles":"outside_floor_material_only_unsaved_comparison","full_suite":false,"scene_saved":false})
	print("INSTALLED_POOL_CONNECTED_FINISH_CAPTURE_COMPLETE: six actual installed same-camera views plus original/new outside-floor comparison; visual first pass pending")
	main.queue_free();await process_frame;quit(0 if bool(outside.passed) else 2)

func capture_outside_floor(main: Node) -> Dictionary:
	var floor:=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms/D09_orchard_market_gallery") as Node3D
	var selected: Array=floor.get_meta("gallery_finish_selected")
	var before: Dictionary=floor.get_meta("gallery_finish_before")
	var finish: ShaderMaterial=floor.get_meta("gallery_finish_material")
	var eye:=Vector3(-14.6,54.15,-435.0);var target:=Vector3(-14.6,53.0,-430.0)
	actor.global_position=Vector3(eye.x,52.5,eye.z);actor.camera.position.y=eye.y-52.5;actor.velocity=Vector3.ZERO
	var direction:=target-eye;actor.rotation.y=atan2(-direction.x,-direction.z);actor.pitch=atan2(direction.y,Vector2(direction.x,direction.z).length());actor.camera.rotation.x=actor.pitch
	main.set_world_resolution(2);main.effects=false;main.post_pass.material.set_shader_parameter("enabled",false);ship.set_display_effects(false)
	for frame in range(4):await physics_frame
	for frame in range(16):await process_frame
	var images: Array[Image]=[];var receipts: Array=[]
	for enabled in [false,true]:
		for name in selected:
			var mesh:=floor.get_node(NodePath(str(name))) as MeshInstance3D
			mesh.set_surface_override_material(0,finish if enabled else before[name].override)
		for frame in range(12):await process_frame
		budget.refresh()
		await RenderingServer.frame_post_draw
		var photo: Image=main.post_view.get_texture().get_image();images.append(photo)
		var name: String="outside_floor_new_shader.png" if enabled else "outside_floor_original_standard_material.png"
		var path: String=OUT+"/"+name;assert(photo.save_png(path)==OK)
		receipts.append({"file":name,"sha256":FileAccess.get_sha256(path),"new_material_enabled":enabled,"eye":vec(actor.camera.global_position),"forward":vec(-actor.camera.global_basis.z),"selection":selection()})
	assert(images[0].get_size()==images[1].get_size())
	assert(receipts[0].selection==receipts[1].selection,"Outside comparison changed natural light selection")
	var points: Array=[];var pixels: Dictionary={};var mismatches: Array=[]
	var physics:=ship.get_world_3d().direct_space_state
	for ix in range(9):
		for iz in range(9):
			var point:=Vector3(-16.6+float(ix)*.32,52.5,-434.6+float(iz)*.3)
			var query:=PhysicsRayQueryParameters3D.create(actor.camera.global_position,point-Vector3.UP*.025,1)
			query.exclude=[actor.get_rid()];query.hit_back_faces=true
			var hit: Dictionary=physics.intersect_ray(query)
			if hit.is_empty() or not floor.is_ancestor_of(hit.collider):continue
			if actor.camera.is_position_behind(point):continue
			var screen: Vector2=actor.camera.unproject_position(point)
			var x:=int(round(screen.x));var y:=int(round(screen.y))
			if x<3 or y<3 or x>=images[0].get_width()-3 or y>=images[0].get_height()-3:continue
			points.append({"world":vec(point),"pixel":[x,y],"actual_first_hit_floor_owner":true})
			for dx in [-1,0,1]:
				for dy in [-1,0,1]:
					var key:=Vector2i(x+dx,y+dy)
					if pixels.has(key):continue
					pixels[key]=true
					var a: Color=images[0].get_pixel(key.x,key.y);var b: Color=images[1].get_pixel(key.x,key.y)
					if a!=b:mismatches.append({"pixel":[key.x,key.y],"original":[a.r,a.g,a.b,a.a],"new":[b.r,b.g,b.b,b.a]})
	for name in selected:
		assert(floor.get_node(NodePath(str(name))).get_surface_override_material(0)==finish)
	var result: Dictionary={"status":"PASS_OUTSIDE_FLOOR_NATIVE_PIXEL_PARITY" if mismatches.is_empty() and pixels.size()>=100 else "FAIL_OUTSIDE_FLOOR_NATIVE_PIXEL_PARITY","passed":mismatches.is_empty() and pixels.size()>=100,"files":receipts,"world_samples":points,"unique_floor_pixels":pixels.size(),"differing_pixels":mismatches.size(),"mismatches":mismatches,"comparison":"Actual original StandardMaterial surface overrides versus bounded successor shader outside exact finish rectangle","final_new_material_restored":true,"no_geometry_or_contact_changed":true,"scene_saved":false}
	save_json(OUT+"/OUTSIDE_FLOOR_COMPARISON.json",result)
	print(result.status," samples=",pixels.size()," differences=",mismatches.size())
	return result
