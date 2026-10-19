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
 for owner in [ship.find_child("Group2CentralSupportedAdjunct",true,false),ship.find_child("D17ConnectedHouse_WIP",true,false),ship.find_child("StarboardHouseUpperArchitecture",true,false),ship.find_child("ReceivedHomes20261015",true,false)]:
  if owner==null:continue
  for m:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):old[m]={"mesh":m.mesh,"pose":m.global_transform}
 for r in p.rooms:
  actor.global_position=Vector3(69.5,102.03,r.entry_origin[2]);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position);ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(actor.global_position);await frames(3)
  var hits:Array=box_hits(space,Vector3(63.06,101.78,r.adopted_z[0]+.06),Vector3(75.94,106.45,r.adopted_z[1]-.06),excludes);record("room_volume_clear_"+str(r.allocation.source_envelope_index),hits.is_empty())
  if not hits.is_empty():preflight.append({"room":r.allocation.source_envelope_index,"hits":hits})
 for r in p.bearings:
  var at:=vec(r.at);var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);record("permanent_bearing_"+r.name,not h.is_empty()and str(h.collider.get_path()).contains(r.owner))
 for r in p.parts:
  var hits:Array=box_hits(space,vec(r.expected_bounds[0]),vec(r.expected_bounds[1]),excludes)
  if not hits.is_empty():preflight.append({"part":r.name,"category":r.category,"hits":hits})
 FileAccess.open(E+"PREFLIGHT.json",FileAccess.WRITE).store_string(JSON.stringify(preflight,"  "))
 var group:Node3D=load("res://scripts/d17_starboard_standard_20261019/package.gd").build(ship,D+str(p.structure_file));await frames(8)
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
 var kept:=true
 for m in old:
  if not m.global_transform.is_equal_approx(old[m].pose)or(str(m.name)not in selected and m.mesh!=old[m].mesh):kept=false
 record("original_poses_unrelated_meshes_preserved",kept)
 var report:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks,"errors":errors,"legs":legs,"original_meshes":old.size(),"preflight_contacts_unclassified":preflight,"scope":"Candidate only; contact classification, full native/patch checks and installation remain separate"};FileAccess.open(E+"CANDIDATE.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("D17_STARBOARD_CANDIDATE ",report.status," ",errors);quit(0 if errors.is_empty()else 1)
