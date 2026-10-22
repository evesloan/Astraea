extends SceneTree
const P:="res://family_specialty_bank_20261022/"
var checks:Array=[]
var routes:Array=[]
var actor:CharacterBody3D
func _initialize()->void:call_deferred("run")
func check(ok:bool,label:String)->void:
 checks.append({"pass":ok,"label":label})
 if not ok:push_error(label)
func key(down:bool)->void:
 var e:=InputEventKey.new();e.physical_keycode=KEY_W;e.pressed=down;Input.parse_input_event(e)
func walk(target:Vector3)->bool:
 for frame in range(240):
  var delta:=target-actor.global_position;delta.y=0
  if delta.length()<.12:
   key(false)
   for settle in range(8):await physics_frame
   return actor.is_on_floor() and absf(actor.global_position.y-target.y)<.12
  actor.rotation.y=atan2(-delta.x,-delta.z);key(true);await physics_frame
 key(false);return false
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var host:Node3D=load("res://scripts/family_specialty_integration_20261022/fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 actor=load("res://scripts/player.gd").new();actor.position=Vector3(10000,10000,10000);actors.add_child(actor);actor.set_physics_process(false)
 var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
 var house:Node3D=load("res://scripts/family_terrace_adoption.gd").build(host)
 # Replay the exact installed D14 mesh input only; unrelated riser geometry is omitted by this bounded fixture.
 var gp:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/GUARD_PLAN.json"))
 for batch:String in gp.current_sources:
  var row:Dictionary=gp.current_sources[batch];var src:Node3D=load("res://"+str(row.file).trim_prefix("Game/")).instantiate();var patch:MeshInstance3D=src.find_child(str(row.replacement_name),true,false);var old:MeshInstance3D=house.find_child(batch,true,false)
  old.mesh=patch.mesh;var shape:CollisionShape3D=old.find_children("*","CollisionShape3D",true,false)[0];var margin:float=shape.shape.margin;shape.shape=old.mesh.create_trimesh_shape();shape.shape.margin=margin;src.free()
 var before_meshes:=house.find_children("*","MeshInstance3D",true,false).size()
 var ordinary:Node3D=districts.get_node("FamilyTerraceRoomCandidates");var original_ids:Array=[]
 for n in ordinary.get_children():original_ids.append(n.get_instance_id())
 check(original_ids.size()==82,"82 retained ordinary homes present")
 await host._construction_step("family_d16_receiving_20261016/package.gd")
 var district:Node3D=districts.get_node("FamilySpecialty47_20261022")
 var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PACKAGE_R002.json"))
 check(district.get_meta("reserved_rests")==59 and district.get_meta("new_capacity")==0,"59 unchanged reserved rest IDs; no new capacity")
 check(manager.entries.size()==47,"47 rooms registered in existing residency owner")
 check(house.find_children("*","MeshInstance3D",true,false).size()==before_meshes-18,"Only18 source guard/infill batches replaced; floors unchanged")
 for id in original_ids:check(instance_from_id(id)!=null,"Original ordinary home object retained")
 for frame in range(100):await physics_frame
 for room in package.rooms:
  var id:String=str(room.allocation.proposed_runtime_id);var home:Node3D=district.get_node(id)
  check(home.get_meta("rest_slot_ids")==room.allocation.proposed_rest_slot_ids,id+" reserved identity")
  var entry:Dictionary=manager.entries.filter(func(e):return str(e.record.model_file)==str(room.model_file))[0]
  manager._load_entry(entry);check(is_instance_valid(entry.detail),id+" actual private detail loaded")
  var door_row:Dictionary=room.doors.filter(func(d):return str(d.controller)=="guest_entry_door.gd")[0]
  var door:Node3D=home.get_node(str(door_row.name));check(door.open_fraction>.99,id+" unchanged entry controller opens fully")
  var y:float=room.allocation.floor_y;var z:float=door_row.position[2];var outboard:bool=room.allocation.allocation_x[0]>45
  actor.position=Vector3(44,y+.04,z);actor.velocity=Vector3.ZERO;actor.set_physics_process(true)
  for settle in range(15):await physics_frame
  var entered:bool=await walk(Vector3(47.4 if outboard else 40.6,y,z));check(entered,id+" street-to-room controller contact")
  var exited:bool=await walk(Vector3(44,y,z));check(exited,id+" room-to-street controller contact")
  routes.append({"allocation":room.allocation.source_envelope_index,"entered":entered,"exited":exited,"actual":str(actor.position)})
  actor.set_physics_process(false);actor.position=Vector3(10000,10000,10000);
  if is_instance_valid(entry.detail):manager._release_entry(entry)
  check(not is_instance_valid(entry.detail),id+" detail released; shell doors lights retained")
 var failed:=checks.filter(func(c):return not c.pass).size()
 var receipt:={"status":"PASS" if failed==0 else "FAIL","checks":checks,"routes":routes,"scope":"actual main hook, existing Family house82ordinary homes and47specialty rooms; no full ship launch","main_hook_executed":true,"full_startup":false,"visual_accepted":false}
 var f:=FileAccess.open(P+"evidence/CHECK_R004.json",FileAccess.WRITE);f.store_string(JSON.stringify(receipt,"\t")+"\n");f.close();print("FAMILY_CHECK ",checks.size()," failures=",failed);host.free();await process_frame;quit(1 if failed else 0)
