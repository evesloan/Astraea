extends RefCounted
# Prepared installed-PackedScene auditor. No importer/state, engine launcher or scene edits.
# asset: name,path,sha256,family,expected_batches,expected_triangles,
#        source_sha256,snapshot_sha256,provenance,provenance_sha256.
# audit_model(wrapper,asset,diagnostic_output="",installed=true) is read-only by default.
# Exact source-part geometry is exposed for separate physical/contact gates.
const OLD_NORMAL_CODEC_LIMIT := 0.0001 # Historical outcome only, never a widened bound.
var records: Array=[]
var native_maps: Dictionary={}
var all_meshes: Array[MeshInstance3D]=[]
var plant_meshes: Array[MeshInstance3D]=[]
var parts: Dictionary={}
var run_installed: bool=true
var audited_assets: Dictionary={}
func v3(a: Array) -> Vector3: return Vector3(a[0],a[1],a[2])

func vec(p: Vector3) -> Array: return [p.x,p.y,p.z]

func matrix(a: Transform3D) -> Array:
	return [[a.basis.x.x,a.basis.y.x,a.basis.z.x,a.origin.x],[a.basis.x.y,a.basis.y.y,a.basis.z.y,a.origin.y],[a.basis.x.z,a.basis.y.z,a.basis.z.z,a.origin.z],[0,0,0,1]]

func accessor(doc: Dictionary,bin: PackedByteArray,index: int) -> Array:
	var a: Dictionary=doc.accessors[index]
	assert(not a.has("sparse") and not a.get("normalized",false))
	var view: Dictionary=doc.bufferViews[int(a.bufferView)]
	assert(int(view.get("buffer",0))==0)
	var width: int={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4}[str(a.type)]
	var element: int={5121:1,5123:2,5125:4,5126:4}[int(a.componentType)]
	var stride: int=int(view.get("byteStride",width*element))
	var start: int=int(view.get("byteOffset",0))+int(a.get("byteOffset",0))
	var rows: Array=[]
	for i in range(int(a.count)):
		var row: Array=[]
		for j in range(width):
			var offset: int=start+i*stride+j*element
			match int(a.componentType):
				5121: row.append(bin.decode_u8(offset))
				5123: row.append(bin.decode_u16(offset))
				5125: row.append(bin.decode_u32(offset))
				5126: row.append(bin.decode_float(offset))
		rows.append(row)
	return rows

func corner_key(p: Vector3,uv: Vector2) -> String:
	# Exact float32 values; sign of zero is normalized, never rounded positions.
	var a:=PackedFloat32Array([p.x,p.y,p.z,uv.x,uv.y])
	for i in range(a.size()):
		if a[i]==0.0:a[i]=0.0
	return a.to_byte_array().hex_encode()

func tri_keys(p: Array,uv: Array) -> Array:
	var c: Array=[]
	for i in range(3):c.append(corner_key(p[i],uv[i]))
	return [c[0]+c[1]+c[2],c[1]+c[2]+c[0],c[2]+c[0]+c[1]]

func sha_bytes(bytes: PackedByteArray) -> String:
	var h:=HashingContext.new();assert(h.start(HashingContext.HASH_SHA256)==OK);h.update(bytes);return h.finish().hex_encode()
# Source-derived codec correspondence. This helper is scratch-prepared, not run.
# Godot 4.6.3 rendering_server.cpp lines 557–572 and 1377–1387;
# vector3.cpp lines 84–105. The uncompressed-attribute path is mandatory.

func json_equal(a: Variant,b: Variant) -> bool:
	if (a is int or a is float) and (b is int or b is float):return float(a)==float(b)
	if a is Dictionary and b is Dictionary:
		if a.size()!=b.size():return false
		for key in a:
			if not b.has(key) or not json_equal(a[key],b[key]):return false
		return true
	if a is Array and b is Array:
		if a.size()!=b.size():return false
		for i in range(a.size()):
			if not json_equal(a[i],b[i]):return false
		return true
	return a==b

