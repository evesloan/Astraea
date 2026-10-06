extends RefCounted
# Separate signage-only candidate. No calibration/audio/control installation.
const CONTRACT := "res://data/architecture/ENGINEERING_CELL_SIGNAGE_RUNTIME.json"
const FIXED := "SIGN_FIXED_EAST_HEADER"
const PRINT := "SIGN_MOVING_GLASS_LEAF"

static func build(cell: Node3D, gate: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.runtime_adoption_approved and data.precision_approved and not data.first_pass_accepted)
	assert(data.groups.size()==2 and data.groups.has(FIXED) and data.groups.has(PRINT))
	assert(FileAccess.get_sha256("res://assets/models/"+str(data.model_file))==str(data.model_sha256))
	var settings := ConfigFile.new()
	assert(settings.load("res://assets/models/"+str(data.model_file)+".import")==OK)
	assert(settings.get_value("params","meshes/force_disable_compression",false),"Thin source ink requires the separately reviewed new-asset precision setting")
	assert(gate!=null and gate.leaves.size()==1 and not gate.desired_open and is_zero_approx(gate.open_fraction))
	assert(cell.get_node_or_null("CellRestrictionSignage")==null)
	var added := (load("res://assets/models/"+str(data.model_file)) as PackedScene).instantiate() as Node3D
	added.name="CellRestrictionSignage"
	cell.add_child(added)
	assert(added.global_transform.is_equal_approx(Transform3D.IDENTITY))
	assert(added.find_children("*","CollisionObject3D",true,false).is_empty() and added.find_children("*","Light3D",true,false).is_empty())
	var parts := added.find_children("*","MeshInstance3D",true,false)
	assert(parts.size()==2)
	var seen: Dictionary={}
	for value in parts:
		var mesh := value as MeshInstance3D
		var label := str(mesh.name)
		assert(data.groups.has(label) and not seen.has(label))
		seen[label]=true
		var expected: Dictionary=data.groups[label]
		assert(mesh.mesh!=null and raw_render_faces(mesh.mesh).size()==int(expected.triangles)*3 and mesh.material_override==null)
		assert(mesh.mesh.get_surface_count()==expected.materials.size())
		for surface in range(mesh.mesh.get_surface_count()):
			assert(mesh.get_surface_override_material(surface)==null)
			var material := mesh.get_active_material(surface) as StandardMaterial3D
			assert(material!=null and material.resource_name==str(expected.materials[surface]) and not material.emission_enabled)
		mesh.set_meta("signage_model_sha256",str(data.model_sha256))
		mesh.set_meta("signage_canonical_world",mesh.global_transform)
		mesh.set_meta("signage_collision_contract","none")
	var leaf := gate.leaves[0].find_child("LEAF_WORKBAY_CELL",true,false) as MeshInstance3D
	var ink := added.find_child(PRINT,true,false) as MeshInstance3D
	var fixed := added.find_child(FIXED,true,false) as MeshInstance3D
	assert(leaf!=null and ink!=null and fixed!=null)
	var rest := ink.global_transform
	ink.reparent(leaf,true)
	assert(ink.global_transform.is_equal_approx(rest))
	ink.set_meta("signage_parent_local",ink.transform)
	cell.set_meta("signage_original_leaf",leaf)
	cell.set_meta("signage_print",ink)
	cell.set_meta("signage_fixed",fixed)
	cell.set_meta("signage_contract",data)
	cell.set_meta("signage_capture_readability_accepted",false)
	assert(live_binding_valid(cell))

static func live_binding_valid(cell: Node3D) -> bool:
	if not is_instance_valid(cell) or not cell.has_meta("signage_contract"): return false
	var leaf := cell.get_meta("signage_original_leaf") as MeshInstance3D
	var ink := cell.get_meta("signage_print") as MeshInstance3D
	var fixed := cell.get_meta("signage_fixed") as MeshInstance3D
	if not is_instance_valid(leaf) or not is_instance_valid(ink) or not is_instance_valid(fixed): return false
	if ink.get_parent()!=leaf or ink.transform!=ink.get_meta("signage_parent_local"): return false
	if not fixed.global_transform.is_equal_approx(fixed.get_meta("signage_canonical_world")): return false
	return ink.find_children("*","CollisionObject3D",true,false).is_empty() and fixed.find_children("*","CollisionObject3D",true,false).is_empty()

static func exact_core_meshes(cell: Node3D, original: Dictionary) -> Array[MeshInstance3D]:
	assert(live_binding_valid(cell))
	var data: Dictionary=cell.get_meta("signage_contract")
	var result: Array[MeshInstance3D]=[]
	var originals: Dictionary={}
	var additions: Dictionary={}
	var all := cell.find_children("*","MeshInstance3D",true,false)
	assert(all.size()==155 and original.groups.size()==153)
	for value in all:
		var mesh := value as MeshInstance3D
		var label := str(mesh.name)
		if original.groups.has(label):
			assert(not originals.has(label))
			originals[label]=true
			result.append(mesh)
		else:
			assert(data.groups.has(label) and not additions.has(label))
			assert(mesh==cell.get_meta("signage_print") or mesh==cell.get_meta("signage_fixed"))
			assert(str(mesh.get_meta("signage_model_sha256"))==str(data.model_sha256))
			assert(raw_render_faces(mesh.mesh).size()==int(data.groups[label].triangles)*3)
			assert(mesh.find_children("*","CollisionShape3D",true,false).is_empty())
			additions[label]=true
	assert(result.size()==153 and originals.size()==153 and additions.size()==2 and additions.has(FIXED) and additions.has(PRINT))
	return result

static func raw_render_faces(mesh: Mesh) -> PackedVector3Array:
	# get_faces() routes through TriangleMesh.create() and snaps by0.0001m.
	# Printed ink is render-only, so preserve native surface arrays here.
	var points := PackedVector3Array()
	for surface in range(mesh.get_surface_count()):
		var arrays: Array=mesh.surface_get_arrays(surface)
		var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
		var indices := PackedInt32Array()
		if arrays[Mesh.ARRAY_INDEX]!=null: indices=arrays[Mesh.ARRAY_INDEX]
		if indices.is_empty(): points.append_array(vertices)
		else:
			for index in indices:points.append(vertices[index])
	assert(not points.is_empty() and points.size()%3==0)
	return points
