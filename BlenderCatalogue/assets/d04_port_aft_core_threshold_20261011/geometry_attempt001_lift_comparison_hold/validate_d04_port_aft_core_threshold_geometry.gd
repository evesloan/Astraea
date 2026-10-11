extends "res://tests/validate_d04_commons_receiving_routes.gd"
func bounds(part:Dictionary)->AABB:
 var lo:=Vector3(INF,INF,INF);var hi:=-lo
 for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
 return AABB(lo,hi-lo)
func owner(hit:Dictionary)->String:return str(hit.collider.get_path())if not hit.is_empty()else "NO_CONTACT"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_AFT_CORE_THRESHOLD.json"));var space:=ship.get_world_3d().direct_space_state
 for f in p.source_pins:record("source_pin_"+f,FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/"+f)==p.source_pins[f])
 for x in [-7.99,-7.9]:
  var h:=ray(space,Vector3(x,16.53,288.7),Vector3(x,16.47,288.7));record("baseline_gap_"+str(x),h.is_empty())
 var floor_at:Array=[Vector3(-8.3,16.5,288.7),Vector3(-7.5,16.5,288.7)];var before:Array=[]
 for at in floor_at:
  var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);before.append(owner(h));record("original_floor_"+str(at.x),not h.is_empty()and absf(h.position.y-16.5)<.002)
 var threshold:Node3D=load("res://scripts/d04_port_aft_core_threshold.gd").build(ship,true)
 if threshold==null:push_error("Candidate build failed");quit(1);return
 for i in range(5):await physics_frame
 var core:Node3D=ship.get_node("ShipSpace/Districts/"+p.core_root);var enclosure:Node3D=core.get_node("PrimaryCoreEnclosure");var own:Array[RID]=[]
 for node in [threshold,enclosure]:
  for body:StaticBody3D in node.find_children("*","StaticBody3D",true,false):own.append(body.get_rid())
 for f in p.model_pins:record("model_pin_"+f,FileAccess.get_sha256("res://assets/models/"+f)==p.model_pins[f])
 var audit:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_aft_core_threshold_20261011/EXACT_NATIVE_MESH_AUDIT.json"));var preserved:=0
 for name in audit.meshes:
  if name in p.exact_removed_source_meshes:continue
  var mesh:MeshInstance3D=enclosure.find_child(str(name).replace(".","_"),true,false);record("unchanged_mesh_exists_"+name,mesh!=null)
  if mesh==null:continue
  var b:AABB=mesh.global_transform*mesh.get_aabb();var old:Dictionary=audit.meshes[name];record("unchanged_mesh_bounds_"+name,b.position.distance_to(vec(old.world_min))<.0002 and b.end.distance_to(vec(old.world_max))<.0002);preserved+=1
 record("837_original_meshes_preserved",preserved==837)
 for part in p.parts:
  var parent:Node3D=enclosure if part.group=="core"else threshold;var mesh:MeshInstance3D=parent.find_child(part.name,true,false);record("owned_mesh_"+part.name,mesh!=null)
  if mesh==null:continue
  var expected:=bounds(part);var actual:AABB=mesh.global_transform*mesh.get_aabb();record("owned_bounds_"+part.name,actual.position.distance_to(expected.position)<.0002 and actual.end.distance_to(expected.end)<.0002)
 var bearings:Array=[]
 for beam in p.beam_bearings:
  for end in beam:
   for dz in [-.095,.095]:
    var at:=vec(end)+Vector3(0,0,dz);var q:=PhysicsRayQueryParameters3D.create(at-Vector3.UP*.025,at+Vector3.UP*.025);q.exclude=own;q.hit_back_faces=true;var h:=space.intersect_ray(q);var ok:bool=not h.is_empty()and absf(h.position.y-16.26)<.002 and ("PA_ReceivingFloor"in owner(h)or"D04_aft_midship_public_core_floor"in owner(h));record("actual_two_slab_underside_bearing_"+str(bearings.size()),ok);bearings.append({"at":str(at),"owner":owner(h),"accepted":ok})
 var frame_contacts:Array=[]
 for z in [287.03,290.37]:
  for y in [16.065,16.255]:
   for dz in [-.095,.095]:
    var at:=Vector3(-8.36,y,z+dz);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.RIGHT*.015,at-Vector3.RIGHT*.015);q.exclude=own;var h:=space.intersect_ray(q);var ok:bool=not h.is_empty()and "PANR_D04SF_ArrivalCross_8_5"in owner(h);record("actual_existing_frame_splice_"+str(frame_contacts.size()),ok);frame_contacts.append({"at":str(at),"owner":owner(h),"accepted":ok})
 var jamb_contacts:=0
 for part in p.parts:
  if not part.name.begins_with("D04PA_JambFoot_"):continue
  var b:=bounds(part)
  for x in [b.position.x+.005,b.end.x-.005]:
   for z in [b.position.z+.005,b.end.z-.005]:
    var at:=Vector3(x,16.5,z);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.025,at-Vector3.UP*.025);q.exclude=own;var h:=space.intersect_ray(q);record("actual_jamb_floor_corner_"+str(jamb_contacts),not h.is_empty()and absf(h.position.y-16.5)<.002 and ("PA_ReceivingFloor"in owner(h)or"D04_aft_midship_public_core_floor"in owner(h)));jamb_contacts+=1
 for at in floor_at:
  var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);record("original_floor_retained_"+str(at.x),owner(h)==before[floor_at.find(at)])
 var route_samples:=0
 for z in [287.5,288.7,289.9]:
  for x in [-9,-8.3,-8.01,-7.99,-7.9,-7.81,-7.79,-7.5,-6,-5.4]:
   var at:=Vector3(x,16.5,z);var h:=ray(space,at+Vector3.UP*.025,at-Vector3.UP*.025);record("route_floor_"+str(route_samples),not h.is_empty()and absf(h.position.y-16.5)<.002 and h.normal.y>.9)
   var shape:=CapsuleShape3D.new();shape.radius=.33;shape.height=1.8;shape.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.93);record("route_capsule_"+str(route_samples),space.intersect_shape(q,32).is_empty()and capsule_clear(space,at));route_samples+=1
 # Opening is genuinely3.2m high; upper original wall remains sealed.
 for z in [287.15,288.7,290.25]:
  record("clear_aperture_headroom_"+str(z),ray(space,Vector3(-8.2,19.65,z),Vector3(-7.4,19.65,z)).is_empty())
  record("retained_upper_wall_"+str(z),not ray(space,Vector3(-8.3,20.3,z),Vector3(-7.4,20.3,z)).is_empty())
 for z in [286.8,290.6]:record("closed_guard_returns_"+str(z),not ray(space,Vector3(-8.2,17.2,z),Vector3(-7.7,17.2,z)).is_empty())
 var datum:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AFT_MIDSHIP_PUBLIC_CORE.json"));record("original_core_identity",core.get_meta("persistent_id")==datum.persistent_id)
 var lift:Node3D=core.get_node("AftMidshipPublicLift");record("original_lift_stops_and_heights",lift.deck_numbers==datum.deck_numbers and lift.floor_heights==datum.floor_y and str(lift.persistent_id)=="aft_midship_public_core_lift_001")
 record("original_stair_count",core.find_children("PrimarySwitchback_D*","Node3D",false,false).size()==16)
 record("original_staff_stops_blank",ship.find_child("ForwardStaffLift",true,false).deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"model_pins":p.model_pins,"unchanged_original_native_meshes":preserved,"actual_two_slab_underside_bearings":bearings,"actual_existing_frame_splice_contacts":frame_contacts,"jamb_floor_corners":jamb_contacts,"route_floor_capsule_samples":route_samples,"new_gap_floor_m2":p.new_floor_m2,"engineering_load_final_graphics_accepted":false};FileAccess.open("res://artifacts/d04_port_aft_core_threshold_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
