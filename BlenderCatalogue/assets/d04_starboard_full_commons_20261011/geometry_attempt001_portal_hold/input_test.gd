extends "res://tests/validate_d04_commons_receiving_routes.gd"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FULL_COMMONS.json"));var space:=ship.get_world_3d().direct_space_state
 var commons:Node3D=load("res://scripts/d04_starboard_full_commons.gd").build(ship,true)
 for i in range(5):await physics_frame
 for f in p.model_pins:record("model_pin_"+f,FileAccess.get_sha256("res://assets/models/"+f)==p.model_pins[f])
 for f in p.source_pins:record("source_pin_"+f,FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/"+f)==p.source_pins[f])
 var own:Array[RID]=[]
 for body:StaticBody3D in commons.find_children("*","StaticBody3D",true,false):own.append(body.get_rid())
 var conflicts:Array=[];var bearings:=0;var contacts:=0
 for part in p.parts:
  var mesh:MeshInstance3D=commons.find_child(str(part.name).replace(".","_"),true,false);record("owned_mesh_"+part.name,mesh!=null)
  if mesh==null:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var b:AABB=mesh.global_transform*mesh.get_aabb();record("owned_bounds_"+part.name,b.position.distance_to(lo)<.00006 and b.end.distance_to(hi)<.00006)
  # Rectangular members are tested using their actual shrunken box; floor/roof polygons are checked by their triangulated footprint offline.
  if part.verts.size()==8 and part.category not in ["floor","staff_floor","roof","staff_roof"]:
   var sh:=BoxShape3D.new();sh.size=(b.size-Vector3.ONE*.006).max(b.size*.5);sh.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=sh;q.transform=Transform3D(Basis.IDENTITY,b.get_center());q.exclude=own;var hits:=space.intersect_shape(q,32);record("baseline_clear_"+part.name,hits.is_empty())
   for h in hits:conflicts.append({"part":part.name,"owner":str(h.collider.get_path())})
 for f in p.support_preimages:
  var at:=vec(f.chosen.foot)
  for dx in [-.135,.135]:
   for dz in [-.135,.135]:
    var q:=PhysicsRayQueryParameters3D.create(at+Vector3(dx,.03,dz),at+Vector3(dx,-.03,dz));q.exclude=own;var h:=space.intersect_ray(q);record("retained_bearing_"+str(bearings),not h.is_empty()and str(h.collider.get_parent().get_path())==str(f.chosen.bearing_source_node)and absf(h.position.y-at.y)<.002);bearings+=1
 for binding in p.rigid_bindings:
  var node:Node3D=commons.find_child("D04SC_"+str(binding.name),true,false);record("rigid_binding_"+binding.name,node!=null and node.scale.is_equal_approx(Vector3.ONE)and node.global_position.distance_to(vec(binding.position))<.00006)
  if node==null or binding.catalogue_id=="AST-CIR-001":continue
  var excluded:Array[RID]=[]
  for body:StaticBody3D in node.find_children("*","StaticBody3D",true,false):excluded.append(body.get_rid())
  for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
   var b:AABB=mesh.global_transform*mesh.get_aabb()
   if absf(b.position.y-float(binding.position[1]))>.003:continue
   for x in [b.position.x+.002,b.end.x-.002]:
    for z in [b.position.z+.002,b.end.z-.002]:
     var at:=Vector3(x,binding.position[1],z);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03);q.exclude=excluded;var h:=space.intersect_ray(q);record("original_fitting_supported_"+str(contacts),not h.is_empty()and commons.is_ancestor_of(h.collider)and absf(h.position.y-at.y)<.002);contacts+=1
 for at in [Vector3(62.4,16.5,-369.5),Vector3(64,16.5,-369.5),Vector3(69,16.5,-369.5),Vector3(72,16.5,-369.5),Vector3(77.7,16.5,-369.5),Vector3(79.1,16.5,-370),Vector3(79.1,16.5,-366),Vector3(79.1,16.5,-360.3),Vector3(81.25,16.5,-360.3),Vector3(71,16.5,-362.8),Vector3(71,16.5,-361),Vector3(75.9,16.5,-361),Vector3(3,12,-381.2),Vector3(8,12,-381.2),Vector3(32,12,-381.2),Vector3(58,12,-381.2),Vector3(61.6,12,-381.2),Vector3(61.6,12,-371.3),Vector3(64.45,12,-371.3),Vector3(64.45,14.25,-381.3),Vector3(67.95,14.25,-381.3),Vector3(67.95,16.5,-372.3),Vector3(67.95,16.5,-371)]:
  var h:=ray(space,at+Vector3.UP*.22,at-Vector3.UP*.08);record("actual_route_floor_"+str(at),not h.is_empty()and absf(h.position.y-at.y)<.22);record("actual_route_capsule_"+str(at),capsule_clear(space,at))
 for at in [Vector3(79.8,18.15,-373.6),Vector3(79.8,18.15,-365)]:
  var h:=ray(space,at,at+Vector3(4,0,0));record("private_planted_glazing_"+str(at),not h.is_empty()and "GardenGlass"in str(h.collider.get_parent().name))
 var original:Node3D=ship.find_child("D04StarboardSouthHomeCandidates",true,false)
 for pre in p.preimages:record("bounded_X63_guard_replaced_"+pre.name,original.find_child(str(pre.name).replace(".","_"),true,false)==null)
 var staff:Node3D=ship.find_child("ForwardStaffLift",true,false);record("protected_D04_D07_blank",staff.deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 record("original20_25_preserved",original.get_meta("total_house_reservation_count")==20 and original.get_meta("capacity_preserved")==25)
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"baseline_conflicts":conflicts,"bearing_corners":bearings,"original_fitting_support_contacts":contacts,"model_pins":p.model_pins,"commons_floor_m2":p.commons_floor_m2,"lower_staff_floor_m2":p.lower_staff_floor_m2,"engineering_full_staff_network_cart_vertical_provider_occupancy_save_biology_final_accepted":false,"active":p.active}
 FileAccess.open("res://artifacts/d04_starboard_full_commons_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
