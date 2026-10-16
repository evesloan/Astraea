extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/Astraea/BlenderCatalogue/assets/moonfruit_service_20261016/"
const E="/workspace/moonfruit-evidence/"
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func query_box(space:PhysicsDirectSpaceState3D,lo:Vector3,hi:Vector3,exclude:Array[RID])->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var b:=BoxShape3D.new();b.size=(hi-lo-Vector3.ONE*.0004).max(Vector3.ONE*.00001);b.margin=0;q.shape=b;q.margin=0;q.transform.origin=(lo+hi)/2;q.exclude=exclude;var result:Array=[]
 for h in space.intersect_shape(q,128):result.append(str(h.collider.get_path()))
 return result
func run()->void:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_PLAN_r002.json"));var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_VERIFICATION_r002.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(-3,61.03,392);actor.velocity=Vector3.ZERO
 ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(Vector3(-50,61.03,407));ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(Vector3(-50,61.03,407));await frames(8)
 var cafe:Node3D=ship.get_node("ShipSpace/Districts/D10_directory_09Receiving_WIP");var original:Node3D=cafe.get_node("SOL_D10_directory_09_remaining_batch");var baseline:Node3D=load("res://assets/models/SOL_D10_directory_09_remaining_batch.glb").instantiate();var preserved:=true;var count:=0
 for m:MeshInstance3D in original.find_children("*","MeshInstance3D",true,false):
  var before:MeshInstance3D=baseline.get_node(original.get_path_to(m));count+=1
  if not m.transform.is_equal_approx(before.transform)or(m.name!="WP05_west_enclosure"and m.mesh!=before.mesh):preserved=false
 record("source_meshes_and_poses_preserved_except_exact_wall",preserved and count==4208);baseline.free()
 var model:Node3D=cafe.get_node("MoonfruitServiceReceiving20261016");record("only_one_receiving_root",cafe.find_children("MoonfruitServiceReceiving20261016","",true,false).size()==1);record("twelve_source_lamps",model.find_children("*","Light3D",true,false).size()==12)
 var space:=ship.get_world_3d().direct_space_state;var floor_points:Array[Vector3]=[]
 for rect in plan.floor_rectangles:
  var x:float=rect[0]+.4
  while x<float(rect[1])-.2:
   var z:float=rect[2]+.4
   while z<float(rect[3])-.2:
    floor_points.append(Vector3(x,61,z));z+=2.
   x+=2.
 for at in floor_points:
  var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record("new_floor_"+str(at),not h.is_empty()and str(h.collider.get_path()).contains("MoonfruitServiceReceiving20261016")and absf(h.position.y-61)<.0002)
 for z in [407.,448.]:
  for x in [-54.3,-54.,-53.7]:
   var h:=ray(space,Vector3(x,61.1,z),Vector3(x,60.99,z));record("positive_threshold_"+str(x)+str(z),not h.is_empty() and h.position.y>61.005 and h.position.y<61.04)
 var mounts:Array=[]
 for row in p.bounds:
  if not str(row.name).contains("CanopyTie"):continue
  var at:Vector3=(vec(row.min)+vec(row.max))/2;at.y=64.79;var h:=ray(space,at,at+Vector3.UP*.03);var good:bool=not h.is_empty()and str(h.collider.get_path()).contains("MoonfruitServiceReceiving20261016")and absf(h.position.y-64.8)<.0002;record("fixture_roof_"+str(row.name),good);mounts.append({"name":row.name,"at":str(at),"passed":good})
 for row in p.lights:
  var at:=vec(row.at);var h:=ray(space,at,at-Vector3.UP*4);record("emitter_to_new_floor_"+str(row.name),not h.is_empty()and str(h.collider.get_path()).contains("MoonfruitServiceReceiving20261016")and absf(h.position.y-61)<.0002)
 var legs:Array=[];var route:Array[Vector3]=[Vector3(-6,61,392),Vector3(-30,61,392),Vector3(-58,61,392),Vector3(-62,61,392),Vector3(-62,61,407),Vector3(-56,61,407),Vector3(-50,61,407),Vector3(-49,61,407),Vector3(-49,61,424),Vector3(-46,61,424),Vector3(-49,61,424),Vector3(-49,61,407),Vector3(-56,61,407),Vector3(-62,61,407),Vector3(-62,61,448),Vector3(-56,61,448),Vector3(-50,61,448),Vector3(-49,61,448),Vector3(-49,61,442),Vector3(-49,61,448),Vector3(-56,61,448),Vector3(-62,61,448),Vector3(-62,61,392),Vector3(-30,61,392),Vector3(-6,61,392),Vector3(-3,61,392)]
 var proceed:bool=errors.is_empty();actor.set_controls_enabled(true);actor.set_physics_process(true);await frames(20)
 for goal in route:
  if not proceed:break
  var leg:Dictionary=await walk_to(actor,goal);legs.append(leg);record("walk_out_"+str(legs.size()),leg.reached and leg.floor_contact);proceed=leg.reached and leg.floor_contact
 record("continuous_route_complete",proceed and legs.size()==26)
 actor.set_physics_process(false);var saved_position:=actor.global_position;var streamer:Node=ship.get_node("ShipSystems/RemainingBatchStreaming");var old_light_ids:Array=[]
 for light:Light3D in model.find_children("*","Light3D",true,false):old_light_ids.append(light.get_instance_id())
 actor.global_position=Vector3(5000,61,0);streamer.refresh();record("normal_stream_unload",not cafe.get_meta("stream_loaded",false))
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var no_dead:=true
 for light in budget.sources:
  if is_instance_valid(light) and light.get_instance_id() in old_light_ids:no_dead=false
 record("old_sources_removed",no_dead);actor.global_position=saved_position;streamer.prepare_position(saved_position);await frames(8);record("normal_stream_restore",cafe.get_meta("stream_loaded",false) and cafe.has_node("MoonfruitServiceReceiving20261016"));record("one_restored_source_set",cafe.get_node("MoonfruitServiceReceiving20261016").find_children("*","Light3D",true,false).size()==12)
 var portal_clear:=true
 for z in [407.,448.]:
  if not capsule_clear(space,Vector3(-53.7,61.03,z)):portal_clear=false
 record("restored_exact_wall_openings",portal_clear)
 var report:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","scope":"Candidate receiving only; unchanged original controller and sources; no operational/cart/species/primary/final-art acceptance","checks":checks,"errors":errors,"original_cafe_meshes":count,"missing_only_floor_samples":floor_points.size(),"fixture_roof_mounts":mounts,"original_controller_legs":legs,"route_teleports":0,"default_installed":true,"separate_stream_lifecycle_test_after_route":true}
 FileAccess.open(E+"MOONFRUIT_INSTALLED_MAIN_r002_corrected.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("MOONFRUIT_CANDIDATE ",report.status," ",checks.size()," checks ",legs.size()," legs errors=",errors);quit(0 if errors.is_empty()else 1)
