extends RefCounted
const LABEL := "UNVERIFIED_IMPORT_EQUIVALENCE"
var records: Array=[]
var all_meshes: Array[MeshInstance3D]=[]
var plant_meshes: Array[MeshInstance3D]=[]

func v3(a: Array) -> Vector3: return Vector3(a[0],a[1],a[2])

func vec(p: Vector3) -> Array: return [p.x,p.y,p.z]

func matrix(a: Transform3D) -> Array:
	return [[a.basis.x.x,a.basis.y.x,a.basis.z.x,a.origin.x],[a.basis.x.y,a.basis.y.y,a.basis.z.y,a.origin.y],[a.basis.x.z,a.basis.y.z,a.basis.z.z,a.origin.z],[0,0,0,1]]

func typed_json_delta(original: Variant,current: Variant,path: String,rows: Array) -> void:
	if typeof(original)!=typeof(current):
		rows.append({"path":path,"kind":"type_changed","original_type":type_string(typeof(original)),"state_type":type_string(typeof(current)),"original":original,"state":current})
		return
	if original is Dictionary:
		for key in original:
			var child: String=path+"/"+str(key).replace("~","~0").replace("/","~1")
			if not current.has(key):rows.append({"path":child,"kind":"removed","original_type":type_string(typeof(original[key])),"original":original[key]})
			else:typed_json_delta(original[key],current[key],child,rows)
		for key in current:
			if not original.has(key):rows.append({"path":path+"/"+str(key).replace("~","~0").replace("/","~1"),"kind":"added","state_type":type_string(typeof(current[key])),"state":current[key]})
	elif original is Array:
		for i in range(maxi(original.size(),current.size())):
			var child: String=path+"/"+str(i)
			if i>=original.size():rows.append({"path":child,"kind":"added","state_type":type_string(typeof(current[i])),"state":current[i]})
			elif i>=current.size():rows.append({"path":child,"kind":"removed","original_type":type_string(typeof(original[i])),"original":original[i]})
			else:typed_json_delta(original[i],current[i],child,rows)
	elif original!=current:
		rows.append({"path":path,"kind":"value_changed","original_type":type_string(typeof(original)),"state_type":type_string(typeof(current)),"original":original,"state":current})

func record_runtime_json_diagnostic(original: Dictionary,current: Dictionary,asset: Dictionary,out: String) -> void:
	# Diagnostic only: runtime state is an importer working document, not an
	# immutable copy. Actual resource/geometry/transform/physics gates follow.
	var delta: Array=[];typed_json_delta(original,current,"",delta)
	var observed_insertion: bool=not original.has("extensionsUsed") and current.has("extensionsUsed") and current["extensionsUsed"]==null
	save_json(out+"/"+str(asset.name)+"_GLTF_STATE_JSON_DIAGNOSTIC.json",{"installed":false,"production_changes":false,"asset":asset.name,"immutable_glb_sha256":asset.sha256,"whole_state_equality_is_not_a_gate":true,"typed_recursive_delta":delta,"original_glb_json":original,"runtime_state_json":current,"source_identified_normalization":{"path":"/extensionsUsed","expected":"absent to null because importer preflight uses mutable Dictionary operator[]","observed_this_run":observed_insertion,"importer_source":"https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/modules/gltf/gltf_document.cpp#L6221","dictionary_source":"https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/core/variant/dictionary.cpp#L93"}})