func native_normal_prediction(source_normal: Vector3) -> Dictionary:
	var oct: Vector2=source_normal.octahedron_encode()
	# C++ multiplies real_t float32 before uint16 truncation. GDScript scalar
	# arithmetic is double, so explicitly reproduce the intermediate float32.
	var qx: int=int(clampf(PackedFloat32Array([oct.x*65535.0])[0],0.0,65535.0))
	var qy: int=int(clampf(PackedFloat32Array([oct.y*65535.0])[0],0.0,65535.0))
	# C++ divides by 65535.0 in double then constructs float32 Vector2.
	var decoded: Vector3=Vector3.octahedron_decode(Vector2(float(qx)/65535.0,float(qy)/65535.0))
	return {"uint16":[qx,qy],"decoded":decoded}

func normal_bits_equal(actual: Vector3,predicted: Vector3) -> bool:
	return PackedVector3Array([actual]).to_byte_array()==PackedVector3Array([predicted]).to_byte_array()

func audit_surface(mesh: MeshInstance3D,surface: int,primitive: Dictionary,doc: Dictionary,bin: PackedByteArray,provenance: Dictionary,asset: Dictionary,out: String) -> void:
	var format: int=mesh.mesh.surface_get_format(surface)
	assert((format&Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES)==0,"Native raw arrays are compressed")
	var array_mesh: ArrayMesh=mesh.mesh as ArrayMesh
	assert(array_mesh!=null and array_mesh.surface_get_primitive_type(surface)==Mesh.PRIMITIVE_TRIANGLES)
	var arrays: Array=mesh.mesh.surface_get_arrays(surface)
	var pos: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
	var norm: PackedVector3Array=arrays[Mesh.ARRAY_NORMAL]
	var uv: PackedVector2Array=arrays[Mesh.ARRAY_TEX_UV]
	var ix: PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
	assert(pos.size()==norm.size() and pos.size()==uv.size() and ix.size()%3==0)
	var attrs: Dictionary=primitive.attributes
	var ep: Array=accessor(doc,bin,int(attrs.POSITION))
	var en: Array=accessor(doc,bin,int(attrs.NORMAL))
	var eu: Array=accessor(doc,bin,int(attrs.TEXCOORD_0))
	var ei: Array=accessor(doc,bin,int(primitive.indices))
	assert(ix.size()==ei.size())
	var buckets: Dictionary={}
	for i in range(0,ei.size(),3):
		# Documented Godot glTF import CCW-to-CW swap. Cyclic only afterwards.
		var order: Array=[int(ei[i][0]),int(ei[i+2][0]),int(ei[i+1][0])]
		var p: Array=[];var u: Array=[];var n: Array=[]
		for j in order:p.append(v3(ep[j]));u.append(Vector2(eu[j][0],eu[j][1]));n.append(v3(en[j]))
		var key: String=tri_keys(p,u)[0]
		if not buckets.has(key):buckets[key]=[]
		var codec_normals: Array=[];var codec_uint16: Array=[]
		for source_normal in n:
			var prediction: Dictionary=native_normal_prediction(source_normal)
			codec_normals.append(prediction.decoded);codec_uint16.append(prediction.uint16)
		buckets[key].append({"triangle":i/3,"normals":n,"codec_normals":codec_normals,"codec_uint16":codec_uint16})
	var correspondence: Array=[]
	var max_normal: float=0.0
	var rows: Array=[]
	for i in range(0,ix.size(),3):
		var p: Array=[pos[ix[i]],pos[ix[i+1]],pos[ix[i+2]]]
		var u: Array=[uv[ix[i]],uv[ix[i+1]],uv[ix[i+2]]]
		var n: Array=[norm[ix[i]],norm[ix[i+1]],norm[ix[i+2]]]
		var keys: Array=tri_keys(p,u)
		var found: bool=false
		for shift in range(3):
			if not buckets.has(keys[shift]):continue
			var list: Array=buckets[keys[shift]]
			for k in range(list.size()):
				var record: Dictionary=list[k]
				var error: float=0.0
				var codec_exact: bool=true
				for j in range(3):
					error=maxf(error,n[(j+shift)%3].distance_to(record.normals[j]))
					codec_exact=codec_exact and normal_bits_equal(n[(j+shift)%3],record.codec_normals[j])
				# Keep the old scalar result as history; never widen its tolerance.
				# Native acceptance instead requires the exact documented codec.
				if not codec_exact:continue
				max_normal=maxf(max_normal,error)
				var ti: int=int(record.triangle)
				var pr: Dictionary=provenance[str(ti)]
				var part: String=str(pr.source_part)
				if not out.is_empty():rows.append({"native_triangle":i/3,"glb_triangle":ti,"cyclic_shift":shift,"source_part":part,"source_triangle":pr.source_triangle,"source_normal_encoded_uint16":record.codec_uint16,"normal_codec_bits_exact":true,"old_scalar_normal_bound_exceeded":error>OLD_NORMAL_CODEC_LIMIT})
				correspondence.append(part)
				var part_key: String=str(asset.name)+"::"+part
				if not parts.has(part_key):parts[part_key]=[]
				parts[part_key].append({"mesh":mesh,"surface":surface,"indices":[ix[i],ix[i+1],ix[i+2]]})
				list.remove_at(k);found=true;break
			if found:break
		assert(found,"Native triangle has no exact position/UV/cyclic and source-derived normal-codec bit match")
	for key in buckets:assert(buckets[key].is_empty(),"GLB triangle was omitted")
	var dump: String="";var map_path: String="";var sections: Array=[]
	if not out.is_empty():
		dump=out+"/"+str(asset.name)+"__"+str(mesh.name)+"_s"+str(surface)+".raw"
		var file:=FileAccess.open(dump,FileAccess.WRITE);assert(file!=null)
		for entry in [["vertices_f32x3",pos.to_byte_array()],["normals_f32x3",norm.to_byte_array()],["uv_f32x2",uv.to_byte_array()],["indices_i32",ix.to_byte_array()]]:
			sections.append({"kind":entry[0],"offset":file.get_position(),"bytes":entry[1].size()});file.store_buffer(entry[1])
		file.close()
		map_path=dump+".correspondence.json"
		save_json(map_path,{"asset":asset.name,"mesh":mesh.name,"surface":surface,"triangles":rows})
	native_maps[str(mesh.get_instance_id())+":"+str(surface)]=correspondence
	records.append({"asset":asset.name,"mesh":mesh.name,"surface":surface,"triangles":ix.size()/3,"raw_positions_uvs_exact":true,"cyclic_bijection":true,"normal_gate":"Exact source-derived Godot4.6.3 octahedral uint16 roundtrip bits","old_scalar_normal_limit":OLD_NORMAL_CODEC_LIMIT,"old_scalar_normal_limit_exceeded":max_normal>OLD_NORMAL_CODEC_LIMIT,"source_derived_codec_residual":0.0,"max_normal_codec_error":max_normal,"compression_disabled":true,"raw_file":dump,"raw_sha256":FileAccess.get_sha256(dump) if not dump.is_empty() else "","raw_sections":sections,"triangle_correspondence":map_path,"correspondence_sha256":FileAccess.get_sha256(map_path) if not map_path.is_empty() else "","installed":run_installed,"production_changes":false})
