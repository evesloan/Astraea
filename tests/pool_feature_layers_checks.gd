extends RefCounted
# Focused installed feature checks, called by the existing pool architecture test.
# Original source/import precision evidence is retained; this checks the actual
# PackedScene instances, source-part contacts, route owners and natural selection.
const QA := "res://data/architecture/GRAND_POOL_FEATURE_QA.json"
const RUNTIME := "res://data/architecture/GRAND_POOL_FEATURE_LAYERS_RUNTIME.json"
var tree: SceneTree
var ship: Node3D
var actor: CharacterBody3D
var budget: Node
var physical_space: PhysicsDirectSpaceState3D
var candidate: Node3D
var audit: RefCounted
var data: Dictionary
var architecture: Dictionary
var runtime: Dictionary
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
var hardware_meshes: Array[MeshInstance3D]=[]
var candidate_on: bool=true
var original_light_state: Dictionary={}
var out: String

func v3(a: Array) -> Vector3:return Vector3(a[0],a[1],a[2])

func vec(p: Vector3) -> Array:return [p.x,p.y,p.z]

func save_json(path: String,value: Variant) -> void:
	var file:=FileAccess.open(path,FileAccess.WRITE);assert(file!=null)
	file.store_string(JSON.stringify(value,"  ",true,true));file.close()

func ray(a: Vector3,b: Vector3,excluded: Array[RID]) -> Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(a,b,1)
	query.hit_back_faces=true;query.exclude=excluded
	return physical_space.intersect_ray(query)

func state(light: Light3D) -> Dictionary:
	return {"position":vec(light.global_position),"direction":vec(-light.global_basis.z),"color":[light.light_color.r,light.light_color.g,light.light_color.b],"energy":light.light_energy,"range":light.spot_range if light is SpotLight3D else 0.0,"angle":light.spot_angle if light is SpotLight3D else 0.0}

func find_reference(part: String) -> MeshInstance3D:
	var found: MeshInstance3D=null
	var built: Node3D=ship.find_child("GrandPoolArchitecture_WIP",true,false)
	for entry in architecture.assemblies:
		var group: Node3D=built.get_node(NodePath(str(entry.name)))
		var spec: Dictionary=architecture.models[str(entry.asset)]
		for name in spec.meshes:
			if part in spec.meshes[name].source_parts:
				assert(found==null);found=group.find_child(str(name),true,false)as MeshInstance3D
	assert(found!=null,"Missing source-backed retained reference: "+part)
	return found

func predict_native_hit(mesh: MeshInstance3D,a: Vector3,b: Vector3,snap: bool=true) -> Variant:
	# The collision grid prediction is independent of the physical query.
	var nearest: Variant=null;var distance: float=INF
	for surface in range(mesh.mesh.get_surface_count()):
		var arrays: Array=mesh.mesh.surface_get_arrays(surface)
		var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
		var indices: PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
		for i in range(0,indices.size(),3):
			var p: Array=[]
			for j in range(3):p.append(vertices[indices[i+j]].snappedf(.0001) if snap else vertices[indices[i+j]])
			var hit: Variant=Geometry3D.segment_intersects_triangle(mesh.to_local(a),mesh.to_local(b),p[0],p[1],p[2])
			if hit==null:continue
			var world: Vector3=mesh.to_global(hit)
			var value: float=a.distance_squared_to(world)
			if value<distance:distance=value;nearest=world
	return nearest

func part_hit(asset: String,part: String,a: Vector3,b: Vector3) -> Variant:
	var key: String=asset+"::"+part;assert(audit.parts.has(key))
	var nearest: Variant=null;var distance: float=INF
	for row in audit.parts[key]:
		var mesh: MeshInstance3D=row.mesh
		var vertices: PackedVector3Array=mesh.mesh.surface_get_arrays(int(row.surface))[Mesh.ARRAY_VERTEX]
		var hit: Variant=Geometry3D.segment_intersects_triangle(mesh.to_local(a),mesh.to_local(b),vertices[row.indices[0]],vertices[row.indices[1]],vertices[row.indices[2]])
		if hit==null:continue
		var world: Vector3=mesh.to_global(hit);var d: float=a.distance_squared_to(world)
		if d<distance:distance=d;nearest=world
	return nearest

