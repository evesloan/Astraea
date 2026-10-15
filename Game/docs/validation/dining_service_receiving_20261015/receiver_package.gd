extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/dining_service_receiving_20261015/NATIVE_RECEIVER_VERIFICATION.json"));assert(not ship.has_node("ShipSpace/DiningServiceReceiving20261015"));assert(ship.has_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms"))
 for path in p.source_pins:assert(FileAccess.get_sha256("res://"+str(path))==str(p.source_pins[path]),"Exact retained dining service pin: "+str(path))
 var file:String="res://assets/dining_service_receiving_20261015/"+str(p.file);assert(FileAccess.get_sha256(file)==str(p.model_sha256));var group:=Node3D.new();group.name="DiningServiceReceiving20261015";ship.get_node("ShipSpace").add_child(group);var model:Node3D=(load(file)as PackedScene).instantiate();model.name="ConnectedFinishingAndUsedReceiving";group.add_child(model);assert(model.find_children("*","MeshInstance3D",true,false).size()==int(p.meshes));var contacts:Array[Node]=[]
 for row in p.batches:
  var mesh:MeshInstance3D=model.find_child(str(row.name),true,false);assert(mesh!=null);var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(v(row.min))<.001 and b.end.distance_to(v(row.max))<.001)
  if row.collide:contacts.append(mesh)
 load("res://scripts/static_contact_cache.gd").attach_group(model,contacts);var native_bounds:Dictionary={}
 for row in p.bounds:native_bounds[str(row.name)]=row
 var lights:Array[Light3D]=[]
 for row in p.lights:
  var lens:MeshInstance3D=model.find_child(str(row.lens_batch),true,false);assert(lens!=null);var source:Dictionary=native_bounds[str(row.lens)];assert(AABB(v(source.min),v(source.max)-v(source.min)).grow(.03).has_point(v(row.at)));var light:=SpotLight3D.new();light.name=str(row.name).validate_node_name();group.add_child(light);light.position=v(row.at);light.rotation.x=-PI/2;light.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);light.light_energy=float(row.energy);light.spot_range=float(row.range);light.spot_angle=70;light.shadow_enabled=true;light.visible=false;lights.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship);group.set_meta("default_main_adoption",false);group.set_meta("new_room_ids_or_capacity",0);group.set_meta("programme_keys",["D10_directory_01","D10_directory_02","D10_directory_03"]);group.set_meta("new_lift_stops",0);group.set_meta("asset_owned_missing_only_floor_m2",float(p.new_floor_area_m2));group.set_meta("source_floor_records_and_original_sources_preserved",true);group.set_meta("food_water_stock_species_save_primary_engineering_or_final_art_accepted",false);return group