func resolve_declared_node(parent: Node3D,index: int,parent_index: int,doc: Dictionary,state: GLTFState,resolved: Dictionary,names: Dictionary,rows: Array) -> void:
	assert(index>=0 and index<doc.nodes.size() and not resolved.has(index),"Invalid/cyclic/repeated declared GLB node")
	var source: Dictionary=doc.nodes[index]
	var expected_name: String=str(source.name).validate_node_name()
	assert(not names.has(expected_name),"Validated GLB names are not a complete bijection")
	names[expected_name]=index
	# Never use GLTFState.get_scene_node after generate_scene: runtime mesh
	# conversion replaces and deletes ImporterMeshInstance3D without updating it.
	var node: Node3D=parent.get_node_or_null(NodePath(expected_name))as Node3D
	assert(node!=null and node.get_parent()==parent and str(node.name)==expected_name,"Exact declared child path missing after conversion")
	var gltf_node: GLTFNode=state.get_nodes()[index]
	assert(gltf_node.original_name==str(source.name) and int(gltf_node.parent)==parent_index)
	assert(str(gltf_node.resource_name)==expected_name,"Imported name generation was not the verified bijection")
	var mesh_id: int=-1
	if source.has("mesh"):
		var mesh: MeshInstance3D=node as MeshInstance3D
		assert(mesh!=null and mesh.mesh!=null)
		var gltf_mesh: GLTFMesh=state.get_meshes()[int(source.mesh)]
		var importer_mesh: ImporterMesh=gltf_mesh.mesh
		assert(importer_mesh!=null and mesh.mesh==importer_mesh.get_mesh(),"Actual converted ArrayMesh identity differs from declared GLTF mesh")
		mesh_id=mesh.mesh.get_instance_id()
	else:assert(node.get_class()=="Node3D","Unexpected native class for source marker/root")
	resolved[index]=node
	rows.append({"source_node_index":index,"source_name":source.name,"validated_name":expected_name,"parent_source_index":parent_index,"native_parent":str(parent.get_path()),"native_path":str(node.get_path()),"native_class":node.get_class(),"declared_mesh_index":int(source.get("mesh",-1)),"native_mesh_resource_id":mesh_id,"exact_declared_hierarchy":true})
	var children: Array=source.get("children",[])
	assert(node.get_child_count()==children.size(),"Unexpected/missing generated node descendants")
	for child in children:resolve_declared_node(node,int(child),index,doc,state,resolved,names,rows)

func resolve_generated_tree(root: Node3D,doc: Dictionary,state: GLTFState) -> Dictionary:
	assert(not "GODOT_single_root" in doc.get("extensionsUsed",[]),"Unreviewed root convention")
	assert(doc.scenes.size()==1)
	var roots: Array=doc.scenes[int(doc.get("scene",0))].nodes
	assert(root.get_child_count()==roots.size(),"Generated scene wrapper differs from declared GLB roots")
	var resolved: Dictionary={};var names: Dictionary={};var rows: Array=[]
	for index in roots:resolve_declared_node(root,int(index),-1,doc,state,resolved,names,rows)
	assert(resolved.size()==doc.nodes.size() and names.size()==doc.nodes.size(),"Generated-tree bijection incomplete")
	return {"by_index":resolved,"records":rows}
func save_json(path: String,value: Dictionary) -> void:
	value["verification"]=LABEL;value["installed"]=false;value["geometry_acceptance"]=false;value["physical_acceptance"]=false;value["final_acceptance"]=false
	var file:=FileAccess.open(path,FileAccess.WRITE);assert(file!=null)
	file.store_string(JSON.stringify(value,"  ",true,true));file.close()
func save_bytes(path: String,bytes: PackedByteArray) -> Dictionary:
	var file:=FileAccess.open(path,FileAccess.WRITE);assert(file!=null);file.store_buffer(bytes);file.close()
	return {"file":path,"bytes":bytes.size(),"sha256":FileAccess.get_sha256(path),"verification":LABEL,"installed":false,"geometry_acceptance":false}
func scalar(value: Variant) -> Variant:
	if value==null or value is bool or value is int or value is float or value is String:return value
	if value is StringName or value is NodePath:return str(value)
	if value is Color:return [value.r,value.g,value.b,value.a]
	if value is Vector2 or value is Vector2i:return [value.x,value.y]
	if value is Vector3 or value is Vector3i:return [value.x,value.y,value.z]
	if value is Vector4 or value is Vector4i:return [value.x,value.y,value.z,value.w]
	if value is Transform3D:return matrix(value)
	if value is Resource:return {"class":value.get_class(),"id":value.get_instance_id(),"resource_name":value.resource_name,"resource_path":value.resource_path}
	return {"type":type_string(typeof(value)),"text":str(value)}
