extends RefCounted
# One installed-area check. Reuses the already verified raw-array codec reader.
const CONTRACT := "res://data/architecture/GRAND_POOL_EAST_GALLERY_RUNTIME.json"
const REVIEWED_CONTRACT_SHA := "14aaaca21f264701cfe495f5064c5e493710cbf71d71628c3384b2b2555ac140"
var tree: SceneTree
var ship: Node3D
var area: Node3D
var actor: CharacterBody3D
var space: PhysicsDirectSpaceState3D
var data: Dictionary
var geo: RefCounted
var meshes: Dictionary = {}
var contacts: Array[RID] = []
var records: Dictionary = {"geometry":[],"floor_bearing":[],"soil":[],"routes":[],"views":[],"lights":[]}
func v3(a: Array) -> Vector3: return Vector3(a[0],a[1],a[2])
func vec(p: Vector3) -> Array: return [p.x,p.y,p.z]
func ray(a: Vector3,b: Vector3,extra: Array[RID]=[]) -> Dictionary:
	var q:=PhysicsRayQueryParameters3D.create(a,b,1)
	var exclusions: Array[RID]=[actor.get_rid()];exclusions.append_array(extra)
	q.exclude=exclusions;q.hit_back_faces=true
	return space.intersect_ray(q)
func raw_faces(mesh: MeshInstance3D) -> PackedVector3Array:
	var result:=PackedVector3Array()
	for si in range(mesh.mesh.get_surface_count()):
		var arrays: Array=mesh.mesh.surface_get_arrays(si)
		var p: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX];var ix: PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
		for i in ix:result.append(p[i])
	return result
func native_hit(mesh: MeshInstance3D,a: Vector3,b: Vector3) -> Variant:
	# The 0.1mm TriangleMesh grid is the actual collider representation, distinct
	# from uncompressed render arrays. Its own support prediction stays strict.
	var faces: PackedVector3Array=mesh.mesh.get_faces()
	var lo: Vector3=mesh.to_local(a);var hi: Vector3=mesh.to_local(b)
	var nearest: Variant=null;var distance:=INF
	for i in range(0,faces.size(),3):
		var hit: Variant=Geometry3D.segment_intersects_triangle(lo,hi,faces[i],faces[i+1],faces[i+2])
		if hit==null:continue
		var world: Vector3=mesh.to_global(hit);var value: float=a.distance_squared_to(world)
		if value<distance:distance=value;nearest=world
	return nearest
func clear_render_segment(a: Vector3,b: Vector3,except_name: String="") -> bool:
	for mesh in area.find_children("*","MeshInstance3D",true,false):
		if str(mesh.name)==except_name.validate_node_name():continue
		var x: Vector3=mesh.to_local(a);var y: Vector3=mesh.to_local(b);var box: AABB=mesh.mesh.get_aabb().grow(.00005)
		if maxf(x.x,y.x)<box.position.x or minf(x.x,y.x)>box.end.x or maxf(x.y,y.y)<box.position.y or minf(x.y,y.y)>box.end.y or maxf(x.z,y.z)<box.position.z or minf(x.z,y.z)>box.end.z:continue
		var faces: PackedVector3Array=raw_faces(mesh)
		for i in range(0,faces.size(),3):
			if Geometry3D.segment_intersects_triangle(x,y,faces[i],faces[i+1],faces[i+2])!=null:return false
	return true
func source_sampler(material: StandardMaterial3D,doc: Dictionary,ref: Dictionary) -> void:
	# Exact Godot4.6.3 GLTFTextureSampler representation for these source samplers.
	# Retained signs use nearest/mipmapped ink; the screen image clamps at its edges.
	assert(int(ref.get("texCoord",0))==0 and not ref.has("extensions"))
	var texture: Dictionary=doc.textures[int(ref.index)]
	var sampler: Dictionary=doc.samplers[int(texture.sampler)] if texture.has("sampler") else {}
	var mag: int=int(sampler.get("magFilter",9729));var minimum: int=int(sampler.get("minFilter",9987))
	assert([mag,minimum] in [[9729,9987],[9728,9984]],"Unreviewed source filter pair")
	var expected_filter: int=BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS if minimum==9984 else BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	var wrap_s: int=int(sampler.get("wrapS",10497));var wrap_t: int=int(sampler.get("wrapT",10497))
	assert([wrap_s,wrap_t] in [[10497,10497],[33071,33071]],"Unreviewed source wrapping pair")
	assert(material.texture_filter==expected_filter and material.texture_repeat==(wrap_s==10497 and wrap_t==10497),"Imported sampler differs from the exact source declaration")
