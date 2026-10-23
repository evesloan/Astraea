extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,raw_path:String="")->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D17_STARBOARD_STANDARD_CANDIDATE_20261019.json"))
 assert(ship.find_child("D17StarboardStandardReceiving",true,false)==null)
 for f in p.source_pins:
  if str(f).begins_with("Game/"):assert(FileAccess.get_sha256("res://"+str(f).trim_prefix("Game/"))==p.source_pins[f])
 var file:String="res://assets/models/"+str(p.structure_file)if raw_path.is_empty()else raw_path
 assert(FileAccess.get_sha256(file)==p.structure.export_sha256)
 var model:Node3D
 if raw_path.is_empty():model=load(file).instantiate()
 else:
  model=load("res://scripts/release_operations_20261023/guard.gd").load_gltf(file,64)
  if model==null:return null
 # Validate both imported and raw branches before mutating any retained owner.
 if not load("res://scripts/release_operations_20261023/guard.gd").require_ok(model!=null and model.get_child_count()>0,"D17 standard scene is missing or empty"):return null
 for row in p.walls:
  var owner:Node3D=ship.find_child("Group2CentralSupportedAdjunct",true,false)if row.owner=="fore"else ship.find_child("D17ConnectedHouse_WIP",true,false)
  if not load("res://scripts/release_operations_20261023/guard.gd").require_ok(owner!=null,"D17 retained owner missing: "+str(row.owner)):model.free();return null
  var old:MeshInstance3D=owner.find_child(str(row.name),true,false)
  var replacement:MeshInstance3D=model.find_child(str(row.replacement_name).replace(".","_"),true,false)
  if not load("res://scripts/release_operations_20261023/guard.gd").require_ok(old!=null and old.mesh!=null and replacement!=null and replacement.mesh!=null,"D17 preimage/replacement missing: "+str(row.name)):model.free();return null
  if not load("res://scripts/release_operations_20261023/guard.gd").require_ok(old.mesh.get_faces().size()==int(row.source_triangles)*3 and old.global_transform.is_equal_approx(Transform3D.IDENTITY) and old.get_aabb().position.distance_to(v(row.min))<.0002 and old.get_aabb().end.distance_to(v(row.max))<.0002,"D17 preimage geometry differs: "+str(row.name)):model.free();return null
  if not load("res://scripts/release_operations_20261023/guard.gd").require_ok(old.mesh.get_surface_count()==replacement.mesh.get_surface_count(),"D17 surface count differs: "+str(row.name)):model.free();return null
  if not load("res://scripts/release_operations_20261023/guard.gd").require_ok(row.owner=="fore" or old.find_children("*","CollisionShape3D",true,false).size()==1,"D17 retained contact missing: "+str(row.name)):model.free();return null
 var shared_preflight:Node=ship.get_node_or_null("ShipSpace/Group2CentralSupportedAdjunct/ReceivingFrame/RoomStaticContacts/SharedRoomTriangles")
 # Find the actual nested fore owner rather than assuming its parent path.
 var fore_preflight:Node=ship.find_child("Group2CentralSupportedAdjunct",true,false)
 shared_preflight=fore_preflight.get_node_or_null("ReceivingFrame/RoomStaticContacts/SharedRoomTriangles")if fore_preflight!=null else null
 if not load("res://scripts/release_operations_20261023/guard.gd").require_ok(shared_preflight is CollisionShape3D and shared_preflight.shape!=null,"D17 shared fore contact missing"):model.free();return null
 var group:=Node3D.new();group.name="D17StarboardStandardReceiving";ship.get_node("ShipSpace").add_child(group);group.add_child(model)
 for row in p.walls:
  var owner:Node3D=ship.find_child("Group2CentralSupportedAdjunct",true,false)if row.owner=="fore"else ship.find_child("D17ConnectedHouse_WIP",true,false)
  var old:MeshInstance3D=owner.find_child(row.name,true,false);assert(old!=null);assert(old.global_transform.is_equal_approx(Transform3D.IDENTITY));assert(old.mesh.get_faces().size()==int(row.source_triangles)*3)
  assert(old.get_aabb().position.distance_to(v(row.min))<.0002 and old.get_aabb().end.distance_to(v(row.max))<.0002)
  var shapes:=old.find_children("*","CollisionShape3D",true,false);assert(shapes.size()==1 or row.owner=="fore");var shape:CollisionShape3D=shapes[0] if not shapes.is_empty() else null;var replacement:MeshInstance3D=model.find_child(str(row.replacement_name).replace(".","_"),true,false);assert(replacement!=null)
  var mesh:Mesh=replacement.mesh.duplicate();assert(mesh.get_surface_count()==old.mesh.get_surface_count())
  for i in range(mesh.get_surface_count()):mesh.surface_set_material(i,old.mesh.surface_get_material(i))
  group.set_meta(str(row.name)+"_original_mesh",old.mesh);old.mesh=mesh
  if shape!=null:
   group.set_meta(str(row.name)+"_original_contact",shape.shape);var margin:float=shape.shape.margin;shape.shape=mesh.create_trimesh_shape();shape.shape.margin=margin
  replacement.free()
 # Rebuild the exact opaque shared fore contact in place; preserve all original node/body identities.
 var fore:Node3D=ship.find_child("Group2CentralSupportedAdjunct",true,false).get_node("ReceivingFrame")
 var shared:CollisionShape3D=fore.get_node("RoomStaticContacts/SharedRoomTriangles");group.set_meta("fore_original_shared_contact",shared.shape)
 var faces:PackedVector3Array=[]
 for m:MeshInstance3D in fore.find_children("*","MeshInstance3D",true,false):
  var opaque:=true
  for i in range(m.mesh.get_surface_count()):
   var mat:Material=m.get_active_material(i)
   if not mat is BaseMaterial3D or mat.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or mat.albedo_color.a<.999:opaque=false
  if opaque:
   var pose:Transform3D=fore.global_transform.affine_inverse()*m.global_transform
   for vertex in m.mesh.get_faces():faces.append(pose*vertex)
 var rebuilt:=ConcavePolygonShape3D.new();rebuilt.set_faces(faces);rebuilt.margin=shared.shape.margin;shared.shape=rebuilt
 var contacts:Array[Node]=[]
 for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
  if p.structure.collision_policy[str(mesh.name)].collide:contacts.append(mesh)
 load("res://scripts/static_contact_cache.gd").attach_group(model,contacts)
 for r in p.rooms:
  var home:=Node3D.new();home.name=r.allocation.proposed_runtime_id;home.position=v(r.rigid_room_transform.translation);home.rotation.y=PI;group.add_child(home)
  home.set_meta("allocation_sha256",r.allocation.allocation_sha256);home.set_meta("rest_slot_ids",r.allocation.proposed_rest_slot_ids);home.set_meta("historical_save_identity_recovered",false);home.set_meta("species_ready",false)
  var room:Node3D=load("res://assets/models/"+str(p.source_room_model)).instantiate();room.name="RetainedFittedInterior";home.add_child(room);load("res://scripts/static_contact_cache.gd").attach_group(room,room.find_children("*","MeshInstance3D",true,false))
  for spec in [{"name":"HomeEntry","script":"guest_entry_door","at":Vector3(-63.175,102,35.6),"yaw":PI/2},{"name":"BathroomDoor","script":"guest_privacy_door","at":Vector3(-65.95,102,36.3),"yaw":PI}]:
   var door:Node3D=load("res://scripts/"+str(spec.script)+".gd").new();door.name=spec.name;door.persistent_id=StringName(str(r.allocation.proposed_runtime_id)+":"+str(spec.name));door.position=spec.at;door.rotation.y=spec.yaw;door.desired_open=false;door.open_fraction=0;home.add_child(door)
 var lights:Array[Light3D]=[]
 for row in p.fixture_instances:
  var marker:Node3D=model.find_child(row.name+"__LightExit",true,false);assert(marker!=null)
  var light:=OmniLight3D.new();light.name=row.name+"__Light";group.add_child(light);light.global_position=marker.global_position;light.light_color=Color(row.color[0],row.color[1],row.color[2]);light.light_energy=row.energy;light.omni_range=row.range;light.shadow_enabled=true;light.visible=false;lights.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 group.set_meta("construction_accepted",false);group.set_meta("new_units",0);group.set_meta("new_rest_places",0);group.set_meta("retained_standard_reservations",18)
 return group
