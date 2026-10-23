extends RefCounted
const P="res://royalty790_integration_20261022/"
static func raw(file:String)->Node3D:
 return load("res://scripts/release_operations_20261023/guard.gd").load_gltf(file)
static func build(ship:Node3D)->Node3D:
 assert(ship.find_child("Royalty790UpperIntegratedWIP",true,false)==null,"Upper must be integrated exactly once")
 var pins:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/INPUT_PINS.json"))
 for path in pins:
  if str(path).begins_with("Game/"):assert(FileAccess.get_sha256("res://"+str(path).trim_prefix("Game/"))==pins[path],"Retained input changed: "+str(path))
 var owner:Node3D=ship.get_node("ShipSpace/Districts/D17ConnectedHouse_WIP")
 assert(owner.get_meta("persistent_id")=="D17_connected_aft_house_platform" and owner.get_meta("source_guest_index")==790)
 assert(ship.get_node_or_null("ShipSpace/CompiledStructuralFloors_NotFinishedRooms/D17_connected_house_floor_00")!=null,"Existing compiler slab required")
 assert(ship.get_node_or_null("ShipSpace/D17StarboardStandardReceiving")!=null,"Later standard receiving package must precede this adapter")
 var architecture:Node3D=owner.get_node("D17ConnectedArchitecture")
 var standard:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D17_STARBOARD_STANDARD_CANDIDATE_20261019.json"))
 var expected:=raw("res://assets/models/"+str(standard.structure_file))
 if expected==null:return null
 var preserved:=0
 for row in standard.walls:
  if row.owner=="fore":continue
  var current:MeshInstance3D=architecture.find_child(row.name,true,false)
  var replacement:MeshInstance3D=expected.find_child(str(row.replacement_name).replace(".","_"),true,false)
  assert(current!=null and replacement!=null)
  var a:=current.mesh.get_faces();var b:=replacement.mesh.get_faces();assert(a.size()==b.size(),"Installed approach cut missing")
  for i in range(a.size()):assert(a[i].distance_to(b[i])<.0003,"Installed approach patch differs")
  preserved+=1
 expected.free();assert(preserved==4)
 var delta:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/RUNTIME_DELTA.json"))
 for patch in delta.patches:
  var old:MeshInstance3D=architecture.find_child(patch.name,true,false)
  assert(old!=null and old.mesh.get_faces().size()==int(patch.source_triangles)*3)
  assert(old.find_children("*","CollisionShape3D",true,false).size()==1)
  assert(FileAccess.get_sha256(patch.path)==patch.sha256)
 var marker:Node3D=architecture.find_child("DATUM_light_CourtView",true,false)
 var lamp:SpotLight3D=owner.get_node("D17HouseSource_DATUM_light_CourtView")
 assert(marker!=null and lamp.global_position.distance_to(marker.global_position)<.002)
 assert(FileAccess.get_sha256(delta.scene)==delta.scene_sha256)
 # Retain node, body, lamp, floor-owner and room identities; change only bounded mesh resources.
 for patch in delta.patches:
  var old:MeshInstance3D=architecture.find_child(patch.name,true,false)
  var changed:Mesh=load(patch.path).duplicate()
  assert(changed.get_surface_count()==old.mesh.get_surface_count())
  for i in range(changed.get_surface_count()):changed.surface_set_material(i,old.mesh.surface_get_material(i))
  var contact:CollisionShape3D=old.find_children("*","CollisionShape3D",true,false)[0]
  var margin:float=contact.shape.margin;old.mesh=changed;contact.shape=changed.create_trimesh_shape();contact.shape.margin=margin
 var at:Array=delta.court_light_position;marker.global_position=Vector3(at[0],at[1],at[2]);lamp.global_position=marker.global_position
 var result:=Node3D.new();result.name="Royalty790UpperIntegratedWIP";owner.add_child(result)
 result.set_meta("source_guest_index",790);result.set_meta("finished",false);result.set_meta("new_units",0);result.set_meta("new_capacity",0)
 result.set_meta("private_admission_accepted",false);result.set_meta("visual_acceptance",false)
 var additions:Node3D=load(delta.scene).instantiate();result.add_child(additions)
 var solids:Array[Node]=[]
 for m:MeshInstance3D in additions.find_children("*","MeshInstance3D",true,false):
  if not (str(m.name).begins_with("RG_StairFlight_") or str(m.name).begins_with("RG_StairNosing_")):solids.append(m)
 load("res://scripts/static_contact_cache.gd").attach_group(additions,solids)
 var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://royalty_790_completion_20261020/evidence/BUILD_RECEIPT.json"))
 for row in source.collision_ramps:
  var body:=StaticBody3D.new();body.name=row.name;var shape:=ConvexPolygonShape3D.new();var points:=PackedVector3Array()
  for p in row.vertices:points.append(Vector3(p[0],p[1],p[2]))
  shape.points=points;shape.margin=.001;var contact:=CollisionShape3D.new();contact.shape=shape;body.add_child(contact);result.add_child(body)
 var lift:Node3D=load("res://scripts/group2_private_vertical/moving_lift.gd").new()
 lift.name="Royalty790PrivateLift";lift.position=Vector3(101.75,0,45.65);lift.rotation.y=-PI/2;lift.gate_origin_xz=Vector2.ZERO
 lift.floor_heights.assign([102.2,106.5]);lift.deck_numbers.assign([17,17]);lift.stop_ids.assign(["private_lower","private_upper"])
 lift.stop_names.assign(["Lower living","Upper gallery"]);lift.stop_codes.assign(["L","U"])
 lift.identity_prefix="royalty790_candidate";lift.persistent_id=&"royalty790_candidate_private_lift";lift.district_label="Private suite"
 lift.operation_ready=false;result.add_child(lift);lift.phase="held_receivers_and_private_access"
 lift.cabin_gate.cabin_present_and_stopped=false;lift.cabin_gate.request_close()
 for gate in lift.landing_gates:gate.cabin_present_and_stopped=false;gate.request_close()
 for datum:Node3D in additions.find_children("DATUM_RG_light_*","Node3D",true,false):
  var light:=OmniLight3D.new();light.name=str(datum.name)+"_Light";result.add_child(light);light.global_position=datum.global_position
  light.light_color=Color(1,.91,.78);light.light_energy=.65;light.omni_range=5;light.shadow_enabled=true;light.visible=false
 var lights:Array[Light3D]=[]
 for light:Light3D in result.find_children("*","Light3D",true,false):lights.append(light)
 assert(lights.size()==6)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 return result
