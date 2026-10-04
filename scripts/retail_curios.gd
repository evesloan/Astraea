extends RefCounted
static func build(parent:Node3D,ship:Node3D) -> void:
	var district:=Node3D.new()
	district.name="D09_R070_KindCurios_WIP"
	district.set_meta("historical_room_id","R070")
	district.set_meta("programme","Existing small retail; transactions and guest use pending")
	parent.add_child(district)
	var room:Node3D=ship.model(district,"AST-RTL-005.glb","KindCuriosAuthoredRoom",Vector3(72,52.5,236),PI/2)
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	var approach:Node3D=ship.model(district,"AST-RTL-005_approach.glb","KindCuriosApproachGuards",Vector3(72,52.5,236),PI/2)
	for part in approach.find_children("APP_glass*","MeshInstance3D",true,false):part.material_override=glass
	for part in room.find_children("CUR_FrontGlass*","MeshInstance3D",true,false):part.material_override=glass
	for part in room.find_children("CUR_VisualFloorBorder*","MeshInstance3D",true,false):
		var contact:=part.get_node_or_null("StaticContact")
		if contact!=null:contact.free()
	for key in ["column_light_-1","column_light_1","ceiling_light_0","ceiling_light_1","ceiling_light_2"]:
		var datum:=room.find_child("DATUM_"+key,true,false)as Node3D
		assert(datum!=null)
		var light:=SpotLight3D.new()
		district.add_child(light)
		light.name="CuriosSource_"+key
		light.global_position=datum.global_position
		light.rotation.x=-PI/2
		light.spot_angle=65 if key.begins_with("column") else 52
		light.spot_range=9
		light.light_energy=.90 if key.begins_with("column") else .72
		light.light_color=Color(1,.95,.88)
		light.shadow_enabled=true

	var merchandise_index:=0
	for marker in room.find_children("DATUM_display_*","Node3D",true,false)+room.find_children("DATUM_case_*","Node3D",true,false):
		var object_id:="R070_display_item_%02d"%merchandise_index
		var file:="AST-CUR-%03d.glb"%(1+merchandise_index%3)
		var item:Node3D=ship.model(district,file,object_id,marker.global_position,merchandise_index*.63)
		item.set_meta("display_item_id",object_id)
		item.set_meta("interaction_status","Static merchandise placement; pickup, inventory and sales pending")
		merchandise_index+=1
