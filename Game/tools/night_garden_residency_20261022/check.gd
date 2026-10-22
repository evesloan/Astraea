extends SceneTree
var host:Node3D
var manager
var actor:Node3D
var checks:Array=[]
var walks:=0
var route_samples:Array=[]
var receiving_only:=false
var oracle:Dictionary={}
var data:Dictionary
func _initialize()->void:call_deferred("run")
func check(label:String,ok:bool)->void:
 checks.append({"check":label,"pass":ok})
 if not ok:push_error(label)
func ray(a:Vector3,b:Vector3)->Dictionary:
 return host.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(a,b))
func raw(file:String)->Node3D:
 var d:=GLTFDocument.new();var s:=GLTFState.new()
 assert(d.append_from_file("res://assets/models/"+file,s)==OK)
 return d.generate_scene(s)
func probes(room:Dictionary)->Array:
 var a:Dictionary=room.allocation;var result:Array=[]
 for x in [.2,.5,.8]:
  for z in [.2,.5,.8]:
   var px:float=lerpf(a.allocation_x[0],a.allocation_x[1],x)
   var pz:float=lerpf(a.allocation_z[0],a.allocation_z[1],z)
   result.append([Vector3(px,94.2,pz),Vector3(px,92.8,pz)])
 return result
func key(down:bool)->void:
 var event:=InputEventKey.new();event.physical_keycode=KEY_W;event.pressed=down;Input.parse_input_event(event)
func walk_to(target:Vector3)->bool:
 for frame in range(1200):
  var offset:=target-actor.global_position;offset.y=0
  if offset.length()<.15:
   key(false)
   for settle in range(12):await physics_frame
   walks+=1
   route_samples.append({"target":str(target),"actual":str(actor.global_position),"floor":actor.is_on_floor()})
   return absf(actor.global_position.y-target.y)<.15
  actor.rotation.y=atan2(-offset.x,-offset.z);key(true)
  await physics_frame
 key(false);route_samples.append({"target":str(target),"actual":str(actor.global_position),"floor":actor.is_on_floor(),"timeout":true});return false