func material_check(mesh: MeshInstance3D,si: int,p: Dictionary,doc: Dictionary,bin: PackedByteArray) -> void:
	var mat:=mesh.get_active_material(si)as StandardMaterial3D
	assert(mat!=null and mat==mesh.mesh.surface_get_material(si) and mesh.get_surface_override_material(si)==null)
	var gm: Dictionary=doc.materials[int(p.material)];var pbr: Dictionary=gm.get("pbrMetallicRoughness",{})
	assert(mat.resource_name==str(gm.name) and mat.transparency==BaseMaterial3D.TRANSPARENCY_DISABLED)
	assert(mat.metallic==PackedFloat32Array([pbr.get("metallicFactor",1)])[0] and mat.roughness==PackedFloat32Array([pbr.get("roughnessFactor",1)])[0])
	assert(mat.cull_mode==(BaseMaterial3D.CULL_DISABLED if gm.get("doubleSided",false) else BaseMaterial3D.CULL_BACK))
	var factor: Array=pbr.get("baseColorFactor",[1,1,1,1]);var expected:=Color(factor[0],factor[1],factor[2],factor[3]).linear_to_srgb()
	assert(mat.albedo_color==expected and mat.uv1_scale==Vector3.ONE and mat.uv1_offset==Vector3.ZERO)
	if gm.has("emissiveFactor"):
		var ef: Array=gm.emissiveFactor
		assert(mat.emission_enabled and mat.emission==Color(ef[0],ef[1],ef[2]).linear_to_srgb())
		assert(mat.emission_energy_multiplier==PackedFloat32Array([gm.get("extensions",{}).get("KHR_materials_emissive_strength",{}).get("emissiveStrength",1.0)])[0])
	else:assert(not mat.emission_enabled)
	for entry in [["baseColorTexture",pbr,mat.albedo_texture],["emissiveTexture",gm,mat.emission_texture]]:
		if entry[1].has(entry[0]):
			geo.texture_check(entry[2],doc,bin,entry[1][entry[0]]);source_sampler(mat,doc,entry[1][entry[0]])
		else:assert(entry[2]==null)
func geometry() -> void:
	assert(FileAccess.get_sha256("res://tests/pool_feature_geometry.gd")==str(data.geometry_audit_helper_sha256))
	geo=load("res://tests/pool_feature_geometry.gd").new()
	for entry in data.assemblies:
		var spec: Dictionary=data.models[str(entry.asset)];var path: String="res://assets/models/"+str(spec.file)
		assert(FileAccess.get_sha256(path)==str(spec.sha256))
		var cfg:=ConfigFile.new();assert(cfg.load(path+".import")==OK and cfg.get_value("params","meshes/force_disable_compression",false))
		var remap: String=cfg.get_value("remap","path","");assert(not remap.is_empty())
		var digest:=ConfigFile.new();assert(digest.load(remap.get_basename()+".md5")==OK and digest.get_value("","source_md5","")==FileAccess.get_md5(path))
		var raw: PackedByteArray=FileAccess.get_file_as_bytes(path);var length: int=raw.decode_u32(12)
		var doc: Dictionary=JSON.parse_string(raw.slice(20,20+length).get_string_from_utf8());var bin: PackedByteArray=raw.slice(28+length)
		var wrapper:=area.get_node(NodePath(str(entry.name)))as Node3D
		var binding: Dictionary=geo.bind_installed_tree(wrapper,doc);var count:=0;var triangles:=0
		for ni in range(doc.nodes.size()):
			var source: Dictionary=doc.nodes[ni]
			if not source.has("mesh"):continue
			var mesh: MeshInstance3D=binding.by_index[ni];meshes[str(source.name)]=mesh
			assert(mesh.material_override==null and mesh.material_overlay==null)
			var primitives: Array=doc.meshes[int(source.mesh)].primitives
			assert(primitives.size()==mesh.mesh.get_surface_count())
			for si in range(primitives.size()):
				var primitive: Dictionary=primitives[si];var n: int=int(doc.accessors[int(primitive.indices)].count)/3;var provenance: Dictionary={}
				for ti in range(n):provenance[str(ti)]={"source_part":str(source.name),"source_triangle":ti}
				geo.audit_surface(mesh,si,primitive,doc,bin,provenance,{"name":str(entry.asset)},"")
				material_check(mesh,si,primitive,doc,bin);triangles+=n
			count+=1
		assert(count==spec.meshes.size() and triangles==int(spec.triangles))
		records.geometry.append({"asset":entry.asset,"meshes":count,"triangles":triangles,"exact_raw_position_uv_normal_codec":true,"source_materials":true,"native_node_mapping":binding.records})
	for body in area.find_children("*","StaticBody3D",true,false):contacts.append(body.get_rid())
	var declared_mesh_count: int=0
	for entry in data.assemblies:declared_mesh_count+=data.models[str(entry.asset)].meshes.size()
	assert(meshes.size()==declared_mesh_count and area.get_child_count()==data.assemblies.size()+data.plants.size()+data.fixtures.size())