func foliage_ray(a: Vector3,b: Vector3) -> Dictionary:
	# Raw rendered opaque triangles, independently of physics (plants have no colliders).
	var nearest: Dictionary={};var distance: float=INF
	for mesh in audit.plant_meshes:
		if not mesh.get_aabb().intersects_segment(mesh.to_local(a),mesh.to_local(b)):continue
		for surface in range(mesh.mesh.get_surface_count()):
			var mat: StandardMaterial3D=mesh.get_active_material(surface)as StandardMaterial3D
			assert(mat!=null and mat.transparency==BaseMaterial3D.TRANSPARENCY_DISABLED)
			var arrays: Array=mesh.mesh.surface_get_arrays(surface)
			var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX];var ix: PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
			for i in range(0,ix.size(),3):
				var hit: Variant=Geometry3D.segment_intersects_triangle(mesh.to_local(a),mesh.to_local(b),vertices[ix[i]],vertices[ix[i+1]],vertices[ix[i+2]])
				if hit==null:continue
				var world: Vector3=mesh.to_global(hit);var d: float=a.distance_squared_to(world)
				if d>=distance:continue
				distance=d
				nearest={"mesh":str(mesh.get_path()),"source_part":audit.native_maps[str(mesh.get_instance_id())+":"+str(surface)][i/3],"point_xyz":vec(world),"distance_m":sqrt(d),"native_triangle":i/3,"surface":surface,"opaque":true,"cast_shadow":mesh.cast_shadow,"collision":false}
	return nearest

func set_candidate(enabled: bool) -> void:
	candidate_on=enabled;candidate.visible=enabled
	for node in sparse:node.visible=not enabled
	for shape in shape_nodes:shape.set_deferred("disabled",not enabled)
	for light in lights:light.set_meta("fixture_powered",enabled)
	budget.refresh()

func physical_check() -> void:
	var excluded: Array[RID]=[actor.get_rid()]
	for body in bodies:excluded.append(body.get_rid())
	for fixture in data.proposal.fixtures:
		var light: SpotLight3D=light_markers[str(fixture.name)]
		var direction: Vector3=-light.global_basis.z
		assert(ray(light.global_position,light.global_position+direction*.06,[actor.get_rid()]).is_empty(),"Source lens exit obstructed")
		var target: Vector3=v3(fixture.receiver_xyz);var receiver: MeshInstance3D=find_reference(str(fixture.receiver_source_part))
		var expected: Variant=predict_native_hit(receiver,light.global_position,target+direction*.02)
		var hit: Dictionary=ray(light.global_position,target+direction*.02,[actor.get_rid()])
		assert(expected!=null and not hit.is_empty() and receiver.is_ancestor_of(hit.collider) and hit.position.distance_to(expected)<.00005,"Receiver physical/predicted mismatch")
		assert(budget._clear_sample(light.global_position,v3(fixture.visibility_sample_xyz)))
		var support: MeshInstance3D=find_reference(str(fixture.host));var p: Vector3=v3(fixture.source_support_anchor_xyz);var normal: Vector3=v3(fixture.source_support_normal_xyz)
		var predicted: Variant=predict_native_hit(support,p+normal*.02,p-normal*.02)
		var host: Dictionary=ray(p+normal*.02,p-normal*.02,excluded)
		assert(predicted!=null and not host.is_empty() and support.is_ancestor_of(host.collider) and host.position.distance_to(predicted)<.00005,"Support physical/predicted mismatch")
		var raw_support: Variant=predict_native_hit(support,p+normal*.02,p-normal*.02,false)
		var backplate: String=str(fixture.physical_housing).replace("RecessHousing","SourceBackplate")
		var plate: Variant=part_hit("AST-AQU-016_pool_feature_lighting",backplate,p-normal*.01,p+normal*.01)
		assert(plate!=null and raw_support!=null and plate.distance_to(raw_support)<.00005,"Raw backplate/host contact exceeds source ceiling")
		physical_records.append({"kind":"fixture","name":fixture.name,"marker":vec(light.global_position),"lens_exit_clear":true,"receiver_owner":str(hit.collider.get_path()),"receiver_position":vec(hit.position),"receiver_physics_to_independent_snapped_prediction_m":hit.position.distance_to(expected),"support_owner":str(host.collider.get_path()),"support_position":vec(host.position),"support_physics_to_independent_snapped_prediction_m":host.position.distance_to(predicted),"raw_backplate_to_raw_host_m":plate.distance_to(raw_support)})
	for marker in root_markers:
		var p: Vector3=marker.node.global_position;var support: MeshInstance3D=find_reference(str(marker.support))
		var predicted: Variant=predict_native_hit(support,p+Vector3.UP*.02,p-Vector3.UP*.02)
		var raw_support: Variant=predict_native_hit(support,p+Vector3.UP*.02,p-Vector3.UP*.02,false)
		var hit: Dictionary=ray(p+Vector3.UP*.02,p-Vector3.UP*.02,excluded)
		assert(predicted!=null and raw_support!=null and not hit.is_empty() and support.is_ancestor_of(hit.collider))
		assert(hit.position.distance_to(predicted)<.00005,"Root soil physics exceeds independently predicted collision bound")
		var root_bottom: Variant=part_hit(str(marker.asset),str(marker.part),p-Vector3.UP*.01,p+Vector3.UP*.01)
		assert(root_bottom!=null and root_bottom.distance_to(p)<.00005 and root_bottom.distance_to(raw_support)<.00005,"Root marker/actual root/soil contact changed")
		physical_records.append({"kind":"root_soil","placement":marker.placement,"source_root":marker.part,"marker":vec(p),"raw_root_bottom":vec(root_bottom),"raw_soil":vec(raw_support),"physics_soil":vec(hit.position),"physics_to_predicted_m":hit.position.distance_to(predicted),"root_to_raw_soil_m":root_bottom.distance_to(raw_support),"root_to_marker_m":root_bottom.distance_to(p),"decorative_noncolliding":true})

