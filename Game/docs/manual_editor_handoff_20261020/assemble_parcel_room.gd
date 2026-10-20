extends SceneTree
# One-room offline conversion only. Never invoke on project startup.
# Refuses to overwrite the manually owned scene. No ship bootstrap is loaded.
const OUT="res://docs/manual_editor_handoff_20261020/ParcelRoom_R064_Authored.tscn"
const HERE="res://docs/manual_editor_handoff_20261020/"
const KEY="SHOP_D09_S72_A080"
func _initialize()->void:
	call_deferred("run")
func surface(role:String)->StandardMaterial3D:
	var material:=StandardMaterial3D.new()
	material.albedo_color=Color.WHITE
	material.albedo_texture=load("res://assets/textures/"+role+".png")
	material.roughness=.83
	material.texture_filter=BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	return material
func own(node:Node,scene:Node)->void:
	if node!=scene:
		node.owner=scene
		node.scene_file_path=""
	for child in node.get_children():own(child,scene)
func run()->void:
	if FileAccess.file_exists(OUT):
		push_error("Refusing to overwrite manually owned authoring scene. Create a separate revision deliberately.")
		quit(2);return
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/SHOPPING_PROMENADE.json"))
	var completion:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/CONSTRUCTION.json"))
	var row:Dictionary={}
	for candidate in definition.chunks:
		if str(candidate.chunk_id)==KEY:row=candidate
	assert(not row.is_empty() and row.stable_room_id=="R064")
	for layer in row.layers.values():assert(FileAccess.get_sha256(layer.path)==layer.sha256)
	for revision in completion.fitout_revisions:assert(str(revision.chunk_id)!=KEY,"Selected baseline has an admitted successor; update conversion explicitly")
	var scene:=Node3D.new();scene.name=KEY;root.add_child(scene)
	scene.set_meta("source_chunk_id",KEY);scene.set_meta("stable_room_id","R064")
	scene.set_meta("production_placement",Vector3(72,52.5,80))
	scene.set_meta("authoring_status","Saved local room successor. NOT INSTALLED. Source lineage retained separately; do not regenerate over edits.")
	scene.set_meta("finished",false)
	var visual:Node3D=load(str(row.visual_scene)).instantiate()
	visual.name="SourceGeometry";scene.add_child(visual)
	var collidable:Array[Node]=[]
	var meshes:=visual.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==int(row.visual_mesh_count))
	for mesh in meshes:
		assert(definition.node_policy.has(str(mesh.name)))
		if bool(definition.node_policy[str(mesh.name)].collide):collidable.append(mesh)
	load("res://scripts/static_contact_cache.gd").attach_group(visual,collidable)
	# Keep the exact production slab generator and world-coordinate UVs. The
	# compensating frame places that one floor at the section-local origin.
	var floor_frame:=Node3D.new();floor_frame.name="Floor_SourceWorldFrame";floor_frame.position=-Vector3(72,52.5,80);scene.add_child(floor_frame)
	var regions:Array=[]
	for item in definition.floor_proposals:
		if str(item.chunk_id)!=KEY:continue
		var rings:Array=[item.boundary];rings.append_array(item.holes)
		regions.append({"id":item.id,"floor_y":item.floor_y,"thickness":item.thickness,"triangles":item.triangles_xz,"rings":rings,"render_chunks":item.render_chunks})
	assert(regions.size()==1)
	load("res://scripts/structural_floor_builder.gd").build_regions(floor_frame,surface("warm_stone"),surface("ivory_enamel"),regions,{},"OwnedFloor")
	var doors:=0
	for item in completion.doors:
		if str(item.chunk_id)!=KEY:continue
		assert(FileAccess.get_sha256(str(item.model_path))==str(item.model_sha256))
		assert(FileAccess.get_sha256("res://assets/models/group5/retail_door_control_r001.glb")==str(item.control_model_sha256))
		var door:=Node3D.new();door.name=str(item.local_name)
		door.set_script(load("res://scripts/group5_retail_slider.gd"))
		door.persistent_id=StringName(str(item.physical_id));door.width=float(item.width);door.height=float(item.height)
		door.model_path=str(item.model_path);door.controls=item.controls
		door.position=Vector3(item.local_xyz[0],item.local_xyz[1],item.local_xyz[2]);door.rotation.y=float(item.rotation_y)
		scene.add_child(door) # original _ready constructs the exact existing panels once
		assert(door.panels.size()==4)
		door.set_meta("authored_width",item.width);door.set_meta("authored_height",item.height)
		door.set_meta("source_model",item.model_path)
		door.set_script(load(HERE+"saved_retail_slider.gd"))
		doors+=1
	assert(doors==3)
	var lights:=0
	for spec in definition.lights:
		if str(spec.chunk_id)!=KEY:continue
		assert(spec.kind=="SpotLight3D")
		var light:=SpotLight3D.new();light.name=str(spec.id)
		light.position=Vector3(spec.local_xyz[0],spec.local_xyz[1],spec.local_xyz[2]);light.rotation_degrees.x=-90
		light.spot_range=minf(float(spec.range_m),8);light.spot_angle=float(spec.angle_deg)
		light.light_color=Color(spec.colour[0],spec.colour[1],spec.colour[2]);light.light_energy=float(spec.energy)
		light.visible=false;light.shadow_enabled=false
		light.set_meta("register_with_existing_source_budget_on_adoption",true)
		scene.add_child(light);lights+=1
	assert(lights==3)
	for sign in completion.wayfinding:assert(str(sign.chunk_id)!=KEY,"Selected section acquired wayfinding; include it deliberately")
	var additions:=Node3D.new();additions.name="ManualAdditions";scene.add_child(additions)
	own(scene,scene)
	var packed:=PackedScene.new();assert(packed.pack(scene)==OK)
	assert(ResourceSaver.save(packed,OUT,ResourceSaver.FLAG_BUNDLE_RESOURCES)==OK)
	print("PARCEL_AUTHORED_SAVED ",OUT," original_meshes=",meshes.size()," doors=",doors," lights=",lights)
	scene.free();quit()