func save_json(path: String,value: Dictionary) -> void:
	value["installed"]=run_installed;value["production_changes"]=false;value["physical_acceptance"]=false;value["final_acceptance"]=false
	var file:=FileAccess.open(path,FileAccess.WRITE);assert(file!=null);file.store_string(JSON.stringify(value,"  ",true,true));file.close()
func declared_local(source: Dictionary) -> Transform3D:
	if source.has("matrix"):
		var m: Array=source.matrix;assert(m.size()==16)
		return Transform3D(Basis(Vector3(m[0],m[1],m[2]),Vector3(m[4],m[5],m[6]),Vector3(m[8],m[9],m[10])),Vector3(m[12],m[13],m[14]))
	var q: Array=source.get("rotation",[0,0,0,1])
	var basis:=Basis(Quaternion(q[0],q[1],q[2],q[3]))
	basis=basis*Basis.from_scale(v3(source.get("scale",[1,1,1])))
	return Transform3D(basis,v3(source.get("translation",[0,0,0])))
func declared_world(index: int,doc: Dictionary,parents: Dictionary,cache: Dictionary) -> Transform3D:
	if cache.has(index):return cache[index]
	var local: Transform3D=declared_local(doc.nodes[index])
	var world: Transform3D=declared_world(int(parents[index]),doc,parents,cache)*local if parents.has(index) else local
	cache[index]=world
	return world