func receiver_check() -> void:
	var interception_count: int=0
	for sample in data.receiver_samples:
		var light: SpotLight3D=light_markers[str(sample.fixture)];var target: Vector3=v3(sample.target_xyz)
		var delta: Vector3=target-light.global_position;var direction: Vector3=delta.normalized()
		assert(delta.length()<light.spot_range and direction.dot(-light.global_basis.z)>=cos(deg_to_rad(light.spot_angle)))
		var reference_names: PackedStringArray=str(sample.baseline_first_hit.part).split("::");assert(reference_names.size()==2)
		var built: Node3D=ship.find_child("GrandPoolArchitecture_WIP",true,false)
		var reference: MeshInstance3D=built.get_node(NodePath(reference_names[0])).find_child(reference_names[1],true,false)as MeshInstance3D
		assert(reference!=null)
		var predicted: Variant=predict_native_hit(reference,light.global_position,target+direction*.02)
		var hit: Dictionary=ray(light.global_position,target+direction*.02,[actor.get_rid()])
		assert(predicted!=null and not hit.is_empty() and reference.is_ancestor_of(hit.collider) and hit.position.distance_to(predicted)<.00005,"Native collider receiver differs from predicted receiver")
		var optical: Dictionary=foliage_ray(light.global_position,target-direction*.02)
		var expected_leaf: bool=not bool(sample.clear_in_joint)
		assert(optical.is_empty()==not expected_leaf,"Actual native opaque foliage interception differs from retained compound source")
		if not optical.is_empty():
			interception_count+=1
			assert(str(sample.joint_first_hit_from_marker.part).ends_with("::"+str(optical.source_part)))
			assert(v3(optical.point_xyz).distance_to(v3(sample.joint_first_hit_from_marker.point_xyz))<.00005)
		optical_records.append({"sample":sample.sample_name,"fixture":sample.fixture,"target_xyz":sample.target_xyz,"source_classification":sample.classification,"native_render_triangle_interception":optical,"native_collider_receiver":str(hit.collider.get_path()),"native_collider_point":vec(hit.position),"physics_to_snapped_prediction_m":hit.position.distance_to(predicted),"collider_ray_does_not_test_decorative_leaf_shadows":true,"rendered_pixel_evidence":"Recorded per capture; visible shadow appearance requires pixel review"})
	assert(optical_records.size()==30 and interception_count==1,"Keep honest 29-clear/1-leaf result")

