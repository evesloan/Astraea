extends RefCounted
static func digest(bytes:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/synthesis_external_receiving_20261015/NATIVE_VERIFICATION.json"));assert(not ship.has_node("ShipSpace/SynthesisExternalReceiving20261015"))
 for path in p.source_pins:assert(FileAccess.get_sha256("res://"+str(path))==str(p.source_pins[path]),"Synthesis exact source pin: "+str(path))
 var file:String="res://assets/synthesis_external_receiving_20261015/"+str(p.file);assert(FileAccess.get_sha256(file)==str(p.model_sha256));var group:=Node3D.new();group.name="SynthesisExternalReceiving20261015";ship.get_node("ShipSpace").add_child(group);var model:Node3D=(load(file)as PackedScene).instantiate();group.add_child(model);var original:Node3D=ship.get_node("ShipSpace/Districts/Group8SynthesisPlant_Candidate");var witnesses:Array=[]
 for row in p.walls:
  var mesh:MeshInstance3D=original.find_child(str(row.source_name),true,false);assert(mesh!=null and mesh.global_transform.is_equal_approx(Transform3D(Basis.IDENTITY,Vector3.ZERO)));assert(mesh.mesh.get_faces().size()==int(row.source_triangles)*3);var b:AABB=mesh.get_aabb();assert(b.position.distance_to(v(row.input_bounds_local[0]))<.0001 and b.end.distance_to(v(row.input_bounds_local[1]))<.0001)
  var shapes:=mesh.find_children("*","CollisionShape3D",true,false);assert(shapes.size()==1);var shape:CollisionShape3D=shapes[0];assert(shape.shape is ConcavePolygonShape3D);assert(digest(shape.shape.get_faces().to_byte_array())==digest(mesh.mesh.get_faces().to_byte_array()));var replacement:MeshInstance3D=model.find_child(str(row.replacement_name),true,false);assert(replacement!=null);var before:Mesh=mesh.mesh;var prior:Shape3D=shape.shape;var edited:Mesh=replacement.mesh.duplicate();assert(edited.get_surface_count()==before.get_surface_count())
  for i in range(edited.get_surface_count()):edited.surface_set_material(i,before.surface_get_material(i))
  mesh.mesh=edited;shape.shape=edited.create_trimesh_shape();shape.shape.margin=prior.margin;group.set_meta(str(row.source_name)+"_retained_mesh",before);group.set_meta(str(row.source_name)+"_retained_shape",prior);witnesses.append({"source_node":str(mesh.get_path()),"original_faces_sha256":digest(before.get_faces().to_byte_array()),"new_faces_sha256":digest(edited.get_faces().to_byte_array())});replacement.free()
 var contacts:Array[Node]=[]
 for row in p.batches:
  var mesh:MeshInstance3D=model.find_child(str(row.name),true,false);assert(mesh!=null);var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(v(row.min))<.001 and b.end.distance_to(v(row.max))<.001)
  if row.collide:contacts.append(mesh)
 load("res://scripts/static_contact_cache.gd").attach_group(model,contacts);var lights:Array[Light3D]=[]
 for row in p.lights:
  var lamp:=SpotLight3D.new();lamp.name=str(row.name);group.add_child(lamp);lamp.position=v(row.at);lamp.rotation.x=-PI/2;lamp.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);lamp.light_energy=float(row.energy);lamp.spot_range=float(row.range);lamp.spot_angle=70;lamp.shadow_enabled=true;lamp.visible=false;lights.append(lamp)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship);group.set_meta("exact_selected_wall_preimages",witnesses);group.set_meta("default_main_adoption",true);group.set_meta("new_room_ids_capacity_or_lift_stops",0);group.set_meta("programme_key","D01_directory_05");group.set_meta("asset_owned_missing_only_floor_m2",float(p.new_floor_area_m2));group.set_meta("food_water_stock_loaded_cart_species_save_pressure_primary_engineering_or_final_art_accepted",false);return group
