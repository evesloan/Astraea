extends RefCounted
static func contact_visual(parent:Node3D,file:String)->Node3D:
	var visual:Node3D=load("res://assets/models/"+file).instantiate()
	parent.add_child(visual)
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		var extra:Dictionary=mesh.get_meta("extras",{})
		var normalized_name:=str(mesh.name).to_lower().replace("_","").replace("-","").replace(".","").replace(" ","")
		var presentation_only:bool="previewground" in normalized_name or bool(extra.get("preview_only",false)) or bool(extra.get("presentation_only",false)) or bool(extra.get("exclude_from_production",false))
		assert(not presentation_only,"Presentation-only geometry rejected in production GLB: "+file+" / "+str(mesh.name))
		if str(extra.get("material_role",""))=="hospitality_glass":
			var glass:=ShaderMaterial.new();glass.shader=load("res://shaders/hospitality_glass.gdshader");mesh.material_override=glass
	return visual
