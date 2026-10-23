extends RefCounted
static func contact_visual(parent:Node3D,file:String)->Node3D:
	var visual:Node3D=load("res://scripts/release_operations_20261023/guard.gd").load_gltf("res://assets/models/"+file)
	if visual==null:return null
	parent.add_child(visual)
	var solids:Array[Node]=[]
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		var extra:Dictionary=mesh.get_meta("extras",{})
		var normalized_name:=str(mesh.name).to_lower().replace("_","").replace("-","").replace(".","").replace(" ","")
		var presentation_only:bool="previewground" in normalized_name or bool(extra.get("preview_only",false)) or bool(extra.get("presentation_only",false)) or bool(extra.get("exclude_from_production",false))
		assert(not presentation_only,"Presentation-only geometry rejected in production GLB: "+file+" / "+str(mesh.name))
		if str(extra.get("material_role",""))=="hospitality_glass":
			var glass:=ShaderMaterial.new();glass.shader=load("res://shaders/hospitality_glass.gdshader");mesh.material_override=glass
		if bool(extra.get("runtime_collision",false)) and str(extra.get("collision_policy",""))!="no_collision_detail":solids.append(mesh)
	load("res://scripts/static_contact_cache.gd").attach_group(visual,solids)
	return visual