func compact_hit(hit: Dictionary) -> Dictionary:
	if hit.is_empty():return {}
	return {"owner":str(hit.collider.get_path()),"position":vec(hit.position),"normal":vec(hit.normal)}

func hits_equal(a: Dictionary,b: Dictionary) -> bool:
	if a.is_empty() or b.is_empty():return a.is_empty() and b.is_empty()
	return a.owner==b.owner and v3(a.position).distance_to(v3(b.position))<.00005

func query_route(row: Dictionary) -> Dictionary:
	var capsule:=CapsuleShape3D.new();capsule.radius=float(row.r);capsule.height=float(row.h)
	var query:=PhysicsShapeQueryParameters3D.new();query.shape=capsule;query.collision_mask=1;query.exclude=[actor.get_rid()];query.margin=0.001
	var segments: Array=[]
	for i in range(row.points.size()-1):
		var a: Vector3=v3(row.points[i]);var b: Vector3=v3(row.points[i+1]);query.transform=Transform3D(Basis.IDENTITY,a+Vector3.UP*(capsule.height/2));query.motion=b-a
		var fractions: PackedFloat32Array=physical_space.cast_motion(query)
		var sampled: Array=[];var steps: int=maxi(1,ceili(a.distance_to(b)/.1))
		query.motion=Vector3.ZERO
		for j in range(steps+1):
			query.transform.origin=a.lerp(b,float(j)/steps)+Vector3.UP*(capsule.height/2)
			var owners: Array=[]
			for hit in physical_space.intersect_shape(query,256):owners.append(str(hit.collider.get_path()))
			owners.sort();sampled.append(owners)
		segments.append({"safe_fraction":fractions[0],"unsafe_fraction":fractions[1],"sampled_owners":sampled})
	return {"name":row.name,"segments":segments}

func preserve_access_checks() -> void:
	set_candidate(false)
	for frame in range(3):await tree.physics_frame
	var base_routes: Array=[];var base_views: Array=[];var base_rays: Array=[]
	for row in data.routes:base_routes.append(query_route(row))
	for row in data.views:base_views.append(compact_hit(ray(v3(row.eye),v3(row.target),[actor.get_rid()])))
	for row in data.old_fixture_rays:base_rays.append(compact_hit(ray(v3(row.origin_xyz),v3(row.endpoint_xyz),[actor.get_rid()])))
	set_candidate(true)
	for frame in range(3):await tree.physics_frame
	for i in range(data.routes.size()):
		var value: Dictionary=query_route(data.routes[i]);var before: Dictionary=base_routes[i]
		assert(value.segments.size()==before.segments.size())
		for k in range(value.segments.size()):
			assert(value.segments[k].sampled_owners==before.segments[k].sampled_owners,"Approach collision owners changed")
			assert(absf(value.segments[k].safe_fraction-before.segments[k].safe_fraction)<.00001 and absf(value.segments[k].unsafe_fraction-before.segments[k].unsafe_fraction)<.00001,"Approach cast changed")
		route_records.append({"name":value.name,"baseline":before,"candidate":value,"unchanged":true})
	for i in range(data.views.size()):
		var row: Dictionary=data.views[i];var after: Dictionary=compact_hit(ray(v3(row.eye),v3(row.target),[actor.get_rid()]));var foliage: Dictionary=foliage_ray(v3(row.eye),v3(row.target))
		assert(hits_equal(base_views[i],after) and foliage.is_empty(),"Retained seated/sign/wayfinding view changed")
		view_records.append({"name":row.name,"kind":row.kind,"eye":row.eye,"target":row.target,"baseline":base_views[i],"candidate":after,"opaque_foliage_hits":foliage,"unchanged":true})
	for i in range(data.old_fixture_rays.size()):
		var row: Dictionary=data.old_fixture_rays[i];var after: Dictionary=compact_hit(ray(v3(row.origin_xyz),v3(row.endpoint_xyz),[actor.get_rid()]));var foliage: Dictionary=foliage_ray(v3(row.origin_xyz),v3(row.endpoint_xyz))
		assert(hits_equal(base_rays[i],after) and foliage.is_empty(),"Retained fixture ray changed")
		old_ray_records.append({"fixture":row.fixture,"kind":row.kind,"baseline":base_rays[i],"candidate":after,"opaque_foliage_hits":foliage,"unchanged":true})
	assert(route_records.size()==30 and view_records.size()==162 and old_ray_records.size()==91)

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


