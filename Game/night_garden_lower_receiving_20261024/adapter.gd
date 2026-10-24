extends RefCounted
const P:="res://night_garden_lower_receiving_20261024/"
const BANK:="res://night_garden_lower_bank_20261022/"
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func fail(message:String)->Dictionary:
 push_error("NightGarden17 receiving: "+message);return {"error":message}
static func preflight(ship:Node3D,plan:Dictionary,package:Dictionary,index:Dictionary)->Dictionary:
 var pins:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"CONTRACTS.json"))
 for path:String in pins:
  if FileAccess.get_sha256(path)!=pins[path]:return fail("Exact prerequisite changed: "+path)
 var districts:=ship.get_node("ShipSpace/Districts")
 if districts.has_node("NightGardenLower17_20261024"):return fail("Already installed")
 var manager:Node=ship.private_detail_residency
 if manager==null or not bool(ship.get_meta("central_residential_streets_installed",false)):return fail("Existing manager/street owner absent")
 if package.rooms.size()!=17 or index.size()!=17:return fail("Allocation count differs")
 var doors:={};var rests:={}
 for room:Dictionary in package.rooms:
  var record:Dictionary=index[room.model_file]
  if manager.index.has(room.model_file)or districts.find_child(record.room_id,true,false)!=null:return fail("Duplicate room "+record.room_id)
  if record.room_id!=room.allocation.proposed_runtime_id:return fail("Room identity differs")
  for pair:Array in [[record.full_path,record.sha256],[record.shell_path,record.shell_sha256],[record.detail_path,record.detail_sha256]]:
   if FileAccess.get_sha256(pair[0])!=pair[1]:return fail("Retained room bytes differ: "+str(pair[0]))
  for door:Dictionary in room.doors:
   if doors.has(door.persistent_id):return fail("Duplicate door ID")
   doors[door.persistent_id]=true
  for id:String in room.allocation.proposed_rest_slot_ids:
   if rests.has(id):return fail("Duplicate rest ID")
   rests[id]=true
 if doors.size()!=53 or rests.size()!=19:return fail("Door/rest totals differ")
 var guards:=ship.get_node("ShipSpace/CentralResidentialStreetFloors/CentralResidentialStreetGuards")
 var remove:Array[Node]=[];var expected_posts:Array[Vector3]=[]
 for row:Dictionary in plan.replace_exact_guards:
  var a:=v(row.a);var b:=v(row.b)
  var rail:=guards.get_node_or_null(str(row.id)+"Rail")as MeshInstance3D
  var body:=guards.get_node_or_null(str(row.id)+"Contact")as StaticBody3D
  if rail==null or body==null or not rail.mesh is CylinderMesh:return fail("Original guard owner absent: "+row.id)
  if rail.position.distance_to((a+b)*.5+Vector3.UP*1.1)>.0001 or absf(rail.mesh.height-a.distance_to(b))>.0001:return fail("Guard rail preimage changed")
  var shapes:=body.find_children("*","CollisionShape3D",true,false)
  if shapes.size()!=1 or not shapes[0].shape is BoxShape3D:return fail("Guard contact shape changed")
  if body.position.distance_to((a+b)*.5+Vector3.UP*.55)>.0001 or shapes[0].shape.size.distance_to(Vector3(a.distance_to(b),1.1,.08))>.0001:return fail("Guard contact preimage changed")
  remove.append(rail);remove.append(body)
  var steps:=maxi(1,ceili(a.distance_to(b)/2.0))
  for i in range(steps+1):expected_posts.append(a.lerp(b,float(i)/steps)+Vector3.UP*.55)
 # Repeated original post names are auto-renamed by Godot. Match their exact
 # source geometry/positions as a multiset; shared terminal posts occur twice.
 var posts:Array[Node]=[]
 for position:Vector3 in expected_posts:
  var found:Node=null
  for child:Node in guards.get_children():
   if posts.has(child)or not child is MeshInstance3D or not child.mesh is CylinderMesh:continue
   if absf(child.mesh.height-1.1)>.00001 or absf(child.mesh.top_radius-.035)>.00001 or absf(child.mesh.bottom_radius-.035)>.00001:continue
   if child.position.distance_to(position)<.0001:found=child;break
  if found==null:return fail("Exact guard post absent at "+str(position))
  posts.append(found)
 remove.append_array(posts)
 return {"remove":remove,"guard_parent":guards,"old_guard_child_count":guards.get_child_count()}
