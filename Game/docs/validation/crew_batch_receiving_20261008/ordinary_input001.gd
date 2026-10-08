extends "res://tests/medical_test_scene.gd"
# Five crew destinations on one D03 circuit, one existing public approach setup;
# production W input through all branches and return without further relocation.
const DATA="res://data/architecture/crew_batch/runtime_manifest.json"
const DATA_SHA="a549b97cf3c74539b3730d803878475384c6fd2e9f2c13f3666be5f610e10e17"
var travelled_m:float=0.0
var walked_frames:int=0
var completed:Array=[]
var arrivals:int=0
var aperture_clear_rays:int=0
var retained_wall_controls:int=0
# Finite wall allowance for five destinations; assertions/input/physics unchanged.
func _process(_delta:float)->bool:
 if started>0 and Time.get_ticks_msec()-started>1200000 and not failed:
  require(false,"1200-second bounded five-section watchdog")
 return false
func _initialize()->void:
 test_name="crew_batch_ordinary_input"
 call_deferred("run")
func advance(count:int,_check:bool=false)->bool:
 for frame in range(count):
  await physics_frame
  frames+=1
  if failed:return false
  if not require(frames<100000,"100000-frame circuit budget"):return false
 return true
func write_receipt(status:String,detail:String="")->void:
 var f:=FileAccess.open(receipt_path,FileAccess.WRITE)
 if f!=null:f.store_string(JSON.stringify({"status":status,"detail":detail,"completed_branches":completed,"initial_deck_arrivals":arrivals,"walked_frames":walked_frames,"walked_m":travelled_m,"support_samples":support_samples,"aperture_clear_rays":aperture_clear_rays,"retained_wall_controls":retained_wall_controls,"data_sha256":FileAccess.get_sha256(DATA),"scope":"One D03 connected five-destination circuit from an existing public approach, all source branches and return. No loaded cart, species, programme operation, visual or hardware acceptance."},"  ")+"\n")
func walk(point:Vector2,y:float)->bool:
 release_inputs()
 var allowance:=ceili(Vector2(actor.position.x,actor.position.z).distance_to(point)/3.1*60)+240
 for i in range(allowance):
  var delta:=point-Vector2(actor.position.x,actor.position.z)
  var speed:=Vector2(actor.velocity.x,actor.velocity.z).length()
  if delta.length()<.16 and speed<.08:
   key(KEY_W,false)
   return support_at(Vector3(point.x,y,point.y))
  if delta.length()>.025:actor.rotation.y=atan2(-delta.x,-delta.y)
  actor.set("pitch",0.0);actor.camera.rotation.x=0
  key(KEY_W,delta.length()>maxf(.11,speed*speed/32.0+.035))
  var previous:Vector3=actor.global_position
  if not await advance(1):return false
  if not require(actor.global_position.distance_to(previous)<.25,"Unexpected displacement"):return false
  if not require(absf(actor.position.y-y)<.08,"Left deck datum"):return false
  if not support_at(Vector3(actor.position.x,y,actor.position.z)):return false
  travelled_m+=Vector2(actor.position.x-previous.x,actor.position.z-previous.z).length()
  walked_frames+=1
 var contacts:Array=[]
 for j in range(actor.get_slide_collision_count()):
  var hit:KinematicCollision3D=actor.get_slide_collision(j)
  contacts.append({"collider":str(hit.get_collider().get_path()),"normal":str(hit.get_normal()),"position":str(hit.get_position())})
 print("CREW BLOCKING CONTACTS ",contacts)
 return require(false,"Blocked at %s toward %s"%[actor.position,point])
