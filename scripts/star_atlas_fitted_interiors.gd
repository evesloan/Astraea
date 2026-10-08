extends RefCounted
# Additive fitted activities. Existing district, source architecture and transport own
# the room. Static stock is intentionally not a second inventory or pickup system.
static func build(district:Node3D,ship:Node3D) -> void:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/star_atlas_fitted_interiors.json"))
	var fitted:=Node3D.new()
	fitted.name="StarAtlasFittedInteriors_Candidate"
	fitted.set_meta("authoring_owner","D12_D14_star_atlas")
	fitted.set_meta("capacity_change",0)
	district.add_child(fitted)
	for item in data.models:
		var p:Array=item.position
		var model:Node3D=ship.model(fitted,item.file,item.id,Vector3(p[0],p[1],p[2]),item.yaw)
		model.set_meta("fitted_role",item.role)
		if item.has("support"):model.set_meta("support_id",item.support)
		if item.role=="static_stock":
			for contact in model.find_children("StaticContact","StaticBody3D",true,false):contact.free()
	for source in data.fixtures:
		var fixture:Node3D=fitted.get_node(NodePath(source.id))
		var light:=SpotLight3D.new()
		light.name=source.id+"_OpticalSource"
		fitted.add_child(light)
		light.shadow_enabled=true
		light.light_color=Color(.82,.90,1.0) if source.id=="D12_ReturnCare_Fixture" else Color(1,.94,.86)
		if source.type=="task":
			var lens:=fixture.find_child("POINT_diffuser_face",true,false)as Node3D
			assert(lens!=null)
			light.global_position=lens.global_position+Vector3.DOWN*.01
			light.rotation.x=-PI/2
			light.spot_angle=75
			light.spot_range=2
			light.light_energy=.35
			var control:=Node3D.new()
			control.name=source.id+"_Switch"
			control.set_script(load("res://scripts/fixture_switch.gd"))
			fitted.add_child(control)
			control.configure(fixture,light,StringName("star_atlas_fitted_"+source.id))
		else:
			var lens:=fixture.find_child("FLOOR_DIFFUSER",true,false)as Node3D
			var aim:=fixture.find_child("FLOOR_READING_AIM",true,false)as Node3D
			assert(lens!=null and aim!=null)
			light.global_position=lens.global_position+Vector3.DOWN*.015
			light.look_at(aim.global_position,Vector3.UP)
			light.spot_angle=65
			light.spot_range=3
			light.light_energy=.65
	for item in data.labels:
		var backing:Node3D=fitted.get_node(NodePath(item.parent))
		var label:=Label3D.new()
		label.name="IntegratedCollectionLabel"
		label.text=item.text
		label.font_size=32
		label.pixel_size=item.pixel_size
		label.modulate=Color(.88,.77,.55)
		label.outline_size=0
		label.no_depth_test=false
		label.position=Vector3(item.position[0],item.position[1],item.position[2])
		label.rotation.x=item.rotation_x
		backing.add_child(label)
	_build_stock(fitted,data.stock_profiles)

static func _build_stock(parent:Node3D,profiles:Array) -> void:
	var anchors:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/library_stock_anchors.json"))
	var transforms:Array[Transform3D]=[]
	for profile in profiles:
		var origin:=Vector3(profile.position[0],profile.position[1],profile.position[2])
		var basis:=Basis(Vector3.UP,profile.yaw)
		for anchor in anchors[profile.profile]:
			var p:Array=anchor.position_m
			var local:=Vector3(p[0],p[2],-p[1])
			var orientation:=Basis(Vector3.UP,profile.yaw+deg_to_rad(anchor.rotation_z_degrees))
			transforms.append(Transform3D(orientation,origin+basis*local))
	var variants:Array[String]=["AST-LIB-006.glb","AST-LIB-006_reordered.glb","AST-LIB-006_short_flat.glb"]
	for variant in range(variants.size()):
		var selected:Array[Transform3D]=[]
		for i in range(transforms.size()):
			if (i*7+i/3)%3==variant:selected.append(transforms[i])
		var stock:Node3D=(load("res://assets/models/"+variants[variant])as PackedScene).instantiate()
		parent.add_child(stock)
		for part in stock.find_children("*","MeshInstance3D",true,false):
			var batch:=MultiMeshInstance3D.new()
			batch.name="FittedCollectionStock_"+str(variant)+"_"+str(parent.get_child_count())
			var mm:=MultiMesh.new()
			mm.transform_format=MultiMesh.TRANSFORM_3D
			mm.mesh=part.mesh
			mm.instance_count=selected.size()
			for i in range(selected.size()):mm.set_instance_transform(i,selected[i]*part.global_transform)
			batch.multimesh=mm
			batch.set_meta("stock_groups",selected.size())
			batch.set_meta("catalogue_file",variants[variant])
			parent.add_child(batch)
		stock.free()
