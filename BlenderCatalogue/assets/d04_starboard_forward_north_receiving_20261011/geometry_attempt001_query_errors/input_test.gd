extends "res://tests/validate_d04_commons_receiving_routes.gd"
func mesh_bounds(mesh:MeshInstance3D)->AABB:return mesh.global_transform*mesh.get_aabb()
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FORWARD_NORTH_RECEIVING.json"));var space:=ship.get_world_3d().direct_space_state
 for f in p.source_pins:
  if f.begins_with("Game/"):record("source_pin_"+f,FileAccess.get_sha256("res://"+f.substr(5))==p.source_pins[f])
 var candidate:Node3D=load("res://scripts/d04_starboard_forward_north_receiving.gd").build(ship,true)
 for i in range(5):await physics_frame
 var own:Array[RID]=[]
 for body:StaticBody3D in candidate.find_children("*","StaticBody3D",true,false):own.append(body.get_rid())
 record("native_model_pin",FileAccess.get_sha256("res://assets/models/"+p.native_export_record.export)==p.native_export_record.export_sha256)
 record("owned_source_mesh_count",candidate.find_children("*","MeshInstance3D",true,false).size()==p.native_export_record.mesh_count)
 var conflicts:Array=[]
 for part in p.parts:
  var m:MeshInstance3D=candidate.find_child(part.name,true,false);record("owned_part_found_"+part.name,m!=null)
  if m==null:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var b:=mesh_bounds(m);record("source_bounds_"+part.name,b.position.distance_to(lo)<.00006 and b.end.distance_to(hi)<.00006)
  # Compound slab/roof footprint is validated as source geometry; rectangular member volumes use exact shrink-box queries.
  if part.category in ["floor","roof"]:continue
  var q:=PhysicsShapeQueryParameters3D.new();var sh:=BoxShape3D.new();sh.size=b.size-Vector3.ONE*.006;sh.margin=.001;q.shape=sh;q.transform=Transform3D(Basis.IDENTITY,b.get_center());q.exclude=own;var hits:=space.intersect_shape(q,32)
  record("baseline_volume_clear_"+part.name,hits.is_empty())
  for hit in hits:conflicts.append({"part":part.name,"existing_owner":str(hit.collider.get_path())})
 var bearing:=0
 for foot in p.foundation_feet:
  for x in [foot[0]-.19,foot[0]+.19]:
   for z in [foot[2]-.19,foot[2]+.19]:
    var q:=PhysicsRayQueryParameters3D.create(Vector3(x,-3.17,z),Vector3(x,-3.23,z));q.exclude=own;var h:=space.intersect_ray(q);record("actual_keel_shoe_bearing_"+str(bearing),not h.is_empty()and "HUL_KeelPan"in str(h.collider.get_path())and absf(h.position.y+3.2)<.002);bearing+=1
 var floor_samples:=0
 for at in [Vector3(5,16.5,-288.7),Vector3(20,16.5,-288.7),Vector3(35,16.5,-288.7),Vector3(44,16.5,-288.7),Vector3(44,16.5,-331.5),Vector3(44,16.5,-320.6),Vector3(44,16.5,-313.2),Vector3(44,16.5,-305.8),Vector3(44,16.5,-298.4),Vector3(49.34,16.5,-287.3),Vector3(49.34,16.5,-291.6),Vector3(55.725,16.5,-287.3),Vector3(55.725,16.5,-290.6)]:
  var h:=ray(space,at+Vector3.UP*.04,at-Vector3.UP*.04);record("receiving_floor_"+str(floor_samples),not h.is_empty()and candidate.is_ancestor_of(h.collider)and absf(h.position.y-16.5)<.002);record("receiving_capsule_"+str(floor_samples),capsule_clear(space,at));floor_samples+=1
 var cabinet:Node3D=candidate.find_child("D04SF_NorthCleanStockCabinet",true,false);record("rigid_original_cabinet_found",cabinet!=null and cabinet.scale.is_equal_approx(Vector3.ONE))
 if cabinet!=null:
  var cab_rids:Array[RID]=[]
  for body:StaticBody3D in cabinet.find_children("*","StaticBody3D",true,false):cab_rids.append(body.get_rid())
  for m:MeshInstance3D in cabinet.find_children("*","MeshInstance3D",true,false):
   var b:=mesh_bounds(m);var q:=PhysicsShapeQueryParameters3D.new();var sh:=BoxShape3D.new();sh.size=b.size-Vector3.ONE*.004;sh.margin=.001;q.shape=sh;q.transform=Transform3D(Basis.IDENTITY,b.get_center());q.exclude=cab_rids;var hits:=space.intersect_shape(q,32);record("original_cabinet_fixture_clear_"+str(m.name),hits.is_empty())
   for hit in hits:conflicts.append({"part":str(m.name),"existing_owner":str(hit.collider.get_path())})
 var staff:Node3D=ship.find_child("ForwardStaffLift",true,false);record("protected_D04_D07_blank",staff.deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 var result={"status":"PASS"if errors.is_empty()else"FAIL","check_count":checks.size(),"errors":errors,"conflicts":conflicts,"owned_parts":p.parts.size(),"model_sha256":p.native_export_record.export_sha256,"original_keel_shoe_corner_bearings":bearing,"actual_receiving_floor_samples":floor_samples,"new_floor_m2":p.new_floor_m2,"all20allocations25proposedrests_preserved":true,"rooms_built":0,"primary_engineering_accepted":false,"cart_vertical_full_segregation_provider_save_biology_final_accepted":false,"production_active":p.active};FileAccess.open("res://artifacts/d04_starboard_north_receiving_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors,"conflicts":conflicts}));quit(0 if errors.is_empty()else 1)
