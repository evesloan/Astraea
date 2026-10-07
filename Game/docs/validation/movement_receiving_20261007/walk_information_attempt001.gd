extends "res://tests/validate_team_lounge_access.gd"
var pin_before: Dictionary={}
var info_checks:=0
const PINS := ["scripts/ship.gd","scripts/player.gd","scripts/movement_studio_receiving.gd","data/generated/structural_meshes.json","data/architecture/D07_MOVEMENT_STUDIO_RECEIVING.json","data/architecture/packages/movement_studio/INFORMATION_TARGETS.json","tests/medical_triage_successor_guard.gd"]
func _initialize() -> void:
 test_name="movement_studio_ordinary_input001"
 call_deferred("run")
func snapshot() -> Dictionary:
 var result: Dictionary={}
 for p in PINS: result[p]=FileAccess.get_sha256("res://"+p)
 return result
func write_receipt(status: String, detail: String="") -> void:
 if receipt_path.is_empty(): return
 var f:=FileAccess.open(receipt_path,FileAccess.WRITE)
 f.store_string(JSON.stringify({"status":status,"detail":detail,"walked_m":travelled_m,"walked_frames":walked_frames,"support_samples":support_samples,"information_cycles":info_checks,"input_hashes":pin_before,"end_hashes":snapshot(),"initial_supported_arrivals":1,"later_teleports":0,"scope":"Actual unchanged-player entrance, nine rest approaches, three niches, practice/care routes, two RMB/E information open/close and unfocused rejection, return. No cart/species/art acceptance."},"  ")+"\n");f.close()
func route(points: Array) -> bool:
 for p in points:
  if not await walk(Vector2(p[0],p[1])): return false
 return true
func info_cycle(id: String,target: Vector3) -> bool:
 release_inputs()
 var node: Node=built.find_child(id,true,false)
 if not require(node!=null,"Authored information target missing"): return false
 var delta: Vector3=target-actor.camera.global_position
 actor.rotation.y=atan2(-delta.x,-delta.z);actor.pitch=atan2(delta.y,Vector2(delta.x,delta.z).length());actor.camera.rotation.x=actor.pitch
 if not await advance(5,false):return false
 if not require(actor.target_from_view()==node,"Actual plaque not selectable from authored stance"):return false
 key(KEY_E,true)
 if not await advance(2,false):return false
 key(KEY_E,false)
 if not await advance(2,false):return false
 if not require(not node.expanded,"Unfocused input opened information"):return false
 focus(true)
 if not await advance(3,false):return false
 for expected in [true,false]:
  key(KEY_E,true)
  if not await advance(2,false):return false
  key(KEY_E,false)
  if not await advance(2,false):return false
  if not require(node.expanded==expected,"RMB/E information toggle failed"):return false
 focus(false);info_checks+=1
 return true
func run() -> void:
 started=Time.get_ticks_msec();receipt_path="/workspace/scratch/375c2e438292/movement_receiving_20261007/root_apply001/walk_information001.json"
 if FileAccess.file_exists(receipt_path):quit(1);return
 pin_before=snapshot()
 main=(load("res://scenes/main.tscn") as PackedScene).instantiate();root.add_child(main)
 for i in range(150):await physics_frame
 ship=main.get_node("World360/Astraea");actor=ship.get_node("ShipSpace/PersistentActors/Player");cart=ship.find_child("CustodialCart",true,false);floors=ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false);built=ship.find_child("D07_MovementStudio_Receiving_WIP",true,false);space=ship.get_world_3d().direct_space_state
 if not require(built!=null and actor.get_script().resource_path=="res://scripts/player.gd","Actual installed room/player required"):return
 if not require(ship.arrive_at(Vector3(0,35.6,-458),-PI/2),"Initial supported arrival refused"):return
 if not await advance(45,false):return
 if not await route([[0,-458],[6,-458],[13,-458],[13,-456],[13,-461],[18,-461],[28,-461],[35,-461],[42,-461],[47.8,-461.5]]):return
 if not await info_cycle("WP11_info_studio_01",Vector3(49.63,37.08,-461.5)):return
 if not await route([[47.8,-456],[38,-456],[38,-454],[45.3,-454],[45.3,-423],[50.1,-423],[50.05,-426]]):return
 if not await info_cycle("WP11_info_care_01",Vector3(51.97,36.93,-426)):return
 if not await route([[50.1,-429],[50.1,-423],[45.3,-423],[45.3,-454],[38,-454],[22,-456],[22,-449],[21,-448]]):return
 for z in [-442.5,-427.5,-412.5]:
  if not await route([[21,z],[14.2,z],[21,z]]):return
 if not await route([[21,-405],[13,-405],[13,-402],[13,-405],[18,-405],[18,-402],[18,-405],[29,-405],[29,-402],[29,-405],[35,-405],[35,-402],[35,-405],[21,-405],[21,-448],[22,-449],[22,-456],[13,-456],[13,-458],[6,-458],[0,-458]]):return
 release_inputs()
 if not require(snapshot()==pin_before,"Input bytes changed during run"):return
 write_receipt("PASS");print("MOVEMENT ORDINARY INPUT PASS: ",travelled_m," metres, ",walked_frames," frames, two information cycles")
 main.queue_free();await process_frame;quit(0)
