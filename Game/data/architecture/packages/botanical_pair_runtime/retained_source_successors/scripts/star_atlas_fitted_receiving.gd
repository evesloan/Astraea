extends RefCounted
# Exact synchronous insertion witness. Original district and candidate builders stay unchanged.
const CHILD := "StarAtlasFittedInteriors_Candidate"
const LEGACY_QUEUED_CONTACTS: Array[String] = ["StarAtlasPassengerLift/CabinGate/AST-DOR-003/LIFT_fixed_ivory_enamel/StaticContact", "StarAtlasPassengerLift/CabinGate/AST-DOR-003/LIFT_fixed_champagne_metal/StaticContact", "StarAtlasPassengerLift/CabinGate/AST-DOR-003/LIFT_fixed_warm_walnut/StaticContact"]
const LEGACY_LIFT_SHA := "e53ba41f6e066ff2454340d2b73ad405a2db301f8176046f7741b401fcc8e203"
static var receipts: Dictionary = {}

static func audit_enabled() -> bool:
	# Expensive deep witness work belongs to validation, never normal graphical startup.
	return DisplayServer.get_name()=="headless" or OS.get_environment("ASTRAEA_STAR_ATLAS_AUDIT")=="1"

static func digest(value: Variant) -> String:
	var hash: HashingContext=HashingContext.new()
	assert(hash.start(HashingContext.HASH_SHA256)==OK)
	assert(hash.update(var_to_bytes(value))==OK)
	return hash.finish().hex_encode()

static func value_state(value: Variant,resources: Dictionary) -> Variant:
	if value is Resource:
		var id: int=value.get_instance_id()
		if not resources.has(id):
			resources[id]={"pending":true}
			var state: Dictionary={"id":id,"class":value.get_class(),"path":value.resource_path,"name":value.resource_name}
			if value is Script:
				state["source_code"]=digest(value.source_code)
			elif value is Texture2D:
				var pixels: Image=value.get_image()
				assert(pixels!=null)
				state["pixels"]={"size":pixels.get_size(),"format":pixels.get_format(),"mipmaps":pixels.has_mipmaps(),"data":digest(pixels.get_data())}
			else:
				state["properties"]=properties(value,resources,false)
			if value is Mesh:
				assert(value is ArrayMesh or value is PrimitiveMesh,"Unexpected mesh representation in exact snapshot")
				var surfaces: Array=[]
				for index in range(value.get_surface_count()):
					surfaces.append({"primitive":value.surface_get_primitive_type(index) if value is ArrayMesh else Mesh.PRIMITIVE_TRIANGLES,"arrays":digest(value.surface_get_arrays(index)),"material":value_state(value.surface_get_material(index),resources)})
				state["surfaces"]=surfaces
			if value is ConcavePolygonShape3D: state["faces"]=digest(value.get_faces())
			if value is ConvexPolygonShape3D: state["points"]=digest(value.points)
			if value is MultiMesh: state["buffer"]=digest(value.buffer)
			resources[id]=state
		return {"resource_id":id}
	if value is Object: return {"object_id":value.get_instance_id(),"class":value.get_class()}
	if value is Dictionary:
		var result: Dictionary={}
		for key in value: result[digest(key)]=value_state(value[key],resources)
		return result
	if value is Array:
		var result: Array=[]
		for item in value: result.append(value_state(item,resources))
		return result
	return {"type":typeof(value),"value":digest(value)}

static func properties(object: Object,resources: Dictionary,ignore_budget_state: bool) -> Dictionary:
	var result: Dictionary={}
	for spec in object.get_property_list():
		var key: String=str(spec.name)
		if (int(spec.usage) & (PROPERTY_USAGE_STORAGE|PROPERTY_USAGE_SCRIPT_VARIABLE))==0: continue
		# The sole manager legitimately controls these two fields after construction.
		# No other light state, material, metadata or node property is exempted.
		if ignore_budget_state and object is Light3D and key in ["visible","shadow_enabled"]: continue
		result[key]=value_state(object.get(key),resources)
	return result

