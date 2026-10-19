extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/Astraea/BlenderCatalogue/assets/d17_starboard_standard_20261019/"
const E="/workspace/d17-starboard-integration/"
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func box_hits(space:PhysicsDirectSpaceState3D,lo:Vector3,hi:Vector3,exclude:Array[RID])->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=(hi-lo-Vector3.ONE*.0004).max(Vector3.ONE*.00001);shape.margin=0;q.shape=shape;q.margin=0;q.transform.origin=(lo+hi)/2;q.exclude=exclude;var result:Array=[]
 for h in space.intersect_shape(q,128):result.append(str(h.collider.get_path()))
 return result
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"PLAN.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(80,102.03,12);actor.velocity=Vector3.ZERO
 var space:=ship.get_world_3d().direct_space_state;var excludes:Array[RID]=[actor.get_rid()];var preflight:Array=[];var old:Dictionary={};var selected:Array=[]
 for r in p.walls:selected.append(str(r.name))
 for owner in [ship.find_child("Group2CentralSupportedAdjunct",true,false),ship.find_child("D17ConnectedHouse_WIP",true,false),ship.find_child("StarboardHouseUpperArchitecture",true,false),ship.find_child("ApprovedGroup2Homes",true,false)]:
  if owner==null:continue
  for m:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):old[m]={"mesh":m.mesh,"pose":m.global_transform,"local_pose":m.transform}
 var registered_homes:Dictionary={}
 for entry in ship.get_node("ShipSystems/ReceivedRoomResidency").entries:
  if str(entry.parent.name)=="ApprovedGroup2Homes":registered_homes[entry.room]={"parent":entry.parent,"pose":entry.parent.global_transform*entry.room.transform,"bounds":entry.bounds}
 record("all80_home_roots_in_registry",registered_homes.size()==80)
 var group:Node3D=ship.get_node("ShipSpace/D17StarboardStandardReceiving")
 record("installed_root",group!=null)
 for r in p.rooms:
  var home:Node3D=group.get_node(r.allocation.proposed_runtime_id)
  record("reservation_"+str(r.allocation.source_envelope_index),home.get_meta("rest_slot_ids")==r.allocation.proposed_rest_slot_ids)
 var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file("res://assets/models/"+str(p.structure_file),state,64)==OK);var raw:Node=doc.generate_scene(state);var imported:Node=load("res://assets/models/"+str(p.structure_file)).instantiate()
 for a:MeshInstance3D in raw.find_children("*","MeshInstance3D",true,false):
  var b:MeshInstance3D=imported.find_child(a.name,true,false);var am:Dictionary={};var bm:Dictionary={}
  for vertex in a.mesh.get_faces():am[vertex]=am.get(vertex,0)+1
  for vertex in b.mesh.get_faces():bm[vertex]=bm.get(vertex,0)+1
  record("exact_import_"+str(a.name),am==bm and a.transform.is_equal_approx(b.transform))
 raw.free();imported.free()
 var legs:Array=[]
 for bank in ["Fore","Aft"]:
  actor.set_physics_process(false);actor.global_position=Vector3(60,102.03,-13)if bank=="Fore"else Vector3(80,102.03,12);actor.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position);actor.set_controls_enabled(true);actor.set_physics_process(true);await frames(20)
  var entry_route:Array=[Vector3(60,102,-15),Vector3(61.5,102,-15),Vector3(61.5,102,-18)]if bank=="Fore"else[Vector3(80,102,16),Vector3(76,102,16),Vector3(70,102,16),Vector3(61.5,102,16),Vector3(61.5,102,30)]
  var proceed:=true
  for goal in entry_route:
   var leg:Dictionary=await walk_to(actor,goal);legs.append(leg);record(bank+"_entry_"+str(legs.size()),leg.reached and leg.floor_contact);proceed=proceed and leg.reached and leg.floor_contact
   if not proceed:break
  var rooms:Array=[]
  for r in p.rooms:
   if (r.entry_origin[2]<0)==(bank=="Fore"):rooms.append(r)
  rooms.sort_custom(func(a,b):return a.entry_origin[2]>b.entry_origin[2]if bank=="Fore"else a.entry_origin[2]<b.entry_origin[2])
  for r in rooms:
   if not proceed:break
   var z:float=r.entry_origin[2];var home:Node3D=group.get_node(r.allocation.proposed_runtime_id)
   var leg:Dictionary=await walk_to(actor,Vector3(61.5,102,z));legs.append(leg);record("street_"+str(r.allocation.source_envelope_index),leg.reached and leg.floor_contact)
   home.get_node("HomeEntry").interact(null);home.get_node("BathroomDoor").interact(null);await frames(100)
   for goal in [Vector3(64,102,z),Vector3(68.3,102,z),Vector3(70.8,102,z),Vector3(68.3,102,z),Vector3(64,102,z),Vector3(61.5,102,z)]:
    leg=await walk_to(actor,goal);legs.append(leg);record("room_"+str(r.allocation.source_envelope_index)+"_"+str(legs.size()),leg.reached and leg.floor_contact);proceed=proceed and leg.reached and leg.floor_contact
    if not proceed:break
 var kept:=true;var streamed_detached:=0
 for m in old:
  var pose_ok:bool=m.global_transform.is_equal_approx(old[m].pose)if m.is_inside_tree()else m.transform.is_equal_approx(old[m].local_pose)
  if not m.is_inside_tree():streamed_detached+=1
  if not pose_ok or(str(m.name)not in selected and m.mesh!=old[m].mesh):kept=false
 for home in registered_homes:record("registered_world_pose_"+str(home.name),(registered_homes[home].parent.global_transform*home.transform).is_equal_approx(registered_homes[home].pose))
 record("original_poses_unrelated_meshes_preserved",kept)
 var report:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks,"errors":errors,"legs":legs,"original_meshes":old.size(),"streamed_detached_meshes_checked_in_retained_local_space":streamed_detached,"registered_home_world_roots_checked":registered_homes.size(),"preflight_contacts_unclassified":preflight,"scope":"Installed physical guest approach and room routes; engineering, service operations and final art remain open"};FileAccess.open(E+"INSTALLED.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("D17_STARBOARD_INSTALLED ",report.status," ",errors);quit(0 if errors.is_empty()else 1)