static func build(ship:Node3D)->Node3D:
 var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(BANK+"PACKAGE.json"))
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(BANK+"evidence/INDEX.json")).rooms
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"RECEIVING.json"))
 var verified:=preflight(ship,plan,package,index)
 if verified.has("error"):return null
 var manager:Node=ship.private_detail_residency
 var district:=Node3D.new();district.name="NightGardenLower17_20261024";ship.get_node("ShipSpace/Districts").add_child(district)
 var floor_owner:Node3D=load("res://scripts/structural_floor_builder.gd").build_regions(district,ship.stone,ship.ivory,plan.regions,{},"MissingOnlyStreetConnections")
 for room:Dictionary in package.rooms:
  var record:Dictionary=index[room.model_file];var home:=Node3D.new();home.name=record.room_id;district.add_child(home)
  manager.index[room.model_file]=record;manager.night_files[room.model_file]=true
  home.set_meta("census_source_index",room.allocation.source_envelope_index);home.set_meta("allocation_sha256",room.allocation.allocation_sha256);home.set_meta("rest_slot_ids",room.allocation.proposed_rest_slot_ids);home.set_meta("species_ready",false);home.set_meta("finished",false)
  var rests:Array=room.components.filter(func(c):return c.has("rest_slot_id"));home.set_meta("bank_rest_bindings",rests)
  var fittings:Array=[]
  for binding:Dictionary in rests:fittings.append({"rest_slot_id":binding.rest_slot_id,"binding":binding,"operation_accepted":false})
  home.set_meta("rest_fittings",fittings)
  var shell:Node3D=manager.register_room(home,room.model_file)
  load("res://quiet_grove_bank_20261022/adapter.gd").decorate_shell(shell,room)
  var owner:Dictionary=plan.retained_private_floor_owners.filter(func(o):return o.room_id==record.room_id)[0]
  var slab:=shell.find_child(owner.mesh_name,true,false)as MeshInstance3D
  if slab==null:push_error("Retained private floor absent");return null
  var bounds:AABB=slab.global_transform*slab.get_aabb()
  if bounds.position.distance_to(v(owner.min))>.0002 or bounds.end.distance_to(v(owner.max))>.0002:push_error("Retained private floor pose differs");return null
  home.set_meta("retained_floor_owner",str(home.get_path_to(slab)))
  for data:Dictionary in room.doors:
   var door:Node3D=load("res://scripts/"+data.controller).new();door.name=data.name;door.persistent_id=data.persistent_id;door.position=v(data.position);door.rotation.y=data.yaw;home.add_child(door)
  for data:Dictionary in room.lights:
   var light:=SpotLight3D.new();light.name=data.name;light.position=v(data.position);light.rotation.x=-PI/2;light.light_color=Color(1,.90,.74);light.light_energy=data.energy;light.spot_range=data.range;light.spot_angle=72;light.shadow_enabled=true;light.visible=false;home.add_child(light)
 var new_guards:=Node3D.new();new_guards.name="ConnectedStreetGuards";floor_owner.add_child(new_guards)
 for row:Dictionary in plan.new_guards:load("res://scripts/central_house_connections.gd").guard_segment(ship,new_guards,row.id,v(row.a),v(row.b))
 # Only after all protected shells/slabs and replacement barriers exist.
 for old:Node in verified.remove:old.free()
 if verified.guard_parent.get_child_count()!=int(verified.old_guard_child_count)-verified.remove.size():push_error("Unexpected guard mutation");return null
 district.set_meta("source_rooms",17);district.set_meta("reserved_rests",19);district.set_meta("door_ids",53);district.set_meta("new_capacity",0);district.set_meta("new_private_floors",0);district.set_meta("missing_street_area_m2",273.06);district.set_meta("replaced_guard_groups",5);district.set_meta("removed_guard_nodes",verified.remove.size());district.set_meta("visual_accepted",false);district.set_meta("primary_structure_accepted",false);district.set_meta("operating_admission_accepted",false)
 return district
