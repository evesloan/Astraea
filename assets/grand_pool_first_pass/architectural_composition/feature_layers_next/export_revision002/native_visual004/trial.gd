extends SceneTree
# VISUAL STUDY ONLY: UNVERIFIED_IMPORT_EQUIVALENCE. No geometry/physical/final acceptance.
const PREP := "/workspace/scratch/375c2e438292/pool-feature-VISUAL_STUDY004/"
const INPUT := PREP+"NATIVE_INPUTS.json"
const OUT := PREP+"output"
var ship: Node3D
var actor: CharacterBody3D
var budget: Node
var physical_space: PhysicsDirectSpaceState3D
var candidate: Node3D
var audit: RefCounted
var data: Dictionary
var architecture: Dictionary
var imported: Array=[]
var lights: Array[SpotLight3D]=[]
var bodies: Array[StaticBody3D]=[]
var shape_nodes: Array[CollisionShape3D]=[]
var sparse: Array[Node3D]=[]
var preserved_plants: Array=[]
var light_markers: Dictionary={}
var root_markers: Array=[]
var physical_records: Array=[]
var optical_records: Array=[]
var route_records: Array=[]
var view_records: Array=[]
var old_ray_records: Array=[]
var captures: Array=[]
var material_records: Array=[]
var original_light_state: Dictionary={}
var original_source_count: int
var placement_records: Array=[]
var hardware_meshes: Array[MeshInstance3D]=[]
var hardware_foliage_checks: Array=[]
var candidate_on: bool=false
var post_draw_arrays_saved: bool=false
const LABEL := "UNVERIFIED_IMPORT_EQUIVALENCE"
func v3(a: Array) -> Vector3:return Vector3(a[0],a[1],a[2])

func vec(p: Vector3) -> Array:return [p.x,p.y,p.z]

func _initialize() -> void:call_deferred("run")

func save_json(path: String,value: Dictionary) -> void:
	value["verification"]=LABEL;value["installed"]=false;value["geometry_acceptance"]=false;value["physical_acceptance"]=false;value["final_acceptance"]=false
	var file:=FileAccess.open(path,FileAccess.WRITE);assert(file!=null)
	file.store_string(JSON.stringify(value,"  ",true,true));file.close()

func state(light: Light3D) -> Dictionary:
	return {"position":vec(light.global_position),"direction":vec(-light.global_basis.z),"color":[light.light_color.r,light.light_color.g,light.light_color.b],"energy":light.light_energy,"range":light.spot_range if light is SpotLight3D else 0.0,"angle":light.spot_angle if light is SpotLight3D else 0.0}