func support() -> void:
	var compilation: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	for expected in data.preserved_pool_floor_records:
		var found:=0
		for row in compilation.regions:
			if row.id==expected.id:assert(row==expected);found+=1
		assert(found==1,"Retained pool floor record changed")
	for probe in data.floor_bearing_probes:
		for value in probe.points_xyz:
			var p:=v3(value);var hit: Dictionary=ray(p+Vector3.UP*.025,p-Vector3.UP*.025,contacts)
			assert(not hit.is_empty() and str(hit.collider.get_parent().name)==str(probe.floor_owner),"New bearing lacks its retained compiled floor")
			assert(absf(hit.position.y-52.5)<.00005)
		records.floor_bearing.append({"part":probe.part,"actual_contact_points":probe.points_xyz.size(),"owner":probe.floor_owner})
	for entry in data.plants:
		var wrapper:=area.get_node(NodePath(str(entry.name)))as Node3D
		assert(wrapper.scale==Vector3.ONE and wrapper.position.distance_to(v3(entry.position_xyz))<.00005)
		assert(wrapper.find_children("*","CollisionObject3D",true,false).is_empty())
		var soil: MeshInstance3D=meshes[str(entry.support)];var root_count:=0;var seen: Dictionary={}
		for mesh in wrapper.find_children("*","MeshInstance3D",true,false):
			for vertex in raw_faces(mesh):
				var p: Vector3=mesh.to_global(vertex)
				if absf(p.y-float(entry.position_xyz[1]))>.00005 or seen.has(p):continue
				seen[p]=true;var expected: Variant=native_hit(soil,p+Vector3.UP*.025,p-Vector3.UP*.025)
				var hit: Dictionary=ray(p+Vector3.UP*.025,p-Vector3.UP*.025)
				assert(expected!=null and not hit.is_empty() and soil.is_ancestor_of(hit.collider) and hit.position.distance_to(expected)<.00005,"Native planted root lost actual soil contact")
				assert(absf(p.y-hit.position.y)<.00005);root_count+=1
		assert(root_count>0,"No actual planted root vertices found")
		records.soil.append({"instance":entry.name,"actual_soil_contacts":root_count,"unchanged_retained_model":true})
func sweep(row: Dictionary,exclude_new: bool) -> Dictionary:
	var capsule:=CapsuleShape3D.new();capsule.radius=float(row.radius_m);capsule.height=float(row.height_m)
	var query:=PhysicsShapeQueryParameters3D.new();query.shape=capsule;query.collision_mask=1;query.margin=.001
	var exclusions: Array[RID]=[actor.get_rid()]
	if exclude_new:exclusions.append_array(contacts)
	query.exclude=exclusions
	var result: Array=[]
	for i in range(row.points_xyz.size()-1):
		var a:=v3(row.points_xyz[i]);var b:=v3(row.points_xyz[i+1]);query.transform=Transform3D(Basis.IDENTITY,a+Vector3.UP*(capsule.height/2+.006));query.motion=b-a
		var fraction: PackedFloat32Array=space.cast_motion(query);var samples: Array=[]
		query.motion=Vector3.ZERO
		var steps: int=maxi(1,ceili(a.distance_to(b)/.15))
		for j in range(steps+1):
			query.transform.origin=a.lerp(b,float(j)/steps)+Vector3.UP*(capsule.height/2+.006)
			var names: Array[String]=[]
			for hit in space.intersect_shape(query,256):names.append(str(hit.collider.get_path()))
			names.sort();samples.append(names)
		result.append({"fraction":[fraction[0],fraction[1]],"owners":samples})
	return {"name":row.name,"segments":result}
func routes() -> void:
	for row in data.route_sweeps:
		var before: Dictionary=sweep(row,true);var after: Dictionary=sweep(row,false)
		assert(before==after,"New gallery changed retained physical approach: "+str(row.name))
		if str(row.name) in ["central_bench_approach","bench_return_to_apron","cleaning_cart_stop","cleaner_bench_stance","cleaner_table_stance","upper_apron"]:
			for segment in after.segments:
				assert(float(segment.fraction[0])==1.0)
				for names in segment.owners:assert(names.is_empty(),"Bay use approach is occupied")
		records.routes.append({"name":row.name,"native_before_after_equal":true,"radius_m":row.radius_m,"height_m":row.height_m})
	for volume in data.use_envelopes:
		var lo:=v3(volume.bounds_xyz[0]);var hi:=v3(volume.bounds_xyz[1]);var shape:=BoxShape3D.new();shape.size=hi-lo
		var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.transform.origin=(lo+hi)/2;query.exclude=[actor.get_rid()];query.collision_mask=1;query.margin=0
		assert(space.intersect_shape(query,64).is_empty(),"Seated knees/feet use volume blocked")
