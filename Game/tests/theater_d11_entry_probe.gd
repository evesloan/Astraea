extends RefCounted
# Independent source-resource, transform and collider assertions. Never repairs the scene.
const CONTRACT: String="res://data/architecture/THEATER_D11_MAIN_ENTRY023.json"
const CONTACT_HELPER=preload("res://tests/court_a_aimed_optic_probe.gd")
const RAW=preload("res://scripts/court_a_increment004.gd")

static func xyz(a: Array) -> Vector3:return Vector3(float(a[0]),float(a[1]),float(a[2]))
static func relative(node: Node3D,ancestor: Node3D) -> Transform3D:return CONTACT_HELPER.relative(node,ancestor)
static func same(actual: Transform3D,expected: Transform3D) -> void:CONTACT_HELPER.same_transform(actual,expected)
static func get_door(ship: Node3D) -> Node3D:
	return ship.get_node("ShipSpace/Districts/GrandLanternTheater_ConnectedStaticStage_WIP/TheaterUnpoweredDoorLiftAssemblies/D11MainEntrance")as Node3D
static func contract() -> Dictionary:
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.schema=="astraea.theater.d11.main_entry023" and data.groups.size()==2)
	assert(data.persistent_id=="THEATER_D11_MAIN_ENTRY" and float(data.travel_m)==2.65 and float(data.maximum_leaf_speed_m_s)==1.0)
	assert(data.retained_inactive_groups.size()==37 and data.source_chairs_preserved==2200)
	for path in data.protected_runtime_sha256:assert(FileAccess.get_sha256("res://"+str(path))==str(data.protected_runtime_sha256[path]))
	return data
static func check_active_group(ship: Node3D,node: Node3D,original: Node3D,template: Node3D) -> void:
	var door: Node3D=get_door(ship)
	var data: Dictionary=contract()
	var index: int=-1
	for i in range(2):
		if str(data.groups[i].node)==str(node.name):index=i
	assert(index>=0)
	var record: Dictionary=data.groups[index]
	var body: AnimatableBody3D=node.get_parent()as AnimatableBody3D
	assert(body!=null and body.get_parent()==door and str(body.name)==str(record.body_name) and body.sync_to_physics)
	assert(body.collision_layer==1 and body.collision_mask==1)
	assert(node.get_meta("operation_enabled")==true and not node.has_meta("locked_pose_fraction") and not node.has_method("interact"))
	assert(node.find_children("*","Area3D",true,false).is_empty())
	same(node.transform,Transform3D.IDENTITY)
	var fraction: float=clampf(float(door.open_fraction)/.85,0.,1.)if index==0 else clampf((float(door.open_fraction)-.15)/.85,0.,1.)
	assert(float(node.get_meta("current_pose_fraction"))==fraction)
	var expected: Transform3D=relative(original,template)
	expected.origin+=xyz(record.axis)*float(data.travel_m)*fraction
	same(body.transform,expected)
	var contacts: Dictionary=door.source_contacts
	var count: int=0
	var triangles: int=0
	for name in record.mesh_nodes:
		var actual: MeshInstance3D=node.find_child(str(name),true,false)as MeshInstance3D
		var source: MeshInstance3D=original.find_child(str(name),true,false)as MeshInstance3D
		assert(actual!=null and source!=null and actual.mesh==source.mesh and actual.visible==source.visible)
		same(relative(actual,node),relative(source,original))
		assert(actual.material_override==source.material_override and actual.material_overlay==source.material_overlay and actual.cast_shadow==source.cast_shadow and actual.layers==source.layers)
		assert(actual.find_children("*","CollisionObject3D",true,false).is_empty())
		assert(contacts.has(str(name)))
		var shape: CollisionShape3D=body.get_node(str(name)+"_RetainedContact")as CollisionShape3D
		assert(shape!=null and shape==contacts[str(name)].shape and not shape.disabled)
		assert(shape.shape==contacts[str(name)].original_shape_resource and shape.shape is ConcavePolygonShape3D)
		assert(absf(shape.shape.margin-.001)<.000001)
		same(shape.transform,relative(source,original))
		assert(shape.shape.get_faces().to_byte_array()==source.mesh.get_faces().to_byte_array())
		assert(shape.shape.get_faces().to_byte_array()==contacts[str(name)].faces.to_byte_array())
		triangles+=shape.shape.get_faces().size()/3
		count+=1
	assert(count==3 and triangles==int(record.triangles))
	assert(body.find_children("*","CollisionShape3D",true,false).size()==3)