func build_candidate() -> void:
	candidate=Node3D.new();candidate.name="GrandPoolFeatures_UninstalledTrial";ship.get_node("ShipSpace").add_child(candidate)
	assert(candidate.global_transform==Transform3D.IDENTITY)
	var native_dir: String=OUT+"/native_arrays";assert(DirAccess.make_dir_recursive_absolute(native_dir)==OK)
	audit=load(PREP+"visual_import.gd").new()
	var built: Node3D=ship.find_child("GrandPoolArchitecture_WIP",true,false)
	var hardware_parts: int=0;var hardware_batches: int=0;var native_triangles: int=0
	for asset in data.assets:
		var item: Dictionary=audit.load_checked(asset,candidate,native_dir)
		imported.append(item);material_records.append({"asset":asset.name,"materials":item.materials,"actual_generated_node_mapping":item.node_mapping})
		native_triangles+=int(item.triangles)
		if asset.family=="plant":
			var root: Node3D=item.nodes[str(asset.name)]
			var e: Dictionary=item.extras[str(asset.name)]
			var old: Node3D=built.get_node(NodePath(str(e.placement_name)))
			var placement: Dictionary={}
			for row in data.replacement.assets:
				if str(row.instance)==str(e.placement_name):placement=row
			assert(not placement.is_empty() and old.visible and old.scale.is_equal_approx(Vector3.ONE))
			assert(old.position==v3(placement.position_xyz) and absf(old.rotation.y-float(placement.yaw_radians))<0.000001)
			assert(root.position==Vector3.ZERO and root.basis==Basis.IDENTITY)
			# Exact original instance transform, same parent frame and unit scale.
			item.root.transform=old.transform
			assert(item.root.global_transform==old.global_transform)
			var placed_nodes: Array=[]
			for placed_name in item.nodes:
				var placed: Node3D=item.nodes[placed_name]
				placed_nodes.append({"name":placed_name,"local_transform":audit.matrix(placed.transform),"actual_world_transform":audit.matrix(placed.global_transform)})
			save_json(native_dir+"/"+str(asset.name)+"_PLACED_TRANSFORMS.json",{"asset":asset.name,"nodes":placed_nodes})
			placement_records.append({"instance":e.placement_name,"old_transform":audit.matrix(old.global_transform),"candidate_transform":audit.matrix(item.root.global_transform),"unit_scale":vec(item.root.scale),"source_asset":asset.name,"source_support":e.support,"original_instance_preserved":true})
			sparse.append(old);preserved_plants.append({"node":old,"transform":old.global_transform,"visible":old.visible,"kind":"middle_sparse"})
			for name in item.nodes:
				var node: Node3D=item.nodes[name];var extra: Dictionary=item.extras[name]
				if node is MeshInstance3D:
					assert(str(extra.collision)=="decorative_noncolliding" and bool(extra.cast_shadow))
					assert(node.find_children("*","CollisionObject3D",true,false).is_empty())
				elif extra.get("marker_kind","")=="soil_contact":
					root_markers.append({"node":node,"asset":asset.name,"part":extra.physical_part,"support":str(e.support),"placement":e.placement_name})
		else:
			assert(asset.family=="light")
			for name in item.nodes:
				var node: Node3D=item.nodes[name];var e: Dictionary=item.extras[name]
				if node is MeshInstance3D:
					var names: Array=JSON.parse_string(str(e.source_part_names));hardware_parts+=names.size();hardware_batches+=1
					hardware_meshes.append(node)
					if not bool(e.cast_shadow):node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
					if str(e.collision_contract)=="concave_static_surface":
						var body:=StaticBody3D.new();body.name="TrialStaticContact";node.add_child(body)
						var shape:=CollisionShape3D.new();shape.shape=node.mesh.create_trimesh_shape();body.add_child(shape);bodies.append(body);shape_nodes.append(shape)
					else:assert(str(e.collision_contract)=="visual_lens_no_contact" and not bool(e.cast_shadow))
				else:
					assert(str(name).begins_with("DATUM_finish_light_"))
					var light:=SpotLight3D.new();light.name=("PoolUninstalledFeature_"+str(name)).validate_node_name();candidate.add_child(light);light.global_position=node.global_position
					light.look_at(light.global_position+v3(e.direction_godot_xyz).normalized(),Vector3.UP)
					ship.apply_light_profile(light,str(e.profile));light.light_energy=float(e.suggested_energy);light.spot_range=float(e.suggested_range_m);light.spot_angle=float(e.suggested_spot_angle_degrees)
					light.set_meta("source_marker",str(name));light.set_meta("physical_housing",str(e.physical_housing));light.set_meta("physical_receiver_xyz",v3(e.receiver_godot_xyz));light.set_meta("illumination_anchor",v3(e.visibility_sample_godot_xyz));light.set_meta("fixture_powered",false)
					light.shadow_enabled=false;light.visible=false;budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true;lights.append(light);light_markers[str(name)]=light
	for row in data.replacement.six_basal_instances_retained:
		var node: Node3D=built.get_node(NodePath(str(row.name)))
		assert(node.position==v3(row.position_xyz) and absf(node.rotation.y-float(row.yaw_radians))<0.000001 and node.scale.is_equal_approx(Vector3.ONE) and node.visible)
		preserved_plants.append({"node":node,"transform":node.global_transform,"visible":node.visible,"kind":"basal"})
	assert(hardware_parts==12 and hardware_batches==3 and bodies.size()==2 and lights.size()==3)
	assert(sparse.size()==6 and root_markers.size()==30 and preserved_plants.size()==12)
	assert(audit.all_meshes.size()==33 and native_triangles==42540 and budget.sources.size()==original_source_count+3)
	for hardware in hardware_meshes:
		var hardware_bounds: AABB=hardware.global_transform*hardware.get_aabb()
		for plant in audit.plant_meshes:
			var plant_bounds: AABB=plant.global_transform*plant.get_aabb()
			var disjoint: bool=not hardware_bounds.intersects(plant_bounds)
			hardware_foliage_checks.append({"hardware":str(hardware.get_path()),"plant":str(plant.get_path()),"actual_transformed_native_bounds_disjoint":disjoint,"acceptance":"PENDING_NOT_A_GATE"})
	save_json(OUT+"/ACTUAL_NATIVE_COMPOSITION_UNVERIFIED.json",{"status":"UNVERIFIED_IMPORT_EQUIVALENCE","installed":false,"production_changes":false,"source_equivalence_is_separate":true,"assets":data.assets,"surfaces":audit.records,"materials":material_records,"placements":placement_records,"hardware_foliage":hardware_foliage_checks,"triangles":native_triangles,"raw_matching":"PENDING_NOT_RUN","physical_checks":"PENDING_NOT_RUN","source_marker_node_mapping":"Actual generated-tree exact validated-name/hierarchy bijection plus GLTF mesh resource identity; no post-conversion state scene pointers","rendered_pictures_yet":false})

