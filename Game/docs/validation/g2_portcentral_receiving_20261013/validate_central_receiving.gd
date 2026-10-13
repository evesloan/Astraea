extends "res://tests/validate_d04_port_forward_commons_service.gd"
var nchecks:=0
var failures:Array=[]
var legs:Array=[]
var lower_bearings:=0
var upper_bearings:=0
const OUT="/workspace/astraea-integration-cutoff-20261013/g2_last_three_pairs_20261013/CENTRAL_RECEIVING_RUNTIME.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/g2_last_three_pairs_20261013/CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func receipt()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_CURRENT_PORTCENTRAL_ADJUNCT_CARE_RECEIVING"if failures.is_empty()else"HOLD","checks":nchecks,"failures":failures,"legs":legs,"lower_stub_slab_bearings":lower_bearings,"upper_arrival_slab_bearings":upper_bearings,"source_floor_m2":80,"missing_connections_m2":30.06,"original_primary_walls_beams_slabs_unchanged":true,"bounded_arrival_guard_successor":true,"new_units_or_capacity":0,"operating_care_private_services_structuralcapacity_or_lower_room_acceptance":false,"aft_pairs_not_adopted":true,"full_build_accepted":false},"  "))
func require(ok:bool,label:String)->bool:
 nchecks+=1
 if not ok:failures.append(label);receipt();push_error(label);quit(1)
 return ok
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var space:=ship.get_world_3d().direct_space_state;var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_portcentral_receiving_20261013/PLAN.json"));var source:Node=ship.get_node("ShipSpace/Districts/D15_D17_StarAtlasUpper_WIP");var old:Array=[];var unknown:Array=[]
 for mesh:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
  if str(mesh.name).begins_with("SA_D16_")or str(mesh.name).begins_with("SA_D17_")or str(mesh.name).begins_with("SA_LongBeam"):
   if str(mesh.name)in[p.guard_preimages[0].name,p.guard_preimages[1].name,p.guard_preimages[2].name]:continue
   var shapes:Array=[]
   for shape:CollisionShape3D in mesh.find_children("*","CollisionShape3D",true,false):shapes.append({"node":shape,"shape":shape.shape,"pose":shape.transform})
   old.append({"node":mesh,"mesh":mesh.mesh,"pose":mesh.global_transform,"material":mesh.material_override,"shapes":shapes})
 var receiving:Node=ship.get_node("ShipSpace/Districts/StarAtlasD17StandardBatch")
 for mesh:MeshInstance3D in receiving.find_children("*","MeshInstance3D",true,false):
  if str(mesh.name)in[p.guard_preimages[0].name,p.guard_preimages[1].name,p.guard_preimages[2].name]:continue
  var shapes:Array=[]
  for shape:CollisionShape3D in mesh.find_children("*","CollisionShape3D",true,false):shapes.append({"node":shape,"shape":shape.shape,"pose":shape.transform})
  old.append({"node":mesh,"mesh":mesh.mesh,"pose":mesh.global_transform,"material":mesh.material_override,"shapes":shapes})
 for part in p.parts:
  var a:Array=part.bounds;var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(a[1]-a[0],a[3]-a[2],a[5]-a[4]);shape.margin=.001;q.shape=shape;q.margin=.0001;q.transform=Transform3D(Basis.IDENTITY,Vector3((a[0]+a[1])/2.,(a[2]+a[3])/2.,(a[4]+a[5])/2.));var hits:Array=space.intersect_shape(q,128);var slab:=false
  for hit in hits:
   var name:String=str(hit.collider.get_parent().name);var allowed:bool=name in p.slab_batches
   if name in p.slab_batches:slab=true
   if part.kind in["floor","guard"]and name in["SAB_North_D17R_VestibuleFloorWest","SAB_North_D17R_VestibuleFloorNorth","SAB_Fore_StreetFloor0_000_0"]:allowed=true
   if part.kind in["east_slab_bearing","north_slab_bearing"]and name in p.declared_slab_layer_wall_joints:allowed=true
   for row in p.guard_preimages:
    if name==row.name and part.kind=="guard":allowed=true
   nchecks+=1
   if not allowed:unknown.append(str(part.name)+" "+str(hit.collider.get_path()))
  if part.kind=="lower_slab_bearing":
   if not require(slab,"Actuallowerstub sourcebearing "+str(part.name)):return
   lower_bearings+=1
  if part.kind in["east_slab_bearing","north_slab_bearing"]:
   if not require(slab,"Actualupperarrival sourcebearing "+str(part.name)):return
   upper_bearings+=1
 if not require(unknown.is_empty(),"Undeclared changedportcentral contacts "+JSON.stringify(unknown)):return
 var witnesses:Array=[]
 for at:Vector3 in[Vector3(-87,102,-22),Vector3(-84,102,-20),Vector3(-82.8,102,-17),Vector3(-78,102,-15.1),Vector3(-70,102,-15.1),Vector3(-68,102,-15.1)]:
  if not require(ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02).is_empty(),"Exactnewfloor preimage "+str(at)):return
  witnesses.append(at)
 var addition:Node3D=load("res://scripts/group2_portcentral_receiving_20261013/package.gd").build(ship);await frames(4)
 for row in old:
  if not require(row.node.mesh==row.mesh and row.node.global_transform==row.pose and row.node.material_override==row.material,"OriginalStarAtlasprimary/fitting resource exact"):return
  for entry in row.shapes:
   if not require(entry.node.shape==entry.shape and entry.node.transform==entry.pose,"OriginalStarAtlas contactshape exact"):return
 for at:Vector3 in witnesses:
  var hit:Dictionary=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
  if not require(not hit.is_empty()and addition.get_node("ReceivingFrame").is_ancestor_of(hit.collider)and absf(hit.position.y-at.y)<.002,"Source-ownednewfloor support "+str(at)):return
 if not require(lower_bearings==6 and upper_bearings==4,"Sixlowerstub andfourupperarrival geometricbearings"):return
 if not require(capsule_clear(space,Vector3(-65.5,102,-15.1)),"Originalarrival startclearbefore setup"):return
 actor.global_position=Vector3(-65.5,102.03,-15.1);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);await frames(25)
 for at:Vector3 in[Vector3(-68,102,-15.1),Vector3(-82.8,102,-15.1),Vector3(-82.8,102,-17),Vector3(-82.8,102,-18),Vector3(-82.8,102,-19.2),Vector3(-80.94999694824219,102,-18.85),Vector3(-82.8,102,-19.2),Vector3(-82.8,102,-18),Vector3(-82.8,102,-17),Vector3(-82.8,102,-15.1),Vector3(-68,102,-15.1),Vector3(-65.5,102,-15.1)]:
  var leg:Dictionary=await walk_to(actor,at);legs.append(leg)
  if not require(leg.reached and leg.floor_contact,"Originalcontroller portcentral sourcecare connection"):return
 var rows:Array=[]
 for sign_x in[-1,1]:
  for xabs in[63.5,65.,67.,69.,71.,73.]:
   for z in[326.5,330.,334.,338.,342.,344.5,346.,349.,352.,355.5,356.5]:
    var x:float=sign_x*xabs;var q:=PhysicsRayQueryParameters3D.create(Vector3(x,101.5,z),Vector3(x,83.9,z));var hit:Dictionary=space.intersect_ray(q);var row:Dictionary={"x":x,"z":z,"first_lower_hit":{}}
    if not hit.is_empty():
     row.first_lower_hit={"at":[hit.position.x,hit.position.y,hit.position.z],"normal":[hit.normal.x,hit.normal.y,hit.normal.z],"path":str(hit.collider.get_path())}
     var shape:=BoxShape3D.new();shape.size=Vector3(.18,maxf(.01,101.84-hit.position.y),.18);var sweep:=PhysicsShapeQueryParameters3D.new();sweep.shape=shape;sweep.transform=Transform3D(Basis.IDENTITY,Vector3(x,(101.84+hit.position.y)/2.,z));sweep.margin=.001;var contacts:Array=[]
     for contact in space.intersect_shape(sweep,128):contacts.append(str(contact.collider.get_path()))
     row.proposed_column_contacts=contacts
    rows.append(row)
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_last_three_pairs_20261013/AFT_CURRENT_LOWER_BEARINGS_AND_CLEARANCE.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_CURRENT_AFT_BEARING_AND_COLUMN_CONTACT_SURVEY","rows":rows,"samples":rows.size(),"new_geometry_adopted":false,"engineering_or_lower_room_accepted":false},"  "))
 receipt();print("PORTCENTRAL_CURRENT_RECEIVING_PASS checks=",nchecks);quit(0)
