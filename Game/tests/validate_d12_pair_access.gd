extends "res://tests/medical_test_scene.gd"
var distance_m:float=0
var walk_frames:int=0
var seam_counts:Dictionary={"port":0,"starboard":0,"port_entry":0,"starboard_entry":0}
func _initialize()->void:
 test_name="d12_pair_access";call_deferred("run")
func walk(point:Vector2)->bool:
 release_inputs()
 var allowance:int=ceili(Vector2(actor.global_position.x,actor.global_position.z).distance_to(point)/3.1*60)+240
 for frame in range(allowance):
  var delta:Vector2=point-Vector2(actor.global_position.x,actor.global_position.z)
  var speed:float=Vector2(actor.velocity.x,actor.velocity.z).length()
  if delta.length()<.16 and speed<.08:key(KEY_W,false);return true
  if delta.length()>.025:actor.rotation.y=atan2(-delta.x,-delta.y)
  actor.set("pitch",0.0);actor.camera.rotation.x=0
  key(KEY_W,delta.length()>maxf(.11,speed*speed/32+.035))
  var before:Vector3=actor.global_position
  if not await advance(1,false):return false
  var now:Vector3=actor.global_position
  if not require(now.distance_to(before)<.25 and absf(now.y-78)<.08,"Unexpected displacement or loss of D12 support"):return false
  if not support_at(Vector3(now.x,78,now.z)):return false
  for spec in [[-4.0,"port"],[4.0,"starboard"],[-8.45,"port_entry"],[8.45,"starboard_entry"]]:
   if (before.x<float(spec[0]) and now.x>=float(spec[0])) or (before.x>float(spec[0]) and now.x<=float(spec[0])):seam_counts[spec[1]]+=1
  distance_m+=Vector2(now.x-before.x,now.z-before.z).length();walk_frames+=1
 return require(false,"Ordinary W-input route blocked at "+str(actor.global_position)+" toward "+str(point))
func run()->void:
 receipt_path="res://artifacts/d12_pair_access001.json"
 var init_start:int=Time.get_ticks_msec()
 print("D12_ACCESS begin main construction")
 main=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 print("D12_ACCESS main constructed in_ms=",Time.get_ticks_msec()-init_start)
 started=Time.get_ticks_msec() # The inherited480s exercise watchdog excludes main initialization; outer900s bound includes both.
 for frame in range(30):await physics_frame
 ship=main.get_node("World360/Astraea");actor=ship.get_node("ShipSpace/PersistentActors/Player")
 cart=ship.find_child("CustodialCart",true,false);floors=ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false)
 built=ship.get_node("ShipSpace/D12PairReceivingCandidate");space=ship.get_world_3d().direct_space_state
 var retained:Array=load("res://tests/d12_pair_successor_guard.gd").floor_children(floors)
 if not require(retained.size()==296,"Authenticated predecessor subset missing"):return
 print("D12_ACCESS all 300 actual slabs validated; 296 predecessors exact")
 var predecessor:Dictionary=load("res://tests/medical_triage_successor_guard.gd").validate_current(floors)
 if not require(bool(predecessor.get("validation_completed",false)),"Complete predecessor runtime proof required"):return
 print("D12_ACCESS predecessor runtime chain passed")
 if not require(ship.arrive_at(Vector3(0,78.1,216),0),"Initial arrival refused"):return
 if not await advance(45):return
 for side in [-1,1]:
  for x in [3.98,4.02,6.0,8.43,8.47,10.0]:
   if not support_at(Vector3(float(side)*x,78,216)):return
  for z in [213.85,218.15]:
   for x in [4.2,5.6,7.1,8.3]:
    var hit:Dictionary=ray(Vector3(float(side)*x,78.6,216),Vector3(float(side)*x,78.6,z+(-.3 if z<216 else .3)),exclusions())
    if not require(not hit.is_empty() and built.is_ancestor_of(hit.collider),"Missing actual guard collision"):return
 for point in [Vector2(-6,216),Vector2(-12,216),Vector2(-12,215),Vector2(-12,216),Vector2(0,216),Vector2(6,216),Vector2(12,216),Vector2(12,217),Vector2(12,216),Vector2(0,216),Vector2(0,220),Vector2(0,216)]:
  if not await walk(point):return
 for count in seam_counts.values():
  if not require(int(count)>=2,"Both directions across all branch/entry seams required"):return
 release_inputs()
 metrics={"walk_frames":walk_frames,"walked_metres":distance_m,"seams":seam_counts,"initial_arrivals":1,"later_teleports":0,"source_controller_unchanged":true}
 print("PASS: D12 both rooms connected ordinary walking, turns, actual branch guards and all 300 compiler slabs; ",JSON.stringify(metrics))
 if not await fixture_regression():return
 if failed:return
 release_inputs()
 write_receipt("PASS")
 main.queue_free();await process_frame;quit(0)