func run()->void:
 started=Time.get_ticks_msec()
 receipt_path="/workspace/scratch/375c2e438292/crew_batch_receiving_20261008/ordinary_input_result001.json"
 if not require(FileAccess.get_sha256(DATA)==DATA_SHA,"Frozen runtime contract"):return
 main=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
 for i in range(150):await physics_frame
 ship=main.get_node("World360/Astraea");actor=ship.get_node("ShipSpace/PersistentActors/Player")
 cart=ship.find_child("CustodialCart",true,false);floors=ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false)
 space=ship.get_world_3d().direct_space_state
 # Check the actual D03-only doorway and retained adjacent wall/head/other-deck controls.
 for z in [430.25,430.75,431.25,431.75,432.25,432.75,433.25,433.75]:
  for y in [12.2,12.6,13.0,13.4,13.8,14.3,14.5]:
   if not require(ray(Vector3(7.1,y,z),Vector3(8.6,y,z),exclusions()).is_empty(),"D03 aperture obstructed at "+str(Vector2(y,z))):return
   aperture_clear_rays+=1
 for q in [[13.0,429.5],[13.0,434.5],[15.0,432.0],[7.0,432.0],[19.0,432.0]]:
  var hit:Dictionary=ray(Vector3(7.1,q[0],q[1]),Vector3(8.1,q[0],q[1]),exclusions())
  if not require(not hit.is_empty(),"Retained aft sidewall/header control missing"):return
  retained_wall_controls+=1
 for x in [7.2,7.6,7.79,7.9,8.01,8.3]:
  for z in [430.4,432.0,433.6]:
   if not support_at(Vector3(x,12.0,z)):return
 if not require(actor.get_script().resource_path=="res://scripts/player.gd" and actor.gameplay_input_enabled and actor.is_physics_processing(),"Unchanged active production player"):return
 if not require(ship.arrive_at(Vector3(-49,12.1,0),0),"Supported existing public approach"):return
 arrivals=1
 if not await advance(45):return
 var circuits:Array=[{"id": "D03_directory_05_entry", "points": [[-49, 0], [-52, 0], [-54, 0]]}, {"id": "D03_directory_05_east_west_transfer_cart", "points": [[-54, 0], [-54, 0], [-96, 0], [-54, 0], [-54, 0]]}, {"id": "D03_directory_05_demonstration_body", "points": [[-54, 0], [-85, 0], [-85, -12], [-91.5, -12], [-91.5, -20], [-91.5, -12], [-85, -12], [-85, 0], [-54, 0]]}, {"id": "D03_directory_05_practical_cart_approach", "points": [[-54, 0], [-65, 0], [-65, -15.5], [-65, 0], [-54, 0]]}, {"id": "D03_directory_05_focused_body", "points": [[-54, 0], [-65, 0], [-65, 15.5], [-65, 0], [-54, 0]]}, {"id": "D03_directory_05_equipment_cart", "points": [[-54, 0], [-85, 0], [-85, 16.8], [-85, 0], [-54, 0]]}, {"id": "D03_directory_05_public_return", "points": [[-54, 0], [-52, 0], [-49, 0]]}, {"id": "training_to_administration", "points": [[-49, 0], [-33, 46], [-28, 50], [5, 51], [27, 51], [33, 47], [49, 0]]}, {"id": "D03_directory_06_entry", "points": [[49, 0], [52, 0], [54, 0]]}, {"id": "D03_directory_06_help_transfer_cart", "points": [[54, 0], [54, 0], [96, 0], [54, 0], [54, 0]]}, {"id": "D03_directory_06_working_bay_body", "points": [[54, 0], [66, 0], [66, -18], [66, 0], [54, 0]]}, {"id": "D03_directory_06_private_interview_body", "points": [[54, 0], [86, 0], [86, -10.5], [90, -10.5], [90, -17], [90, -10.5], [86, -10.5], [86, 0], [54, 0]]}, {"id": "D03_directory_06_records_cart_receiving", "points": [[54, 0], [66, 0], [66, 10.6], [66, 0], [54, 0]]}, {"id": "D03_directory_06_care_stock_cart", "points": [[54, 0], [86, 0], [86, 11], [90, 11], [90, 20.5], [90, 11], [86, 11], [86, 0], [54, 0]]}, {"id": "D03_directory_06_public_return", "points": [[54, 0], [52, 0], [49, 0]]}, {"id": "administration_to_recreation", "points": [[49, 0], [32, 51], [3, 80], [-3, 216]]}, {"id": "D03_directory_07_entry", "points": [[-3, 216], [-8, 216], [-10, 216]]}, {"id": "D03_directory_07_through_transfer_cart", "points": [[-10, 216], [-10, 216], [-52, 216], [-10, 216], [-10, 216]]}, {"id": "D03_directory_07_social_body", "points": [[-10, 216], [-35, 216], [-32, 211], [-32, 206], [-32, 211], [-35, 216], [-10, 216]]}, {"id": "D03_directory_07_game_body", "points": [[-10, 216], [-20, 216], [-20, 206], [-20, 216], [-10, 216]]}, {"id": "D03_directory_07_quiet_reading_body", "points": [[-10, 216], [-22, 216], [-22, 223], [-20, 223], [-20, 228.5], [-20, 223], [-22, 223], [-22, 216], [-10, 216]]}, {"id": "D03_directory_07_care_supply_cart", "points": [[-10, 216], [-10.2, 216], [-10.2, 247.5], [-15, 247.5], [-10.2, 247.5], [-10.2, 216], [-10, 216]]}, {"id": "D03_directory_07_public_return", "points": [[-10, 216], [-8, 216], [-3, 216]]}, {"id": "recreation_to_briefing", "points": [[-3, 216], [3, 216]]}, {"id": "D03_directory_08_entry", "points": [[3, 216], [8, 216], [10, 216]]}, {"id": "D03_directory_08_shared_shift_transfer_cart", "points": [[10, 216], [10, 216], [52, 216], [10, 216], [10, 216]]}, {"id": "D03_directory_08_port_brief_body", "points": [[10, 216], [22, 216], [22, 205], [22, 216], [10, 216]]}, {"id": "D03_directory_08_starboard_brief_body", "points": [[10, 216], [42, 216], [42, 205], [42, 216], [10, 216]]}, {"id": "D03_directory_08_preparation_cart_receiving", "points": [[10, 216], [22, 216], [22, 224.5], [22, 216], [10, 216]]}, {"id": "D03_directory_08_afterbrief_rest_body", "points": [[10, 216], [43, 216], [43, 234.9], [43, 216], [10, 216]]}, {"id": "D03_directory_08_public_return", "points": [[10, 216], [8, 216], [3, 216]]}, {"id": "briefing_to_uniforms", "points": [[3, 216], [4, 291], [3, 293], [3, 426], [6, 432]]}, {"id": "D03_directory_10_entry", "points": [[6, 432], [8, 432], [9.8, 432]]}, {"id": "D03_directory_10_main_transfer_cart", "points": [[9.8, 432], [9.8, 432], [51.9, 432], [9.8, 432], [9.8, 432]]}, {"id": "D03_directory_10_rear_change_and_issue_cart", "points": [[9.8, 432], [51.9, 432], [51.9, 450.1], [22, 450.1], [22, 452.7], [22, 450.1], [51.9, 450.1], [51.9, 432], [9.8, 432]]}, {"id": "D03_directory_10_front_change_body", "points": [[9.8, 432], [19, 432], [19, 418.8], [20.8, 418.8], [20.8, 413], [20.8, 418.8], [19, 418.8], [19, 432], [9.8, 432]]}, {"id": "D03_directory_10_used_return_body", "points": [[9.8, 432], [51.9, 432], [51.9, 450.1], [42, 450.1], [42, 455], [42, 450.1], [51.9, 450.1], [51.9, 432], [9.8, 432]]}, {"id": "D03_directory_10_public_return", "points": [[9.8, 432], [8, 432], [6, 432]]}, {"id": "return_briefing_to_uniforms", "points": [[6, 432], [3, 426], [3, 293], [4, 291], [3, 216]]}, {"id": "return_recreation_to_briefing", "points": [[3, 216], [-3, 216]]}, {"id": "return_administration_to_recreation", "points": [[-3, 216], [3, 80], [32, 51], [49, 0]]}, {"id": "return_training_to_administration", "points": [[49, 0], [33, 47], [27, 51], [5, 51], [-28, 50], [-33, 46], [-49, 0]]}]
 for circuit in circuits:
  for p in circuit.points:
   if not await walk(Vector2(p[0],p[1]),12.0):return
  completed.append(circuit.id);print("CREW CIRCUIT ",circuit.id)
 release_inputs();write_receipt("PASS")
 print("CREW ORDINARY INPUT PASS: ",travelled_m," m; ",walked_frames," input frames")
 main.queue_free();await process_frame;quit(0)
