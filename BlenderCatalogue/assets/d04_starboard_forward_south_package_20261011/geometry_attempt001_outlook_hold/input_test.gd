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
 var allparts:Array=p.commons_parts+p.guard_successor_parts
 var removed:Dictionary={}
 for pre in p.guard_preimages:removed[pre.name]=true
 for part in p.receiving_parts:
  if not removed.has(part.name):allparts.append(part)
 var own:Array[RID]=[]
 for body:StaticBody3D in homes.find_children("*","StaticBody3D",true,false):own.append(body.get_rid())
 var contacts:=0;var fixtures:=0
 for r in p.rooms:
  allparts+=r.parts
  var home:Node3D=homes.get_node(r.allocation.proposed_runtime_id);var idx:=str(int(r.source_index));record("reservation_"+idx,home.get_meta("rest_slot_ids")==r.allocation.proposed_rest_slot_ids and not home.get_meta("species_ready"))
  var door:Node3D=home.get_node("HomeEntry");record("closed_entry_"+idx,not door.desired_open and door.open_fraction<.001)
  var side:float=1 if r.court_side=="east"else -1;var front:float=r.allocation.allocation_x[0]if side>0 else r.allocation.allocation_x[1];var foyer:=Vector3(front+side*.72,16.5,r.entry.origin[2])
  for at in [foyer,vec(r.approach_world),vec(r.outlook_world)]:
   var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);record("home_floor_"+idx+"_"+str(contacts),not h.is_empty()and home.is_ancestor_of(h.collider)and absf(h.position.y-16.5)<.002);record("home_capsule_"+idx+"_"+str(contacts),capsule_clear(space,at));contacts+=1
  for a in r.get("rest_approach_worlds",[]):record("rest_dry_approach_"+a.rest_slot_id,capsule_clear(space,vec(a.position)))
  for c in r.components:
   var node:Node3D=home.find_child("D04SH"+idx+"_"+c.name,true,false);record("rigid_original_"+idx+"_"+c.name,node!=null and node.scale.is_equal_approx(Vector3.ONE)and node.global_position.distance_to(vec(c.position))<.00006 and absf(wrapf(node.global_rotation.y-c.yaw,-PI,PI))<.00006)
   if node==null:continue
   for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
    var b:=bounds(mesh);record("fixture_in_own_allocation_"+idx+"_"+str(mesh.name),b.position.x>=r.allocation.allocation_x[0]-.001 and b.end.x<=r.allocation.allocation_x[1]+.001 and b.position.z>=r.allocation.allocation_z[0]-.001 and b.end.z<=r.allocation.allocation_z[1]+.001);fixtures+=1
  for component in r.components:
   if component.name in ["Toilet","Shower"]:
    var h:=ray(space,foyer+Vector3.UP*1.65,vec(component.position)+Vector3.UP*(.55 if component.name=="Toilet"else 1.1));record("privacy_screen_"+idx+"_"+component.name,not h.is_empty()and "Bath"in str(h.collider.get_parent().name))
  var h:=ray(space,vec(r.outlook_world)+Vector3.UP*1.65,vec(r.outlook_world)+Vector3(side*8,1.65,0));record("private_court_glass_"+idx,not h.is_empty()and "GardenGlass"in str(h.collider.get_parent().name))
  door.interact(null)
  for i in range(100):
   await physics_frame
   if i in [0,20,40,60,80,99]:
    for leaf in door.leaves:
     var shape:CollisionShape3D=leaf.get_node("LeafContact");var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape.shape;q.transform=shape.global_transform;var foreign:Array=[]
     for hit in space.intersect_shape(q,32):
      if not door.is_ancestor_of(hit.collider):foreign.append(str(hit.collider.get_path()))
     record("door_sweep_"+idx+"_"+str(i)+"_"+str(leaf.name),foreign.is_empty())
     if not foreign.is_empty():print("FOREIGN_LEAF ",idx," ",foreign)
  record("door_open_"+idx,door.open_fraction>.999)
  door.interact(null)
  for i in range(100):await physics_frame
  record("door_roundtrip_"+idx,door.open_fraction<.001)
 for part in allparts:
  var mesh:MeshInstance3D=homes.find_child(str(part.name).replace(".","_"),true,false);record("owned_part_found_"+part.name,mesh!=null)
  if mesh==null:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var b:=bounds(mesh);record("owned_part_source_bounds_"+part.name,b.position.distance_to(lo)<.00006 and b.end.distance_to(hi)<.00006)
 for sample in p.rest_reference_samples:
  var at:=vec(sample.position)+Basis(Vector3.UP,sample.yaw)*vec(sample.local_reference.position);var h:=ray(space,at+Vector3.UP*.035,at-Vector3.UP*.035)
  record("source_rest_contact_"+str(sample.room)+"_"+sample.binding+"_"+sample.local_reference.name,not h.is_empty()and homes.is_ancestor_of(h.collider)and str(h.collider.get_parent().name)==str(sample.source_contact_node).replace(".","_")and absf(h.position.y-sample.source_contact_surface_y)<.0002)
 for i in range(p.courts.size()):
  var points:Array=p.courts[i].geometry.coordinates[0];var center:=Vector3.ZERO
  for j in range(points.size()-1):center+=Vector3(points[j][0],16.5,points[j][1])
  center/=points.size()-1
  for dz in [-1,0,1]:
   var at:=center+Vector3(0,0,dz);var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);record("court_floor_"+str(i)+"_"+str(dz),not h.is_empty()and homes.is_ancestor_of(h.collider)and absf(h.position.y-16.5)<.002)
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
  var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);record("receiving_floor_"+str(at),not h.is_empty()and homes.is_ancestor_of(h.collider)and absf(h.position.y-16.5)<.002);record("receiving_capsule_"+str(at),capsule_clear(space,at))
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
 var staff:Node3D=ship.find_child("ForwardStaffLift",true,false);record("forward_D04_D07_blank",staff.deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"model_pins":p.model_pins,"southern_homes":10,"reserved_rests":12,"private_courts":6,"owned_parts":allparts.size(),"original_fixture_meshes_in_allocation":fixtures,"all_house_allocations":20,"all_house_reserved_rests":25,"remaining_native_interiors":0,"full_commons_unbuilt":true,"dedicated_service_connections_unfinished":true,"foundation_bearing_corners":bearings,"receiving_baseline_conflicts":baseline_conflicts,"receiving_floor_m2":p.receiving_floor_m2,"primary_engineering_provider_privacy_occupancy_save_biology_final_accepted":false,"production_active":p.active}
 FileAccess.open("res://artifacts/d04_starboard_south_package_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