func bind_installed_tree(wrapper: Node3D,doc: Dictionary) -> Dictionary:
	# Every source name has exactly one validated spelling, occurrence and parent.
	# PackedScene/importer wrapper names are irrelevant; only their identity frames
	# on source-root ancestor paths are permitted. No wildcard or loose fallback.
	assert(not "GODOT_single_root" in doc.get("extensionsUsed",[]),"Unreviewed single-root import convention")
	# ship.model adds one instantiated PackedScene below its placement wrapper.
	# These exact GLBs use the normal scene wrapper, not GODOT_single_root.
	# Ignore that import wrapper's name even if the editor names it like a source.
	assert(wrapper.get_child_count()==1 and wrapper.get_child(0) is Node3D)
	var visual_root: Node3D=wrapper.get_child(0)as Node3D
	assert(visual_root.get_class()=="Node3D" and visual_root.transform==Transform3D.IDENTITY)
	var declared_names: Dictionary={};var parents: Dictionary={};var named: Dictionary={}
	for i in range(doc.nodes.size()):
		var name: String=str(doc.nodes[i].name).validate_node_name()
		assert(not name.is_empty() and not declared_names.has(name),"Source names fail validated-name bijection")
		declared_names[name]=i
		for child in doc.nodes[i].get("children",[]):
			assert(int(child)>=0 and int(child)<doc.nodes.size() and not parents.has(int(child)),"Invalid source child graph")
			parents[int(child)]=i
	var scene_roots: Array=doc.scenes[int(doc.get("scene",0))].nodes
	var root_indices: Dictionary={}
	for value in scene_roots:
		var root_index: int=int(value)
		assert(root_index>=0 and root_index<doc.nodes.size() and not root_indices.has(root_index))
		root_indices[root_index]=true
	for i in range(doc.nodes.size()):assert(parents.has(i)!=root_indices.has(i),"Declared source roots and child-parent graph disagree")
	var pending: Array[Node]=[]
	for child in visual_root.get_children():pending.append(child)
	var actual: Array[Node]=[]
	while not pending.is_empty():
		var node: Node=pending.pop_front();actual.append(node)
		if declared_names.has(str(node.name)):
			var index: int=int(declared_names[str(node.name)])
			assert(not named.has(index) and node is Node3D,"Native source-name occurrence is not unique Node3D")
			named[index]=node
		for child in node.get_children():pending.append(child)
	assert(named.size()==doc.nodes.size(),"Missing installed source nodes")
	var permitted_wrappers: Dictionary={visual_root.get_instance_id():true};var cache: Dictionary={};var rows: Array=[]
	for i in range(doc.nodes.size()):
		var node: Node3D=named[i];var source: Dictionary=doc.nodes[i]
		if parents.has(i):assert(node.get_parent()==named[int(parents[i])],"Installed source hierarchy changed")
		else:
			var ancestor: Node=node.get_parent()
			while ancestor!=wrapper:
				assert(ancestor!=null and ancestor is Node3D and ancestor.get_class()=="Node3D" and ancestor.transform==Transform3D.IDENTITY,"Importer wrapper changed source frame")
				assert(ancestor==visual_root or not declared_names.has(str(ancestor.name)),"Source root unexpectedly nested under another source node")
				permitted_wrappers[ancestor.get_instance_id()]=true;ancestor=ancestor.get_parent()
		var expected_local: Transform3D=declared_local(source)
		var expected_world: Transform3D=wrapper.global_transform*declared_world(i,doc,parents,cache)
		assert(node.transform==expected_local and node.global_transform==expected_world,"Installed source local/world transform differs exactly")
		if source.has("mesh"):assert(node is MeshInstance3D and node.mesh!=null)
		else:assert(not node is MeshInstance3D and not node is CollisionObject3D and not node is Light3D)
		rows.append({"source_index":i,"source_name":source.name,"actual_path":str(node.get_path()),"source_parent_index":int(parents.get(i,-1)),"local_transform":matrix(node.transform),"world_transform":matrix(node.global_transform),"expected_world_transform":matrix(expected_world),"exact_f32_transform":true})
	for node in actual:
		if declared_names.has(str(node.name)) or permitted_wrappers.has(node.get_instance_id()):continue
		# ship.model creates modeled contact descendants. They are exposed to the
		# separate physical gates, never treated as source mesh/marker hierarchy.
		assert(node is StaticBody3D or node is CollisionShape3D,"Unexpected non-source model descendant")
		var ancestor: Node=node.get_parent()
		while ancestor!=null and not ancestor is MeshInstance3D:ancestor=ancestor.get_parent()
		assert(ancestor!=null and declared_names.has(str(ancestor.name)),"Contact descendant has no declared source mesh")
	return {"by_index":named,"records":rows}
