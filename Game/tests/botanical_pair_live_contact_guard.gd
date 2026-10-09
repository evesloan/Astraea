extends RefCounted
# Scoped importer fidelity is necessary but not sufficient for actual-world access.
# Match every imported hierarchy/mesh/material and its production static contact
# against each actual main-scene source root, without removing scene obstacles.
static func validate_current(ship: Node3D,data: Dictionary) -> Dictionary:
	var manifest: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(str(data.runtime_manifest)))
	var rows: Array=[]
	for section in manifest.sections:
		var relative: String="ShipSpace/"+str(manifest.root_name)+"/"+str(section.root_name)+"/Source"
		rows.append(_compare(ship,relative,str(section.model_file),Vector3(float(section.position[0]),float(section.position[1]),float(section.position[2]))))
	rows.append(_compare(ship,"ShipSpace/"+str(manifest.root_name)+"/CloudLinkAuthoredReceivingGuards",str(manifest.cloud_link_guard.model_file),Vector3.ZERO))
	for row in rows:
		if not row is Dictionary or not bool(row.get("actual_main_scene_correspondence",false)):
			return {"validation_completed":false,"detail":"An actual main-scene correspondence check did not finish"}
	return {"validation_completed":true,"actual_main_scene_sources":rows,"scope":"All imported room/link mesh resources, hierarchy, transforms, material overrides and generated mesh-local triangle contacts matched in the actual main scene; court and Moss use the independent complete medical chain."}

static func _compare(ship: Node3D,path: String,file: String,position: Vector3) -> Dictionary:
	var wrapper: Node3D=ship.get_node(NodePath(path)) as Node3D
	assert(wrapper!=null and wrapper.get_meta("catalogue_file","")==file,"Exact assembled source root required")
	assert(wrapper.position==position and wrapper.basis==Basis.IDENTITY and wrapper.get_child_count()==1,"Assembled source placement or hierarchy changed")
	var actual: Node3D=wrapper.get_child(0) as Node3D
	var expected: Node3D=(load("res://assets/models/"+file) as PackedScene).instantiate()
	assert(actual.name==expected.name and actual.transform==expected.transform,"Imported root differs in actual main scene")
	var expected_nodes: Array=[expected];expected_nodes.append_array(expected.find_children("*","Node",true,false))
	var count: int=0
	var triangles: int=0
	for node in expected_nodes:
		var relative: NodePath=expected.get_path_to(node)
		var live: Node=actual.get_node(relative)
		assert(live!=null and live.get_class()==node.get_class(),"Actual source hierarchy/class changed: "+str(relative))
		if node is Node3D: assert((live as Node3D).transform==(node as Node3D).transform,"Actual source local transform changed: "+str(relative))
		if node is MeshInstance3D:
			var source: MeshInstance3D=node as MeshInstance3D
			var part: MeshInstance3D=live as MeshInstance3D
			assert(source.mesh!=null and part.mesh==source.mesh and part.visible==source.visible and part.is_visible_in_tree(),"Actual source mesh/resource/visibility changed: "+str(relative))
			assert(part.material_override==source.material_override and part.material_overlay==source.material_overlay,"Actual room/link material override changed")
			assert(part.mesh.get_surface_count()==source.mesh.get_surface_count())
			for surface in range(source.mesh.get_surface_count()): assert(part.get_surface_override_material(surface)==source.get_surface_override_material(surface),"Actual per-surface material changed")
			var body: StaticBody3D=part.get_node("StaticContact") as StaticBody3D
			assert(body!=null and body.transform==Transform3D.IDENTITY and body.collision_layer==1 and body.collision_mask==1 and body.get_child_count()==1,"Actual production mesh-local body changed")
			var contact: CollisionShape3D=body.get_node("SharedShape") as CollisionShape3D
			assert(contact!=null and not contact.disabled and contact.transform==Transform3D.IDENTITY and contact.shape is ConcavePolygonShape3D,"Actual generated static contact changed")
			var expected_shape: ConcavePolygonShape3D=source.mesh.create_trimesh_shape()
			assert(contact.shape.get_faces()==expected_shape.get_faces(),"Actual contact triangle arrays differ from the verified source import")
			triangles+=contact.shape.get_faces().size()/3
			count+=1
	assert(count>0 and actual.find_children("*","MeshInstance3D",true,false).size()==expected.find_children("*","MeshInstance3D",true,false).size(),"Actual room/link mesh roster differs")
	assert(actual.find_children("*","StaticBody3D",true,false).size()==count and actual.find_children("*","CollisionShape3D",true,false).size()==count,"Missing or extra actual room/link contact bodies")
	assert(actual.find_children("*","Node",true,false).size()==expected.find_children("*","Node",true,false).size()+2*count,"Missing or added actual source hierarchy records")
	expected.free()
	return {"source":file,"root":path,"meshes":count,"contact_triangles":triangles,"actual_main_scene_correspondence":true}
