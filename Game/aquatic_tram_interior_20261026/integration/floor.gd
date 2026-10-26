extends RefCounted
const P := "res://aquatic_tram_interior_20261026/integration/"

static func apply(ship: Node3D) -> bool:
	var proof: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(P+"PIT_AND_BINDING.json"))
	if FileAccess.get_sha256("res://data/generated/structural_meshes.json") != proof.compiled_source_sha256:
		push_error("Aquatic pit source mismatch");return false
	var parent := ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms")
	var original: Node3D = parent.get_node(proof.before.id)
	if original.has_meta("aquatic_pit_successor"):
		push_error("Duplicate Aquatic floor receiving");return false
	# Compare the complete generated collision representation to the same
	# retained builder output. Mesh.get_faces quantizes source coordinates;
	# comparing its points directly to unsnapped JSON falsely rejected217.7074508.
	# This checks every face exactly, including sides/underside, without raising
	# any clearance tolerance. The detached reference never joins physics.
	if not original.global_transform.is_equal_approx(Transform3D.IDENTITY):
		push_error("Aquatic original floor transform differs");return false
	var scratch:=Node3D.new()
	load("res://scripts/structural_floor_builder.gd").build_regions(scratch,null,null,[proof.before],{})
	var expected_shapes:=scratch.find_children("*","CollisionShape3D",true,false)
	var actual_shapes:=original.find_children("*","CollisionShape3D",true,false)
	var identical:=actual_shapes.size()==expected_shapes.size() and actual_shapes.size()==1
	if identical:
		identical=actual_shapes[0].shape is ConcavePolygonShape3D and actual_shapes[0].shape.get_faces()==expected_shapes[0].shape.get_faces()
	scratch.free()
	if not identical:
		push_error("Aquatic complete original floor collision faces differ from exact retained builder output");return false
	# Stage the exact replacement with inherited materials; keep the floor owner ID.
	var material: Material = null
	var side: Material = null
	for visual: MeshInstance3D in original.find_children("*","MeshInstance3D",true,false):
		if visual.mesh.get_surface_count()==2:
			material=visual.get_active_material(0);side=visual.get_active_material(1);break
	if not proof.before.get("render_chunks",[]).is_empty():
		var chunks:Array=proof.before.render_chunks
		var first:MeshInstance3D=original.get_node(chunks[0].id)
		material=first.get_active_material(0)
		for chunk:Dictionary in chunks:
			if original.get_node(chunk.id).get_active_material(0)!=material:
				push_error("Aquatic floor chunk material identity differs");return false
		side=original.get_node("StructuralSidesAndUnderside").get_active_material(0)
	if material==null or side==null:push_error("Original aquatic floor materials unavailable");return false
	var builder = load("res://scripts/structural_floor_builder.gd")
	var staged: Node3D = builder.build_regions(ship.get_node("ShipSpace"),material,side,[proof.after],{"guest_floor":material},"AquaticFloorReceivingStaging")
	var replacement: Node3D = staged.get_node(proof.after.id)
	for key: StringName in original.get_meta_list():replacement.set_meta(key,original.get_meta(key))
	original.free()
	replacement.reparent(parent,true)
	replacement.name=proof.after.id
	replacement.set_meta("aquatic_pit_successor",true)
	replacement.set_meta("pit_removed_m2",proof.removed_m2)
	staged.free()
	var infill: Node3D=builder.build_regions(ship.get_node("ShipSpace"),material,side,[proof.old_pit_infill],{"guest_floor":material},"RetiredAftmidPitClosure")
	infill.set_meta("new_room_or_capacity",false)
	return true
