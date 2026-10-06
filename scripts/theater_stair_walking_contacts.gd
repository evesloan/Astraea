extends RefCounted
# Same-family source-derived non-rendered walking contacts. Literal source contacts stay.
const CONTRACT := "res://data/architecture/THEATER_STAIR_WALK_CONTACTS_011.json"
const ROOT_NAME := "GrandLanternTheater_StairWalkingContacts"
static func build(parent: Node3D) -> void:
	assert(not parent.has_node(ROOT_NAME), "Duplicate stair walking-contact component")
	assert(parent.has_node("GrandLanternTheater_ConnectedStaticStage_WIP"), "Retained venue must exist first")
	assert(parent.global_transform.is_equal_approx(Transform3D.IDENTITY))
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.schema==1 and data.catalogue_family=="AST-CUL-005" and data.contact_count==8 and data.contacts.size()==8)
	assert(not data.rendered and not data.load_certification and not data.compiler_floor_credit and data.source_meshes_and_existing_contacts_retained)
	var component := Node3D.new()
	component.name = ROOT_NAME
	component.set_meta("persistent_id","grand_lantern_theater_stair_walking_contacts_011")
	component.set_meta("walking_contact_approximation",true)
	component.set_meta("rendered",false)
	component.set_meta("compiler_floor_credit",false)
	component.set_meta("load_certification",false)
	component.set_meta("source_original_blend_sha256",str(data.original_source_blend_sha256))
	component.set_meta("source_proposal_sha256",str(data.proposal_sha256))
	parent.add_child(component)
	for row in data.contacts:
		assert(row.source_meshes_and_existing_contacts_retained and row.vertices_world.size()==8 and row.faces.size()==12)
		assert(absf(float(row.width_m)-3.2)<.000001 and float(row.thickness_m)==.04 and float(row.shape_margin_m)==.001)
		assert(not component.has_node(str(row.id)))
		var body := StaticBody3D.new()
		body.name = str(row.id)
		body.collision_layer = 1
		body.collision_mask = 1
		body.set_meta("source_flight_id",str(row.source_flight.id))
		body.set_meta("walking_contact_approximation",true)
		body.set_meta("non_rendered",true)
		body.set_meta("original_meshes_and_contacts_retained",true)
		body.set_meta("source_lower_receivers",row.lower_landing_receivers)
		body.set_meta("source_upper_receivers",row.upper_landing_receivers)
		var points := PackedVector3Array()
		for value in row.vertices_world: points.append(Vector3(float(value[0]),float(value[1]),float(value[2])))
		var shape := ConvexPolygonShape3D.new()
		shape.points = points
		shape.margin = .001
		var contact := CollisionShape3D.new()
		contact.name = "SourceDerivedWalkingContact"
		contact.shape = shape
		body.add_child(contact)
		component.add_child(body)
	assert(component.get_child_count()==8)
