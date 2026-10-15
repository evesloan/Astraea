extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/aquatic_external_receiving_20261015/RECEIVING_PLAN.json"));var r:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/aquatic_external_receiving_20261015/NATIVE_VERIFICATION.json"));assert(not ship.has_node("ShipSpace/AquaticExternalReceiving20261015"))
 for path in p.source_pins:assert(FileAccess.get_sha256("res://"+str(path))==str(p.source_pins[path]),"Exact aquatic receiving pin: "+str(path))
 var annex:Node3D=ship.get_node("ShipSpace/Districts/AquaticRiverSlideAnnex_WIP");assert(annex.has_node("Group6Completion"));assert(annex.get_node("ExactAquaticArchitecture").get_meta("checked_group6_export_sha256")==p.source_pins["assets/models/AquaticCompletion_r019.glb"])
 var file:String="res://assets/aquatic_external_receiving_20261015/"+str(r.file);assert(FileAccess.get_sha256(file)==str(r.model_sha256));var group:=Node3D.new();group.name="AquaticExternalReceiving20261015";ship.get_node("ShipSpace").add_child(group);var model:Node3D=(load(file)as PackedScene).instantiate();group.add_child(model);assert(model.find_children("*","MeshInstance3D",true,false).size()==int(r.runtime_meshes));var contacts:Array[Node]=[]
 for row in r.batches:
  var mesh:MeshInstance3D=model.find_child(str(row.name),true,false);assert(mesh!=null);var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(v(row.min))<.001 and b.end.distance_to(v(row.max))<.001)
  if row.collide:contacts.append(mesh)
 load("res://scripts/static_contact_cache.gd").attach_group(model,contacts);var bounds:Dictionary={}
 for row in r.bounds:bounds[str(row.name)]=row
 var lights:Array[Light3D]=[]
 for row in r.lights:
  var lens:Dictionary=bounds[str(row.lens)];assert(AABB(v(lens.min),v(lens.max)-v(lens.min)).grow(.03).has_point(v(row.at)));assert(model.find_child(str(row.lens_batch),true,false)!=null);var lamp:=SpotLight3D.new();lamp.name=str(row.name);group.add_child(lamp);lamp.position=v(row.at);lamp.rotation.x=-PI/2;lamp.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);lamp.light_energy=float(row.energy);lamp.spot_range=float(row.range);lamp.spot_angle=70;lamp.shadow_enabled=true;lamp.visible=false;lights.append(lamp)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship);group.set_meta("asset_owned_projected_floor_m2",float(p.verified_projected_new_floor_m2));group.set_meta("original_portal_flanges_public_seam_gates_and_capacity_preserved",true);group.set_meta("new_floor_records_room_ids_or_lift_stops",0);group.set_meta("narrow_final_operator_leg_m",1.65);group.set_meta("primary_load_pressure_stock_water_loaded_cart_species_save_final_art_accepted",false);return group