func inspect_actual_models() -> void:
	var old_root: Node3D=ship.find_child("GrandPoolArchitecture_WIP",true,false)
	assert(old_root!=null and candidate.get_parent()==old_root.get_parent())
	assert(candidate.transform==Transform3D.IDENTITY and candidate.visible)
	assert(old_root.get_child_count()==15 and candidate.get_child_count()==10)
	for asset in data.assets:
		var wrapper: Node3D=candidate.get_node(NodePath(str(asset.wrapper_name)))
		var item: Dictionary=audit.audit_model(wrapper,asset,"",true)
		if str(asset.family)=="plant":
			var source_root: Dictionary=item.extras[str(asset.name)]
			var old: Node3D=old_root.get_node(NodePath(str(source_root.placement_name)))
			assert(not old.visible and wrapper.global_transform==old.global_transform and wrapper.scale.is_equal_approx(Vector3.ONE))
			assert(wrapper.find_children("*","CollisionObject3D",true,false).is_empty())
			sparse.append(old);preserved_plants.append({"node":old,"transform":old.global_transform,"visible":true,"kind":"middle_sparse"})
			for name in item.nodes:
				var extra: Dictionary=item.extras[name]
				if extra.get("marker_kind","")=="soil_contact":
					root_markers.append({"node":item.nodes[name],"asset":asset.name,"part":extra.physical_part,"support":source_root.support,"placement":source_root.placement_name})
		else:
			assert(str(asset.family)=="light" and wrapper.global_transform==Transform3D.IDENTITY)
			for name in item.nodes:
				var node: Node3D=item.nodes[name];var extra: Dictionary=item.extras[name]
				if node is MeshInstance3D:
					hardware_meshes.append(node)
					if str(extra.collision_contract)=="concave_static_surface":
						var contact: StaticBody3D=node.get_node("StaticContact")
						assert(contact.get_child_count()==1 and contact.transform==Transform3D.IDENTITY)
						var shape: CollisionShape3D=contact.get_child(0)
						assert(shape.shape is ConcavePolygonShape3D and not shape.disabled)
						bodies.append(contact);shape_nodes.append(shape)
					else:
						assert(str(extra.collision_contract)=="visual_lens_no_contact" and not bool(extra.cast_shadow))
						assert(node.find_children("*","CollisionObject3D",true,false).is_empty() and node.cast_shadow==GeometryInstance3D.SHADOW_CASTING_SETTING_OFF)
				else:
					assert(str(name).begins_with("DATUM_finish_light_"))
					var light: SpotLight3D=candidate.get_node(NodePath("PoolFeature_"+str(name)))
					assert(light.global_position.distance_to(node.global_position)<.00005)
					# Node3D.look_at subtracts its rounded float32 world target at z≈-450m.
					# Compare against that actual representation, keeping the1e-6 bound.
					var ideal_direction: Vector3=v3(extra.direction_godot_xyz).normalized()
					var native_direction: Vector3=((light.global_position+ideal_direction)-light.global_position).normalized()
					assert((-light.global_basis.z).distance_to(native_direction)<.000001,"Light direction differs from source-derived native look_at representation")
					assert(absf(light.light_energy-float(extra.suggested_energy))<.000001 and absf(light.spot_range-float(extra.suggested_range_m))<.000001 and absf(light.spot_angle-float(extra.suggested_spot_angle_degrees))<.000001)
					assert(str(light.get_meta("source_marker"))==str(name) and bool(light.get_meta("fixture_powered")))
					assert(light in budget.sources and budget.requested_shadow[light.get_instance_id()])
					lights.append(light);light_markers[str(name)]=light
	for entry in data.replacement.six_basal_instances_retained:
		var node: Node3D=old_root.get_node(NodePath(str(entry.name)))
		assert(node.position==v3(entry.position_xyz) and absf(node.rotation.y-float(entry.yaw_radians))<.000001 and node.scale.is_equal_approx(Vector3.ONE) and node.visible)
		preserved_plants.append({"node":node,"transform":node.global_transform,"visible":true,"kind":"basal"})
	assert(audit.all_meshes.size()==33 and hardware_meshes.size()==3 and lights.size()==3 and bodies.size()==2)
	assert(root_markers.size()==30 and sparse.size()==6 and preserved_plants.size()==12)
	for hardware in hardware_meshes:
		for plant in audit.plant_meshes:
			assert(not (hardware.global_transform*hardware.get_aabb()).intersects(plant.global_transform*plant.get_aabb()),"Feature hardware intersects planted envelope")
	verify_preserved_plants()

