extends RefCounted
const P:="res://sunset_specialty_bank_20261022/"
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PACKAGE_R002.json"))
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/INDEX_R002.json")).rooms
 var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/RECEIVING_BUILD_R002.json"))
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 assert(not districts.has_node("SunsetSpecialty47_20261022"))
 var house:Node3D=districts.get_node("SunsetReceivingCandidate")
 assert(FileAccess.get_sha256("res://assets/models/SUNSET_ARCHITECTURE_lift_r003.glb")=="a6f6646dce45a5cda6b8562be2b0c768c734591021fe1b39c713310c94a7b21f")
 var manager:Node=ship.private_detail_residency;assert(manager!=null)
 var patch:Node3D=load(P+"runtime/Sunset47Receiving_r002.scn").instantiate()
 var old_guards:Array[MeshInstance3D]=[]
 for row:Dictionary in receipt.guard_batches:
  var old:=house.find_child(row.batch,true,false)as MeshInstance3D
  assert(old!=null and old.mesh!=null and old.get_meta("extras",{}).get("category","")=="guard")
  assert(old.find_children("StaticContact","StaticBody3D",true,false).size()==1 and patch.find_child(row.batch,true,false)!=null);old_guards.append(old)
 for room:Dictionary in package.rooms:
  var record:Dictionary=index[room.model_file]
  assert(record.room_id==room.allocation.proposed_runtime_id and not manager.index.has(room.model_file))
  assert(FileAccess.get_sha256("res://assets/models/"+room.model_file)==record.sha256)
  assert(FileAccess.get_sha256(record.shell_path)==record.shell_sha256 and FileAccess.get_sha256(record.detail_path)==record.detail_sha256)
  assert(districts.find_child(record.room_id,true,false)==null)
 var district:=Node3D.new();district.name="SunsetSpecialty47_20261022";districts.add_child(district)
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
  for data:Dictionary in room.doors:
   var door:Node3D=load("res://scripts/"+data.controller).new();door.name=data.name;door.persistent_id=data.persistent_id;door.position=v(data.position);door.rotation.y=data.yaw;home.add_child(door)
  for data:Dictionary in room.lights:
   var light:=SpotLight3D.new();light.name=data.name;home.add_child(light);light.position=v(data.position);light.rotation.x=-PI/2;light.light_color=Color(1,.90,.74);light.light_energy=data.energy;light.spot_range=data.range;light.spot_angle=72;light.shadow_enabled=true;light.visible=false
 district.add_child(patch)
 for mesh:MeshInstance3D in patch.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 for old in old_guards:old.free()
 district.set_meta("rooms",47);district.set_meta("reserved_rests",59);district.set_meta("new_capacity",0);district.set_meta("visual_accepted",false);district.set_meta("primary_structure_accepted",false)
 return district
