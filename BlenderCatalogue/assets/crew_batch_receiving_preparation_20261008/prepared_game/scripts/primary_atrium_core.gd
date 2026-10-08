extends RefCounted
# Actual central public circulation platform. Other core reservations remain plans.
static func build(parent:Node3D,ship:Node3D,contract_path:String="res://data/architecture/PRIMARY_ATRIUM_CORE.json")->void:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(contract_path))
	var root:=Node3D.new()
	root.name=str(data.get("root_name","PrimaryAtriumCore_WIP"))
	root.set_meta("persistent_id",str(data.get("persistent_id","primary_atrium_core_001")))
	parent.add_child(root)
	var origin:Array=data.get("origin",[0,0,-100])
	var enclosure:Node3D=ship.model(root,str(data.get("enclosure_file","AST-CIR-005.glb")),"PrimaryCoreEnclosure",Vector3(origin[0],origin[1],origin[2]))
	for marker in enclosure.find_children("DATUM_light_*","Node3D",true,false):
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="PrimaryCoreLight_"+str(marker.name)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		light.spot_angle=70
		light.spot_range=8
		light.light_energy=1.1
		light.light_color=Color(1,.95,.88)
		light.shadow_enabled=true
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for i in range(data.stairs.size()):
		var s:Dictionary=data.stairs[i]
		var stairs:Node3D=(load("res://assets/models/"+str(s.file))as PackedScene).instantiate()
		stairs.name="PrimarySwitchback_D%02d"%(i+1)
		stairs.set_meta("catalogue_file",str(s.file))
		root.add_child(stairs)
		var at:Array=s.get("origin",[3,float(s.base_y),-96])
		stairs.position=Vector3(at[0],at[1],at[2])
		stairs.rotation.y=PI
		for part in stairs.find_children("CIR_Guard*","MeshInstance3D",true,false):
			part.material_override=glass
			part.create_trimesh_collision()
		var half:float=float(s.rise)/2
		var quads:Array=[
			[Vector3(0,0,0),Vector3(2.5,0,0),Vector3(2.5,half,-7.5),Vector3(0,half,-7.5)],
			[Vector3(0,half,-7.5),Vector3(6,half,-7.5),Vector3(6,half,-10.5),Vector3(0,half,-10.5)],
			[Vector3(3.5,float(s.rise),0),Vector3(6,float(s.rise),0),Vector3(6,half,-7.5),Vector3(3.5,half,-7.5)]]
		for j in range(quads.size()):
			var points:=PackedVector3Array()
			for p:Vector3 in quads[j]:
				points.append(stairs.global_transform*p)
				points.append(stairs.global_transform*(p-Vector3.UP*.24))
			var body:=StaticBody3D.new()
			body.name="PrimaryStairContact_%02d_%d"%[i,j]
			var contact:=CollisionShape3D.new()
			var shape:=ConvexPolygonShape3D.new()
			shape.points=points;shape.margin=.001
			contact.shape=shape;body.add_child(contact);root.add_child(body)
	var lift:Node3D=load("res://scripts/commons_lift.gd").new()
	var lift_data:Dictionary=data.lift
	lift.name=str(lift_data.get("name","PrimaryAtriumLift"))
	var heights:Array[float]=[]
	var decks:Array[int]=[]
	var ids:Array[String]=[]
	var names:Array[String]=[]
	var codes:Array[String]=[]
	for i in range(data.floor_y.size()):
		var deck_number:int=int(data.deck_numbers[i]) if data.has("deck_numbers") else i+1
		heights.append(float(data.floor_y[i]));decks.append(deck_number)
		ids.append("D%02d"%deck_number);names.append("Deck %02d"%deck_number);codes.append("%02d"%deck_number)
		var label:=Label3D.new()
		label.name="PrimaryDeckSign_%02d"%(i+1)
		label.text="D%02d  |  %s"%[deck_number,str(lift_data.get("district_label","Atrium core")).to_upper()]
		label.font_size=48;label.pixel_size=.005
		label.position=Vector3(float(data.get("sign_x",-7.66)),heights[i]+1.75,float(origin[2]))
		label.rotation.y=float(data.get("sign_yaw",PI/2))
		root.add_child(label)
	lift.floor_heights.assign(heights);lift.deck_numbers.assign(decks)
	lift.stop_ids.assign(ids);lift.stop_names.assign(names);lift.stop_codes.assign(codes)
	lift.cabin_file=str(lift_data.get("cabin_file","AST-CIR-003_eighteen_stop.glb"))
	var gate:Array=lift_data.get("gate_origin_xz",[-1.8,-106])
	lift.gate_origin_xz=Vector2(gate[0],gate[1])
	lift.maximum_speed=2.4;lift.acceleration=.8
	lift.identity_prefix=str(lift_data.get("identity_prefix","primary_atrium"))
	lift.district_label=str(lift_data.get("district_label","Atrium"))
	lift.persistent_id=StringName(lift.identity_prefix+"_lift_001")
	root.add_child(lift)