func dump_material(material: Material,base: String) -> Dictionary:
	if material==null:return {"present":false}
	var properties: Dictionary={};var textures: Array=[]
	for property in material.get_property_list():
		var name: String=str(property.name)
		if (int(property.usage)&PROPERTY_USAGE_STORAGE)==0:continue
		var value: Variant=material.get(name)
		properties[name]={"type":type_string(typeof(value)),"value":scalar(value)}
		if value is Texture2D:
			var image: Image=value.get_image()
			var row: Dictionary={"property":name,"resource_id":value.get_instance_id(),"resource_path":value.resource_path,"image_available":image!=null}
			if image!=null:
				row["format"]=image.get_format();row["width"]=image.get_width();row["height"]=image.get_height();row["mipmaps"]=image.has_mipmaps();row["compressed"]=image.is_compressed()
				row["actual_pixel_bytes"]=save_bytes(base+"_"+name.validate_filename()+".pixels",image.get_data())
			textures.append(row)
	return {"present":true,"class":material.get_class(),"resource_name":material.resource_name,"resource_id":material.get_instance_id(),"resource_path":material.resource_path,"properties":properties,"textures":textures,"material_mutated":false}
func dump_actual_tree(root: Node3D,asset: Dictionary,out: String) -> Array:
	# Dump all actual nodes/surfaces before any hierarchy, shape or material check.
	var rows: Array=[];var pending: Array[Node]=[root];var ordinal: int=0
	while not pending.is_empty():
		var node: Node=pending.pop_front()
		for child in node.get_children():pending.append(child)
		var row: Dictionary={"name":str(node.name),"path_from_import_root":str(root.get_path_to(node)),"class":node.get_class(),"id":node.get_instance_id()}
		if node is Node3D:row["local_transform"]=matrix(node.transform);row["actual_world_transform"]=matrix(node.global_transform);row["visible"]=node.visible
		if node is MeshInstance3D and node.mesh!=null:
			var surfaces: Array=[]
			for si in range(node.mesh.get_surface_count()):
				var arrays: Array=node.mesh.surface_get_arrays(si)
				var base: String=out+"/"+str(asset.name)+"_mesh"+str(ordinal)+"_s"+str(si)
				var surface: Dictionary={"surface":si,"format":node.mesh.surface_get_format(si),"compression_disabled":(node.mesh.surface_get_format(si)&Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES)==0,"raw_arrays_godot_variant_binary":save_bytes(base+".arrays",var_to_bytes(arrays)),"array_slots":[],"actual_tangent_array":Array(arrays[Mesh.ARRAY_TANGENT]) if arrays[Mesh.ARRAY_TANGENT]!=null else [],"active_material":dump_material(node.get_active_material(si),base+"_material")}
				for slot in range(arrays.size()):
					var value: Variant=arrays[slot]
					surface.array_slots.append({"slot":slot,"type":type_string(typeof(value)),"elements":value.size() if value!=null else 0})
				surfaces.append(surface)
			row["mesh_resource_id"]=node.mesh.get_instance_id();row["mesh_resource_name"]=node.mesh.resource_name;row["cast_shadow"]=node.cast_shadow;row["surfaces"]=surfaces
			row["material_override"]=dump_material(node.material_override,out+"/"+str(asset.name)+"_mesh"+str(ordinal)+"_override")
			row["material_overlay"]=dump_material(node.material_overlay,out+"/"+str(asset.name)+"_mesh"+str(ordinal)+"_overlay")
			ordinal+=1
		rows.append(row)
	save_json(out+"/"+str(asset.name)+"_ACTUAL_NATIVE_DUMP.json",{"asset":asset.name,"glb_sha256":asset.sha256,"phase":"UNCONDITIONAL_BEFORE_ANY_ACCEPTANCE_CHECK","nodes":rows,"matcher":"PENDING_DIAGNOSTIC_NOT_RUN","physical":"PENDING_DIAGNOSTIC_NOT_RUN"})
	return rows