static func snapshot(root: Node,excluded: Node=null,ignore_budget_state: bool=false) -> Dictionary:
	var resource_states: Dictionary={}
	var result: Dictionary={}
	var todo: Array=[root]
	while not todo.is_empty():
		var node: Node=todo.pop_front()
		if node==excluded: continue
		var children: Array=[]
		for child in node.get_children():
			if child==excluded: continue
			children.append(child.get_instance_id());todo.append(child)
		var meta: Dictionary={}
		for key in node.get_meta_list(): meta[str(key)]=value_state(node.get_meta(key),resource_states)
		var row: Dictionary={"id":node.get_instance_id(),"class":node.get_class(),"name":str(node.name),"parent_id":node.get_parent().get_instance_id() if node.get_parent()!=null else 0,"children":children,"queued_for_deletion":node.is_queued_for_deletion(),"script":value_state(node.get_script(),resource_states),"metadata":meta,"properties":properties(node,resource_states,ignore_budget_state)}
		if node is Node3D: row["transform"]=node.transform
		if node is CollisionObject3D: row["physics_rid"]=str(node.get_rid())
		result[str(root.get_path_to(node))]=row
	return {"nodes":result,"resources":resource_states}

static func legacy_retirements(district: Node3D,before: Dictionary) -> Dictionary:
	assert(FileAccess.get_sha256("res://scripts/commons_lift.gd")==LEGACY_LIFT_SHA,"Exact original cabin-gate initializer required")
	var result: Dictionary={}
	for path in LEGACY_QUEUED_CONTACTS:
		var body: StaticBody3D=district.get_node(NodePath(path)) as StaticBody3D
		assert(body!=null and body.is_queued_for_deletion() and body.get_script()==null and body.get_child_count()==1,"Only an already-queued original cabin-frame contact may retire")
		assert(body.get_parent() is MeshInstance3D and str(body.name)=="StaticContact")
		var contact: CollisionShape3D=body.get_node("SharedShape") as CollisionShape3D
		assert(contact!=null and contact.get_script()==null and contact.get_child_count()==0 and contact.shape is ConcavePolygonShape3D)
		assert(before.nodes[path].queued_for_deletion and int(before.nodes[path].id)==body.get_instance_id())
		assert(int(before.nodes[path+"/SharedShape"].id)==contact.get_instance_id())
		result[path]=body.get_instance_id()
		result[path+"/SharedShape"]=contact.get_instance_id()
	var queued:=0
	for path in before.nodes:
		if bool(before.nodes[path].queued_for_deletion):
			assert(str(path) in LEGACY_QUEUED_CONTACTS,"Any other old queued node needs separate source evidence")
			queued+=1
	assert(queued==3 and result.size()==6)
	return result

static func build(district: Node3D,ship: Node3D) -> void:
	assert(str(district.name)=="D12_D14_StarAtlas_WIP" and district.get_node_or_null(CHILD)==null)
	assert(not receipts.has(district.get_instance_id()))
	var auditing: bool=audit_enabled()
	var before: Dictionary={}
	var retiring: Dictionary={}
	var prior_children: Array[Node]=district.get_children()
	if auditing:
		before=snapshot(district)
		retiring=legacy_retirements(district,before)
	# No yield/frame/physics advancement occurs between these two exact snapshots.
	load("res://scripts/star_atlas_fitted_interiors.gd").build(district,ship)
	var fitted: Node3D=district.get_node(CHILD) as Node3D
	assert(fitted!=null and district.get_child_count()==prior_children.size()+1)
	for index in range(prior_children.size()): assert(district.get_child(index)==prior_children[index])
	assert(district.get_child(prior_children.size())==fitted)
	if not auditing: return
	var after: Dictionary=snapshot(district,fitted)
	assert(before==after,"New fitted builder changed a pre-existing Star Atlas node, transform, material, contact, metadata or child identity")
	receipts[district.get_instance_id()]={"before":before,"after":after,"before_hash":digest(before),"after_hash":digest(after),"added_node_id":fitted.get_instance_id(),"original_child_ids":prior_children.map(func(node: Node) -> int: return node.get_instance_id()),"owned_startup_snapshot":snapshot(fitted,null,true),"legacy_retirements":retiring,"synchronous_insertion_passed":true}

