extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,raw_path:String="")->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/quiet_d14_receiving_20261016/RECEIPT.json"));assert(ship.get_node_or_null("ShipSpace/QuietD14StaffReceiving")==null)
 for f in p.source_pins:
  if str(f).begins_with("Game/"):assert(FileAccess.get_sha256("res://"+str(f).trim_prefix("Game/"))==p.source_pins[f])
 var file:String="res://assets/quiet_d14_receiving_20261016/"+str(p.file) if raw_path.is_empty() else raw_path;assert(FileAccess.get_sha256(file)==p.model_sha256)
 var model:Node3D
 if raw_path.is_empty():model=load(file).instantiate()
 else:
  var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file(file,state,64)==OK);model=doc.generate_scene(state)
 var group:=Node3D.new();group.name="QuietD14StaffReceiving";ship.get_node("ShipSpace").add_child(group);group.add_child(model)
 for row in p.walls:
  var owner:Node3D=ship.get_node("ShipSpace/Districts/QuietGroveReceivingCandidate")if row.owner=="house"else ship.get_node("ShipSpace/Group3ForeStarboardClinical")
  var old:MeshInstance3D=owner.find_child(row.name,true,false);assert(old!=null);assert(old.global_transform.is_equal_approx(Transform3D.IDENTITY));assert(old.mesh.get_faces().size()==int(row.source_triangles)*3)
  _trace_bounds(ship,owner,old,row)
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

# Diagnostic-only: no mutations, resource replacement, guard changes or file writes.
static func _trace_bounds(ship:Node3D,owner:Node3D,old:MeshInstance3D,row:Dictionary)->void:
 var bounds:AABB=old.get_aabb()
 var faces:PackedVector3Array=old.mesh.get_faces()
 var formats:Array=[]
 for surface in old.mesh.get_surface_count():formats.append(old.mesh.surface_get_format(surface) if old.mesh is ArrayMesh else -1)
 var matches:Array=[]
 for n:Node in ship.find_children(str(row.name),"MeshInstance3D",true,false):matches.append(str(n.get_path()))
 var contacts:Array=[]
 for n:CollisionShape3D in old.find_children("*","CollisionShape3D",true,false):contacts.append({"path":str(n.get_path()),"shape_id":n.shape.get_instance_id() if n.shape!=null else 0,"shape_class":n.shape.get_class() if n.shape!=null else "null"})
 var predecessor:Node=ship.get_node_or_null("ShipSpace/QuietD15StaffReceiving")
 var previous:Mesh=predecessor.get_meta(str(row.name)+"_original_mesh",null) if predecessor!=null else null
 var fingerprint:=HashingContext.new();fingerprint.start(HashingContext.HASH_SHA256);fingerprint.update(faces.to_byte_array())
 var evidence:={"phase":"BEFORE_UNCHANGED_D14_BOUNDS_ASSERT","wall":row.name,"receipt_row":row,"owner_path":str(owner.get_path()),"node_path":str(old.get_path()),"node_id":old.get_instance_id(),"mesh_id":old.mesh.get_instance_id(),"mesh_path":old.mesh.resource_path,"mesh_class":old.mesh.get_class(),"mesh_local_to_scene":old.mesh.resource_local_to_scene,"global_transform":str(old.global_transform),"local_transform":str(old.transform),"custom_aabb":str(old.custom_aabb),"actual_min":[bounds.position.x,bounds.position.y,bounds.position.z],"actual_max":[bounds.end.x,bounds.end.y,bounds.end.z],"min_delta":bounds.position.distance_to(v(row.min)),"max_delta":bounds.end.distance_to(v(row.max)),"surface_formats":formats,"triangles":faces.size()/3,"faces_sha256":fingerprint.finish().hex_encode(),"mesh_extras":old.get_meta("extras",{}),"matching_paths":matches,"contacts":contacts,"d15_receiver_present":predecessor!=null,"d15_original_mesh_id":previous.get_instance_id() if previous!=null else 0,"d15_original_mesh_bounds":str(previous.get_aabb()) if previous!=null else "absent","quiet17_present":ship.has_node("ShipSpace/Districts/QuietGrove17Specialty20261022"),"quiet30_present":ship.has_node("ShipSpace/Districts/QuietGrove30Specialty20261022"),"engine":Engine.get_version_info().string,"receipt_sha256":FileAccess.get_sha256("res://data/quiet_d14_receiving_20261016/RECEIPT.json")}
 print("QUIET_D14_RUNTIME_BOUNDS ",JSON.stringify(evidence))
