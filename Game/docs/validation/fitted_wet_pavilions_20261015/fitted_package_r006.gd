extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/fitted_wet_pavilions_20261015/FITTED_CONFIG_r006.json"));assert(ship.get_node_or_null("ShipSpace/FittedWetPavilions20261015")==null)
 var group:=Node3D.new();group.name="FittedWetPavilions20261015";ship.get_node("ShipSpace").add_child(group)
 load("res://scripts/fitted_wet_pavilions_20261015/roof_successor.gd").apply(ship,group,p.roofs)
 var furniture:Array=[]
 for row in p.loose_furniture_moves:
  var node:Node3D=ship.get_node("ShipSpace/Districts/QuietGroveReceivingCandidate/RetainedLandscapeAndSeating/"+str(row.name));assert(node.global_position.distance_to(v(row.preimage_xyz))<.001)
  var original:Transform3D=node.global_transform;node.global_position=v(row.target_xyz);assert(node.global_basis.is_equal_approx(original.basis))
  for body:CollisionObject3D in node.find_children("*","CollisionObject3D",true,false):body.force_update_transform()
  furniture.append({"node":str(node.get_path()),"before":original,"target":node.global_transform})
 group.set_meta("exact_loose_furniture_successors",furniture)
 for row in p.models:
  var file:String="res://assets/fitted_wet_pavilions_20261015/"+str(row.file);assert(FileAccess.get_sha256(file)==str(row.sha256));var model:Node3D=(load(file)as PackedScene).instantiate();model.name=str(row.kit);group.add_child(model);var meshes:Array[Node]=model.find_children("*","MeshInstance3D",true,false);assert(meshes.size()==int(row.meshes));var contacts:Array[Node]=[]
  for mesh:MeshInstance3D in meshes:
   if not str(mesh.name).contains("Water_Illustrative"):contacts.append(mesh)
  load("res://scripts/static_contact_cache.gd").attach_group(model,contacts)
 var lights:Array[Light3D]=[]
 for row in p.lights:
  var lens:MeshInstance3D=group.find_child(str(row.source_mesh).validate_node_name(),true,false);assert(lens!=null and (lens.global_transform*lens.get_aabb()).grow(.03).has_point(v(row.at)))
  var light:=OmniLight3D.new();light.name=str(row.kit)+"_"+str(row.source_mesh).validate_node_name()+"_Emitter";group.add_child(light);light.position=v(row.at);light.light_color=Color(1,.86,.68);light.light_energy=float(row.energy);light.omni_range=float(row.range);light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE;light.visible=false;light.shadow_enabled=true;lights.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 for row in p.doors:
  var door:Node3D=load("res://scripts/group2_vip_pavilions/privacy_door.gd").new();door.name=str(row.kit)+"_ChangingPrivacy"+str(row.source_index);door.position=v(row.at);door.rotation.y=float(row.yaw);door.persistent_id=StringName(str(row.persistent_id));group.add_child(door)
 group.set_meta("default_main_adoption",false);group.set_meta("original_source_kits_retained",true);group.set_meta("two_physical_wet_proposals",true);group.set_meta("room_identity_capacity_membership_or_water_operation_admitted",false);group.set_meta("body_load_food_hygiene_weather_pressure_final_art_accepted",false)
 return group
