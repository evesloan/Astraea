extends "res://tests/validate_d04_commons_receiving_routes.gd"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_NEIGHBORHOOD.json"));var space:=ship.get_world_3d().direct_space_state;var district:Node3D=load("res://scripts/d04_port_central_neighborhood.gd").build(ship,true)
 for i in range(5):await physics_frame
 for f in p.model_pins:record("model_pin_"+f,FileAccess.get_sha256("res://assets/models/"+f)==p.model_pins[f])
 for f in p.source_pins:record("source_pin_"+f,FileAccess.get_sha256("/workspace/astraea-recovered-532087b9-20261010T083844Z/"+f)==p.source_pins[f])
 var own:Array[RID]=[]
 for body:StaticBody3D in district.find_children("*","StaticBody3D",true,false):own.append(body.get_rid())
 var parts:Array=[]
 for group in p.assemblies.values():parts.append_array(group)
 for r in p.rooms:parts.append_array(r.parts)
 var conflicts:Array=[];var triangles:=0
 for part in parts:
  var name:String=str(part.name).replace(".","_");var mesh:MeshInstance3D=district.find_child(name,true,false);record("owned_mesh_"+name,mesh!=null)
  if mesh==null:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var b:AABB=mesh.global_transform*mesh.get_aabb();record("owned_bounds_"+name,b.position.distance_to(lo)<.0001 and b.end.distance_to(hi)<.0001)
  if not part.runtime_collision:continue
  if part.category in ["floor","court_floor","staff_floor","roof","staff_roof"]:
   for face in part.faces:
    if face.size()!=3:continue
    var is_top:=true;var centroid:=Vector3.ZERO
    for index in face:is_top=is_top and absf(part.verts[index][1]-hi.y)<.00001;centroid+=vec(part.verts[index])/3
    if not is_top:continue
    var points:=PackedVector3Array()
    for index in face:
     var v:=vec(part.verts[index]);v+=(centroid-v).normalized()*.003;points.append(Vector3(v.x,lo.y+.003,v.z));points.append(Vector3(v.x,hi.y-.003,v.z))
    var sh:=ConvexPolygonShape3D.new();sh.points=points;sh.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=sh;q.exclude=own;var hits:=space.intersect_shape(q,32);record("plate_triangle_"+str(triangles),hits.is_empty());triangles+=1
    for h in hits:conflicts.append({"part":name,"owner":str(h.collider.get_parent().get_path())})
  elif part.verts.size()==8:
   var q:=PhysicsShapeQueryParameters3D.new();q.exclude=own
   if part.category=="bearing_toe"and hi.y-lo.y>.081:
    var sh:=ConvexPolygonShape3D.new();var points:=PackedVector3Array()
    for v in part.verts:points.append(b.get_center()+(vec(v)-b.get_center())*.95)
    sh.points=points;sh.margin=.001;q.shape=sh
   else:
    var sh:=BoxShape3D.new();sh.size=(b.size-Vector3.ONE*.006).max(b.size*.5);sh.margin=.001;q.shape=sh;q.transform=Transform3D(Basis.IDENTITY,b.get_center())
   var hits:=space.intersect_shape(q,32);record("member_baseline_clear_"+name,hits.is_empty())
   for h in hits:conflicts.append({"part":name,"owner":str(h.collider.get_parent().get_path())})
 var bearings:=0
 for toe in p.assemblies.CombinedStructure:
  if toe.category!="bearing_toe":continue
  for index in [0,1,4,5]:
   var at:=vec(toe.verts[index]);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.04,at-Vector3.UP*.04);q.exclude=own;var h:=space.intersect_ray(q);record("actual_source_bearing_corner_"+str(bearings),not h.is_empty()and str(h.collider.get_parent().get_path())==toe.source_bearing_preimage.bearing_source_node and absf(h.position.y-at.y)<.003);bearings+=1
 var roof_contacts:=0;var floor_only_excludes:Array[RID]=[];var roof_only_excludes:Array[RID]=[]
 for body:StaticBody3D in district.find_children("*","StaticBody3D",true,false):
  var n:String=str(body.get_parent().name)
  if not n.begins_with("PC_ReceivingFloor")and n!="PCC_CommonsFloor":floor_only_excludes.append(body.get_rid())
  if not n.begins_with("PC_ReceivingRoof")and n!="PCC_CommonsRoof":roof_only_excludes.append(body.get_rid())
 for part in parts:
  if part.category!="roof_pier":continue
  var mesh:MeshInstance3D=district.find_child(str(part.name).replace(".","_"),true,false);var b:AABB=mesh.global_transform*mesh.get_aabb()
  for x in [b.position.x+.008,b.end.x-.008]:
   for z in [b.position.z+.008,b.end.z-.008]:
    var base:=Vector3(x,b.position.y,z);var top:=Vector3(x,b.end.y,z);var q:=PhysicsRayQueryParameters3D.create(base+Vector3.UP*.03,base-Vector3.UP*.03);q.exclude=floor_only_excludes;var h:=space.intersect_ray(q);record("roof_pier_actual_floor_contact_"+str(roof_contacts),not h.is_empty()and district.is_ancestor_of(h.collider)and absf(h.position.y-base.y)<.003)
    q=PhysicsRayQueryParameters3D.create(top-Vector3.UP*.03,top+Vector3.UP*.03);q.exclude=roof_only_excludes;h=space.intersect_ray(q);record("roof_pier_actual_roof_contact_"+str(roof_contacts),not h.is_empty()and district.is_ancestor_of(h.collider)and absf(h.position.y-top.y)<.003);roof_contacts+=1
 var fixture_meshes:=0;var rests:=0
 for r in p.rooms:
  var home:Node3D=district.get_node(r.allocation.proposed_runtime_id);rests+=int(r.allocation.proposed_rest_place_count);record("allocation_identity_"+str(int(r.source_index)),home.get_meta("allocation_sha256")==r.allocation.allocation_sha256 and home.get_meta("rest_slot_ids")==r.allocation.proposed_rest_slot_ids and not home.get_meta("species_ready"))
  for binding in r.components:
   var node:Node3D=home.find_child("PC"+str(int(r.source_index))+"_"+str(binding.name),true,false);record("rigid_fixture_"+str(int(r.source_index))+"_"+binding.name,node!=null and node.scale.is_equal_approx(Vector3.ONE)and node.global_position.distance_to(vec(binding.position))<.0001)
  for mesh:MeshInstance3D in home.find_children("*","MeshInstance3D",true,false):
   var b:AABB=mesh.global_transform*mesh.get_aabb()
   if str(mesh.name).begins_with("PC"+str(int(r.source_index))+"_")and not r.parts.any(func(a):return str(a.name).replace(".","_")==str(mesh.name)):
    record("fixture_in_allocation_"+str(int(r.source_index))+"_"+str(mesh.name),b.position.x>=float(r.allocation.allocation_x[0])-.0001 and b.end.x<=float(r.allocation.allocation_x[1])+.0001 and b.position.z>=float(r.allocation.allocation_z[0])-.0001 and b.end.z<=float(r.allocation.allocation_z[1])+.0001);fixture_meshes+=1
  for key in ["approach_world","outlook_world"]:
   if not r.has(key):continue
   var at:=vec(r[key]);var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);record(key+"_floor_"+str(int(r.source_index)),not h.is_empty()and district.is_ancestor_of(h.collider)and absf(h.position.y-16.5)<.003);record(key+"_capsule_"+str(int(r.source_index)),capsule_clear(space,at))
  var door:Node3D=home.get_node("HomeEntry");record("closed_entry_"+str(int(r.source_index)),not capsule_clear(space,vec(r.entry.origin)));door.interact(null)
 for i in range(100):await physics_frame
 for r in p.rooms:record("open_entry_"+str(int(r.source_index)),capsule_clear(space,vec(r.entry.origin)));district.get_node(r.allocation.proposed_runtime_id+"/HomeEntry").interact(null)
 for i in range(100):await physics_frame
 for r in p.rooms:record("door_roundtrip_"+str(int(r.source_index)),district.get_node(r.allocation.proposed_runtime_id+"/HomeEntry").open_fraction<.001)
 var bindings:Array=[]
 for label in p.bindings:
  for binding in p.bindings[label]:bindings.append({"prefix":"PCC_"if label=="CO"else"PC"+label+"_","binding":binding})
 var support_contacts:=0
 for item in bindings:
  var binding:Dictionary=item.binding;var node:Node3D=district.find_child(item.prefix+binding.name,true,false);record("common_rigid_"+item.prefix+binding.name,node!=null and node.scale.is_equal_approx(Vector3.ONE)and node.global_position.distance_to(vec(binding.position))<.0001)
  if node==null or binding.catalogue_id=="AST-CIR-001":continue
  var excluded:Array[RID]=[]
  for body:StaticBody3D in node.find_children("*","StaticBody3D",true,false):excluded.append(body.get_rid())
  for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
   var b:AABB=mesh.global_transform*mesh.get_aabb()
   if absf(b.position.y-float(binding.position[1]))>.003:continue
   for x in [b.position.x+.002,b.end.x-.002]:
    for z in [b.position.z+.002,b.end.z-.002]:
     var at:=Vector3(x,binding.position[1],z);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03);q.exclude=excluded;var h:=space.intersect_ray(q);record("commons_fitting_supported_"+str(support_contacts),not h.is_empty()and district.is_ancestor_of(h.collider)and absf(h.position.y-at.y)<.003);support_contacts+=1
 for at in [Vector3(-50.9,16.5,-32),Vector3(-50.9,16.5,0),Vector3(-50.9,16.5,32),Vector3(-70,16.5,-32),Vector3(-70,16.5,32),Vector3(-84,16.5,-42),Vector3(-84,16.5,42),Vector3(-84,16.5,0),Vector3(-66,16.5,0),Vector3(-75,16.5,0),Vector3(-90,16.5,7),Vector3(-74.4,16.5,-4.3),Vector3(-71,16.5,-4.3)]:
  var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);record("connected_floor_"+str(at),not h.is_empty()and absf(h.position.y-at.y)<.003);record("connected_capsule_"+str(at),capsule_clear(space,at))
 var staff:Node3D=ship.find_child("ForwardStaffLift",true,false);record("forward_D04_D07_blank",staff.deck_numbers==[1,2,3,8,9,13,14,15,16,17]);record("exact20_25",p.rooms.size()==20 and rests==25)
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"baseline_conflicts":conflicts,"model_pins":p.model_pins,"owned_parts":parts.size(),"plate_triangles":triangles,"actual_source_bearing_corners":bearings,"original_fixture_meshes_in_allocations":fixture_meshes,"commons_fitting_support_contacts":support_contacts,"actual_roof_pier_four_corner_contacts":roof_contacts,"retained_outlook_metadata_count":p.rooms.filter(func(r):return r.has("outlook_world")).size(),"outlook_source_metadata_missing_indices":p.rooms.filter(func(r):return not r.has("outlook_world")).map(func(r):return int(r.source_index)),"physical_home_proposals":20,"original_reserved_rests":rests,"production_active":p.active,"dedicated_network_cart_vertical_gameplay_engineering_final_accepted":false};FileAccess.open("res://artifacts/d04_port_central_neighborhood_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
