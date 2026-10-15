extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/wet_receiving/"
var count:=0
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var group:Node3D=ship.get_node("ShipSpace/FittedWetPavilions20261015");await frames(4)
 var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var space:=ship.get_world_3d().direct_space_state;var suites:Array=[]
 var routes:Array=[{"name":"Tidal public-to-ramp","start":Vector3(-96.1,102,-370),"goals":[Vector3(-96.1,102,-357.2),Vector3(-95.4,102,-357.2),Vector3(-94.5,102.04167,-357.2),Vector3(-77.4,103.46667,-357.2),Vector3(-73.8,103.5,-357.2),Vector3(-73.8,103.5,-360.8)]},{"name":"Quiet public-to-L-ramp","start":Vector3(63.5,102,-370),"goals":[Vector3(63.5,102,-382.7),Vector3(64.7,102.01667,-382.7),Vector3(77.2,103.05833,-382.7),Vector3(78.4,103.08333,-382.7),Vector3(78.4,103.08333,-381.6),Vector3(78.4,103.5,-376.1),Vector3(77.4,103.5,-376.1),Vector3(77.35,103.5,-375.6)]}]
 for route in routes:
  player.global_position=route.start+Vector3.UP*.03;player.velocity=Vector3.ZERO;player.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position);await frames(20)
  var legs:Array=[]
  for goal:Vector3 in route.goals:
   var leg:Dictionary=await walk_to(player,goal);legs.append(leg)
   if not leg.reached or not leg.floor_contact:break
  suites.append({"name":route.name,"legs":legs,"complete":legs.size()==route.goals.size()and legs.all(func(a):return a.reached and a.floor_contact)})
 player.set_physics_process(false);player.global_position=Vector3(0,0,0);player.force_update_transform();await frames(2)
 var stances:Array=[]
 for point:Vector3 in[Vector3(-73.9,103.5,-360.8),Vector3(77.35,103.5,-375.6),Vector3(-91.7,102,-374.5),Vector3(-88.3,102,-374.5),Vector3(66.55,102,-363.1),Vector3(71.05,102,-363.1)]:stances.append({"at":str(point),"capsule_clear":capsule_clear(space,point)})
 inventory(ship,group)
 var config:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"FITTED_CONFIG_r010.json"));var p:Dictionary=config
 var results:Array=[]
 for row in p.doors:
  var door:Node3D=group.get_node(str(row.kit)+"_ChangingPrivacy"+str(int(row.source_index)))
  player.set_physics_process(true)
  var outward:Vector3=Vector3(0,0,1)if row.kit=="TIDAL"else Vector3(0,0,-1);var outside:Vector3=vec(row.at)+outward*1.8;var inside:Vector3=vec(row.at)-outward*1.3;player.global_position=outside+Vector3.UP*.03;player.velocity=Vector3.ZERO;await frames(20)
  var closed_before:bool=not door.desired_open and door.open_fraction==0;door.interact(player);await frames(100);var opened:bool=door.desired_open and door.open_fraction>.999
  var leg:Dictionary=await walk_to(player,inside);var back:Dictionary={}
  if leg.reached:back=await walk_to(player,outside)
  if back.get("reached",false):door.interact(player);await frames(100)
  results.append({"kit":row.kit,"index":row.source_index,"closed_before":closed_before,"opened":opened,"entered":leg,"returned":back,"closed_after":not door.desired_open and door.open_fraction==0})
 player.set_physics_process(false);player.global_position=Vector3(0,0,0);player.force_update_transform();await frames(2)
 var privacy_stances:Array=[]
 for point:Vector3 in[Vector3(-73.9,103.5,-360.8),Vector3(77.35,103.5,-375.6),Vector3(-91.7,102,-374.5),Vector3(-88.3,102,-374.5),Vector3(66.55,102,-363.1),Vector3(71.05,102,-363.1)]:privacy_stances.append({"at":str(point),"capsule_clear":capsule_clear(space,point)})
 var rest_approaches:Array=[]
 for kit in["TIDAL","QUIET"]:
  for i in range(6):
   var chair:MeshInstance3D=group.find_child("F010__G2VIP_"+kit+"_Rest"+str(i)+"_Seat",true,false);assert(chair!=null);var b:AABB=chair.global_transform*chair.get_aabb();var at:=b.get_center();at.y=103.5 if kit=="TIDAL"else 102.;at.x+=1.15 if kit=="TIDAL"or i%2==0 else -1.15;rest_approaches.append({"kit":kit,"chair":i,"at":str(at),"capsule_clear":capsule_clear(space,at)})
 var moved_floor_pins:Array=[]
 var all_excludes:Array[RID]=[]
 for row in config.loose_furniture_moves:
  var asset:Node3D=ship.find_child(str(row.name),true,false)
  for body:CollisionObject3D in asset.find_children("*","CollisionObject3D",true,false):all_excludes.append(body.get_rid())
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):all_excludes.append(body.get_rid())
 for row in config.loose_furniture_moves:
  var point:=vec(row.target_xyz);var q:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.02,point-Vector3.UP*.02);q.exclude=all_excludes;var h:=space.intersect_ray(q);moved_floor_pins.append({"name":row.name,"floor":str(h.collider.get_path())if not h.is_empty()else"","supported":not h.is_empty()and absf(h.position.y-102)<.002})
 var group_contacts:Array=[]
 for key in["D17_QuietReading_1","D17_QuietReading_2","D17_SharedTable_1"]:
  var item:Node3D=ship.find_child(key,true,false);var excluded:Array[RID]=[]
  for body:CollisionObject3D in item.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
  for mesh:MeshInstance3D in item.find_children("*","MeshInstance3D",true,false):
   var q:=PhysicsShapeQueryParameters3D.new();q.shape=mesh.mesh.create_convex_shape(true,false);q.shape.margin=0.;q.margin=0.;q.transform=mesh.global_transform;q.exclude=excluded
   for hit in space.intersect_shape(q,128):
    var parent:Node=hit.collider.get_parent()
    if parent.get_meta("extras",{}).get("category","")!="floor":group_contacts.append({"item":key,"mesh":str(mesh.name),"hit":str(hit.collider.get_path())})
 var light_registration:Array=[];var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for light:Light3D in group.find_children("*","Light3D",true,false):light_registration.append({"name":str(light.name),"registered_once":budget.sources.count(light)==1})
 var ok:bool=group.get_meta("default_main_adoption")and light_registration.size()==14 and light_registration.all(func(a):return a.registered_once)and group_contacts.is_empty()and moved_floor_pins.all(func(a):return a.supported)and rest_approaches.all(func(a):return a.capsule_clear)and results.all(func(a):return a.closed_before and a.opened and a.entered.reached and a.returned.get("reached",false)and a.closed_after)and suites.all(func(a):return a.complete)and stances.all(func(a):return a.capsule_clear)
 FileAccess.open(D+"INSTALLED_COMPLETE_r010.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","routes":suites,"privacy_doors":results,"rest_approaches":rest_approaches,"moved_floor_pins":moved_floor_pins,"reading_group_contacts":group_contacts,"light_registration":light_registration,"stances":stances,"original_player_controller":true,"new_capacity_or_water_operation_admitted":false},"  "));print("PASS_FITTED_R010_ROUTE_INVENTORY"if ok else"FAIL_FITTED_R010_ROUTE_INVENTORY");quit(0 if ok else 1)

