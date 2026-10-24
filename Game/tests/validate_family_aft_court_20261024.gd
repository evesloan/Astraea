extends SceneTree
const P:="res://family_aft_court_20261024/"
var checks:=0
var failures:Array=[]
func _initialize()->void:call_deferred("run")
func check(ok:bool,label:String)->void:
 checks+=1
 if not ok:failures.append(label);push_error(label)
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func edge(z:float)->float:return 100.0 if z<=423.164 else 100.0-(z-423.164)*(37.0/(491.123-423.164))
func run()->void:
 var main:Node=load("res://scenes/main_family_aft_court_integrated_20261024.tscn").instantiate();root.add_child(main)
 # Keep the actual ship intact, but defer drawing until the one review image.
 main.world_view.render_target_update_mode=SubViewport.UPDATE_DISABLED
 main.post_view.render_target_update_mode=SubViewport.UPDATE_DISABLED
 var ship:Node3D=main.get_node("World360/Astraea")
 while not ship.get_meta("runtime_ready",false):await process_frame
 for i in range(8):await physics_frame
 paused=true
 var house:Node3D=ship.get_node("ShipSpace/Districts/FamilyTerraceReceivingCandidate")
 var district:Node3D=house.get_node("FamilyAftCourt20261024")
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"))
 check(district.get_meta("new_capacity")==0 and district.get_meta("new_floor_area_m2")==0,"No new room capacity or floor")
 check(district.get_meta("architecture_parts")==136 and district.get_meta("plant_placements")==53,"Complete aft-zone package")
 check(district.get_meta("original_meshes_preserved",0)>410,"Exact original mesh resources and poses preserved before/after adapter")
 var bank:Node=ship.get_node("ShipSpace/Districts/FamilySpecialty47_20261022")
 check(bank.get_meta("rooms")==47 and bank.get_meta("reserved_rests")==59,"47 specialty identities and59 reserved rests preserved")
 check(house.get_meta("installed_guest_units")==82,"82 ordinary homes preserved")
 check(house.has_meta("family_enclosure_finish_20261022"),"Forward enclosure successor preserved")
 var floor:=ship.get_world_3d().direct_space_state;var excluded:Array[RID]=[]
 for b in ship.find_children("*","CharacterBody3D",true,false):excluded.append(b.get_rid())
 for b in ship.find_children("*","RigidBody3D",true,false):excluded.append(b.get_rid())
 var points:Array[Vector3]=[]
 for z in range(400,481,4):points.append(Vector3(65,84,z))
 # The outer route ends before the tapered second planting bed; the retained
 # west path continues to the tip. Never invent a route through that bed.
 for z in range(402,439,4):points.append(Vector3(edge(z)-2,84,z))
 points.append(Vector3(91.1,84,417.8));points.append(Vector3(91.1,84,422.2))
 for point:Vector3 in points:
  var ray:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.15,point-Vector3.UP*.4);ray.exclude=excluded;var hit:=floor.intersect_ray(ray)
  check(not hit.is_empty()and absf(hit.position.y-84)<.02,"Retained court floor "+str(point))
  var cap:=CapsuleShape3D.new();cap.radius=.3;cap.height=1.8;var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.margin=.001;q.exclude=excluded;q.transform.origin=point+Vector3.UP*.925;var hs:=floor.intersect_shape(q,8);var names:Array=[]
  for h in hs:names.append(str(h.collider.get_path()))
  check(hs.is_empty(),"Court route/seat approach "+str(point)+" "+str(names))
 var named_parts:=0
 for mesh:MeshInstance3D in district.find_children("Architecture_*","MeshInstance3D",true,false):
  named_parts+=mesh.get_meta("authored_part_names",[]).size()
  check(mesh.get_active_material(0).resource_name=="COURT_"+str(mesh.get_meta("retained_material_role")),"Original textured court material shared")
  var bounds:=mesh.global_transform*mesh.get_aabb();check(bounds.position.y>=83.999 and bounds.end.y<=106.026,"No lower-floor/cover intrusion")
 check(named_parts==136,"All authored parts present in runtime batches")
 for row:Dictionary in plan.plants:
  var point:=vec(row.position);var supported:=false
  if str(row.owner).begins_with("FT_RootedGardenSoil_"):
   # Retained soil is deliberately visual-only. Check the actual installed
   # owner's triangles, not a physics collider that its source forbids.
   for mesh:MeshInstance3D in house.find_children("*","MeshInstance3D",true,false):
    var extras:Dictionary=mesh.get_meta("extras",{});var owns:=false
    for member:Dictionary in extras.get("source_part_ranges",[]):
     if member.source_part_id==row.owner:owns=true
    if not owns:continue
    check(extras.get("runtime_collision",true)==false,"Original soil collision policy preserved")
    var faces:=mesh.mesh.get_faces()
    for i in range(0,faces.size(),3):
     var intersection=Geometry3D.segment_intersects_triangle(point+Vector3.UP*.08,point-Vector3.UP*.15,mesh.global_transform*faces[i],mesh.global_transform*faces[i+1],mesh.global_transform*faces[i+2])
     if intersection!=null and absf(intersection.y-point.y)<.025:supported=true;break
  else:
   var ray:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.08,point-Vector3.UP*.15);ray.exclude=excluded;var hit:=floor.intersect_ray(ray);supported=not hit.is_empty()and absf(hit.position.y-point.y)<.025
  check(supported,"Plant supported by retained/new soil "+str(row.name))
 var plant_batches:=0
 for batch:MultiMeshInstance3D in district.find_children("PlantBatch_*","MultiMeshInstance3D",true,false):
  check(batch.multimesh.mesh!=null and batch.multimesh.instance_count==int(batch.get_meta("source_instance_count")),"Complete shared plant batch")
  for i in range(batch.multimesh.instance_count):
   var bounds: AABB=batch.multimesh.get_instance_transform(i)*batch.multimesh.mesh.get_aabb()
   for corner in range(8):
    var v:=bounds.get_endpoint(corner);check(v.x>=62.99 and v.x<=edge(v.z)+.02 and v.y<=106.02,"Plant bounds inside real tapered court")
  plant_batches+=1
 # Check the actual retained opening, not an assumed rectangular hull boundary.
 var open_rays:=0
 for z in [405.0,417.0,430.0,444.0]:
  var from:=Vector3(edge(z)-1.5,104,z);var to:=Vector3(edge(z)+.12,104,z);var ray:=PhysicsRayQueryParameters3D.create(from,to);ray.exclude=excluded;var hit:=floor.intersect_ray(ray)
  check(hit.is_empty()or not district.is_ancestor_of(hit.collider),"New architecture leaves original clerestory opening clear");open_rays+=1
 var budget:=ship.get_node("ShipSystems/LocalShadowSourceBudget");var original_pose:Vector3=budget.actor.global_position;var light_rows:Array=[]
 for position in [Vector3(91,84,420),Vector3(70,84,456),Vector3(66,84,475)]:
  budget.actor.global_position=position;budget.refresh();var active:=0
  for light:Light3D in budget.previously_active:
   if district.is_ancestor_of(light):active+=1
  check(budget.shadow_source_budget==8 and budget.previously_active.size()<=8,"Existing global light budget")
  check(active>0,"Existing lantern successor illuminates aft destination "+str(position))
  light_rows.append({"position":[position.x,position.y,position.z],"aft_active":active,"total_active":budget.previously_active.size()})
 for row:Dictionary in plan.lights:
  var old:Light3D=house.get_node(row.original);check(not old.visible and not old.shadow_enabled and old.get_meta("fixture_powered")==false,"Original lamp not duplicated")
  district.get_node(row.name).set_meta("fixture_powered",false)
 budget.refresh()
 for light:Light3D in budget.previously_active:check(not district.is_ancestor_of(light),"Aft fixture power-off honored")
 for row:Dictionary in plan.lights:district.get_node(row.name).set_meta("fixture_powered",true)
 budget.actor.global_position=original_pose;budget.refresh()
 var result:={"status":"PASS"if failures.is_empty()else"FAIL","checks":checks,"failures":failures,"actual_main_runtime_ready":true,"parts":named_parts,"plants":plan.plants.size(),"architecture_batches":district.get_meta("architecture_batches"),"plant_batches":plant_batches,"preserved_original_meshes":district.get_meta("original_meshes_preserved"),"floor_route_points":points.size(),"clerestory_rays":open_rays,"lights":light_rows,"new_rooms":0,"new_capacity":0,"new_floor_area_m2":0,"visual_accepted":false,"whole_gameplay_performance_accepted":false}
 FileAccess.open(P+"evidence/INSTALLED_CHECK.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  ")+"\n");print("FAMILY_AFT_INSTALLED ",JSON.stringify(result))
 if failures.is_empty()and "--capture"in OS.get_cmdline_user_args():
  var camera:=Camera3D.new();ship.add_child(camera);camera.position=Vector3(66,89.8,402);camera.look_at(Vector3(85,94,439));camera.fov=78;camera.far=600;camera.current=true
  budget.actor.global_position=Vector3(82,84.1,432);budget.refresh();main.world_view.size=Vector2i(960,540);main.world_view.render_target_update_mode=SubViewport.UPDATE_ALWAYS
  for i in range(3):await process_frame
  await RenderingServer.frame_post_draw
  var image:Image=main.world_view.get_texture().get_image();var path:=P+"evidence/FAMILY_AFT_ACTUAL_SHIP_UNFINISHED.png"
  if FileAccess.file_exists(path):push_error("Refuse overwriting existing contextual view");quit(1);return
  var saved:=image.save_png(path);check(saved==OK,"Context image saved")
  FileAccess.open(P+"evidence/CAPTURE.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"UNFINISHED_ACTUAL_SHIP_CANDIDATE","sha256":FileAccess.get_sha256(path),"renderer":RenderingServer.get_video_adapter_name(),"camera":[66,89.8,402],"target":[85,94,439],"actual_complete_ship":true,"scene":"res://scenes/main_family_aft_court_integrated_20261024.tscn","production_selected_at_capture":false,"post_effects_applied":false,"no_exposure_change":true,"final_visual_accepted":false},"  ")+"\n")
 main.free();await process_frame;quit(0 if failures.is_empty()else 1)
