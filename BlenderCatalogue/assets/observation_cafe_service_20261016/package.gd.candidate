extends RefCounted
static func digest(bytes:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/observation_cafe_service_20261016/NATIVE_VERIFICATION.json"));assert(not ship.has_node("ShipSpace/ObservationCafeServiceReceiving20261016"))
 for path in p.source_pins:assert(FileAccess.get_sha256("res://"+str(path))==str(p.source_pins[path]),"Observation Cafe exact source pin: "+str(path))
 var file:String="res://assets/observation_cafe_service_20261016/"+str(p.file);assert(FileAccess.get_sha256(file)==str(p.model_sha256));var group:=Node3D.new();group.name="ObservationCafeServiceReceiving20261016";ship.get_node("ShipSpace").add_child(group);var model:Node3D=(load(file)as PackedScene).instantiate();group.add_child(model)
 var contacts:Array[Node]=[]
 for row in p.batches:
  var mesh:MeshInstance3D=model.find_child(str(row.name),true,false);assert(mesh!=null);var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(v(row.min))<.001 and b.end.distance_to(v(row.max))<.001)
  if row.collide:contacts.append(mesh)
 load("res://scripts/static_contact_cache.gd").attach_group(model,contacts);var lights:Array[Light3D]=[]
 for row in p.lights:
  var lens:MeshInstance3D=model.find_child(str(row.lens_batch),true,false);assert(lens!=null);var lamp:=SpotLight3D.new();lamp.name=str(row.name);group.add_child(lamp);lamp.position=v(row.at);lamp.rotation.x=-PI/2;lamp.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);lamp.light_energy=float(row.energy);lamp.spot_range=float(row.range);lamp.spot_angle=70;lamp.shadow_enabled=true;lamp.visible=false;lights.append(lamp)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship);group.set_meta("default_main_adoption",true);group.set_meta("new_room_ids_capacity_or_lift_stops",0);group.set_meta("programme_key","D10_directory_10");group.set_meta("asset_owned_missing_only_floor_m2",float(p.new_floor_area_m2));group.set_meta("food_water_stock_loaded_cart_species_save_pressure_primary_engineering_or_final_art_accepted",false);return group