func texture_check(texture: Texture2D,doc: Dictionary,bin: PackedByteArray,ref: Dictionary) -> Dictionary:
	assert(texture!=null)
	var image_spec: Dictionary=doc.images[int(doc.textures[int(ref.index)].source)]
	assert(not image_spec.has("uri") and image_spec.mimeType=="image/png")
	var view: Dictionary=doc.bufferViews[int(image_spec.bufferView)]
	var start: int=int(view.get("byteOffset",0));var count: int=int(view.byteLength)
	var png: PackedByteArray=bin.slice(start,start+count)
	var expected:=Image.new();assert(expected.load_png_from_buffer(png)==OK)
	var obtained: Image=texture.get_image();assert(obtained!=null)
	# get_image may expose compressed backing data after normal editor import.
	# Work only on a duplicate; never mutate the original texture/image Resource.
	var actual: Image=obtained.duplicate()as Image;assert(actual!=null)
	var was_compressed: bool=actual.is_compressed()
	if was_compressed:assert(actual.decompress()==OK,"Cannot independently inspect imported texture pixels")
	expected.convert(Image.FORMAT_RGBA8);actual.convert(Image.FORMAT_RGBA8)
	assert(expected.get_size()==actual.get_size(),"Imported texture dimensions changed")
	var bytes: int=expected.get_width()*expected.get_height()*4
	assert(expected.get_data().slice(0,bytes)==actual.get_data().slice(0,bytes),"Lossless imported texture base RGBA differs from exact GLB PNG")
	return {"packed_png_sha256":sha_bytes(png),"native_rgba8_base_sha256":sha_bytes(actual.get_data().slice(0,bytes)),"size":[actual.get_width(),actual.get_height()],"texture_class":texture.get_class(),"texture_resource_path":texture.resource_path,"backing_image_was_compressed":was_compressed,"duplicate_only_decompression":true,"base_rgba_exact":true}
func check_sampler(material: StandardMaterial3D,doc: Dictionary,ref: Dictionary) -> void:
	assert(int(ref.get("texCoord",0))==0 and not ref.has("extensions"),"Unreviewed texture UV mapping")
	var texture: Dictionary=doc.textures[int(ref.index)]
	var sampler: Dictionary=doc.samplers[int(texture.sampler)] if texture.has("sampler") else {}
	# All seven accepted GLBs use this verified linear/repeat source sampler.
	assert(int(sampler.get("magFilter",9729))==9729 and int(sampler.get("minFilter",9987))==9987)
	assert(int(sampler.get("wrapS",10497))==10497 and int(sampler.get("wrapT",10497))==10497)
	assert(material.texture_filter==BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS and material.texture_repeat,"Imported source texture sampler differs")
