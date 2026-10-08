extends "res://tests/medical_test_scene.gd"
# Three independent deck circuits. Each has one verified entrance setup;
# all 24 outward/return branches use production W input, without relocation.
const DATA="res://data/architecture/night_table/runtime_manifest.json"
const DATA_SHA="ba078361858ba4a3f1afb6cd105a974dbd63f04fb8ab5c6661cae21a485d879f"
var travelled_m:float=0.0
var walked_frames:int=0
var completed:Array=[]
var arrivals:int=0
func _initialize()->void:
 test_name="night_table_ordinary_input"
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
 if f!=null:f.store_string(JSON.stringify({"status":status,"detail":detail,"completed_branches":completed,"initial_deck_arrivals":arrivals,"walked_frames":walked_frames,"walked_m":travelled_m,"support_samples":support_samples,"data_sha256":FileAccess.get_sha256(DATA),"scope":"One connected ordinary W-input Night Table circuit from existing public route. Two dining aisles and two service door approaches; not every seat, loaded cart, visual or hardware acceptance."},"  ")+"\n")
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
 return require(false,"Blocked at %s toward %s"%[actor.position,point])
func run()->void:
 started=Time.get_ticks_msec()
 receipt_path="/workspace/scratch/375c2e438292/night_table_receiving_20261008/ordinary_input_result001.json"
 if not require(FileAccess.get_sha256(DATA)==DATA_SHA,"Frozen runtime contract"):return
 main=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
 for i in range(150):await physics_frame
 ship=main.get_node("World360/Astraea");actor=ship.get_node("ShipSpace/PersistentActors/Player")
 cart=ship.find_child("CustodialCart",true,false);floors=ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false)
 space=ship.get_world_3d().direct_space_state
 if not require(actor.get_script().resource_path=="res://scripts/player.gd" and actor.gameplay_input_enabled and actor.is_physics_processing(),"Unchanged active production player"):return
 if not require(ship.arrive_at(Vector3(-3,61.1,216),0),"Supported existing public approach"):return
 arrivals=1
 if not await advance(45):return
 var circuits:Array=[
  {"id":"quiet dining aisle","points":[[-8,216],[-19,216],[-19,210],[-30.5,210],[-30.5,185],[-30.5,210],[-19,210],[-19,216]]},
  {"id":"supper dining aisle","points":[[-19,222],[-30.5,222],[-30.5,247],[-30.5,222],[-19,222],[-19,216]]},
  {"id":"clean finishing approach","points":[[-19,210],[-33.5,210],[-33.5,214],[-33.5,210],[-19,210],[-19,216]]},
  {"id":"used return approach","points":[[-19,222],[-33.5,222],[-33.5,218],[-33.5,222],[-19,222],[-19,216],[-8,216],[-3,216]]}
 ]
 for circuit in circuits:
  for p in circuit.points:
   if not await walk(Vector2(p[0],p[1]),61.0):return
  completed.append(circuit.id);print("NIGHT TABLE CIRCUIT ",circuit.id)
 release_inputs();write_receipt("PASS")
 print("NIGHT TABLE ORDINARY INPUT PASS: ",travelled_m," m; ",walked_frames," input frames")
 main.queue_free();await process_frame;quit(0)
