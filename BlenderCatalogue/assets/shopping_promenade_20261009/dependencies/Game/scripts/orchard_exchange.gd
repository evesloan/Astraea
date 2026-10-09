extends RefCounted
# Shared local arrival inside existing retail/dining allocations; food hall pending.
static func build(parent:Node3D,ship:Node3D)->void:
	var root:=Node3D.new()
	root.name="D09_D10_OrchardExchange_WIP"
	root.set_meta("programme_keys",["D09_directory_04","D10_directory_04"])
	parent.add_child(root)
	var architecture:Node3D=ship.model(root,"AST-RTL-009.glb","OrchardExchangeArchitecture",Vector3(4,52.5,-250))
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for part in architecture.find_children("*","MeshInstance3D",true,false):
		if "glass" in str(part.name).to_lower():part.material_override=glass
	for marker in architecture.find_children("DATUM_light_*","Node3D",true,false):
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		light.light_color=Color(1,.95,.88)
		light.light_energy=1.1
		light.spot_range=7
		light.spot_angle=70
		light.shadow_enabled=true
	for level in [52.5,61.0]:
		for x in [5.45,22.48]:
			ship.model(root,"AST-STR-001-H826.glb" if level<61 else "AST-STR-001-H810.glb","ExchangeBearing_%s_%s"%[level,x],Vector3(x,level,-248.4))
	var stairs:Node3D=(load("res://assets/models/AST-CIR-001.glb")as PackedScene).instantiate()
	stairs.name="ExchangeSwitchback"
	stairs.set_meta("catalogue_file","AST-CIR-001.glb")
	root.add_child(stairs)
	stairs.position=Vector3(8,52.5,-237.5)
	for part in stairs.find_children("CIR_Guard*","MeshInstance3D",true,false):
		part.material_override=glass
		part.create_trimesh_collision()
	var contact=load("res://scripts/aquatic_section.gd")
	var quad0:Array[Vector3]=[Vector3(8,52.5,-237.5),Vector3(10.5,52.5,-237.5),Vector3(10.5,56.75,-245),Vector3(8,56.75,-245)]
	contact._contact(root,quad0)
	var quad1:Array[Vector3]=[Vector3(8,56.75,-245),Vector3(14,56.75,-245),Vector3(14,56.75,-248),Vector3(8,56.75,-248)]
	contact._contact(root,quad1)
	var quad2:Array[Vector3]=[Vector3(11.5,61,-237.5),Vector3(14,61,-237.5),Vector3(14,56.75,-245),Vector3(11.5,56.75,-245)]
	contact._contact(root,quad2)
	var lift:Node3D=load("res://scripts/commons_lift.gd").new()
	lift.name="OrchardExchangeLift"
	lift.floor_heights.assign([52.5,61.0])
	lift.deck_numbers.assign([9,10])
	lift.stop_ids.assign(["D09","D10"])
	lift.stop_names.assign(["Retail court","Orchard arrival"])
	lift.stop_codes.assign(["09","10"])
	lift.gate_origin_xz=Vector2(19.8,-241.5)
	lift.identity_prefix="orchard_exchange"
	lift.district_label="OrchardExchange"
	lift.persistent_id=&"orchard_exchange_lift_001"
	root.add_child(lift)
