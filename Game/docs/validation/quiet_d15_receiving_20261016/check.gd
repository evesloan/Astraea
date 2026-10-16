extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/Astraea/BlenderCatalogue/assets/quiet_d15_staff_receiving_20261016/r003/"
const E="/workspace/quiet-d15-integration/"
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func query_box(space:PhysicsDirectSpaceState3D,lo:Vector3,hi:Vector3,exclude:Array[RID])->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var b:=BoxShape3D.new();b.size=(hi-lo-Vector3.ONE*.0004).max(Vector3.ONE*.00001);b.margin=0;q.shape=b;q.margin=0;q.transform.origin=(lo+hi)/2;q.exclude=exclude;var result:Array=[]
 for h in space.intersect_shape(q,128):result.append(str(h.collider.get_path()))
 return result
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"RECEIPT.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(21,93.03,-488);actor.velocity=Vector3.ZERO
 var qlift:Node=ship.find_child("QuietGrovePassengerLift",true,false)
 for i in range(300):
  if qlift.phase=="idle":break
  await frames(1)
 record("baseline_lift_settled",qlift.phase=="idle")
 var original:Dictionary={};var selected:Array=[]
 for row in p.walls:selected.append(str(row.name))
 for owner in [ship.get_node("ShipSpace/Districts/QuietGroveReceivingCandidate"),ship.get_node("ShipSpace/Group3ForeStarboardClinical")]:
  for m:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):original[m]={"mesh":m.mesh,"pose":m.global_transform}
 var space:=ship.get_world_3d().direct_space_state;var excludes:Array[RID]=[actor.get_rid()];var preflight:Array=[];var points:Array[Vector3]=[]
 for x in [24.,27.,30.,33.,36.,39.,42.,44.]:
  for z in [-485.1,-484.0,-482.7]:
   var at:=Vector3(x,93,z);points.append(at);record("missing_before_"+str(at),ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02).is_empty())
 for row in p.parts:
  var hits:Array=query_box(space,vec(row.min),vec(row.max),excludes)
  var allowed:Array=[]
  if str(row.name)=="Q15_Canopy":allowed=["lobby_wall_staff_white_paint_y11"]
  if str(row.name).begins_with("Q15_Edge1_"):allowed=["QG_Batch_57","QG_Batch_85"]
  if str(row.name)=="Q15_Post_-482.33_5":allowed=["QG_Batch_57"]
  if str(row.name).begins_with("Q15_LobbySlabTie"):allowed=["floor_staff_floor_D15"]
  if str(row.name).begins_with("Q15_HouseSlabTie"):allowed=["QG_Batch_52"]
  var good:bool=true
  for h in hits:
   var matched:bool=false
   for token in allowed:
    if str(h).contains("/"+str(token)+"/"):matched=true
   if not matched:good=false
  if str(row.name)=="Q15_MissingFloor":good=true # Concave polygon AABB includes the deliberately subtracted lobby corner; exact two-rectangle checks follow.
  if str(row.name).contains("SlabTie"):good=good and hits.size()==1
  record("classified_contacts_"+str(row.name),good)
  if not hits.is_empty():preflight.append({"part":row.name,"contacts":hits,"classified":good})
 for rect in [[23.1801,45.7,-485.6,-482.2001],[19.3,23.1801,-483.9999,-482.2001]]:
  record("exact_floor_volume_"+str(rect),query_box(space,Vector3(rect[0],92.76,rect[2]),Vector3(rect[1],93,rect[3]),excludes).is_empty())
 var group:Node3D=load("res://scripts/quiet_d15_receiving_20261016/package.gd").build(ship,D+str(p.file));await frames(6)
 for at in points:
  var h:=ray(space,at+Vector3.UP*.04,at-Vector3.UP*.04);record("new_floor_"+str(at),not h.is_empty()and absf(h.position.y-93)<.0002 and str(h.collider.get_path()).contains("QuietD15StaffReceiving"))
 for row in p.lights:
  var at:=vec(row.at);var h:=ray(space,at,at-Vector3.UP*4);record("light_floor_"+str(row.name),not h.is_empty()and absf(h.position.y-93)<.0002)
 for i in range(4):
  var x:float=[26.22,31.78,34.22,39.78][i];var at:=Vector3(x+.07,95.78,-483.9);var h:=ray(space,at,at+Vector3.UP*.08);record("fixture_socket_"+str(i),not h.is_empty()and str(h.collider.get_path()).contains("QuietD15StaffReceiving")and absf(h.position.y-95.795)<.0002)
  at=Vector3(x+.15,95.78,-483.9);h=ray(space,at,at+Vector3.UP*.08);record("fixture_canopy_"+str(i),not h.is_empty()and str(h.collider.get_path()).contains("QuietD15StaffReceiving")and absf(h.position.y-95.82)<.0002)
  var socket:MeshInstance3D=group.find_child("Q15_FixtureRoofSocket"+str(i),true,false);var roof:MeshInstance3D=group.find_child("Q15_Canopy",true,false);var sb:AABB=socket.global_transform*socket.get_aabb();var rb:AABB=roof.global_transform*roof.get_aabb();record("positive_fixture_canopy_join_"+str(i),sb.intersection(rb).get_volume()>.0001)
 var route:Array[Vector3]=[Vector3(21,93,-485),Vector3(21,93,-483.8),Vector3(24,93,-483.8),Vector3(29,93,-483.8),Vector3(34,93,-483.8),Vector3(39,93,-483.8),Vector3(44,93,-483.8),Vector3(44,93,-481),Vector3(44,93,-477),Vector3(44,93,-481),Vector3(44,93,-483.8),Vector3(39,93,-483.8),Vector3(34,93,-483.8),Vector3(29,93,-483.8),Vector3(24,93,-483.8),Vector3(21,93,-483.8),Vector3(21,93,-485),Vector3(21,93,-488)]
 var legs:Array=[];var proceed:=errors.is_empty();actor.set_controls_enabled(true);actor.set_physics_process(true);await frames(20)
 for goal in route:
  if not proceed:break
  var leg:Dictionary=await walk_to(actor,goal);legs.append(leg);record("walk_"+str(legs.size()),leg.reached and leg.floor_contact);proceed=leg.reached and leg.floor_contact
 var kept:=true;var preservation_failures:Array=[]
 for m in original:
  if not m.global_transform.is_equal_approx(original[m].pose)or(str(m.name)not in selected and m.mesh!=original[m].mesh):kept=false;preservation_failures.append({"path":str(m.get_path()),"pose":str(m.global_transform),"before":str(original[m].pose),"same_mesh":m.mesh==original[m].mesh})
 record("retained_poses_resources",kept);record("continuous_walk",legs.size()==18 and proceed)
 var report:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks,"errors":errors,"classified_old_contacts":preflight,"preservation_failures":preservation_failures,"original_meshes":original.size(),"legs":legs,"no_intra_route_teleports":true,"scope":"Candidate geometry and unladen walking; preflight contacts require explicit classification before adoption"};FileAccess.open(E+"CANDIDATE.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("QUIET_D15_CANDIDATE ",report.status," ",errors);quit(0 if errors.is_empty()else 1)
