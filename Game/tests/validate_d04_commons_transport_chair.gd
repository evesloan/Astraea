extends "res://tests/validate_d04_commons_receiving_routes.gd"
func bounds(mesh:MeshInstance3D)->AABB:return mesh.global_transform*mesh.get_aabb()
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_TRANSPORT_ROUTE.json"));var c:Dictionary=p.chair_revision;var chair:Node3D=ship.find_child(c.node,true,false)
 record("original_source_model_pin",FileAccess.get_sha256("res://assets/models/D04_PORT_FORWARD_HOMES_RECEIVING_r001.glb")==p.original_homes_model_sha256)
 record("revised_native_export_pin",FileAccess.get_sha256("res://assets/models/"+p.revised_chair_model_file)==p.revised_chair_model_sha256)
 record("exact_original_binding",chair!=null and chair.global_position.distance_to(vec(c.preimage_position))<.00005 and absf(wrapf(chair.global_rotation.y-c.preimage_yaw,-PI,PI))<.00005)
 if not errors.is_empty():quit(1);return
 var meshes:Array=chair.find_children("*","MeshInstance3D",true,false);var old_ids:Array=[];var own:Array[RID]=[]
 for m:MeshInstance3D in meshes:
  old_ids.append(m.get_instance_id())
  for b:StaticBody3D in m.find_children("*","StaticBody3D",true,false):own.append(b.get_rid())
 record("original_registered_mesh_count",meshes.size()==p.original_chair_mesh_count)
 chair.global_position=vec(c.position);chair.rotation.y=c.yaw
 for i in range(5):await physics_frame
 var candidate:Node3D=load("res://assets/models/"+p.revised_chair_model_file).instantiate();ship.get_node("ShipSpace/Districts").add_child(candidate)
 var fresh:Array=candidate.find_children("*","MeshInstance3D",true,false);var space:=ship.get_world_3d().direct_space_state;var contacts:Array=[];var bearing:=0
 record("native_mesh_count",fresh.size()==meshes.size())
 for i in range(meshes.size()):
  var m:MeshInstance3D=meshes[i];var qmesh:MeshInstance3D=candidate.find_child(m.name,true,false);var b:=bounds(m)
  record("native_world_geometry_"+str(i),qmesh!=null and bounds(qmesh).position.distance_to(b.position)<.00005 and bounds(qmesh).size.distance_to(b.size)<.00005)
  record("original_mesh_identity_"+str(i),m.get_instance_id()==old_ids[i]and m.get_meta("extras",{}).get("source_catalogue_id","")=="AST-FUR-002")
  var sh:=BoxShape3D.new();sh.size=b.size-Vector3.ONE*.003;sh.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=sh;q.transform=Transform3D(Basis.IDENTITY,b.get_center());q.exclude=own
  var hits:=space.intersect_shape(q,32)
  record("fixture_clear_"+str(i),hits.is_empty())
  for hit in hits:contacts.append({"chair_mesh":str(m.name),"collision_owner":str(hit.collider.get_path())})
  if b.position.y<16.502:
   for x in [b.position.x+.003,b.end.x-.003]:
    for z in [b.position.z+.003,b.end.z-.003]:
     var h:=ray(space,Vector3(x,16.52,z),Vector3(x,16.48,z));record("real_original_floor_"+str(bearing),not h.is_empty()and absf(h.position.y-16.5)<.002);bearing+=1
 # Bounded changed-entry pose smoke; long public route and physics operation remain separate.
 var route:Array=p.cart_poses;var poses:=0
 for leg in range(2):
  var a:=vec(route[leg]);var b:=vec(route[leg+1]);var ya:float=route[leg][3];var yb:=ya+wrapf(float(route[leg+1][3])-ya,-PI,PI);var n:=maxi(1,maxi(int(ceil(a.distance_to(b)/.25)),int(ceil(absf(yb-ya)/.1))))
  for k in range(n+1):
   var t:=float(k)/n;var at:=a.lerp(b,t);var yaw:=lerpf(ya,yb,t);var operator:=at+Basis(Vector3.UP,yaw)*Vector3(0,0,1.62)
   record("changed_entry_cart_"+str(poses),cart_clear(space,at,yaw));record("changed_entry_operator_"+str(poses),capsule_clear(space,operator));poses+=1
 record("original_chair_scale",chair.scale.is_equal_approx(Vector3.ONE));record("original_floor_bearing_samples",bearing>=8)
 var result={"status":"PASS"if errors.is_empty()else"FAIL","check_count":checks.size(),"errors":errors,"contacts":contacts,"original_mesh_objects_preserved":meshes.size(),"native_world_meshes_match":fresh.size(),"actual_floor_bearing_samples":bearing,"new_furniture_units_floor":0,"bounded_changed_entry_poses":poses,"candidate_chair_revision":c,"candidate_only":true,"production_active":false}
 FileAccess.open("res://artifacts/d04_commons_transport_chair_sealed_r002.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify(result));quit(0 if errors.is_empty()else 1)