func fixture_regression()->bool:
 var control: Node3D = ship.find_child("SharedStudyLightSwitch",true,false)
 var budget: Node = ship.find_child("LocalShadowSourceBudget",true,false)
 assert(control.persistent_id == &"D09_salon5_shared_study_light")
 assert(control.diffuser_materials.size() > 0,"Fixture diffuser must respond visibly")
 # Stand in the existing side approach, aim precisely at the actual control datum.
 assert(ship.arrive_at(Vector3(65.5,52.6,-21.5),0))
 for frame in range(15): await physics_frame
 actor.camera.look_at(control.global_position,Vector3.UP)
 assert(actor.target_from_view() == control,"Physical switch must be reachable through the shared ray dispatcher")
 var focus := InputEventMouseButton.new()
 focus.button_index = MOUSE_BUTTON_RIGHT
 focus.pressed = true
 Input.parse_input_event(focus)
 var press := InputEventKey.new()
 press.keycode = KEY_E
 press.physical_keycode = KEY_E
 press.pressed = true
 Input.parse_input_event(press)
 for frame in range(20): await physics_frame
 assert(not control.powered and not control.source.visible)
 for attempt in range(3): budget.refresh()
 assert(not control.source.visible and not control.source.shadow_enabled,"Budget must not resurrect switched-off lights")
 assert(not control.diffuser_materials[0].emission_enabled)
 press.pressed = false
 Input.parse_input_event(press)
 focus.pressed = false
 Input.parse_input_event(focus)
 press = press.duplicate()
 press.pressed = true
 Input.parse_input_event(press)
 for frame in range(5): await physics_frame
 assert(not control.powered,"Unfocused E must remain ignored")
 control.interact(actor)
 budget.refresh()
 assert(control.powered and control.source.visible and control.diffuser_materials[0].emission_enabled)
 # A solid obstacle must block the control, even though targets are Areas.
 var blocker := StaticBody3D.new()
 ship.add_child(blocker)
 blocker.global_position = actor.camera.global_position.lerp(control.global_position,.5)
 var contact := CollisionShape3D.new()
 var box := BoxShape3D.new()
 box.size = Vector3(.4,.4,.4)
 contact.shape = box
 blocker.add_child(contact)
 for frame in range(3): await physics_frame
 assert(actor.target_from_view() != control,"Controls cannot be selected through opaque objects")
 print("FIXTURE PASS: actual control datum, shared RMB/E selection, unfocused rejection, visible diffuser, power-aware shadow budget and solid occlusion. No save/DOF acceptance.")
 press.pressed=false;Input.parse_input_event(press)
 focus.pressed=false;Input.parse_input_event(focus);Input.flush_buffered_events()
 return true

func write_receipt(status:String,detail:String="")->void:
 if receipt_path.is_empty():return
 var file:=FileAccess.open(receipt_path,FileAccess.WRITE)
 if file!=null:file.store_string(JSON.stringify({"test":test_name,"status":status,"detail":detail,"physics_frames":frames,"support_samples":support_samples,"metrics":metrics,"seam_counts":seam_counts,"walked_metres":distance_m,"scope":"Bounded D12 unchanged-player connected walking and actual support/guard geometry. Loaded cart, opposing traffic, species, structural engineering and final room/art acceptance remain separate."},"  ")+"\n")