func sightlines() -> void:
	var eyes: Dictionary={}
	for view in data.seated_views:eyes[str(view.name)]=v3(view.eye_xyz)
	for sample in data.media_image_rays:
		var eye: Vector3=eyes[str(sample.view)];var target:=v3(sample.target_xyz);var stop: Vector3=target+(eye-target).normalized()*.002
		assert(ray(eye,stop).is_empty(),"Seated display ray physically obstructed")
		assert(clear_render_segment(eye,stop,"EAST_Display__M0__original_pool_leisure_image"),"Actual decorative geometry blocks seated image")
	for view in data.seated_views:
		var eye:=v3(view.eye_xyz);var target:=v3(view.neutral_target_xyz)
		assert(clear_render_segment(eye,target),"Neutral seated outlook blocked by new gallery")
		records.views.append({"name":view.name,"side_glance_angle_degrees":view.horizontal_media_angle_from_actual_backrest_degrees,"centre_and_four_image_corners_clear":true,"primary_outlook":"upper shared volume/opposite market","comfort_requires_native_image_review":true})
func light_checks() -> void:
	var budget:=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	assert(budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
	for fixture in data.fixtures:
		var light:=area.get_node(NodePath(str(fixture.name)))as SpotLight3D
		assert(light!=null and light.light_energy==PackedFloat32Array([fixture.energy])[0] and light.spot_range==PackedFloat32Array([fixture.range_m])[0] and light.spot_angle==PackedFloat32Array([fixture.half_angle_degrees])[0])
		var expected: Vector3=v3(fixture.direction_xyz).normalized()
		assert((-light.global_basis.z).angle_to(expected)<.000002,"Actual basis differs from source optic axis")
		assert(ray(light.global_position,light.global_position+expected*.06).is_empty())
		assert(clear_render_segment(light.global_position,light.global_position+expected*.06))
		var lens: MeshInstance3D=meshes[str(fixture.physical_lens)]
		assert(native_hit(lens,light.global_position,light.global_position-expected*.06)!=null,"Source light has no physical lens")
		var receiver:=v3(fixture.receiver_xyz);var offset: Vector3=receiver-light.global_position
		assert(offset.length()<light.spot_range and offset.normalized().dot(expected)>cos(deg_to_rad(light.spot_angle)))
		assert(budget._clear_sample(light.global_position,v3(fixture.visibility_sample_xyz)))
		records.lights.append({"name":fixture.name,"physical_exit_clear":true,"actual_source_lens":fixture.physical_lens,"receiver_within_local_range_cone":true,"energy":light.light_energy,"native_balance_accepted":false})
	var saved_transform: Transform3D=actor.global_transform
	for pose in [[-14,54.15,-443.2],[-13.1,54.15,-449.8],data.seated_views[0].eye_xyz]:
		actor.global_position=v3(pose)-Vector3.UP*1.5;budget.refresh()
		var selected: Array[String]=[]
		for fixture in data.fixtures:
			var lamp:=area.get_node(NodePath(str(fixture.name)))as SpotLight3D
			if lamp.visible:selected.append(str(lamp.name))
		print("EAST GALLERY NATURAL LIGHT SELECTION ",pose," ",selected)
		assert(not selected.is_empty(),"Gallery has no naturally selected source at approach/seat")
	actor.global_transform=saved_transform;budget.refresh()
func check(owner: SceneTree,world: Node3D) -> void:
	tree=owner;ship=world;actor=ship.get_node("ShipSpace/PersistentActors/Player");space=ship.get_world_3d().direct_space_state
	assert(FileAccess.get_sha256(CONTRACT)==REVIEWED_CONTRACT_SHA,"Approved gallery contract changed; omitted assemblies cannot pass a derived census")
	data=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT));area=ship.find_child(str(data.root_name),true,false)
	assert(area!=null);geometry();support();routes();sightlines();light_checks()
	for path in data.walk_paths:
		await owner.settle(v3(path.points_xyz[0]))
		for point in path.points_xyz:await owner.walk_to(v3(point))
	print("GRAND POOL EAST GALLERY PASS: exact four imported derivatives/materials, rooted beds, retained supports/routes and ordinary rest-bay walk. Lighting balance and side-glance comfort remain native image review.")
	var output: String=OS.get_environment("ASTRAEA_EAST_GALLERY_RECEIPT")
	if not output.is_empty():
		var file:=FileAccess.open(output,FileAccess.WRITE);assert(file!=null)
		records["status"]="PASS_AFFECTED_GEOMETRY_PHYSICAL_SCOPE";records["first_pass_accepted"]=false;records["loaded_cart_new_route_claim"]=false
		file.store_string(JSON.stringify(records,"  ",true,true));file.close()
