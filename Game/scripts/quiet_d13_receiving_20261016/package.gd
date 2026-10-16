extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,raw_path:String="")->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/quiet_d13_receiving_20261016/RECEIPT.json"));assert(ship.get_node_or_null("ShipSpace/QuietD13StaffReceiving")==null)
 for f in p.source_pins:
  if str(f).begins_with("Game/"):assert(FileAccess.get_sha256("res://"+str(f).trim_prefix("Game/"))==p.source_pins[f])
 var file:String="res://assets/quiet_d13_receiving_20261016/"+str(p.file) if raw_path.is_empty() else raw_path;assert(FileAccess.get_sha256(file)==p.model_sha256)
 var model:Node3D
 if raw_path.is_empty():model=load(file).instantiate()
 else:
  var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file(file,state,64)==OK);model=doc.generate_scene(state)
 var group:=Node3D.new();group.name="QuietD13StaffReceiving";ship.get_node("ShipSpace").add_child(group);group.add_child(model)
 for row in p.walls:
  var owner:Node3D=ship.get_node("ShipSpace/Districts/QuietGroveReceivingCandidate")if row.owner=="house"else ship.get_node("ShipSpace/Group3ForeStarboardClinical")
  var old:MeshInstance3D=owner.find_child(row.name,true,false);assert(old!=null);assert(old.global_transform.is_equal_approx(Transform3D.IDENTITY));assert(old.mesh.get_faces().size()==int(row.source_triangles)*3)
  assert(old.get_aabb().position.distance_to(v(row.min))<.0002 and old.get_aabb().end.distance_to(v(row.max))<.0002)
  var shapes:=old.find_children("*","CollisionShape3D",true,false);assert(shapes.size()==1);var shape:CollisionShape3D=shapes[0];var replacement:MeshInstance3D=model.find_child(str(row.replacement_name).replace(".","_"),true,false);assert(replacement!=null)
  var mesh:Mesh=replacement.mesh.duplicate();assert(mesh.get_surface_count()==old.mesh.get_surface_count())
  for i in range(mesh.get_surface_count()):mesh.surface_set_material(i,old.mesh.surface_get_material(i))
  group.set_meta(str(row.name)+"_original_mesh",old.mesh);group.set_meta(str(row.name)+"_original_contact",shape.shape);old.mesh=mesh;var margin:float=shape.shape.margin;shape.shape=mesh.create_trimesh_shape();shape.shape.margin=margin;replacement.free()
 var contacts:Array[Node]=[]
 for row in p.parts:
  var m:MeshInstance3D=model.find_child(str(row.name).replace(".","_"),true,false);assert(m!=null)
  if row.collide:contacts.append(m)
 load("res://scripts/static_contact_cache.gd").attach_group(model,contacts)
 var lights:Array[Light3D]=[]
 for row in p.lights:
  var light:=SpotLight3D.new();light.name=row.name;group.add_child(light);light.position=v(row.at);light.rotation.x=-PI/2;light.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);light.light_energy=row.energy;light.spot_range=row.range;light.spot_angle=70;light.shadow_enabled=true;light.visible=false;lights.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship);group.set_meta("missing_only_floor_m2",p.floor_m2);group.set_meta("physical_receiving_only",true);group.set_meta("new_ids_capacity_lift_stops",0);group.set_meta("engineering_operations_final_art_accepted",false);return group