static func validate(district: Node3D) -> Dictionary:
	assert(audit_enabled(),"Actual preservation validation requires headless mode or ASTRAEA_STAR_ATLAS_AUDIT=1 before construction")
	assert(receipts.has(district.get_instance_id()),"Real insertion-time witness is mandatory")
	var record: Dictionary=receipts[district.get_instance_id()]
	assert(record.synchronous_insertion_passed and record.before==record.after and record.before_hash==digest(record.before) and record.after_hash==digest(record.after))
	var fitted: Node3D=district.get_node(CHILD) as Node3D
	assert(fitted!=null and fitted.get_instance_id()==int(record.added_node_id))
	assert(district.get_child_count()==record.original_child_ids.size()+1)
	for index in range(record.original_child_ids.size()): assert(district.get_child(index).get_instance_id()==int(record.original_child_ids[index]))
	# Later proof retains every old node/parent/child identity. Lift/gate startup
	# animation may legitimately evolve after the strict synchronous insertion check.
	# The original transport source/tests remain pinned and unchanged.
	var retired: Dictionary=record.legacy_retirements
	assert(retired.size()==6)
	for path in LEGACY_QUEUED_CONTACTS:
		assert(retired.has(path) and retired.has(path+"/SharedShape") and bool(record.before.nodes[path].queued_for_deletion))
		assert(int(retired[path])==int(record.before.nodes[path].id) and int(retired[path+"/SharedShape"])==int(record.before.nodes[path+"/SharedShape"].id))
	for path in retired:
		assert(district.get_node_or_null(NodePath(str(path)))==null,"Original queued cabin-frame contact must complete deferred retirement")
	for path in record.before.nodes:
		var expected: Dictionary=record.before.nodes[path]
		if retired.has(str(path)): continue
		var actual: Node=district if str(path)=="." else district.get_node_or_null(NodePath(str(path)))
		assert(actual!=null,"Unexpected missing old node outside the six proven deferred retirements: "+str(path))
		assert(actual.get_instance_id()==int(expected.id) and actual.get_class()==str(expected.class) and str(actual.name)==str(expected.name))
		assert(actual.get_parent().get_instance_id()==int(expected.parent_id))
		var child_ids: Array=[]
		for child in actual.get_children():
			if actual==district and child==fitted: continue
			child_ids.append(child.get_instance_id())
		var expected_surviving_children: Array=[]
		for id in expected.children:
			if int(id) not in retired.values(): expected_surviving_children.append(id)
		assert(child_ids==expected_surviving_children,"Every other old child identity/order must remain exact")
	assert(snapshot(fitted,null,true)==record.owned_startup_snapshot,"Owned fitted startup state changed beyond normal budget visibility/shadow selection")
	return {"passed":true,"preserved_old_nodes":record.before.nodes.size(),"old_state_before_sha256":record.before_hash,"old_state_after_sha256":record.after_hash,"legacy_deferred_contact_roots":3,"legacy_deferred_nodes":6,"owned_nodes":record.owned_startup_snapshot.nodes.size(),"scope":"Strict synchronous old-tree insertion preservation plus later old identity graph and exact new subtree startup state. Only three exact pre-existing queued cabin-frame contact subtrees (sixnodes) retire later; other old child identities remain exact. Later old animated poses are not falsely frozen; only new Light3D visible/shadow_enabled are omitted from the startup comparison."}