func audit_model(wrapper: Node3D,asset: Dictionary,diagnostic_output: String="",installed: bool=true) -> Dictionary:
	run_installed=installed
	assert(wrapper!=null and wrapper.is_inside_tree() and not audited_assets.has(str(asset.name)))
	assert(FileAccess.get_sha256(str(asset.path))==str(asset.sha256),"Installed GLB differs from accepted immutable export")
	assert(asset.has("provenance_sha256") and FileAccess.get_sha256(str(asset.provenance))==str(asset.provenance_sha256),"Source triangle provenance is not hash-pinned")
	assert(bool(asset.get("lossless_texture_policy",true)),"Exact base-pixel gate requires reviewed lossless import policy; no lossy fallback")
	var raw: PackedByteArray=FileAccess.get_file_as_bytes(str(asset.path))
	assert(raw.decode_u32(0)==0x46546c67 and raw.decode_u32(4)==2 and raw.decode_u32(8)==raw.size())
	var json_length: int=raw.decode_u32(12)
	var doc: Dictionary=JSON.parse_string(raw.slice(20,20+json_length).get_string_from_utf8())
	assert(raw.decode_u32(16)==0x4e4f534a and raw.decode_u32(24+json_length)==0x004e4942)
	var bin: PackedByteArray=raw.slice(28+json_length)
	assert(doc.scenes.size()==1 and not doc.has("animations") and not doc.has("skins"))
	assert(doc.buffers.size()==1 and not doc.buffers[0].has("uri"))
	var provenance: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(str(asset.provenance)))
	assert(str(provenance.export_sha256)==str(asset.sha256) and str(provenance.source_sha256)==str(asset.source_sha256) and str(provenance.snapshot_sha256)==str(asset.snapshot_sha256))
	var by_node: Dictionary={}
	for row in provenance.triangles:
		var key: String=str(row.node)+":"+str(int(row.primitive))
		if not by_node.has(key):by_node[key]={}
		assert(not by_node[key].has(str(int(row.export_triangle))))
		by_node[key][str(int(row.export_triangle))]=row
	if not diagnostic_output.is_empty():assert(DirAccess.make_dir_recursive_absolute(diagnostic_output)==OK)
	var binding: Dictionary=bind_installed_tree(wrapper,doc)
	var nodes: Dictionary={};var extras: Dictionary={};var materials: Array=[]
	var count: int=0;var triangles: int=0;var record_start: int=records.size()
	for ni in range(doc.nodes.size()):
		var source: Dictionary=doc.nodes[ni];var node: Node3D=binding.by_index[ni]
		nodes[str(source.name)]=node;extras[str(source.name)]=source.get("extras",{})
		if not source.has("mesh"):continue
		var mesh: MeshInstance3D=node as MeshInstance3D
		assert(mesh.material_override==null and mesh.material_overlay==null)
		var mesh_extras: Dictionary=extras[str(source.name)]
		assert(str(mesh_extras.source_blend_sha256)==str(asset.source_sha256) and str(mesh_extras.source_snapshot_sha256)==str(asset.snapshot_sha256))
		var source_parts: Array=JSON.parse_string(str(mesh_extras.source_part_names))
		var part_provenance: Dictionary=JSON.parse_string(str(mesh_extras.source_part_provenance_json))
		assert(source_parts.size()==part_provenance.size())
		for part in source_parts:assert(part_provenance.has(str(part)))
		var prims: Array=doc.meshes[int(source.mesh)].primitives
		assert(prims.size()==mesh.mesh.get_surface_count())
		for si in range(prims.size()):
			var p: Dictionary=prims[si]
			var mat: StandardMaterial3D=mesh.get_active_material(si)as StandardMaterial3D
			assert(mat!=null and mat==mesh.mesh.surface_get_material(si) and mesh.get_surface_override_material(si)==null)
			var gm: Dictionary=doc.materials[int(p.material)]
			assert(mat.resource_name==str(gm.name) and mat.transparency==BaseMaterial3D.TRANSPARENCY_DISABLED)
			var pbr: Dictionary=gm.get("pbrMetallicRoughness",{})
			assert(mat.metallic==PackedFloat32Array([pbr.get("metallicFactor",1)])[0] and mat.roughness==PackedFloat32Array([pbr.get("roughnessFactor",1)])[0])
			assert(mat.cull_mode==(BaseMaterial3D.CULL_DISABLED if gm.get("doubleSided",false) else BaseMaterial3D.CULL_BACK))
			var factor: Array=pbr.get("baseColorFactor",[1,1,1,1])
			var expected_albedo:=Color(factor[0],factor[1],factor[2],factor[3]).linear_to_srgb()
			assert(mat.albedo_color==expected_albedo,"Exact imported albedo factor/conversion differs")
			if gm.has("emissiveFactor"):
				var ef: Array=gm.emissiveFactor;var expected_emission:=Color(ef[0],ef[1],ef[2]).linear_to_srgb()
				assert(mat.emission_enabled and mat.emission==expected_emission)
				var extension: Dictionary=gm.get("extensions",{}).get("KHR_materials_emissive_strength",{})
				assert(mat.emission_energy_multiplier==PackedFloat32Array([extension.get("emissiveStrength",1.0)])[0])
			else:assert(not mat.emission_enabled)
			assert(mat.uv1_scale==Vector3.ONE and mat.uv1_offset==Vector3.ZERO)
			var textures: Array=[]
			if pbr.has("baseColorTexture"):
				textures.append(texture_check(mat.albedo_texture,doc,bin,pbr.baseColorTexture));check_sampler(mat,doc,pbr.baseColorTexture)
			else:assert(mat.albedo_texture==null)
			if gm.has("emissiveTexture"):
				textures.append(texture_check(mat.emission_texture,doc,bin,gm.emissiveTexture));check_sampler(mat,doc,gm.emissiveTexture)
			else:assert(mat.emission_texture==null)
			materials.append({"mesh":source.name,"surface":si,"material":gm.name,"native_material_id":mat.get_instance_id(),"resource_path":mat.resource_path,"no_overrides":true,"source_factors_exact":true,"metallic":mat.metallic,"roughness":mat.roughness,"textures":textures})
			var map_key: String=str(source.name)+":"+str(si)
			assert(by_node.has(map_key))
			audit_surface(mesh,si,p,doc,bin,by_node[map_key],asset,diagnostic_output)
			triangles+=int(records.back().triangles)
		all_meshes.append(mesh)
		if asset.family=="plant":plant_meshes.append(mesh)
		else:assert(asset.family=="light")
		count+=1
	assert(count==int(asset.expected_batches) and triangles==int(asset.expected_triangles) and triangles==provenance.triangles.size())
	audited_assets[str(asset.name)]=true
	var summary: Dictionary={"asset":asset.name,"installed":installed,"exact_raw_position_uv_cyclic":true,"exact_documented_normal_codec_bits":true,"mesh_batches":count,"triangles":triangles,"materials":materials,"node_mapping":binding.records,"surfaces":records.slice(record_start),"source_glb_sha256":asset.sha256,"source_provenance_sha256":asset.provenance_sha256,"physical_acceptance":false,"final_acceptance":false}
	if not diagnostic_output.is_empty():save_json(diagnostic_output+"/"+str(asset.name)+"_INSTALLED_GEOMETRY.json",summary)
	return {"wrapper":wrapper,"nodes":nodes,"extras":extras,"materials":materials,"node_mapping":binding.records,"mesh_batches":count,"triangles":triangles,"asset":asset,"summary":summary}