func check_natural_selection() -> Array:
	var observations: Array=[]
	var saved_transform: Transform3D=actor.global_transform
	for row in [
		{"name":"wet_loggia_walk","eye":Vector3(-45.9,47.85,-438),"required":["PoolFeature_DATUM_finish_light_ArchTimber_ForeL","PoolFeature_DATUM_finish_light_ArchTimber_ForeR"]},
		{"name":"fore_focal_walk","eye":Vector3(-31,47.85,-458.5),"required":["PoolFeature_DATUM_finish_light_ArchFocal_Crown"]}
	]:
		actor.global_position=Vector3(row.eye.x,46.2,row.eye.z)
		for frame in range(3):await tree.physics_frame
		for repeat in range(3):
			budget.refresh();var sampled: Dictionary=selection()
			for name in row.required:
				var source: SpotLight3D=candidate.get_node(NodePath(str(name)))
				assert(source.visible and source.shadow_enabled,"Physical feature source is not naturally selected at its retained walking view")
			observations.append({"view":row.name,"sample":repeat,"selection":sampled})
	actor.global_transform=saved_transform;budget.refresh()
	return observations

func check(scene_tree: SceneTree,actual_ship: Node3D) -> void:
	tree=scene_tree;ship=actual_ship
	data=JSON.parse_string(FileAccess.get_file_as_string(QA))
	runtime=JSON.parse_string(FileAccess.get_file_as_string(RUNTIME))
	architecture=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GRAND_POOL_ARCHITECTURE_RUNTIME.json"))
	actor=ship.get_node("ShipSpace/PersistentActors/Player");budget=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	physical_space=ship.get_world_3d().direct_space_state;candidate=ship.find_child("GrandPoolFeatureLayers_WIP",true,false)
	assert(candidate!=null and not actor.is_physics_processing() and budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
	var engine: Dictionary=Engine.get_version_info();assert(int(engine.major)==4 and int(engine.minor)==6 and int(engine.patch)==3)
	out="res://artifacts/pool_feature_layers";assert(DirAccess.make_dir_recursive_absolute(out)==OK)
	audit=load("res://tests/pool_feature_geometry.gd").new()
	for light in budget.sources:original_light_state[str(light.get_instance_id())]=state(light)
	inspect_actual_models();physical_check();receiver_check()
	await preserve_access_checks()
	var selection_samples: Array=await check_natural_selection()
	verify_preserved_plants()
	for light in budget.sources:
		var key: String=str(light.get_instance_id());assert(original_light_state.has(key) and state(light)==original_light_state[key],"Source physical/optical properties changed during focused check")
	save_json(out+"/RESULT.json",{"status":"PASS_INSTALLED_POOL_FEATURE_PATH_AND_PHYSICAL_CHECKS","installed":true,"native_model_geometry":audit.records,"root_contacts":physical_records,"receiver_classification":optical_records,"routes":route_records,"views":view_records,"retained_fixture_rays":old_ray_records,"source_selection":selection_samples,"old_source_properties_unchanged":true,"active_budget":8,"candidate_limit":32,"full_suite":false,"visual_first_pass_accepted":false})
	print("POOL FEATURE LAYERS PASS: exact imported model/source correspondence, real hardware and30root contacts,30unchanged route comparisons,162retained views,91oldfixture rays and naturally selected feature lighting; full suite and final visual acceptance remain separate.")
