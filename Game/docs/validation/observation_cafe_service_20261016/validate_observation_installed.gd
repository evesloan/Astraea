extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/Astraea/BlenderCatalogue/assets/observation_cafe_service_20261016/"
const E="/workspace/recovery-evidence/"
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func query_box(space:PhysicsDirectSpaceState3D,lo:Vector3,hi:Vector3,exclude:Array[RID])->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var b:=BoxShape3D.new();b.size=(hi-lo-Vector3.ONE*.0004).max(Vector3.ONE*.00001);b.margin=0;q.shape=b;q.margin=0;q.transform.origin=(lo+hi)/2;q.exclude=exclude;var result:Array=[]
 for h in space.intersect_shape(q,128):result.append(str(h.collider.get_path()))
 return result
func run()->void:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_PLAN.json"));var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_VERIFICATION.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(3,61.03,392);actor.velocity=Vector3.ZERO
 ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(Vector3(51.5,61.03,432));ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(Vector3(51.5,61.03,432));await frames(8)
 var cafe:Node3D=ship.get_node("ShipSpace/Districts/ReceivedSections/D10_directory_10");var original:Dictionary={}
 for m:MeshInstance3D in cafe.find_children("*","MeshInstance3D",true,false):original[m]={"mesh":m.mesh,"pose":m.global_transform}
 record("original_cafe_mesh_count",original.size()==1452)
 for file in plan.source_pins:record("pin_"+str(file),FileAccess.get_sha256("res://"+str(file))==str(plan.source_pins[file]))
 var space:=ship.get_world_3d().direct_space_state;var preflight:Array=[]
 var prior:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(E+"OBSERVATION_CANDIDATE_MAIN_r001_adjudicated.json"));record("candidate_receiving_preflight_passed",prior.status=="PASS")
 record("unchanged_candidate_glb",FileAccess.get_sha256("res://assets/observation_cafe_service_20261016/"+str(p.file))==str(p.model_sha256))
 var floor_points:Array[Vector3]=[]
 for rect in plan.floor_rectangles:
  var x:float=rect[0]+.4
  while x<float(rect[1])-.2:
   var z:float=rect[2]+.4
   while z<float(rect[3])-.2:
    var at:=Vector3(x,61,z);floor_points.append(at);z+=2.
   x+=2.
 var group:Node3D=ship.get_node("ShipSpace/ObservationCafeServiceReceiving20261016");var model:Node3D=group.get_child(0);record("ten_new_source_lights",group.find_children("*","SpotLight3D",true,false).size()==10)
 record("no_new_identity_or_capacity",int(group.get_meta("new_room_ids_capacity_or_lift_stops"))==0)
 for at in floor_points:
  var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record("floor_after_"+str(at),not h.is_empty()and str(h.collider.get_path()).contains("ObservationCafeServiceReceiving20261016")and absf(h.position.y-61)<.0002)
 var mounts:Array=[]
 for row in p.bounds:
  if not str(row.name).contains("CanopyTie"):continue
  var at:Vector3=(vec(row.min)+vec(row.max))/2;at.y=64.79;var h:=ray(space,at,at+Vector3.UP*.03);var good:bool=not h.is_empty()and str(h.collider.get_path()).contains("ObservationCafeServiceReceiving20261016")and absf(h.position.y-64.8)<.0002;record("fixture_roof_"+str(row.name),good);mounts.append({"name":row.name,"at":str(at),"passed":good})
 for row in p.lights:
  var at:=vec(row.at);var h:=ray(space,at,at-Vector3.UP*4);record("emitter_to_new_floor_"+str(row.name),not h.is_empty()and str(h.collider.get_path()).contains("ObservationCafeServiceReceiving20261016")and absf(h.position.y-61)<.0002)
 var legs:Array=[];var route:Array[Vector3]=[Vector3(6,61,392),Vector3(30,61,392),Vector3(58,61,392),Vector3(62,61,392),Vector3(62,61,416),Vector3(62,61,432),Vector3(56,61,432),Vector3(51.5,61,432),Vector3(51.5,61,460.6),Vector3(48,61,460.6),Vector3(48,61,461.2),Vector3(48,61,460.6),Vector3(45,61,460.6),Vector3(45,61,462),Vector3(42,61,462)]
 var proceed:bool=errors.is_empty();actor.set_controls_enabled(true);actor.set_physics_process(true);await frames(20)
 for goal in route:
  if not proceed:break
  var leg:Dictionary=await walk_to(actor,goal);legs.append(leg);record("walk_out_"+str(legs.size()),leg.reached and leg.floor_contact);proceed=leg.reached and leg.floor_contact
 route.reverse();route.remove_at(0);route.append(Vector3(3,61,392))
 for goal in route:
  if not proceed:break
  var leg:Dictionary=await walk_to(actor,goal);legs.append(leg);record("walk_back_"+str(legs.size()),leg.reached and leg.floor_contact);proceed=leg.reached and leg.floor_contact
 var preserved:=true
 for m in original:
  if not is_instance_valid(m)or m.mesh!=original[m].mesh or not m.global_transform.is_equal_approx(original[m].pose):preserved=false
 record("all_original_cafe_meshes_unchanged",preserved);record("continuous_route_complete",proceed and legs.size()==30)
 var report:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","scope":"Installed physical receiving only; unchanged original controller and sources; no operational/cart/species/primary/final-art acceptance","checks":checks,"errors":errors,"original_cafe_meshes":original.size(),"old_geometry_contacts":preflight,"missing_only_floor_samples":floor_points.size(),"fixture_roof_mounts":mounts,"original_controller_legs":legs,"route_teleports":0,"candidate_only":false}
 FileAccess.open(E+"OBSERVATION_INSTALLED_MAIN_r001.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("OBSERVATION_INSTALLED ",report.status," ",checks.size()," checks ",legs.size()," legs errors=",errors);quit(0 if errors.is_empty()else 1)