func run()->void:
 receiving_only="--receiving-only" in OS.get_cmdline_user_args()
 host=load("res://tools/night_garden_residency_20261022/fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 actor=Node3D.new();actor.name="Player";actors.add_child(actor);actor.position=Vector3(10000,10000,10000)
 data=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json"))
 # Independent full-source contact oracles, before adding district geometry.
 for room in ([] if receiving_only else data.rooms):
  var original:Node3D=load("res://scripts/night_garden_residency_20261022/source_visual.gd").contact_visual(host,room.model_file)
  await physics_frame;await physics_frame
  var result:Array=[]
  for q in probes(room):result.append(ray(q[0],q[1]))
  oracle[room.model_file]=result
  original.free();await physics_frame
 var lower:=Node3D.new();lower.name="D13_D14_StarboardCommons_WIP";districts.add_child(lower)
 var upper:=Node3D.new();upper.name="D15_D17_StarboardHouseUpper_WIP";lower.add_child(upper)
 var wrapper:=Node3D.new();wrapper.name="StarboardHouseUpperArchitecture";upper.add_child(wrapper);wrapper.position=Vector3(63,84,0)
 var commons:=raw("AST-COM-003.glb");wrapper.add_child(commons)
 for mesh:MeshInstance3D in commons.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 manager=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false);host.private_detail_residency=manager
 var district:Node3D=load("res://scripts/night_garden_residency_20261022/district.gd").build(host)
 check("all_30_registered",manager.entries.size()==30)
 check("far_initial_detail_not_eager",manager.statistics().resident_interiors==0)
 check("existing_38_index_entries_preserved",manager.index.size()==68)
 await physics_frame;await physics_frame
 for sign in [-1,1]:
  check("source_portal_seam_supported_%s"%sign,not ray(Vector3(90.5,93.2,14.04*sign),Vector3(90.5,92.8,14.04*sign)).is_empty())
  check("no_ghost_portal_wall_%s"%sign,ray(Vector3(90.5,94.3,13.7*sign),Vector3(90.5,94.3,14.4*sign)).is_empty())
 for room in ([] if receiving_only else data.rooms):
  var home:Node3D=district.get_node(room.allocation.proposed_runtime_id)
  var ids:Array=[];var doors:Array=[]
  for spec in room.doors:
   var door=home.get_node(spec.name);doors.append(door);ids.append(door.get_instance_id());door.process_mode=Node.PROCESS_MODE_DISABLED;door.open_fraction=.37;door.desired_open=true;door._apply_pose()
  for spec in room.lights:ids.append(home.get_node(spec.name).get_instance_id())
  var slots=home.get_meta("rest_slot_ids").duplicate()
  var center:=Vector3((room.allocation.allocation_x[0]+room.allocation.allocation_x[1])*.5,93,(room.allocation.allocation_z[0]+room.allocation.allocation_z[1])*.5)
  actor.position=center;manager.prepare_position(center)
  await physics_frame;await physics_frame
  var questions:=probes(room);var expected:Array=oracle[room.model_file]
  for i in range(questions.size()):
   var got:=ray(questions[i][0],questions[i][1]);var same:bool=got.is_empty()==expected[i].is_empty()
   if same and not got.is_empty():same=got.position.distance_to(expected[i].position)<.001
   check("contact_%s_%s"%[room.allocation.source_envelope_index,i],same)
  var entry:Dictionary={}
  for item in manager.entries:
   if item.home.get_ref()==home:entry=item;break
  for cycle in range(3):
   var previous:WeakRef=weakref(entry.detail)
   actor.position=Vector3(10000,10000,10000);manager.refresh(9.0);await physics_frame
   check("real_detail_release_%s_%s"%[room.allocation.source_envelope_index,cycle],previous.get_ref()==null and entry.detail==null)
   check("shell_present_%s_%s"%[room.allocation.source_envelope_index,cycle],home.get_child(0).find_children("*","MeshInstance3D",true,false).size()==7)
   actor.position=center;manager.prepare_position(center);await physics_frame
  var after:Array=[]
  for door in doors:
   after.append(door.get_instance_id());check("door_state_%s"%str(door.persistent_id),door.open_fraction==.37 and door.desired_open)
   door.open_fraction=1;door.desired_open=true;door._apply_pose();door.process_mode=Node.PROCESS_MODE_INHERIT
  for spec in room.lights:after.append(home.get_node(spec.name).get_instance_id())
  check("persistent_ids_%s"%room.allocation.source_envelope_index,ids==after and home.get_meta("rest_slot_ids")==slots)
 actor.position=Vector3(10000,10000,10000);manager.refresh(9.0);await physics_frame
 # Persistent rigid loads must keep nearby detail, even without the player.
 var cart:=RigidBody3D.new();cart.freeze=true;cart.position=Vector3(90,93,-42);actors.add_child(cart)
 manager.refresh(.2);check("rigid_load_keeps_detail",manager.statistics().resident_interiors>0)
 cart.free();manager.refresh(9);await physics_frame
 check("far_details_released",manager.statistics().resident_interiors==0)
 actor.free();actor=load("res://scripts/player.gd").new();actor.position=Vector3(90.5,93.03,-19 if receiving_only else -12.5);actors.add_child(actor);manager.set_physics_process(true)
 for settle in range(24):await physics_frame
 # One real-controller route, no route teleports: commons -> street -> room -> return.
 var targets:Array[Vector3]=[Vector3(90.5,93,-19),Vector3(90.5,93,-25.5),Vector3(87,93,-28),Vector3(84,93,-31),Vector3(84,93,-42),Vector3(87.5,93,-42)]
 for target in targets:
  var ok:=await walk_to(target);check("connected_walk_%s"%walks,ok)
  if not ok:break
 if walks==targets.size():
  var home:Node3D=district.get_node(data.rooms[0].allocation.proposed_runtime_id);var door=home.get_node("EntryDoor")
  door.interact(actor)
  for frame in range(100):await physics_frame
  check("actual_entry_controller_closes",door.open_fraction<.01)
  door.interact(actor)
  for frame in range(100):await physics_frame
  check("actual_entry_controller_opens",door.open_fraction>.99)
  targets.reverse();targets.append(Vector3(90.5,93,-19 if receiving_only else -12.5))
  for target in targets:
   var ok:=await walk_to(target);check("return_walk_%s"%walks,ok)
   if not ok:break
 var failures:=checks.filter(func(row):return not row.pass)
 var result:={"scope":"30-room residency/contact/controller candidate in exact raw commons fixture; not full ship or private admission acceptance","checks":checks,"count":checks.size(),"failures":failures.size(),"receiving_only":receiving_only,"route_samples":route_samples,"continuous_walk_legs":walks,"route_teleports":0,"rooms":30,"registered":manager.entries.size(),"main_integration":false,"visual_acceptance":false}
 var output:=OS.get_cmdline_user_args()[0];assert(not FileAccess.file_exists(output))
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(result,"  ")+"\n");f.close()
 print("NIGHT_GARDEN_RESIDENCY ",checks.size()," failures=",failures.size()," walks=",walks)
 quit(0 if failures.is_empty() else 1)
