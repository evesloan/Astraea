# LAUNDRY_EXACT_SECTION_BEGIN
const LAUNDRY_PROOF="res://data/architecture/packages/laundry/RUNTIME_PROOF.json"
const LAUNDRY_PROOF_SHA="e3ed362925a429ad2080b0fc7c42722b8992d8a6d3a0fa110d8edf2b03c8e2a0"
static var laundry_checked:=false
static var laundry_old:Dictionary={}
static var laundry_current_compiled:Dictionary={}
static var laundry_proof:Dictionary={}
static func _laundry_ensure()->void:
	if laundry_checked:return
	assert(FileAccess.get_sha256(LAUNDRY_PROOF)==LAUNDRY_PROOF_SHA)
	laundry_proof=JSON.parse_string(FileAccess.get_file_as_string(LAUNDRY_PROOF))
	for path in laundry_proof.predecessors:
		var spec:Dictionary=laundry_proof.predecessors[path]
		var file:String="res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(file)==str(spec.sha256))
		laundry_old[path]=FileAccess.get_file_as_string(file)
	for path in laundry_proof.current_sha256:
		assert(FileAccess.get_sha256("res://"+str(path))==str(laundry_proof.current_sha256[path]))
	for path in laundry_proof.inverse_edits:
		var current:=FileAccess.get_file_as_string("res://"+str(path))
		if str(path)=="tests/medical_triage_successor_guard.gd":
			var a:String="# LAUNDRY_EXACT_SECTION_"+"BEGIN\n"
			var z:String="# LAUNDRY_EXACT_SECTION_"+"END\n"
			assert(current.count(a)==1 and current.count(z)==1)
			var i:=current.find(a);var j:=current.find(z)+z.length()
			assert(current.substr(i,j-i).replace(LAUNDRY_PROOF_SHA,"<PROOF_SHA>").sha256_text()==str(laundry_proof.block_normalized_sha256))
			current=current.substr(0,i)+current.substr(j)
		for edit in laundry_proof.inverse_edits[path]:
			assert(current.count(str(edit.after))==int(edit.count))
			current=current.replace(str(edit.after),str(edit.before))
		assert(current==str(laundry_old[path]),"Laundry must preserve every predecessor byte")
	var layout:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/spatial_layout.json"))
	var old_layout:Dictionary=JSON.parse_string(str(laundry_old["data/spatial_layout.json"]))
	laundry_current_compiled=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	var old_compiled_n:Dictionary=JSON.parse_string(str(laundry_old["data/generated/structural_meshes.json"]))
	for pair in [[layout,old_layout,laundry_proof.added_layout],[laundry_current_compiled,old_compiled_n,laundry_proof.added_compiled]]:
		var wanted:Array=pair[1].regions.duplicate(true);wanted.append_array(pair[2])
		assert(pair[0].regions==wanted)
		var ids:Dictionary={}
		for row in pair[0].regions:assert(not ids.has(row.id));ids[row.id]=true
	var a:Dictionary=layout.duplicate(true);var b:Dictionary=old_layout.duplicate(true)
	a.erase("regions");b.erase("regions");assert(a==b)
	a=laundry_current_compiled.duplicate(true);b=old_compiled_n.duplicate(true)
	for key in ["regions","source_checks"]:a.erase(key);b.erase(key)
	assert(a==b)
	assert(laundry_current_compiled.source_checks==JSON.parse_string(FileAccess.get_file_as_string("res://docs/LAYOUT_COMPILE_CHECKS.json")))
	assert(laundry_current_compiled.regions.size()==286 and old_compiled_n.regions.size()==284)
	laundry_checked=true
static func _laundry_current_text(path:String)->String:
	_laundry_ensure()
	var key:=path.trim_prefix("res://")
	return str(laundry_old[key]) if laundry_old.has(key) else FileAccess.get_file_as_string(path)
static func _laundry_current_sha256(path:String)->String:
	_laundry_ensure()
	return _laundry_current_text(path).sha256_text() if laundry_old.has(path.trim_prefix("res://")) else FileAccess.get_sha256(path)
static func _laundry_floor_children(floors:Node)->Array:
	_laundry_ensure()
	assert(floors!=null and floors.get_child_count()==286)
	var children:=floors.get_children();var retained:Array=[]
	for i in range(children.size()):
		var row:Dictionary=laundry_current_compiled.regions[i]
		assert(str(children[i].name)==str(row.id))
		_botanical_validate_slab(children[i],row)
		if i<284:retained.append(children[i])
	return retained
static func _laundry_validate_runtime(ship:Node)->void:
	_laundry_ensure()
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/laundry/runtime_manifest.json"))
	var root:Node3D=ship.get_node("ShipSpace/"+str(data.root_name))
	assert(root.transform==Transform3D.IDENTITY and root.get_child_count()==1)
	assert(root.get_meta("operational_acceptance")==false)
	var wrapper:Node3D=root.get_node("LaundrySource")
	assert(wrapper.position==Vector3.ZERO and wrapper.basis==Basis.IDENTITY)
	var original:Node3D=(load("res://assets/models/"+str(data.model_file))as PackedScene).instantiate()
	assert(wrapper.get_child_count()==1)
	var visual:Node3D=wrapper.get_child(0);assert(visual.transform==original.transform)
	var count:=0
	for mesh in original.find_children("*","MeshInstance3D",true,false):
		var actual:MeshInstance3D=visual.get_node(original.get_path_to(mesh))
		assert(actual.transform==mesh.transform and actual.mesh==mesh.mesh and actual.material_override==null)
		var collision:CollisionShape3D=actual.get_node("StaticContact/SharedShape")
		assert(collision.shape.get_faces()==mesh.mesh.create_trimesh_shape().get_faces())
		count+=1
	assert(count>0)
	for spec in data.lights:
		var light:Light3D=visual.find_child(str(spec.runtime_name),true,false)
		assert(light!=null and is_equal_approx(light.light_energy,float(spec.energy)))
		assert(light.light_color.is_equal_approx(Color(spec.color[0],spec.color[1],spec.color[2])))
		assert(light.get_meta("source_light_name")==str(spec.source_name))
	original.free()
# LAUNDRY_EXACT_SECTION_END