func set_candidate(enabled: bool) -> void:
	candidate_on=enabled;candidate.visible=enabled
	for node in sparse:node.visible=not enabled
	for shape in shape_nodes:shape.set_deferred("disabled",not enabled)
	for light in lights:light.set_meta("fixture_powered",enabled)
	budget.refresh()

func selection() -> Dictionary:
	var selected: Array=[];var proposed: Array=[]
	for light in budget.sources:
		if not budget.requested_shadow[light.get_instance_id()]:continue
		assert(light.visible==light.shadow_enabled)
		if light.visible:assert(budget._has_visible_sample(light));selected.append(str(light.get_path()))
	for light in lights:
		proposed.append({"name":str(light.name),"selected":light.visible,"shadow_enabled":light.shadow_enabled,"receiver_visible":budget._has_visible_sample(light),"position":vec(light.global_position),"energy":light.light_energy,"range":light.spot_range,"angle":light.spot_angle,"observer_distance":actor.global_position.distance_to(light.global_position)})
	assert(selected.size()<=8 and budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
	return {"selected":selected,"proposed":proposed,"budget":budget.shadow_source_budget,"candidate_limit":budget.MAX_VISIBILITY_CANDIDATES}

func verify_preserved_plants() -> void:
	for row in preserved_plants:
		assert(row.node.global_transform==row.transform)
		var expected_visible: bool=bool(row.visible) if row.kind=="basal" else not candidate_on
		assert(row.node.visible==expected_visible)
		assert(row.node.find_children("*","CollisionObject3D",true,false).is_empty())

func run() -> void:
	assert(OS.get_environment("ASTRAEA_POOL_NATIVE_TRIAL_RUN")=="parent_guarded_unsaved")
	var frozen: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PREP+"FINAL_CURRENT_FREEZE.json"))
	assert(FileAccess.get_sha256(INPUT)==str(frozen.native_inputs_sha256))
	assert(FileAccess.get_sha256(PREP+"trial.gd")==str(frozen.prepared_files["trial.gd"]))
	assert(FileAccess.get_sha256(PREP+"visual_import.gd")==str(frozen.prepared_files["visual_import.gd"]))
	data=JSON.parse_string(FileAccess.get_file_as_string(INPUT))
	for path in data.pins:assert(FileAccess.get_sha256(path)==str(data.pins[path]),"Pinned retained/export input changed")
	var engine: Dictionary=Engine.get_version_info();assert(int(engine.major)==4 and int(engine.minor)==6 and int(engine.patch)==3)
	assert(not DirAccess.dir_exists_absolute(OUT));assert(DirAccess.make_dir_recursive_absolute(OUT)==OK)
	architecture=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GRAND_POOL_ARCHITECTURE_RUNTIME.json"))
	var main: Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(30):await physics_frame
	ship=main.get_node("World360/Astraea");actor=ship.get_node("ShipSpace/PersistentActors/Player");budget=ship.get_node("ShipSystems/LocalShadowSourceBudget");physical_space=ship.get_world_3d().direct_space_state
	assert(budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
	assert(budget.get_script().resource_path=="res://scripts/lighting_budget.gd")
	original_source_count=budget.sources.size()
	for light in budget.sources:original_light_state[str(light.get_instance_id())]=state(light)
	actor.set_physics_process(false);actor.set_controls_enabled(false)
	build_candidate();set_candidate(true)
	for frame in range(3):await physics_frame
	verify_preserved_plants()
	save_json(OUT+"/PENDING_ACCEPTANCE_DIAGNOSTICS.json",{"status":LABEL,"strict_matcher":"NOT_RUN_IN_VISUAL_STUDY; actual graphical arrays/materials/transforms dumped before checks","native_physical_contacts":"PENDING; old source-part-dependent gate is not called","native_optical_receiver_interceptions":"PENDING","source_only_optical_result":{"clear":29,"leaf_interception":1},"prior003_failure":"Native triangle matcher assertion; preserved separately, no model-defect conclusion","normal_tangent_packing_hypothesis":"Graphical vs headless packing may differ; hypothesis only. Actual tangent slots and format flags dumped.","controller_changes":false,"full_suite":false})
	var views: Array=[
		{"id":"wet_loggia","eye":Vector3(-45.9,47.85,-438),"target":Vector3(-52,48.45,-442.2),"required":["PoolUninstalledFeature_DATUM_finish_light_ArchTimber_ForeL","PoolUninstalledFeature_DATUM_finish_light_ArchTimber_ForeR"]},
		{"id":"fore_focal","eye":Vector3(-31,47.85,-458.5),"target":Vector3(-31,48.65,-465.5),"required":["PoolUninstalledFeature_DATUM_finish_light_ArchFocal_Crown"]},
		{"id":"long_view","eye":Vector3(-20.5,47.85,-405),"target":Vector3(-20.5,48.15,-415),"required":[]},
		{"id":"seated_view","eye":Vector3(-51.65,47.44,-442.2),"target":Vector3(-31,47.7,-433),"required":[]}
	]
	var primary_pass: bool=true
	for view in views:
		actor.global_position=Vector3(view.eye.x,46.2,view.eye.z);actor.camera.position.y=view.eye.y-46.2;actor.velocity=Vector3.ZERO
		var direction: Vector3=view.target-view.eye;actor.rotation.y=atan2(-direction.x,-direction.z);actor.pitch=atan2(direction.y,Vector2(direction.x,direction.z).length());actor.camera.rotation.x=actor.pitch
		assert(actor.camera.global_position.distance_to(view.eye)<.0001 and actor.camera.fov==72.0)
		for enabled in [false,true]:
			set_candidate(enabled)
			for frame in range(3):await physics_frame
			for frame in range(12):await process_frame
			for shape in shape_nodes:assert(shape.disabled==not enabled)
			verify_preserved_plants()
			var samples: Array=[]
			for sample in range(3):
				for frame in range(4):await process_frame
				budget.refresh();samples.append(selection())
			var primary_selection: bool=true
			if enabled:
				for required in view.required:
					for sample in samples:
						var found: bool=false
						for item in sample.proposed:
							if item.name==required and item.selected:found=true
						primary_selection=primary_selection and found
			primary_pass=primary_pass and primary_selection
			for effects in [true,false]:
				main.set_world_resolution(0 if effects else 2);main.effects=effects;main.post_pass.material.set_shader_parameter("enabled",effects);ship.set_display_effects(effects)
				for frame in range(8):await process_frame
				budget.refresh();await RenderingServer.frame_post_draw
				var name: String=LABEL+"_"+str(view.id)+("_trial"if enabled else"_baseline")+("_native"if effects else"_clear")+".png"
				var path: String=OUT+"/"+name;var capture: Image=main.post_view.get_texture().get_image();assert(capture.save_png(path)==OK)
				if enabled and not post_draw_arrays_saved:
					audit.dump_after_first_draw(OUT+"/after_first_candidate_draw");post_draw_arrays_saved=true
				captures.append({"view":view.id,"file":name,"sha256":FileAccess.get_sha256(path),"candidate_enabled":enabled,"effects":effects,"eye":vec(view.eye),"target":vec(view.target),"selection_samples":samples,"capture_selection":selection(),"required_primary_names":view.required,"primary_selection_satisfied":primary_selection,"adapter":RenderingServer.get_video_adapter_name(),"resolution":[main.world_view.size.x,main.world_view.size.y],"receiver_pixels":pixel_samples(capture,main.world_view.size),"verification":LABEL,"geometry_acceptance":false,"physical_acceptance":false,"final_acceptance":false,"installed":false,"production_changes":false,"visual_acceptance":false,"seated_scope":"Static original eye diagnostic; no sitting-controller claim"if view.id=="seated_view"else"Original ordinary supported route eye"})
				save_json(path+".caption.json",captures.back())
				save_json(OUT+"/CAPTURES.json",{"installed":false,"production_changes":false,"captures":captures})
	set_candidate(false)
	for frame in range(3):await physics_frame
	verify_preserved_plants()
	for light in budget.sources:
		var key: String=str(light.get_instance_id())
		if original_light_state.has(key):assert(state(light)==original_light_state[key],"Retained fixture properties changed")
	assert(budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
	save_json(OUT+"/RESULT.json",{"status":"VISUAL_STUDY_CAPTURE_COMPLETE_UNVERIFIED_IMPORT_EQUIVALENCE","verification":LABEL,"installed":false,"production_changes":false,"geometry_acceptance":false,"physical_acceptance":false,"final_acceptance":false,"strict_matcher":"PENDING","physical_checks":"PENDING","primary_selection_satisfied":primary_pass,"hardware_parts":12,"native_mesh_batches_observed":audit.all_meshes.size(),"source_backed_lights":3,"fuller_plant_instances":6,"sparse_instances_preserved_and_restored":6,"basal_instances_unchanged":6,"root_soil_contacts":"NOT_TESTED_NATIVE","native_optical_leaf_interceptions":"NOT_TESTED_NATIVE","source_only_optical_leaf_interceptions":1,"old_source_count":original_source_count,"old_fixture_properties_unchanged":true,"budget":8,"candidate_limit":32,"captures":captures,"visual_acceptance":false,"full_suite":false,"no_saved_scene":true})
	print("VISUAL_STUDY004_COMPLETE_UNVERIFIED_IMPORT_EQUIVALENCE: sixteen paired images, native asset and physical acceptance pending, uninstalled")
	main.queue_free();await process_frame;quit(0)

func pixel_samples(image: Image,viewport: Vector2i) -> Array:
	var result: Array=[]
	for sample in data.receiver_samples:
		var target: Vector3=v3(sample.target_xyz);var screen: Vector2=actor.camera.unproject_position(target)
		var on_screen: bool=not actor.camera.is_position_behind(target) and Rect2(Vector2.ZERO,Vector2(viewport)).has_point(screen)
		var light: SpotLight3D=light_markers[str(sample.fixture)]
		var row: Dictionary={"sample":sample.sample_name,"target_xyz":sample.target_xyz,"on_screen":on_screen,"candidate_enabled":candidate_on,"source_only_classification":sample.classification,"source_light_selected":light.visible,"source_light_shadow_enabled":light.shadow_enabled,"native_leaf_shadow":"UNVERIFIED","native_collider_receiver":"NOT_TESTED","verification":LABEL,"geometry_acceptance":false,"physical_acceptance":false}
		if on_screen:
			var px: Vector2i=Vector2i(screen*Vector2(image.get_size())/Vector2(viewport));var color:=Color(0,0,0,0);var count: int=0
			for y in range(maxi(0,px.y-1),mini(image.get_height(),px.y+2)):
				for x in range(maxi(0,px.x-1),mini(image.get_width(),px.x+2)):color+=image.get_pixel(x,y);count+=1
			color/=float(count);row["pixel_xy"]=[px.x,px.y];row["mean_3x3_rgb"]=[color.r,color.g,color.b]
		result.append(row)
	return result
