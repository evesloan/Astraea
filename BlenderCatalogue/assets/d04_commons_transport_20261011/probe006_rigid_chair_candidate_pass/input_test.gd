extends "res://tests/validate_d04_commons_receiving_routes.gd"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state
 var candidate:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_TRANSPORT_ROUTE.json")).chair_revision
 var chair:Node3D=ship.find_child(candidate.node,true,false)
 assert(chair!=null and chair.global_position.distance_to(vec(candidate.preimage_position))<.00005 and absf(wrapf(chair.global_rotation.y-candidate.preimage_yaw,-PI,PI))<.00005)
 chair.global_position=vec(candidate.position);chair.rotation.y=candidate.yaw
 for i in range(5):await physics_frame

 var route:Array=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_TRANSPORT_ROUTE.json")).cart_poses
 var results:Array=[];var owners:Dictionary={};var blocks:Dictionary={};var samples:=0;var bad:Array=[]
 var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
 for i in range(route.size()-1):
  var a:Vector3=vec(route[i]);var b:Vector3=vec(route[i+1]);var ya:float=route[i][3];var yb:float=ya+wrapf(float(route[i+1][3])-ya,-PI,PI);var n:=maxi(1,maxi(int(ceil(a.distance_to(b)/.1)),int(ceil(absf(yb-ya)/.035))));var failures:Array=[]
  for k in range(n+1):
   var t:=float(k)/n;var at:=a.lerp(b,t);var yaw:=lerpf(ya,yb,t);var op:=at+Basis(Vector3.UP,yaw)*Vector3(0,0,1.62);var reasons:Array=[]
   if not cart_clear(space,at,yaw):reasons.append("cart_contact")
   if not capsule_clear(space,op):reasons.append("operator_contact")
   var points:Array=[op]
   for w in d.wheel_contacts:points.append(at+Basis(Vector3.UP,yaw)*Vector3(w.center[0],0,w.center[2]))
   for pt in points:
    var h:=ray(space,pt+Vector3.UP*.04,pt-Vector3.UP*.06)
    if h.is_empty()or absf(h.position.y-at.y)>.002:reasons.append("floor_bearing")
    else:owners[str(h.collider.get_path())]=true
   if not reasons.is_empty():
    failures.append({"at":str(at),"yaw":yaw,"reasons":reasons})
    if "operator_contact"in reasons:
     var q:=PhysicsShapeQueryParameters3D.new();var sh:=CapsuleShape3D.new();sh.radius=.3;sh.height=1.8;q.shape=sh;q.transform=Transform3D(Basis.IDENTITY,op+Vector3.UP*.925)
     for hit in space.intersect_shape(q,32):blocks[str(hit.collider.get_path())]=str(at)
   samples+=1
  results.append({"leg":i,"failed_samples":failures.size(),"samples":n+1,"first_failures":failures.slice(0,3)})
  if not failures.is_empty():bad.append(i)
 var result={"status":"PASS_STATIC_POSE_SWEEPS"if bad.is_empty()else"FAIL_STATIC_POSE_SWEEPS","samples":samples,"five_point_bearing_samples":samples*5,"bad_legs":bad,"legs":results,"operator_collision_owners":blocks,"actual_floor_owners":owners.keys(),"poses":route,"candidate_only_fixture":true,"production_chair_active":false,"dynamic_vertical_accepted":false,"shared_public_route":true,"segregation_accepted":false}
 FileAccess.open("res://artifacts/d04_commons_vertical_route_probe006.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"samples":samples,"bad_legs":bad,"failures":results.filter(func(p):return p.failed_samples>0),"operator_blocks":blocks}));quit()
