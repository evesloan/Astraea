extends SceneTree
var sources:Array=[]
var contact_count:=0
func _initialize()->void:call_deferred("run")
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func add_model(world:Node3D,path:String,at:Vector3,yaw:float=0)->void:
	sources.append({"path":path,"sha256":FileAccess.get_sha256(path),"at":str(at),"yaw":yaw})
	var document:=GLTFDocument.new();var state:=GLTFState.new()
	assert(document.append_from_file(ProjectSettings.globalize_path(path),state)==OK)
	var model:Node3D=document.generate_scene(state);world.add_child(model);model.position=at;model.rotation.y=yaw
	for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
		if str(mesh.name) in ["LowerRail_Port","LowerRail_Starboard"]:continue # Intended wheel/rail interface tested separately; all fixed receivers remain.
		if not (mesh.global_transform*mesh.get_aabb()).intersects(AABB(Vector3(-30,-.6,-466),Vector3(42,13,80))):continue
		var body:=StaticBody3D.new();body.name=(path.get_file().get_basename()+"__"+str(mesh.name)).validate_node_name();var col:=CollisionShape3D.new()
		col.shape=mesh.mesh.create_trimesh_shape();body.add_child(col);world.add_child(body);body.global_transform=mesh.global_transform;contact_count+=1
	# Keep the actual source visuals for the same check's natural review capture.
func run()->void:
	var output:=""
	for arg:String in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.substr(9)
	var world:=Node3D.new();world.name="ExactForeMidCoreReceiving";root.add_child(world)
	add_model(world,"res://grand_arrivals_tram_20261026/r007/LowerDeparture.glb",Vector3.ZERO)
	add_model(world,"res://grand_arrivals_tram_20261026/r006/ArrivalsHallExit.glb",Vector3(-31,0,-432))
	add_model(world,"res://assets/models/AST-ARR-003.glb",Vector3(-30,0,-456))
	add_model(world,"res://assets/models/AST-ARR-004.glb",Vector3(-30,0,-456))
	var core:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/FORWARD_PUBLIC_CORE.json"))
	add_model(world,"res://grand_arrivals_tram_20261026/r007/ForwardGroundEnclosure.glb",vec(core.origin))
	for stair:Dictionary in core.stairs:
		if float(stair.base_y)>6:continue
		add_model(world,"res://assets/models/"+str(stair.file),vec(stair.origin),PI)
	# Lower bearings and the next intact deck are real source floors, not proxies.
	var regions:Array=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json")).regions
	var selected:Array=[]
	for region:Dictionary in regions:
		if region.id in ["D01_fore_route","D01_arrivals_ground","D01_forward_public_core_floor","D02_forward_public_core_floor"]:selected.append(region)
	var received:Array=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/received_structural_meshes.json")).regions
	for region:Dictionary in received:
		if region.id in ["D01_directory_02_authored_floor","D01_directory_02_spine_connection"]:selected.append(region)
	var mat:=StandardMaterial3D.new();load("res://scripts/structural_floor_builder.gd").build_regions(world,mat,mat,selected)
	# Original car, portals, trucks, four stocked cart bodies live in a separate
	# physics world. Their exact shapes are queried against the receiving world.
	var viewport:=SubViewport.new();viewport.own_world_3d=true;viewport.render_target_update_mode=SubViewport.UPDATE_DISABLED;root.add_child(viewport)
	var ship:=Node3D.new();viewport.add_child(ship);var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
	var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors);var districts:=Node3D.new();space.add_child(districts)
	var factory=load("res://tram_passenger_successor_20261024/assembly_initial_pose_r002.gd")
	var assembly:Node3D=factory.create(districts);var body:AnimatableBody3D=assembly.get_node("Group4OwnedTram_Source024")
	var cart:RigidBody3D=load("res://scripts/cleaning_cart.gd").new();cart.name="CustodialCart";cart.transform=body.global_transform*Transform3D(Basis.IDENTITY,Vector3(0,.025,.14));actors.add_child(cart);cart.freeze=true
	for stock:RigidBody3D in cart.products:stock.freeze=true
	var motor:Node3D=factory.attach_original_cart(assembly,cart);motor.set_physics_process(false)
	for i in 3:await physics_frame
	assert(cart.products.size()==4 and body.get_meta("exact_original_portal_contact_components",0)==18)
	var poses:Array=JSON.parse_string(FileAccess.get_file_as_string("res://grand_arrivals_tram_20261026/grade_r007/POSES.json"))
	var relevant:Array=[]
	for p:Array in poses:
		if p[11]<2 and p[2]<=-390:relevant.append(p)
	assert(relevant.size()>100)
	var exclusions:Array[RID]=[]
	var result:Dictionary=load("res://grand_arrivals_tram_20261026/grade_r007/component_sweep_diagnostic.gd").audit(ship,assembly,relevant,[relevant[0][0],relevant[-1][0]],exclusions,world.get_world_3d().direct_space_state)
	result.sources=sources;result.receiving_contacts=contact_count;result.source_cart_stock=4;result.pose_samples=relevant.size();result.selected=false
	result.scope="Original car/cart/closed-door/truck against lower station, hall, reception, forward core and original ground/threshold floors. Rail heads omitted only as intentional wheel contacts; wheel contact and live operation remain separate."
	root.size=Vector2i(1280,720)
	var env_node:=WorldEnvironment.new();var env:=Environment.new();env.background_mode=Environment.BG_COLOR;env.background_color=Color(.12,.13,.15);env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color(1,.95,.86);env.ambient_light_energy=.45;env_node.environment=env;world.add_child(env_node)
	var sun:=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-55,-25,0);sun.light_energy=.7;world.add_child(sun)
	var camera:=Camera3D.new();world.add_child(camera);camera.position=Vector3(-26,5,-438);camera.look_at(Vector3(-12,2,-450));camera.fov=75;camera.current=true
	for frame in 3:await process_frame
	await RenderingServer.frame_post_draw
	var picture:=output.get_base_dir().path_join("candidate_lower_station.png");assert(root.get_texture().get_image().save_png(picture)==OK)
	result.source_view={"path":picture,"camera":str(camera.global_position),"lighting":"Source review ambient/directional preview; not installed runtime lighting or visual acceptance","scope":"Actual unselected source hall/boarding/rail context, no operating train"}
	var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close();print(JSON.stringify(result));viewport.free();world.free();quit(0)