static func check_installation(ship: Node3D) -> void:
	var data: Dictionary=contract()
	var door: Node3D=get_door(ship)
	assert(str(door.persistent_id)==str(data.persistent_id) and door.leaves.size()==2 and door.source_contacts.size()==6)
	assert(door.get_script().get_base_script()==load("res://scripts/service_door.gd"))
	assert(door.get_meta("only_D11_main_entry_enabled") and not door.get_meta("save_acceptance"))
	var motion: Node3D=door.get_parent()as Node3D
	same(door.transform,Transform3D.IDENTITY)
	var original: Node3D=(load(str(data.original_moving_asset))as PackedScene).instantiate()as Node3D
	for record in data.groups:
		check_active_group(ship,motion.find_child(str(record.node),true,false),original.find_child(str(record.node),true,false),original)
	original.free()
	assert(motion.find_children("*","MeshInstance3D",true,false).size()==120)
	var venue: Node3D=motion.get_parent()as Node3D
	var call: Node3D=venue.get_node("D11MainExteriorCall")as Node3D
	assert(call.get_parent()==venue and call.find_children("*","MeshInstance3D",true,false).size()==2)
	assert(call.find_children("*","Light3D",true,false).is_empty())
	var path: String=str(data.exterior_call.asset_path)
	assert(FileAccess.get_sha256(path)==str(data.exterior_call.asset_sha256))
	var policy: ConfigFile=ConfigFile.new();assert(policy.load(path+".import")==OK)
	assert(policy.get_value("params","meshes/force_disable_compression",false))
	assert(not policy.get_value("params","meshes/generate_lods",true) and not policy.get_value("params","meshes/create_shadow_meshes",true))
	assert(int(policy.get_value("params","gltf/embedded_image_handling",-1))==3)
	var cache: String=str(policy.get_value("remap","path",""));var stamp: ConfigFile=ConfigFile.new()
	assert(not cache.is_empty() and stamp.load(cache.get_basename()+".md5")==OK and stamp.get_value("","source_md5","")==FileAccess.get_md5(path))
	var template: Node3D=(load(path)as PackedScene).instantiate()as Node3D
	same(call.transform,template.transform)
	for name in data.exterior_call.mesh_nodes:
		var actual: MeshInstance3D=call.find_child(str(name),true,false)as MeshInstance3D
		var source: MeshInstance3D=template.find_child(str(name),true,false)as MeshInstance3D
		assert(actual!=null and source!=null and actual.mesh==source.mesh)
		same(relative(actual,call),relative(source,template))
		assert(RAW.raw_faces(actual.mesh).size()==36)
		CONTACT_HELPER.contact(actual,RAW.raw_faces(source.mesh))
		var low: Vector3=Vector3(INF,INF,INF);var high: Vector3=-low
		for vertex in RAW.raw_faces(actual.mesh):
			var world: Vector3=actual.global_transform*vertex
			low=low.min(world);high=high.max(world)
		var matches: int=0
		for record in data.exterior_call.parts:
			if str(record.node)!=str(name):continue
			matches+=1
			assert(low.distance_to(xyz(record.bounds_native[0]))<.00002 and high.distance_to(xyz(record.bounds_native[1]))<.00002)
		assert(matches==1)
	template.free()
	assert(door.find_children("*","Area3D",true,false).size()==2)
	for control in data.controls:
		var area: Area3D=door.get_node(str(control.id))as Area3D
		assert(area!=null and not area.monitoring and area.collision_layer==1 and area.collision_mask==0)
		assert(area.global_position.distance_to(xyz(control.target_native))<.00002)
		assert(area.get_child_count()==1 and area.get_child(0)is CollisionShape3D)
		var shape: CollisionShape3D=area.get_child(0)as CollisionShape3D
		assert(shape.shape is BoxShape3D and not shape.disabled and shape.shape.size==xyz(control.target_box_size))
		assert(area.get_meta("physical_control_source")==str(control.physical_source))
	assert(venue.find_children("*","Light3D",true,false).size()==139)

