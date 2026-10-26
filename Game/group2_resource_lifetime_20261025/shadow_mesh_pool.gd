extends RefCounted
# Exact material-free shadow geometry only. Main meshes/materials are never pooled.
# Weak owners allow detached-room leases to release every unused GPU mesh.
static var entries:Dictionary={}
static func payload(mesh:ArrayMesh)->PackedByteArray:
	if mesh.resource_local_to_scene or mesh.get_script()!=null or mesh.shadow_mesh!=null or mesh.get_blend_shape_count()!=0:return PackedByteArray()
	var result:Dictionary={}
	for property:Dictionary in mesh.get_property_list():
		if not (int(property.usage)&PROPERTY_USAGE_STORAGE):continue
		var key:=str(property.name)
		if key in ["resource_name","resource_path","resource_local_to_scene"]:continue
		var value:Variant=mesh.get(property.name)
		if key=="_surfaces":
			var surfaces:Array=[]
			for original:Dictionary in value:
				if original.get("material")!=null:return PackedByteArray()
				var surface:Dictionary=original.duplicate()
				# Importer copies the main material's label into material-free shadows.
				# Names do not participate in geometry, LOD, shading or collision.
				surface.erase("name")
				surfaces.append(surface)
			value=surfaces
		result[key]=value
	return var_to_bytes(result)
static func prune()->void:
	for key:String in entries.keys():
		if entries[key].ref.get_ref()==null:entries.erase(key)
static func invalidate(key:String,reference:WeakRef)->void:
	if entries.has(key) and entries[key].ref==reference:entries.erase(key)
static func intern_scene(packed:PackedScene)->Dictionary:
	prune()
	var seen:Dictionary={};var count:=0;var shared:=0;var skipped:=0
	var state:=packed.get_state()
	for n in state.get_node_count():
		for p in state.get_node_property_count(n):
			if state.get_node_property_name(n,p)!=&"mesh":continue
			var main:ArrayMesh=state.get_node_property_value(n,p) as ArrayMesh
			if main==null or main.resource_local_to_scene or seen.has(main.get_instance_id()):continue
			seen[main.get_instance_id()]=true
			var shadow:ArrayMesh=main.shadow_mesh
			if shadow==null:continue
			var bytes:=payload(shadow)
			if bytes.is_empty():skipped+=1;continue
			count+=1
			var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(bytes)
			var key:=hash.finish().hex_encode()
			var canonical:ArrayMesh=null
			if entries.has(key):
				canonical=entries[key].ref.get_ref() as ArrayMesh
				if canonical!=null and entries[key].bytes!=bytes:
					push_error("Shadow digest collision; exact bytes differ")
					continue
			if canonical==null:
				var reference:WeakRef=weakref(shadow)
				entries[key]={"ref":reference,"bytes":bytes}
				shadow.changed.connect(func()->void:invalidate(key,reference))
			elif canonical!=shadow:
				main.shadow_mesh=canonical
				shared+=1
	return {"eligible":count,"shared":shared,"skipped":skipped,"live_groups":entries.size()}
