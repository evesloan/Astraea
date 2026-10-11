extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func visual(parent:Node3D,file:String,policy:Dictionary)->Node3D:
	var node:Node3D=load("res://assets/models/"+file).instantiate();parent.add_child(node)
	for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
		assert(policy.has(str(mesh.name)))
		var spec:Dictionary=policy[str(mesh.name)]
		if spec.role=="hospitality_glass":var mat:=ShaderMaterial.new();mat.shader=load("res://shaders/hospitality_glass.gdshader");mesh.material_override=mat
		if spec.category=="light_source":mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if spec.collide:load("res://scripts/static_contact_cache.gd").attach(mesh)
	return node
static func build(ship:Node3D)->Node3D:
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	if districts.has_node("D04PortForwardCommonsServiceActivity"):return districts.get_node("D04PortForwardCommonsServiceActivity")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_COMMONS_SERVICE.json"))
	if p.open_receiving_connection:
		assert(FileAccess.get_sha256("res://artifacts/d04_port_forward_commons_service_sealed.json")==p.sealed_receipt_sha256)
		var gate:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_port_forward_commons_service_sealed.json"));assert(gate.status=="PASS"and gate.model_pins==p.model_pins)
		for record in p.preimages:
			var mesh:MeshInstance3D=ship.find_child(str(record.name),true,false);assert(mesh!=null)
			var low:=Vector3(INF,INF,INF);var high:=-low
			for v in record.verts:low=low.min(vec(v));high=high.max(vec(v))
			var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(low)<.00004 and b.end.distance_to(high)<.00004);mesh.free()
	var commons:=Node3D.new();commons.name="D04PortForwardCommonsServiceActivity";districts.add_child(commons)
	for spec in [p.structure,p.stock_products,p.entry_successors]if p.open_receiving_connection else[p.structure,p.stock_products]:
		assert(FileAccess.get_sha256("res://assets/models/"+str(spec.model_file))==spec.model_sha256);visual(commons,spec.model_file,spec.collision_policy)
	for j in range(p.lights.size()):
		var item:Dictionary=p.lights[j];var lamp:=SpotLight3D.new();lamp.name=item.name;commons.add_child(lamp);lamp.position=vec(item.at);lamp.rotation.x=-PI/2;lamp.light_color=Color(1,.92,.81);lamp.light_energy=.8;lamp.spot_range=7;lamp.spot_angle=75;lamp.shadow_enabled=j==0
	for item in [["QUIET / READING",-82.2],["CLEAN / STOCK",-77.3],["SOILED / RETURNS",-72.3]]:
		var sign:=Label3D.new();sign.name="DestinationSign"+str(commons.get_child_count());sign.text=str(item[0]);sign.font_size=28;sign.pixel_size=.004;sign.position=Vector3(item[1],19.35,-360.23);sign.rotation.y=PI;commons.add_child(sign)
	commons.set_meta("programme_key",p.programme_key);commons.set_meta("new_floor_m2",p.new_floor_m2);commons.set_meta("preserved_connected_homes",20);commons.set_meta("preserved_existing_rest_positions",25);commons.set_meta("distinct_clean_and_closed_return_enclosures",true);commons.set_meta("stock_refill_save_operation_accepted",false);commons.set_meta("shared_clean_soiled_crossing_operation_accepted",false);commons.set_meta("primary_load_accepted",false);commons.set_meta("cart_safe_vertical_accepted",false);commons.set_meta("whole_neighborhood_complete",false)
	return commons