static func check_external_geometry(ship: Node3D) -> Dictionary:
	var data: Dictionary=contract()
	var path: String=str(data.exterior_call.asset_path)
	var raw: PackedByteArray=FileAccess.get_file_as_bytes(path)
	assert(raw.decode_u32(0)==0x46546c67 and raw.decode_u32(4)==2 and raw.decode_u32(8)==raw.size())
	var length: int=raw.decode_u32(12)
	var doc: Dictionary=JSON.parse_string(raw.slice(20,20+length).get_string_from_utf8())
	assert(raw.decode_u32(16)==0x4e4f534a and raw.decode_u32(24+length)==0x004e4942)
	var bin: PackedByteArray=raw.slice(28+length)
	var helper=load("res://tests/pool_feature_geometry.gd").new()
	var call: Node3D=get_door(ship).get_parent().get_parent().get_node("D11MainExteriorCall")as Node3D
	var rows: Array=[]
	var triangles: int=0
	for node in doc.nodes:
		if not node.has("mesh"):continue
		var mesh: MeshInstance3D=call.find_child(str(node.name).validate_node_name(),true,false)as MeshInstance3D
		assert(mesh!=null and mesh.mesh.get_surface_count()==1 and mesh.material_override==null and mesh.material_overlay==null)
		var primitive: Dictionary=doc.meshes[int(node.mesh)].primitives[0]
		var provenance: Dictionary={}
		for i in range(12):provenance[str(i)]={"source_part":str(node.name),"source_triangle":i}
		helper.audit_surface(mesh,0,primitive,doc,bin,provenance,{"name":"D11_EXTERNAL_CALL"},"")
		triangles+=int(helper.records.back().triangles)
		var material: StandardMaterial3D=mesh.get_active_material(0)as StandardMaterial3D
		var gm: Dictionary=doc.materials[int(primitive.material)]
		var pbr: Dictionary=gm.get("pbrMetallicRoughness",{})
		assert(material!=null and material==mesh.mesh.surface_get_material(0) and mesh.get_surface_override_material(0)==null)
		assert(material.resource_name==str(gm.name) and material.transparency==BaseMaterial3D.TRANSPARENCY_DISABLED)
		assert(material.metallic==PackedFloat32Array([pbr.get("metallicFactor",1)])[0] and material.roughness==PackedFloat32Array([pbr.get("roughnessFactor",1)])[0])
		var c: Array=pbr.get("baseColorFactor",[1,1,1,1])
		assert(material.albedo_color==Color(c[0],c[1],c[2],c[3]).linear_to_srgb())
		assert(material.cull_mode==(BaseMaterial3D.CULL_DISABLED if gm.get("doubleSided",false)else BaseMaterial3D.CULL_BACK))
		var textures: Array=[]
		if pbr.has("baseColorTexture"):
			textures.append(helper.texture_check(material.albedo_texture,doc,bin,pbr.baseColorTexture))
			var ref: Dictionary=pbr.baseColorTexture
			assert(int(ref.get("texCoord",0))==0 and not ref.has("extensions"))
			var texture: Dictionary=doc.textures[int(ref.index)]
			var sampler: Dictionary=doc.samplers[int(texture.sampler)]
			assert(int(sampler.magFilter)==9728 and int(sampler.minFilter)==9984,"Retained theater closest/nearest-mipmap sampler changed")
			assert(int(sampler.get("wrapS",10497))==10497 and int(sampler.get("wrapT",10497))==10497)
			assert(material.texture_filter==BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS and material.texture_repeat,"Native filter must match this exact theater source")
		else:assert(material.albedo_texture==null)
		if gm.has("emissiveFactor"):
			var ef: Array=gm.emissiveFactor
			assert(material.emission_enabled and material.emission==Color(ef[0],ef[1],ef[2]).linear_to_srgb())
			assert(material.emission_energy_multiplier==PackedFloat32Array([gm.get("extensions",{}).get("KHR_materials_emissive_strength",{}).get("emissiveStrength",1.0)])[0])
		else:assert(not material.emission_enabled)
		assert(material.uv1_scale==Vector3.ONE and material.uv1_offset==Vector3.ZERO)
		rows.append({"mesh":node.name,"material":gm.name,"textures":textures})
	assert(triangles==24 and rows.size()==2)
	return {"triangles":triangles,"raw_position_uv_and_normal_codec":helper.records,"materials":rows}