func load_checked(asset: Dictionary,parent: Node3D,out: String) -> Dictionary:
	assert(FileAccess.get_sha256(str(asset.path))==str(asset.sha256),"Immutable source GLB changed")
	var raw: PackedByteArray=FileAccess.get_file_as_bytes(str(asset.path));var count: int=raw.decode_u32(12)
	var doc: Dictionary=JSON.parse_string(raw.slice(20,20+count).get_string_from_utf8())
	var state:=GLTFState.new();state.handle_binary_image_mode=3;state.create_animations=false
	var document:=GLTFDocument.new();assert(document.append_from_buffer(raw,str(asset.path).get_base_dir(),state,64)==OK)
	record_runtime_json_diagnostic(doc,state.json,asset,out)
	var root: Node3D=document.generate_scene(state)as Node3D;assert(root!=null);parent.add_child(root)
	var actual_dump: Array=dump_actual_tree(root,asset,out)
	# This binding is needed only to place source markers/instances safely.
	# It is not a raw geometry, material, contact or acceptance gate.
	var actual_tree: Dictionary=resolve_generated_tree(root,doc,state)
	var nodes: Dictionary={};var extras: Dictionary={};var batches: int=0;var triangles: int=0;var materials: Array=[]
	for ni in range(doc.nodes.size()):
		var source: Dictionary=doc.nodes[ni];var node: Node3D=actual_tree.by_index[ni]
		nodes[str(source.name)]=node;extras[str(source.name)]=source.get("extras",{})
		if node is MeshInstance3D and node.mesh!=null:
			all_meshes.append(node)
			if asset.family=="plant":plant_meshes.append(node)
			batches+=1
			for si in range(node.mesh.get_surface_count()):
				var arrays: Array=node.mesh.surface_get_arrays(si)
				triangles+=arrays[Mesh.ARRAY_INDEX].size()/3 if arrays[Mesh.ARRAY_INDEX]!=null else arrays[Mesh.ARRAY_VERTEX].size()/3
				var material: Material=node.get_active_material(si)
				materials.append({"mesh":source.name,"surface":si,"material":material.resource_name if material!=null else "MISSING","native_material_id":material.get_instance_id() if material!=null else -1,"state_material_identity":material==state.get_materials()[int(doc.meshes[int(source.mesh)].primitives[si].material)]})
	records.append({"asset":asset.name,"actual_batches":batches,"actual_triangles":triangles,"native_dump":out+"/"+str(asset.name)+"_ACTUAL_NATIVE_DUMP.json","verification":LABEL,"matcher":"PENDING","physical":"PENDING"})
	return {"root":root,"nodes":nodes,"extras":extras,"materials":materials,"state":state,"document":document,"node_mapping":actual_tree.records,"mesh_batches":batches,"triangles":triangles,"asset":asset,"actual_dump":actual_dump}
func dump_after_first_draw(out: String) -> void:
	assert(DirAccess.make_dir_recursive_absolute(out)==OK)
	var surfaces: Array=[];var ordinal: int=0
	for mesh in all_meshes:
		for si in range(mesh.mesh.get_surface_count()):
			var arrays: Array=mesh.mesh.surface_get_arrays(si)
			var base: String=out+"/mesh"+str(ordinal)+"_s"+str(si)
			surfaces.append({"mesh":str(mesh.get_path()),"mesh_resource_id":mesh.mesh.get_instance_id(),"surface":si,"format":mesh.mesh.surface_get_format(si),"actual_world_transform":matrix(mesh.global_transform),"raw_arrays_godot_variant_binary":save_bytes(base+".arrays",var_to_bytes(arrays)),"actual_tangent_array":Array(arrays[Mesh.ARRAY_TANGENT]) if arrays[Mesh.ARRAY_TANGENT]!=null else []})
		ordinal+=1
	save_json(out+"/AFTER_FIRST_CANDIDATE_CAPTURE_DRAW.json",{"phase":"AFTER_FIRST_CANDIDATE_CAPTURE_FRAME_POST_DRAW","surfaces":surfaces,"comparison":"PENDING_DIAGNOSTIC_NOT_A_GATE","purpose":"Timing evidence for potential graphical buffer readiness differences; no cause or acceptance inferred"})
