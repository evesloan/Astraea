extends RefCounted
# Scoped northern Tidal chamber. Same programme, floors, working entry/support
# modules and original player. Group1 owns shared-scene adoption and roof joins.
const CONTRACT="res://data/architecture/group6_completion/TIDAL_NORTH_ROOM_CONTRACT.json"
static func build(room:Node3D)->Node3D:
	var spec:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(str(room.get_meta("programme_key"))==str(spec.programme_key) and room.get_node_or_null("Group6TidalNorthRoom")==null)
	var previous:Node3D=room.get_node_or_null("Group6ThermalRecovery");assert(previous!=null and str(previous.get_meta("checked_export_sha256"))==str(spec.required_recovery_export_sha256))
	for pair in [[spec.current_room_runtime,spec.current_room_runtime_sha256],[spec.required_recovery_export,spec.required_recovery_export_sha256],[spec.runtime_addition,spec.export_sha256]]:
		assert(FileAccess.get_sha256("res://"+str(pair[0]).trim_prefix("Game/"))==str(pair[1]))
	var original_meshes:Array=[]
	for name in spec.original_runtime_exclusions:
		var mesh:MeshInstance3D=room.find_child(str(name),true,false);assert(mesh!=null);var a:AABB=mesh.global_transform*mesh.get_aabb();var b:Array=spec.original_source_exclusion_bounds_xyz[str(name)]
		for k in range(3):assert(absf(a.position[k]-float(b[k][0]))<.002 and absf(a.end[k]-float(b[k][1]))<.002)
		original_meshes.append(mesh)
	var old_recovery:Array=[]
	for name in spec.prior_recovery_runtime_exclusions:
		var mesh:MeshInstance3D=previous.find_child(str(name),true,false);assert(mesh!=null);old_recovery.append(mesh)
	var addition:Node3D=load("res://"+str(spec.runtime_addition).trim_prefix("Game/")).instantiate();addition.name="Group6TidalNorthRoom";room.add_child(addition)
	for mesh:MeshInstance3D in original_meshes+old_recovery:
		var contact:Node=mesh.get_node_or_null("StaticContact")
		if contact!=null:contact.free()
		mesh.visible=false;mesh.set_meta("group6_source_successor","connected northern bathing chamber")
	for light:Light3D in previous.find_children("*","Light3D",true,false):
		if "recovery_2_task" in str(light.name) or "existing_bath_light3_lens" in str(light.name):light.set_meta("fixture_powered",false);light.visible=false;light.shadow_enabled=false
	var count:=0
	for mesh:MeshInstance3D in addition.find_children("*","MeshInstance3D",true,false):
		assert(spec.new_mesh_roles.has(str(mesh.name)));var role:String=str(spec.new_mesh_roles[str(mesh.name)]);mesh.set_meta("group6_contact_role",role)
		if role=="architecture":load("res://scripts/static_contact_cache.gd").attach(mesh)
		else:assert(role in ["visual_water","visual_liner","visual_furnishing","fixture_lens"])
		if role=="fixture_lens":
			var lens:StandardMaterial3D=mesh.get_active_material(0).duplicate();lens.emission_enabled=true;lens.emission=Color(1,.90,.72);lens.emission_energy_multiplier=.8;mesh.material_override=lens
		count+=1
	assert(count==spec.new_meshes.size())
	var water:MeshInstance3D=addition.find_child("G6_TIDAL__water_face",true,false);var water_material:=ShaderMaterial.new();water_material.shader=load("res://shaders/group6_tidal_water.gdshader");water.material_override=water_material
	var reflection:=ReflectionProbe.new();reflection.name="TidalActualRoomReflection";reflection.position=Vector3(38,47,-418);reflection.size=Vector3(24,8,30);reflection.origin_offset=Vector3(0,-1.5,0);reflection.box_projection=true;reflection.interior=true;reflection.enable_shadows=true;reflection.ambient_mode=ReflectionProbe.AMBIENT_DISABLED;reflection.update_mode=ReflectionProbe.UPDATE_ONCE;reflection.intensity=.85;reflection.visible=false;addition.add_child(reflection)
	var coping:MeshInstance3D=addition.find_child("G6_TIDAL__coping_east",true,false)
	for name in ["bath_basin_wall_u1_0","bath_basin_wall_u1_1","bath_basin_wall_v1_1"]:
		var wall:MeshInstance3D=room.find_child("D08_directory_02__"+name,true,false);assert(wall!=null);wall.material_override=coping.get_active_material(0)
	for fitting in spec.fittings:
		var source:=Vector3(float(fitting.source_xyz[0]),float(fitting.source_xyz[1]),float(fitting.source_xyz[2]));var target:=Vector3(float(fitting.target_xyz[0]),float(fitting.target_xyz[1]),float(fitting.target_xyz[2]));var light:=SpotLight3D.new();light.name=str(fitting.id)+"_PhysicalSource";addition.add_child(light);light.position=source;light.light_energy=float(fitting.energy);light.light_color=Color(float(fitting.color_rgb[0]),float(fitting.color_rgb[1]),float(fitting.color_rgb[2]));light.spot_range=float(fitting.range_m);light.spot_angle=float(fitting.cone_degrees);light.look_at(addition.to_global(target),Vector3.RIGHT if absf((target-source).normalized().dot(Vector3.UP))>.99 else Vector3.UP);light.shadow_enabled=true;light.set_meta("illumination_anchor",target)
	addition.set_meta("persistent_id","aquatic_tidal_northern_chamber_001");addition.set_meta("new_room_capacity_or_floor_owner",0);addition.set_meta("swimming_implemented",false);addition.set_meta("shared_roof_adoption_pending",true)
	return addition

# Group1 calls this once on local arrival, after the shared budget selects sources.
# Avoid capturing transient pre-budget lights during room construction.
static func activate_reflection(room:Node3D,budget:Node)->void:
	var addition:Node3D=room.get_node("Group6TidalNorthRoom");var reflection:ReflectionProbe=addition.get_node("TidalActualRoomReflection");assert(not reflection.visible and budget.actor!=null)
	var local:Vector3=room.to_local(budget.actor.global_position);assert(local.x>=27.0 and local.x<=51.2 and local.z>=-435 and local.z<=-400)
	var active:=0
	for light:Light3D in budget.sources:
		if light.visible and budget.requested_shadow.get(light.get_instance_id(),false):active+=1;assert(light.shadow_enabled)
	assert(active>0 and active<=8)
	reflection.set_meta("captured_after_shared_budget",true);reflection.visible=true
