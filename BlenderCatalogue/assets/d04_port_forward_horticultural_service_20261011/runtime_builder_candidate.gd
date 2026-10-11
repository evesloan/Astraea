extends RefCounted
static func build(ship:Node3D)->Node3D:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_HORTICULTURAL_SERVICE.json"))
	var root:=Node3D.new();root.name="D04PortForwardHorticulturalService";ship.get_node("ShipSpace/Districts").add_child(root)
	for spec in [p.workbay,p.service_control]:
		assert(FileAccess.get_sha256("res://assets/models/"+str(spec.model_file))==spec.model_sha256)
		load("res://scripts/d04_port_forward_commons_service.gd").visual(root,spec.model_file,spec.collision_policy)
	var lamp:=SpotLight3D.new();root.add_child(lamp);lamp.name="HorticulturalWorkLight";lamp.position=Vector3(-66.55,20.06,-358.65);lamp.rotation.x=-PI/2;lamp.light_color=Color(1,.92,.81);lamp.light_energy=.8;lamp.spot_range=6;lamp.spot_angle=75
	for item in [["TOOLS / TRAYS",-65.3],["CLOSED CUTTINGS",-68.6]]:
		var sign:=Label3D.new();root.add_child(sign);sign.text=str(item[0]);sign.font_size=28;sign.pixel_size=.004;sign.position=Vector3(item[1],19.35,-360.23);sign.rotation.y=PI
	if p.open_garden_service:
		assert(FileAccess.get_sha256("res://artifacts/d04_port_forward_horticultural_service_sealed.json")==p.sealed_receipt_sha256)
		var gate:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_port_forward_horticultural_service_sealed.json"));assert(gate.status=="PASS" and gate.model_pins==p.model_pins)
		assert(FileAccess.get_sha256("res://assets/models/"+str(p.base_structure_model))==p.base_structure_sha256)
		var old:MeshInstance3D=ship.find_child(str(p.preimage.name),true,false);assert(old!=null)
		var b:AABB=old.global_transform*old.get_aabb();assert(b.position.distance_to(Vector3(-84.82,17.25,-357.48))<.00004 and b.end.distance_to(Vector3(-79.89,20.1,-357.3))<.00004);old.free()
		var spec:Dictionary=p.garden_successors;assert(FileAccess.get_sha256("res://assets/models/"+str(spec.model_file))==spec.model_sha256)
		var model:Node3D=load("res://scripts/d04_port_forward_commons_service.gd").visual(root,spec.model_file,spec.collision_policy)
		var control:Node3D=load("res://scripts/d04_garden_service_control.gd").new();control.name="GardenServiceControl";control.specs=p.sashes;root.add_child(control)
		var target:=Area3D.new();target.collision_layer=2;target.collision_mask=0;target.monitoring=false;control.add_child(target);target.position=Vector3(-80.15,17.65,-360.305)
		var trigger:=CollisionShape3D.new();var box:=BoxShape3D.new();box.size=Vector3(.3,.3,.06);trigger.shape=box;target.add_child(trigger)
		for s in p.sashes:
			var body:=AnimatableBody3D.new();body.name=str(s.name)+"_MovingContact";body.sync_to_physics=false;control.add_child(body);body.position=Vector3(s.pivot[0],s.pivot[1],s.pivot[2])
			var mesh:MeshInstance3D=model.find_child(str(s.name),true,false);assert(mesh!=null);mesh.reparent(body,true)
			var collider:=CollisionShape3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(1.15,float(s.height),.18);shape.margin=.001;collider.shape=shape;collider.position=Vector3(0,-float(s.height)/2,.09);body.add_child(collider);body.sync_to_physics=true;control.leaves.append(body)
	root.set_meta("all20_homes_and_25_rests_preserved",true);root.set_meta("horticultural_workbay_and_common_garden_only",true);root.set_meta("private_court_service_complete",false);root.set_meta("shared_clean_soiled_crossing_operation_accepted",false);root.set_meta("cart_safe_vertical_accepted",false);root.set_meta("whole_neighborhood_complete",false)
	return root
