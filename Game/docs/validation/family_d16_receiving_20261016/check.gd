extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/Astraea/BlenderCatalogue/assets/family_d16_staff_receiving_20261016/"
const E="/workspace/family-d16-integration/"
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func query_box(space:PhysicsDirectSpaceState3D,lo:Vector3,hi:Vector3,exclude:Array[RID])->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var b:=BoxShape3D.new();b.size=(hi-lo-Vector3.ONE*.0004).max(Vector3.ONE*.00001);b.margin=0;q.shape=b;q.margin=0;q.transform.origin=(lo+hi)/2;q.exclude=exclude;var result:Array=[]
 for h in space.intersect_shape(q,128):result.append(str(h.collider.get_path()))
 return result
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"RECEIPT.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(21,97.53,488);actor.velocity=Vector3.ZERO
 var qlift:Node=ship.find_child("FamilyPassengerLift",true,false)
 for i in range(300):
  if qlift.phase=="idle":break
  await frames(1)
 record("baseline_lift_settled",qlift.phase=="idle")
 var original:Dictionary={};var selected:Array=[]
 for row in p.walls:selected.append(str(row.name))
 for owner in [ship.get_node("ShipSpace/Districts/FamilyTerraceReceivingCandidate"),ship.get_node("ShipSpace/Group3AftRiserPair"),ship.get_node("ShipSpace/QuietD15StaffReceiving"),ship.get_node("ShipSpace/QuietD14StaffReceiving"),ship.get_node("ShipSpace/QuietD13StaffReceiving"),ship.get_node("ShipSpace/QuietD16StaffReceiving"),ship.get_node("ShipSpace/FamilyD13StaffReceiving"),ship.get_node("ShipSpace/FamilyD14StaffReceiving"),ship.get_node("ShipSpace/FamilyD15StaffReceiving"),ship.get_node("ShipSpace/D17StarboardStandardReceiving")]:
  for m:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):original[m]={"mesh":m.mesh,"pose":m.global_transform}
 var space:=ship.get_world_3d().direct_space_state;var excludes:Array[RID]=[actor.get_rid()];var preflight:Array=[];var points:Array[Vector3]=[]
 for x in [24.,27.,30.,33.,36.,39.,42.,44.]:
  for z in [485.1,484.0,482.7]:
   var at:=Vector3(x,97.5,z);points.append(at);record("missing_before_"+str(at),ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02).is_empty())
 for row in p.parts:
  var hits:Array=query_box(space,vec(row.min),vec(row.max),excludes)
  var allowed:Array=[]
  if str(row.name)=="F16_Canopy"or str(row.name).begins_with("F16_LobbyReveal"):allowed=["lobby_wall_staff_white_paint_y12"]
  if str(row.name).begins_with("F16_GuardCutCap"):allowed=["FT_Batch_345"]
  if str(row.name).begins_with("F16_Edge1_"):allowed=["FT_Batch_345","FT_Batch_347"]
  if str(row.name)=="F16_Post_-482.33_5":allowed=["FT_Batch_345"]
  if str(row.name).begins_with("F16_LobbySlabTie"):allowed=["floor_staff_floor_starboard_service_riser_5_D16"]
  if str(row.name).begins_with("F16_HouseSlabTie"):allowed=["FT_Batch_101"]
  var good:bool=true
  for h in hits:
   var matched:bool=false
   for token in allowed:
    if str(h).contains("/"+str(token)+"/"):matched=true
   if not matched:good=false
  if str(row.name)=="F16_MissingFloor":good=true # Concave polygon AABB includes the deliberately subtracted lobby corner; exact two-rectangle checks follow.
  if str(row.name).contains("SlabTie"):good=good and hits.size()==1
  record("classified_contacts_"+str(row.name),good)
  if not hits.is_empty():preflight.append({"part":row.name,"contacts":hits,"classified":good})
 for rect in [[23.1801,45.7,485.6,482.2001],[19.3,23.1801,483.9999,482.2001]]:
  record("exact_floor_volume_"+str(rect),query_box(space,Vector3(rect[0],97.26,minf(rect[2],rect[3])),Vector3(rect[1],97.5,maxf(rect[2],rect[3])),excludes).is_empty())
 var group:Node3D=load("res://scripts/family_d16_receiving_20261016/package.gd").build(ship,D+str(p.file));await frames(6)
 for at in points:
  var h:=ray(space,at+Vector3.UP*.04,at-Vector3.UP*.04);record("new_floor_"+str(at),not h.is_empty()and absf(h.position.y-97.5)<.0002 and str(h.collider.get_path()).contains("FamilyD16StaffReceiving"))
 for row in p.lights:
  var at:=vec(row.at);var h:=ray(space,at,at-Vector3.UP*4);record("light_floor_"+str(row.name),not h.is_empty()and absf(h.position.y-97.5)<.0002)
 for i in range(4):
  var x:float=[26.22,31.78,34.22,39.78][i];var at:=Vector3(x+.07,100.28,483.9);var h:=ray(space,at,at+Vector3.UP*.08);record("fixture_socket_"+str(i),not h.is_empty()and str(h.collider.get_path()).contains("FamilyD16StaffReceiving")and absf(h.position.y-100.295)<.0002)
  at=Vector3(x+.15,100.28,483.9);h=ray(space,at,at+Vector3.UP*.08);record("fixture_canopy_"+str(i),not h.is_empty()and str(h.collider.get_path()).contains("FamilyD16StaffReceiving")and absf(h.position.y-100.32)<.0002)
  var socket:MeshInstance3D=group.find_child("F16_FixtureRoofSocket"+str(i),true,false);var roof:MeshInstance3D=group.find_child("F16_Canopy",true,false);var sb:AABB=socket.global_transform*socket.get_aabb();var rb:AABB=roof.global_transform*roof.get_aabb();record("positive_fixture_canopy_join_"+str(i),sb.intersection(rb).get_volume()>.0001)
 var route:Array[Vector3]=[Vector3(21,97.5,485),Vector3(21,97.5,483.8),Vector3(24,97.5,483.8),Vector3(29,97.5,483.8),Vector3(34,97.5,483.8),Vector3(39,97.5,483.8),Vector3(44,97.5,483.8),Vector3(44,97.5,481),Vector3(44,97.5,477),Vector3(44,97.5,481),Vector3(44,97.5,483.8),Vector3(39,97.5,483.8),Vector3(34,97.5,483.8),Vector3(29,97.5,483.8),Vector3(24,97.5,483.8),Vector3(21,97.5,483.8),Vector3(21,97.5,485),Vector3(21,97.5,488)]
 var legs:Array=[];var proceed:=errors.is_empty();actor.set_controls_enabled(true);actor.set_physics_process(true);await frames(20)
 for goal in route:
  if not proceed:break
  var leg:Dictionary=await walk_to(actor,goal);legs.append(leg);record("walk_"+str(legs.size()),leg.reached and leg.floor_contact);proceed=leg.reached and leg.floor_contact
 var adjacent:Array=[]
 for y in [84.0,88.5,93.0,97.5]:
  actor.set_physics_process(false);actor.global_position=Vector3(21,y+.03,-485.5);actor.velocity=Vector3.ZERO;actor.set_physics_process(true);await frames(15)
  for goal in [Vector3(21,y,-483.5),Vector3(21,y,-485.5)]:
   var leg:Dictionary=await walk_to(actor,goal);adjacent.append(leg);record("preserved_upper_threshold_"+str(y)+"_"+str(adjacent.size()),leg.reached and leg.floor_contact)
 var prior_family:Array=[]
 for fy in [84.0,88.5,93.0]:
  actor.set_physics_process(false);actor.global_position=Vector3(21,fy+.03,485.5);actor.velocity=Vector3.ZERO;actor.set_physics_process(true);await frames(15)
  for goal in [Vector3(21,fy,483.5),Vector3(21,fy,485.5)]:
   var leg:Dictionary=await walk_to(actor,goal);prior_family.append(leg);record("protected_Family_prior_"+str(fy)+"_"+str(prior_family.size()),leg.reached and leg.floor_contact)
 var kept:=true;var preservation_failures:Array=[]
 for m in original:
  if not m.global_transform.is_equal_approx(original[m].pose)or(str(m.name)not in selected and m.mesh!=original[m].mesh):kept=false;preservation_failures.append({"path":str(m.get_path()),"pose":str(m.global_transform),"before":str(original[m].pose),"same_mesh":m.mesh==original[m].mesh})
 record("retained_poses_resources",kept);record("continuous_walk",legs.size()==18 and proceed)
 var report:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks,"errors":errors,"classified_old_contacts":preflight,"preservation_failures":preservation_failures,"protected_Quiet_D13_D16_legs":adjacent,"protected_Family_D13_D14_D15_legs":prior_family,"separate_adjacent_setup_seeds":true,"original_meshes":original.size(),"legs":legs,"no_intra_route_teleports":true,"scope":"Candidate geometry and unladen walking; preflight contacts require explicit classification before adoption"};FileAccess.open(E+"CANDIDATE.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("FAMILY_D16_CANDIDATE ",report.status," ",errors);quit(0 if errors.is_empty()else 1)
