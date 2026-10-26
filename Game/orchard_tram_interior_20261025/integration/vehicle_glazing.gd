extends RefCounted
# Scoped scenic presentation. Original panes, contacts and controllers stay exact.
static func apply(body:AnimatableBody3D)->void:
	var glass:=ShaderMaterial.new();glass.shader=load("res://shaders/hospitality_glass.gdshader")
	var count:=0
	for mesh:MeshInstance3D in body.find_children("*","MeshInstance3D",true,false):
		if str(mesh.name) not in ["V2__Tram_End_Glazing_-2.26".validate_node_name(),"V2__Tram_End_Glazing_2.26".validate_node_name()]:continue
		assert(mesh.material_override==null,"Do not overwrite a surviving pane presentation")
		mesh.material_override=glass;count+=1
	assert(count==2,"Both retained tram end glazing members must bind")
	body.set_meta("retained_end_glazing_bound",count)
