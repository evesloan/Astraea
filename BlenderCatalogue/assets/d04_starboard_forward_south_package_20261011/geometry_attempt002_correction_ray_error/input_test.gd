extends "res://tests/validate_d04_commons_receiving_routes.gd"
func bounds(mesh:MeshInstance3D)->AABB:return mesh.global_transform*mesh.get_aabb()
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FORWARD_SOUTH_PACKAGE.json"));var space:=ship.get_world_3d().direct_space_state
 var homes:Node3D=load("res://scripts/d04_starboard_forward_south_package.gd").build(ship,true)
 for i in range(5):await physics_frame
 for file in p.model_pins:record("model_pin_"+file,FileAccess.get_sha256("res://assets/models/"+file)==p.model_pins[file])
 for f in p.source_pins:record("source_pin_"+f,FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/"+f)==p.source_pins[f])
 var directory:="/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_starboard_forward_south_package_20261011/"
 var inputs:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(directory+"GEOMETRY_CORRECTION_INPUT.json"));var previous:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(directory+"geometry_attempt001_outlook_hold/result.json"));var old:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(directory+"geometry_attempt001_outlook_hold/runtime_input.json"))
 record("prior_receipt_exact",FileAccess.get_sha256(directory+"geometry_attempt001_outlook_hold/result.json")==inputs.prior_receipt_sha256 and previous.status=="FAIL"and previous.errors==["home_capsule_895_5"]and previous.checks==3730)
 record("prior_input_exact",FileAccess.get_sha256(directory+"geometry_attempt001_outlook_hold/runtime_input.json")==inputs.prior_runtime_sha256)
 record("prior_test_exact",FileAccess.get_sha256(directory+"geometry_attempt001_outlook_hold/input_test.gd")==inputs.prior_test_sha256)
 record("unchanged_original_door_controller",FileAccess.get_sha256("res://scripts/guest_entry_door.gd")==inputs.unchanged_guest_entry_door_source_sha256)
 record("unchanged_runtime_builder",FileAccess.get_sha256("res://scripts/d04_starboard_forward_south_package.gd")==inputs.unchanged_package_builder_sha256)
 for r in p.rooms:
  var before:Dictionary=old.rooms.filter(func(a):return int(a.source_index)==int(r.source_index))[0].duplicate(true);var current:Dictionary=r.duplicate(true)
  if int(r.source_index)==895:before.erase("outlook_world");current.erase("outlook_world")
  record("unchanged_home_geometry_and_door_input_"+str(int(r.source_index)),before==current and old.model_pins[r.model_file]==p.model_pins[r.model_file])
 for name in ["commons_parts","guard_preimages","guard_successor_parts","north_end_guard_preimages","foundation_preimages","rest_reference_samples","receiving_parts","sources","source_pins"]:record("unchanged_geometry_input_"+name,old[name]==p[name])
 for file in old.model_pins:
  if file=="D04_STARBOARD_SOUTH_RECEIVING_r002.glb":continue
  record("immutable_unchanged_model_"+file,p.model_pins[file]==old.model_pins[file])
 var room:Dictionary=p.rooms.filter(func(a):return int(a.source_index)==895)[0];var corrected_outlook_at:=vec(room.outlook_world);var outlook_hit:=ray(space,corrected_outlook_at+Vector3.UP*.03,corrected_outlook_at-Vector3.UP*.03);record("895_corrected_outlook_actual_floor",not outlook_hit.is_empty()and homes.is_ancestor_of(outlook_hit.collider)and absf(outlook_hit.position.y-16.5)<.002);record("895_corrected_dry_outlook_capsule",capsule_clear(space,corrected_outlook_at));outlook_hit=ray(space,corrected_outlook_at+Vector3.UP*1.65,corrected_outlook_at+Vector3(-8,1.65,0));record("895_actual_private_garden_glazing",not outlook_hit.is_empty()and "GardenGlass"in str(outlook_hit.collider.get_parent().name))
 var allparts:Array=[];var removed:Dictionary={}
 for pre in p.guard_preimages:removed[pre.name]=true
 for part in p.receiving_parts:
  if not removed.has(part.name):allparts.append(part)
 for part in allparts:
  var mesh:MeshInstance3D=homes.find_child(str(part.name).replace(".","_"),true,false);record("receiving_r003_owned_part_found_"+part.name,mesh!=null)
  if mesh==null:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var b:=bounds(mesh);record("receiving_r003_source_bounds_"+part.name,b.position.distance_to(lo)<.00006 and b.end.distance_to(hi)<.00006)
 var own:Array[RID]=[]
 for body:StaticBody3D in homes.find_children("*","StaticBody3D",true,false):own.append(body.get_rid())
 var original:Node3D=ship.find_child("D04StarboardForwardNorthReceiving",true,false)
 for g in p.guard_preimages:record("bounded_guard_replaced_"+g.name,homes.find_child(g.name,true,false)==null)
 for pre in p.north_end_guard_preimages:record("north_street_joint_open_"+pre.name,original.find_child(pre.name,true,false)==null)
 var bearings:=0
 for frame in p.foundation_preimages:
  var at:=vec(frame.chosen.foot)
  for dx in [-.135,.135]:
   for dz in [-.135,.135]:
    var q:=PhysicsRayQueryParameters3D.create(at+Vector3(dx,.03,dz),at+Vector3(dx,-.03,dz));q.exclude=own;var h:=space.intersect_ray(q);record("actual_retained_bearing_"+str(bearings),not h.is_empty()and str(h.collider.get_parent().get_path())==str(frame.chosen.bearing_source_node)and absf(h.position.y-at.y)<.002);bearings+=1
 for at in [Vector3(5,16.5,-405.2),Vector3(20,16.5,-405.2),Vector3(44,16.5,-405.2),Vector3(44,16.5,-440),Vector3(44,16.5,-426),Vector3(44,16.5,-412),Vector3(44,16.5,-400),Vector3(44,16.5,-382),Vector3(44,16.5,-369.9),Vector3(44,16.5,-350),Vector3(44,16.5,-335),Vector3(54,16.5,-369.9)]:
  var h:=ray(space,at+Vector3.UP*.03,corrected_outlook_at-Vector3.UP*.03);record("receiving_floor_"+str(at),not h.is_empty()and homes.is_ancestor_of(h.collider)and absf(h.position.y-16.5)<.002);record("receiving_capsule_"+str(at),capsule_clear(space,at))
 var bench:Node3D=homes.find_child("D04SFP_SouthArrivalBench",true,false);record("original_bench_r002_rigid",bench!=null and bench.scale.is_equal_approx(Vector3.ONE)and bench.global_position.distance_to(vec(p.receiving_bindings[0].position))<.00006)
 if bench!=null:
  var excluded:Array[RID]=[]
  for body:StaticBody3D in bench.find_children("*","StaticBody3D",true,false):excluded.append(body.get_rid())
  for mesh:MeshInstance3D in bench.find_children("*","MeshInstance3D",true,false):
   var b:=bounds(mesh)
   if absf(b.position.y-16.5)>.003:continue
   for x in [b.position.x+.002,b.end.x-.002]:
    for z in [b.position.z+.002,b.end.z-.002]:
     var q:=PhysicsRayQueryParameters3D.create(Vector3(x,16.53,z),Vector3(x,16.47,z));q.exclude=excluded;var h:=space.intersect_ray(q);record("bench_native_bearing_"+str(mesh.name)+"_"+str(x)+"_"+str(z),not h.is_empty()and homes.is_ancestor_of(h.collider)and absf(h.position.y-16.5)<.002)
 # Exact shrunk rectangular receiving-member checks against the retained ship; own joints are excluded, other original geometry remains active.
 var baseline_conflicts:Array=[]
 for part in p.receiving_parts:
  if part.category in ["floor","roof"]or removed.has(part.name):continue
  var mesh:MeshInstance3D=homes.find_child(str(part.name).replace(".","_"),true,false);var b:=bounds(mesh);var sh:=BoxShape3D.new();sh.size=(b.size-Vector3.ONE*.006).max(b.size*.5);sh.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=sh;q.transform=Transform3D(Basis.IDENTITY,b.get_center());q.exclude=own;var hits:=space.intersect_shape(q,32);record("receiving_baseline_clear_"+part.name,hits.is_empty())
  for h in hits:baseline_conflicts.append({"part":part.name,"owner":str(h.collider.get_path())})
 for at in [Vector3(35.8,16.5,-405.2),Vector3(37,16.5,-405.2),Vector3(38.2,16.5,-405.2)]:record("bench_clear_arrival_stance_"+str(at),capsule_clear(space,at))
 var staff:Node3D=ship.find_child("ForwardStaffLift",true,false);record("forward_D04_D07_blank",staff.deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 var result={"status":"PASS"if errors.is_empty()else"FAIL","corrective_checks":checks.size(),"prior_unchanged_successful_checks":3729,"prior_receipt_sha256":inputs.prior_receipt_sha256,"errors":errors,"model_pins":p.model_pins,"southern_homes":10,"reserved_rests":12,"private_courts":6,"owned_parts":allparts.size(),"original_fixture_meshes_in_allocation":previous.original_fixture_meshes_in_allocation,"all_house_allocations":20,"all_house_reserved_rests":25,"remaining_native_interiors":0,"full_commons_unbuilt":true,"dedicated_service_connections_unfinished":true,"foundation_bearing_corners":bearings,"receiving_baseline_conflicts":baseline_conflicts,"receiving_floor_m2":p.receiving_floor_m2,"primary_engineering_provider_privacy_occupancy_save_biology_final_accepted":false,"production_active":p.active}
 FileAccess.open("res://artifacts/d04_starboard_south_package_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"corrective_checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
