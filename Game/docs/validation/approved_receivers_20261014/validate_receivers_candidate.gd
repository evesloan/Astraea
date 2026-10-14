extends "res://tests/validate_d04_port_forward_commons_service.gd"
const P="/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/"
var count:=0
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",P+"receiver_frame_candidate/CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func require(ok:bool,label:String)->bool:
 count+=1
 if not ok:push_error(label);quit(1)
 return ok
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state
 var members:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"receiver_frame_candidate/MEMBERS.json"))
 var anchors:Array=[];var missing:Array=[]
 for row in members.regions:
  for anchor in row.source_surface_anchors:
   if not anchor.has("source_model"):continue
   var point:=Vector3(anchor.surface_point_xz[0],anchor.source_slice_y,anchor.surface_point_xz[1])
   var sphere:=SphereShape3D.new();sphere.radius=.04
   var q:=PhysicsShapeQueryParameters3D.new();q.shape=sphere;q.transform=Transform3D(Basis.IDENTITY,point)
   var hits:Array=[];var matching:=false
   for direction:Vector3 in[Vector3.RIGHT,Vector3.UP,Vector3.FORWARD]:
    for sign_value in [-1.,1.]:
     var hit:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(point+direction*.08*sign_value,point-direction*.08*sign_value))
     if not hit.is_empty():
      var path:String=str(hit.collider.get_path());hits.append(path)
      if path.contains(str(anchor.source_node))and hit.position.distance_to(point)<.004:matching=true
   anchors.append({"region":row.region_id,"source_node":anchor.source_node,"point":[point.x,point.y,point.z],"matching_contact":matching,"contacts":hits})
   if not matching:missing.append(anchors[-1])
 FileAccess.open(P+"receiver_frame_candidate/BASELINE_ANCHOR_CONTACTS.json",FileAccess.WRITE).store_string(JSON.stringify({"anchors":anchors,"missing":missing},"  "))
 if not require(missing.is_empty(),"Every specified existing primary anchor has exact runtime collision before new construction"):return
 var original_floor_count:int=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()
 var receiver:Node3D=load("res://scripts/approved_receivers_20261014/package.gd").build(ship);await frames(5)
 if not require(original_floor_count==303 and ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303,"Original floor ownership preserved"):return
 var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"source_floor_regions/REGIONS.json"))
 var witnesses:=0;var retained_surface_overlays:Array=[]
 for row in source.regions:
  for triangle in row.triangles:
   var at:=Vector3((triangle[0][0]+triangle[1][0]+triangle[2][0])/3.,row.floor_y,(triangle[0][1]+triangle[1][1]+triangle[2][1])/3.)
   var query:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02)
   var first:Dictionary=space.intersect_ray(query)
   if not require(not first.is_empty()and first.normal.y>.99,"Actual receiving surface within authored 20mm floor interval "+str(row.id)):return
   var owned:Dictionary={}
   for attempt in range(16):
    var hit:Dictionary=space.intersect_ray(query)
    if hit.is_empty():break
    var path:String=str(hit.collider.get_path())
    if path.contains("ApprovedSixHouseReceiving/ExactRetainedMissingFloors/"+str(row.id)+"/"):owned=hit;break
    retained_surface_overlays.append({"region":row.id,"sample":[at.x,at.y,at.z],"retained_path":path,"retained_y":hit.position.y})
    var excludes:Array[RID]=query.exclude;excludes.append(hit.collider.get_rid());query.exclude=excludes
   if not require(not owned.is_empty()and absf(owned.position.y-at.y)<.002 and owned.normal.y>.99,"Exact owned compiler floor contact "+str(row.id)):return
   witnesses+=1
 var home_plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/consolidated_all_eight_20261013/CONSOLIDATED_PLAN.json"))
 var entry_failures:Array=[]
 for home in home_plan.G2_homes:
  var at:=Vector3(home.entry[0],home.entry[1],home.entry[2]);var hit:Dictionary=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
  var clear:bool=capsule_clear(space,at)
  if not require(not hit.is_empty()and absf(hit.position.y-at.y)<.002 and clear,"Original home entry supported and original controller clear "+str(home.key)):return
 var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.global_position=Vector3(-65.5,102.03,-15.1);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);await frames(25)
 var legs:Array=[]
 for goal:Vector3 in[Vector3(-82.8,102,-15.1),Vector3(-82.8,102,-18),Vector3(-82.8,102,-15.1),Vector3(-65.5,102,-15.1)]:
  var leg:Dictionary=await walk_to(actor,goal);legs.append(leg)
  if not require(leg.reached and leg.floor_contact,"Existing connected route preserved with new receivers"):return
 FileAccess.open(P+"receiver_frame_candidate/RECEIVER_RUNTIME_VERIFICATION.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_COMBINED_RECEIVER_CANDIDATE_CONTACT_FLOORS_ENTRIES_AND_RETAINED_ROUTE","checks":count,"exact_primary_anchors":anchors.size(),"new_floor_regions":source.regions.size(),"floor_witnesses":witnesses,"retained_surface_overlays":retained_surface_overlays,"home_entries":80,"original_controller_legs":legs,"capacity_operations_or_final_art_accepted":false,"production_adoption":false},"  "))
 print("PASS_COMBINED_RECEIVER_CANDIDATE checks=",count);quit(0)
