extends RefCounted
# Actual D05 main-scene receiving/waiting construction candidate. No clinical gameplay.
const CONTRACT: String = "res://data/architecture/D05_MEDICAL_WELCOME_RUNTIME.json"

static func xyz(value: Array) -> Vector3:
	return Vector3(float(value[0]),float(value[1]),float(value[2]))

static func exact_node(root: Node3D, exact_name: String) -> Node3D:
	var found: Array[Node3D] = []
	for value in root.find_children(exact_name,"Node3D",true,false):
		var node: Node3D = value as Node3D
		if str(node.name)==exact_name: found.append(node)
	assert(found.size()==1,"Exactly one retained medical source node required: "+exact_name)
	return found[0]

static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(bool(data.construction_scope_approved) and not bool(data.medical_or_repair_gameplay))
	assert(bool(data.floor_owned_by_compiler_only) and str(data.programme_key)=="D05_directory_01")
	for filename in data.model_pins:
		assert(FileAccess.get_sha256("res://assets/models/"+str(filename))==str(data.model_pins[filename]),"Exact retained medical model required: "+str(filename))
		var config: ConfigFile = ConfigFile.new()
		assert(config.load("res://assets/models/"+str(filename)+".import")==OK)
		var policy: Dictionary = data.new_asset_import_policy[filename]
		assert(bool(config.get_value("params","meshes/force_disable_compression",false))==bool(policy["meshes/force_disable_compression"]),"New-model import policy requires a fresh import: "+str(filename))
	var core: Node3D = ship.find_child(str(data.core_root_name),true,false) as Node3D
	assert(core!=null and str(core.get_meta("persistent_id"))==str(data.core_identity))
	var core_contract: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/FORWARD_PUBLIC_CORE.json"))
	assert(str(core_contract.enclosure_file)==str(data.core_file),"Never install the medical approach through the retained solid core wall")
	var floor_owner: Node3D = ship.find_child(str(data.floor_owner),true,false) as Node3D
	assert(floor_owner!=null and str(floor_owner.get_meta("region_id"))==str(data.floor_owner),"Compiler receiving floor must exist before the aperture is opened")
	assert(data.floor_owners == [data.floor_owner,data.new_floor_owner])
	var triage_floor: Node3D = ship.find_child(str(data.new_floor_owner),true,false) as Node3D
	assert(triage_floor!=null and str(triage_floor.get_meta("region_id"))==str(data.new_floor_owner),"Connected triage floor must exist before the admission wall is opened")
	var root: Node3D = Node3D.new()
	root.name=str(data.root_name)
	root.set_meta("persistent_id",str(data.persistent_id))
	root.set_meta("programme_key",str(data.programme_key))
	root.set_meta("first_pass_quality_accepted",false)
	root.set_meta("clinical_operation_accepted",false)
	root.set_meta("floor_owner",str(data.floor_owner))
	root.set_meta("triage_floor_owner",str(data.new_floor_owner))
	root.set_meta("privacy_leaves_static",true)
	root.set_meta("scope","Unfinished connected waiting/support and eight-pod triage wing; static source-open privacy leaves, no clinical operation")
	parent.add_child(root)
	root.position=xyz(data.origin_xyz)
	var architecture: Node3D = ship.model(root,str(data.architecture_file),"AuthoredMedicalWelcome",Vector3.ZERO)
	architecture.set_meta("source_package","medical_forward_welcome_candidate_20261006/triage010")
	architecture.set_meta("catalogue_id_status","Unregistered architectural candidate; existing component identities retained")
	for value in data.door_sources:
		var doorway: Dictionary = value
		var number: String = str(doorway.programme_child).get_slice("_pod_",1)
		for side in ["left","right"]:
			var leaf: Node3D = exact_node(architecture,"TRIAGE_"+number+"_privacy_leaf_"+side)
			leaf.set_meta("programme_child",str(doorway.programme_child))
			leaf.set_meta("source_open_static",true)
			leaf.set_meta("operation_enabled",false)
	for value in data.instances:
		var item: Dictionary = value
		var instance: Node3D = ship.model(root,str(item.file),str(item.name),xyz(item.local_xyz),float(item.yaw_radians))
		instance.set_meta("catalogue_id",str(item.catalogue_id))
		instance.set_meta("programme_child",str(item.programme_child))
		instance.set_meta("persistent_id",str(item.programme_child)+"__"+str(item.name))
		instance.set_meta("scope",str(item.scope))
		assert(instance.global_position.distance_to(xyz(item.world_xyz))<.001)
	for value in data.fixtures:
		var item: Dictionary = value
		var owner: Node3D = root.get_node(str(item.source_owner)) as Node3D
		var source: Node3D = exact_node(owner,str(item.source_node))
		var light: SpotLight3D = SpotLight3D.new()
		light.name=("MedicalSource_"+str(item.name)).validate_node_name()
		root.add_child(light)
		light.global_position=xyz(item.position_xyz)
		var aim: Vector3 = xyz(item.aim_xyz)
		var direction: Vector3 = (aim-light.global_position).normalized()
		var up: Vector3 = Vector3.FORWARD if absf(direction.dot(Vector3.UP))>.95 else Vector3.UP
		light.look_at(aim,up)
		ship.apply_light_profile(light,str(item.profile))
		light.spot_angle=float(item.spot_angle_degrees)
		light.shadow_enabled=true
		light.set_meta("source_node",str(source.get_path()))
		light.set_meta("source_id","D05_MEDICAL_"+str(item.name))
		light.set_meta("runtime_visual_acceptance",false)
	# The existing LocalShadowSourceBudget discovers these housed sources after ship assembly.
	# Rear service panel, clinical privacy screen and supply trolley remain static.
