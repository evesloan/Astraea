extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,candidate_only:bool=false)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_STAFF_RISER.json"))
 if not p.active and not candidate_only:return null
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 if districts.has_node("D04PortCentralStaffCatchment"):return districts.get_node("D04PortCentralStaffCatchment")
 if p.active:
  assert(FileAccess.get_sha256("res://artifacts/d04_port_central_staff_riser_geometry.json")==p.sealed_receipt_sha256)
  assert(JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_port_central_staff_riser_geometry.json")).status=="PASS")
 for f in p.model_pins:assert(FileAccess.get_sha256("res://assets/models/"+f)==p.model_pins[f])
 var enclosure:Node3D=districts.get_node("LowerStaffNetwork_WIP/LowerStaffEnclosure")
 assert(FileAccess.get_sha256("res://assets/models/AST-STF-009_pool_market_home_equipment.glb")==p.source_pins["Game/assets/models/AST-STF-009_pool_market_home_equipment.glb"])
 var remove:Array[MeshInstance3D]=[]
 for pre in p.portal_preimage_meshes:
  if not pre.name in p.wall_patch.modified_cells:continue
  var mesh:MeshInstance3D=enclosure.find_child(pre.name,true,false);assert(mesh!=null)
  var faces:PackedVector3Array=mesh.mesh.get_faces();assert(faces.size()==pre.world_triangle_vertices.size())
  for i in range(faces.size()):assert((mesh.global_transform*faces[i]).distance_to(vec(pre.world_triangle_vertices[i]))<.00001)
  remove.append(mesh)
 var n:=Node3D.new();n.name="D04PortCentralStaffCatchment";districts.add_child(n);n.set_meta("persistent_id","port_service_riser_3_catchment_001")
 for mesh in remove:mesh.free()
 var visual=load("res://scripts/d04_port_forward_homes_fifth.gd")
 visual.visual(n,p.wall_patch_file,p.wall_patch.native_export.collision_policy)
 visual.visual(n,p.structure_file,p.structure.collision_policy)
 for item in p.service_doors:
  var door:Node3D=load("res://scripts/service_door.gd").new();door.name=item.name;door.position=vec(item.at);door.rotation.y=PI/2;door.persistent_id=StringName(item.persistent_id);door.open_fraction=0.0;door.desired_open=false;n.add_child(door)
 var lift:Node3D=load("res://scripts/commons_lift.gd").new();lift.name="PortCentralStaffLift";lift.position=Vector3(-25,0,-90);lift.rotation.y=PI;lift.floor_heights.assign([0.0,16.5]);lift.deck_numbers.assign([1,4]);lift.stop_ids.assign(["D01","D04"]);lift.stop_names.assign(["D01 staff network","D04 port-central receiving"]);lift.stop_codes.assign(["01","04"]);lift.gate_origin_xz=Vector2(-1.8,0);lift.identity_prefix="port_central_staff";lift.district_label="Port central staff";lift.cabin_file="AST-CIR-003.glb";lift.persistent_id=&"port_central_staff_lift_001";n.add_child(lift)
 for item in p.lights:
  var light:=SpotLight3D.new();light.name=item.name+"_Light";n.add_child(light);light.position=vec(item.at);light.rotation.x=-PI/2;light.light_color=Color(.82,.90,1);light.light_energy=.8;light.spot_range=6;light.spot_angle=75;light.shadow_enabled=false
 for deck in [1,4]:
  var sign:=Label3D.new();sign.name="StaffLandingSignD"+str(deck);sign.text="D%02d  |  PORT CENTRAL SERVICE"%deck;sign.font_size=40;sign.pixel_size=.004;sign.position=Vector3(-19,0 if deck==1 else 16.5,-86);sign.position.y+=1.7;sign.rotation.y=-PI/2;n.add_child(sign)
 return n