func inventory(ship:Node3D,group:Node3D)->void:
 var space:=ship.get_world_3d().direct_space_state;var excludes:Array[RID]=[]
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):excludes.append(body.get_rid())
 var sites:Array=[];var main_hits:Array=[];var config:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/fitted_wet_pavilions_20261015/FITTED_CONFIG_r010.json"))
 for kit in["TIDAL","QUIET"]:
  var model:Node3D=group.get_node(kit);var contacts:Array=[];var footpins:Array=[];var checked:=0
  for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
   if str(mesh.name).contains("Water_Illustrative"):continue
   checked+=1;var b:AABB=mesh.global_transform*mesh.get_aabb();var shape:ConvexPolygonShape3D=mesh.mesh.create_convex_shape(true,false);shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform=mesh.global_transform;q.exclude=excludes
   var hits:Array=space.intersect_shape(q,256)
   if not hits.is_empty():
    var paths:Array=[]
    for hit in hits:paths.append(str(hit.collider.get_path()).trim_prefix(str(ship.get_path())+"/"))
    contacts.append({"part":str(mesh.name),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z],"contacts":paths,"saturated":hits.size()==256})
   if str(mesh.name).contains("ColumnBase") or str(mesh.name).ends_with("_Foot"):
    var centre:Vector3=b.get_center();var ray:=PhysicsRayQueryParameters3D.create(Vector3(centre.x,102.05,centre.z),Vector3(centre.x,101.95,centre.z));ray.exclude=excludes;var hit:Dictionary=space.intersect_ray(ray);footpins.append({"column":str(mesh.name),"at":[centre.x,102,centre.z],"old_floor":str(hit.collider.get_path())if not hit.is_empty()else"","floor_y":hit.position.y if not hit.is_empty()else null})
  sites.append({"kit":kit,"meshes_checked":checked,"contacts":contacts,"column_floor_preimages":footpins})
  var box:=BoxShape3D.new();box.size=Vector3(34,3.98,8);box.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.margin=0.;q.transform=Transform3D(Basis.IDENTITY,Vector3(-80 if kit=="TIDAL"else 80,104.0,-370));var hits:Array=space.intersect_shape(q,8192);assert(hits.size()<8192)
  for hit in hits:
   if group.is_ancestor_of(hit.collider):main_hits.append({"kit":kit,"new_contact":str(hit.collider.get_path())})
 var roof_preservation:Array=[]
 for row in config.roofs:
  var old:Mesh=group.get_meta(str(row.kit)+"_original_roof_mesh");var node:MeshInstance3D=ship.get_node("ShipSpace/Districts/"+str(row.receiver_root)).find_child(str(row.node),true,false);var faces:PackedVector3Array=node.mesh.get_faces();var keys:Dictionary={}
  for i in range(0,faces.size(),3):keys[digest(PackedVector3Array([faces[i],faces[i+1],faces[i+2]]).to_byte_array())]=true
  var original:PackedVector3Array=old.get_faces();var untouched:=0;var missing:=0;var hole:=AABB(Vector3(row.mask[0],row.mask[2],row.mask[4]),Vector3(row.mask[1]-row.mask[0],row.mask[3]-row.mask[2],row.mask[5]-row.mask[4]))
  for i in range(0,original.size(),3):
   var bounds:=AABB(original[i],Vector3.ZERO);bounds=bounds.expand(original[i+1]);bounds=bounds.expand(original[i+2])
   if not bounds.intersects(hole):
    if keys.has(digest(PackedVector3Array([original[i],original[i+1],original[i+2]]).to_byte_array())):untouched+=1
    else:missing+=1
  roof_preservation.append({"kit":row.kit,"untouched_original_triangles_exact":untouched,"unmatched_outside_triangles":missing,"original_source_file_unchanged":FileAccess.get_sha256("res://assets/models/"+str(row.model))==str(row.source_sha256)})
 FileAccess.open(D+"FITTED_CURRENT_CONTACTS_r010.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"FITTED_R010_CURRENT_CONTACT_INVENTORY_REQUIRES_INTERPRETATION","sites":sites,"new_contacts_in_original_eight_metre_main_lanes":main_hits,"roof_outside_preservation":roof_preservation,"retained_loose_models_moved":group.get_meta("exact_loose_furniture_successors").size(),"production_changed":false},"  "))

func digest(b:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(b);return h.finish().hex_encode()
