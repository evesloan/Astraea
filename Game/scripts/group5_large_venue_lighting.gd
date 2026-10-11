extends RefCounted
# Additive ordinary lighting from actual immutable large-venue fixture lenses.
# The existing eight-shadow-source manager remains authoritative.
static func build(ship:Node3D)->Array[Light3D]:
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/LARGE_VENUE_LIGHTING.json"))
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	assert(budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
	var lights:Array[Light3D]=[]
	for row in definition.venues:
		assert(FileAccess.get_sha256(str(row.model_path))==str(row.model_sha256),"Group5 venue model pin changed")
		var owner:Node3D=_owner(ship,str(row.programme_key))
		assert(owner!=null,"Existing Group5 large-venue owner missing")
		assert(owner.position.distance_to(_vec(row.translation_xyz))<.00001 and absf(owner.rotation.y-float(row.rotation_y))<.00001)
		if owner.has_node("Group5SourceLighting"):
			for light:Light3D in owner.get_node("Group5SourceLighting").get_children():lights.append(light)
			continue
		if row.has("fixture_clearance"):_apply_fixture_clearance(ship,owner,row.fixture_clearance)
		var sources:=Node3D.new()
		sources.name="Group5SourceLighting"
		owner.add_child(sources)
		for item in row.fixtures:
			var lens:MeshInstance3D=owner.find_child(str(item.lens_mesh),true,false)
			assert(lens!=null,"Literal source fixture lens missing")
			var box:AABB=_relative_transform(lens,owner)*lens.get_aabb()
			assert(box.position.distance_to(_vec(item.lens_bounds[0]))<.00004 and box.end.distance_to(_vec(item.lens_bounds[1]))<.00004)
			var light:=OmniLight3D.new()
			light.name=str(item.name)
			light.position=_vec(item.local_xyz)
			light.light_color=Color(item.color[0],item.color[1],item.color[2])
			light.light_energy=float(item.energy)
			light.omni_range=float(item.range_m)
			light.omni_attenuation=1.2
			light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE
			light.shadow_bias=.03
			light.shadow_normal_bias=.3
			light.visible=false
			light.shadow_enabled=false
			light.set_meta("fixture_powered",true)
			light.set_meta("source_fixture",str(item.lens_mesh))
			light.set_meta("source_programme_key",str(row.programme_key))
			light.set_meta("calibration","first_pass_unaccepted")
			sources.add_child(light)
			budget.sources.append(light)
			budget.requested_shadow[light.get_instance_id()]=true
			lights.append(light)
	assert(lights.size()==109)
	ship.set_meta("group5_large_venue_lighting_attached",true)
	budget.refresh()
	return lights

static func _owner(ship:Node3D,key:String)->Node3D:
	var received:Node3D=ship.get_node("ShipSpace/Districts/ReceivedSections")
	var current:=received.get_node_or_null(key) as Node3D
	if current!=null:return current
	var residency:=ship.get_node_or_null("ShipSystems/ReceivedRoomResidency")
	if residency!=null:
		for entry in residency.entries:
			if str(entry.room.name)==key:return entry.room
	return null

static func _vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])

static func _relative_transform(node:Node3D,owner:Node3D)->Transform3D:
	var result:=node.transform
	var ancestor:=node.get_parent() as Node3D
	while ancestor!=owner:
		assert(ancestor!=null)
		result=ancestor.transform*result
		ancestor=ancestor.get_parent() as Node3D
	return result

static func _apply_fixture_clearance(ship:Node3D,owner:Node3D,revision:Dictionary)->void:
	assert(FileAccess.get_sha256(str(revision.model_path))==str(revision.model_sha256),"Group5 fixture derivative pin changed")
	var original_count:int=owner.find_children("*","MeshInstance3D",true,false).size()
	var preserved:Dictionary={}
	for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
		if not str(mesh.name) in revision.replaced_mesh_names:
			preserved[mesh.get_instance_id()]=_relative_transform(mesh,owner)
	for name in revision.replaced_mesh_names:
		var original:MeshInstance3D=owner.find_child(str(name),true,false)
		assert(original!=null,"Pinned original fixture member missing")
		original.free()
	var revised:Node3D=(load(str(revision.model_path)) as PackedScene).instantiate()
	revised.name="Group5FixtureClearance"
	owner.add_child(revised)
	ship._static_contacts(revised)
	assert(owner.find_children("*","MeshInstance3D",true,false).size()==original_count)
	var checks:=0
	for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
		if preserved.has(mesh.get_instance_id()):
			assert(_relative_transform(mesh,owner).is_equal_approx(preserved[mesh.get_instance_id()]))
			checks+=1
	assert(checks==preserved.size())
	owner.set_meta("group5_fixture_preserved_meshes",checks)
	owner.set_meta("group5_fixture_source_pin",str(revision.model_sha256))
