extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func digest(bytes:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/salon_receiving_20261016/NATIVE_VERIFICATION.json"));assert(not ship.has_node("ShipSpace/SalonServiceReceiving20261016"))
 for path in p.source_pins:assert(FileAccess.get_sha256("res://"+str(path))==str(p.source_pins[path]),"Exact Salon receiving source: "+str(path))
 var original:Node3D=ship.get_node_or_null("ShipSpace/Districts/ListeningSalonReceiving_WIP")
 if original==null:
  for entry in ship.get_node("ShipSystems/ReceivedRoomResidency").entries:
   if str(entry.room.name)=="ListeningSalonReceiving_WIP":original=entry.room;break
 assert(original!=null and str(original.get_meta("programme_key"))=="D12_directory_03")
 var file:String="res://assets/salon_receiving_20261016/"+str(p.file);assert(FileAccess.get_sha256(file)==str(p.model_sha256));var group:=Node3D.new();group.name="SalonServiceReceiving20261016";ship.get_node("ShipSpace").add_child(group);var model:Node3D=(load(file)as PackedScene).instantiate();group.add_child(model);var witnesses:Array=[]
 for row in p.walls:
  var mesh:MeshInstance3D=original.find_child(str(row.source_name),true,false);assert(mesh!=null);var pose:Transform3D=mesh.transform;var parent:Node3D=mesh.get_parent()
  while parent!=original:assert(parent!=null);pose=parent.transform*pose;parent=parent.get_parent()
  pose=original.transform*pose;assert(pose.origin.distance_to(v(row.source_local_translation))<.0001);assert(mesh.mesh.get_faces().size()==int(row.source_triangles)*3);var b:AABB=mesh.get_aabb();assert(b.position.distance_to(v(row.input_bounds_local[0]))<.0001 and b.end.distance_to(v(row.input_bounds_local[1]))<.0001)
  var shapes:=mesh.find_children("*","CollisionShape3D",true,false);assert(shapes.size()==1);var shape:CollisionShape3D=shapes[0];assert(shape.shape is ConcavePolygonShape3D);assert(digest(shape.shape.get_faces().to_byte_array())==digest(mesh.mesh.get_faces().to_byte_array()));var replacement:MeshInstance3D=model.find_child(str(row.replacement_name).validate_node_name(),true,false);assert(replacement!=null);var before:Mesh=mesh.mesh;var prior:Shape3D=shape.shape;var edited:Mesh=replacement.mesh.duplicate();assert(edited.get_surface_count()==before.get_surface_count())
  for i in range(edited.get_surface_count()):edited.surface_set_material(i,before.surface_get_material(i))
  mesh.mesh=edited;shape.shape=edited.create_trimesh_shape();shape.shape.margin=prior.margin;group.set_meta(str(row.source_name).replace("-","_")+"_retained_mesh",before);group.set_meta(str(row.source_name).replace("-","_")+"_retained_shape",prior);witnesses.append({"source_name":row.source_name,"original_faces_sha256":digest(before.get_faces().to_byte_array()),"new_faces_sha256":digest(edited.get_faces().to_byte_array()),"patched_while_cached":not original.is_inside_tree()});replacement.free()
 var contacts:Array[Node]=[]
 for row in p.batches:
  var mesh:MeshInstance3D=model.find_child(str(row.name),true,false);assert(mesh!=null);var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(v(row.min))<.001 and b.end.distance_to(v(row.max))<.001)
  if row.collide:contacts.append(mesh)
 load("res://scripts/static_contact_cache.gd").attach_group(model,contacts);var lights:Array[Light3D]=[]
 for row in p.lights:
  var light:=SpotLight3D.new();light.name=str(row.name);group.add_child(light);light.position=v(row.at);light.rotation.x=-PI/2;light.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);light.light_energy=float(row.energy);light.spot_range=float(row.range);light.spot_angle=70;light.shadow_enabled=true;light.visible=false;lights.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship);group.set_meta("exact_selected_wall_preimages",witnesses);group.set_meta("default_main_adoption",true);group.set_meta("programme_key_preserved","D12_directory_03");group.set_meta("new_room_capacity_lift_stop_or_door_ids",0);group.set_meta("source_owned_floor_records_preserved",true);group.set_meta("operation_pressure_cart_species_primary_load_or_final_art_accepted",false);return group
