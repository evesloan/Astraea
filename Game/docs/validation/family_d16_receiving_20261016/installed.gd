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
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(21,97.53,488);actor.velocity=Vector3.ZERO;var group:Node3D=ship.get_node("ShipSpace/FamilyD16StaffReceiving")
 var lift:Node=ship.find_child("FamilyPassengerLift",true,false)
 for i in range(300):
  if lift.phase=="idle":break
  await frames(1)
 record("lift_settled_before_baseline",lift.phase=="idle");record("one_installed_receiver",ship.find_children("FamilyD16StaffReceiving","Node3D",true,false).size()==1)
 var original:Dictionary={}
 for owner in [ship.get_node("ShipSpace/Districts/FamilyTerraceReceivingCandidate"),ship.get_node("ShipSpace/Group3AftRiserPair"),ship.get_node("ShipSpace/QuietD15StaffReceiving"),ship.get_node("ShipSpace/QuietD14StaffReceiving"),ship.get_node("ShipSpace/QuietD13StaffReceiving"),ship.get_node("ShipSpace/QuietD16StaffReceiving"),ship.get_node("ShipSpace/FamilyD13StaffReceiving"),ship.get_node("ShipSpace/FamilyD14StaffReceiving"),ship.get_node("ShipSpace/FamilyD15StaffReceiving"),ship.get_node("ShipSpace/D17StarboardStandardReceiving")]:
  for m:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):original[m]={"mesh":m.mesh,"pose":m.global_transform}
 for row in p.walls:
  var owner:Node3D=ship.get_node("ShipSpace/Districts/FamilyTerraceReceivingCandidate")if row.owner=="house"else ship.get_node("ShipSpace/Group3AftRiserPair");var mesh:MeshInstance3D=owner.find_child(row.name,true,false);record("installed_successor_"+str(row.name),mesh.mesh.get_faces().size()==int(row.replacement_triangles)*3);record("retained_preimage_"+str(row.name),group.get_meta(str(row.name)+"_original_mesh").get_faces().size()==int(row.source_triangles)*3)
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for lamp in group.find_children("*","SpotLight3D",true,false):record("unique_registered_"+str(lamp.name),budget.sources.count(lamp)==1)
 record("four_source_lights",group.find_children("*","SpotLight3D",true,false).size()==4)
 var space:=ship.get_world_3d().direct_space_state;var excludes:Array[RID]=[actor.get_rid()]
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):excludes.append(body.get_rid())
 var finishing_contacts:Array=[]
 for row in p.parts:
  if not str(row.name).begins_with("F16_LobbyReveal")and not str(row.name).begins_with("F16_GuardCutCap"):continue
  var hits:Array=query_box(space,vec(row.min),vec(row.max),excludes);var good:=not hits.is_empty()
  for hit in hits:
   if str(row.name).begins_with("F16_LobbyReveal"):good=good and str(hit).contains("/lobby_wall_staff_white_paint_y12/")
   else:good=good and str(hit).contains("/FT_Batch_345/")
  record("bounded_finishing_contact_"+str(row.name),good);finishing_contacts.append({"part":row.name,"hits":hits,"classified":good})
 for x in [21.,24.,29.,34.,39.,44.]:
  var at:=Vector3(x,97.5,483.8);var h:=ray(space,at+Vector3.UP*.04,at-Vector3.UP*.04);record("installed_floor_"+str(x),not h.is_empty()and str(h.collider.get_path()).contains("FamilyD16StaffReceiving")and absf(h.position.y-97.5)<.0002)
 for x in [21.,44.]:
  var z:float=484 if x==21 else 482.2
  for y in [97.9,98.5,99.1,99.7]:record("open_aperture_"+str(x)+str(y),ray(space,Vector3(x,y,z-.35),Vector3(x,y,z+.35)).is_empty())
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
 var kept:=true
 for m in original:
  if not m.global_transform.is_equal_approx(original[m].pose)or m.mesh!=original[m].mesh:kept=false
 record("installed_source_preservation",kept);record("complete_continuous_route",legs.size()==18 and proceed)
 var report:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks,"errors":errors,"finishing_contacts":finishing_contacts,"original_meshes_preserved":original.size(),"legs":legs,"protected_Quiet_D13_D16_legs":adjacent,"protected_Family_D13_D14_D15_legs":prior_family,"separate_adjacent_setup_seeds":true,"route_teleports":0,"fixture_lights":4,"scope":"Installed physical receiving; engineering,operating permissions,loaded carts,species and final art remain held"};FileAccess.open(E+"INSTALLED.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("FAMILY_D16_INSTALLED ",report.status," ",errors);quit(0 if errors.is_empty()else 1)
