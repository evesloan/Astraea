extends "res://tests/validate_d04_commons_receiving_routes.gd"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state
 var route:Array=[Vector3(-66.1,16.5,-361.8),Vector3(-63.8,16.5,-361.8),Vector3(-63.8,16.5,-369.5),Vector3(-44,16.5,-369.5),Vector3(-44,16.5,-405.2),Vector3(-2.8,16.5,-405.2),Vector3(-2.8,16.5,-283),Vector3(-5.5,16.5,-283),Vector3(-5.5,16.5,-253),Vector3(-2.8,16.5,-253),Vector3(-2.8,16.5,-111),Vector3(-5.5,16.5,-111),Vector3(-5.5,16.5,-106),Vector3(-3.8,16.5,-106)]
 var results:Array=[];var owners:Dictionary={};var bad:Array=[];var samples:=0;var blocks:Dictionary={}
 var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/cleaning_cart_contacts.json"))
 for i in range(route.size()-1):
  var a:Vector3=route[i];var b:Vector3=route[i+1];var delta:=b-a;var yaw:=atan2(-delta.x,-delta.z);var failures:Array=[];var n:=int(ceil(delta.length()/.25))
  for k in range(n+1):
   var at:Vector3=a.lerp(b,float(k)/n);var operator:=at+Basis(Vector3.UP,yaw)*Vector3(0,0,1.62);var reasons:Array=[]
   if not cart_clear(space,at,yaw):
    reasons.append("cart_contact")
    var pose:=Transform3D(Basis(Vector3.UP,yaw),at+Vector3.UP*.005)
    for item in d.boxes:
     var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=vec(item.size);shape.margin=.001;q.shape=shape;q.transform=pose*Transform3D(Basis.IDENTITY,vec(item.center))
     for hit in space.intersect_shape(q,32):
      var node:Node3D=hit.collider;var parent:Node3D=node.get_parent();var bounds:Variant=str(parent.get_aabb())if parent is MeshInstance3D else "not_mesh";blocks[str(node.get_path())]={"parent_world_transform":str(parent.global_transform),"local_mesh_aabb":bounds,"first_cart_pose":str(at),"box":item}

   if not capsule_clear(space,operator):reasons.append("operator_contact")
   var pts:Array=[operator]
   for w in d.wheel_contacts:pts.append(at+Basis(Vector3.UP,yaw)*Vector3(w.center[0],0,w.center[2]))
   for pt in pts:
    var h:=ray(space,pt+Vector3.UP*.04,pt-Vector3.UP*.06)
    if h.is_empty()or absf(h.position.y-at.y)>.002:reasons.append("floor_bearing")
    else:owners[str(h.collider.get_path())]=true
   samples+=1
   if not reasons.is_empty():failures.append({"at":str(at),"reasons":reasons})
  results.append({"leg":i,"a":str(a),"b":str(b),"samples":n+1,"failed_samples":failures.size(),"first_failures":failures.slice(0,3)})
  if not failures.is_empty():bad.append(i)
 var result={"status":"PASS_STATIC_LINES_ONLY"if bad.is_empty()else"FAIL_STATIC_LINES","route":route.map(func(p):return [p.x,p.y,p.z]),"samples":samples,"bad_legs":bad,"legs":results,"actual_floor_owners":owners.keys(),"blocked_collision_owners":blocks,"turns_boarding_vertical_accepted":false,"shared_public_route":true,"segregation_accepted":false}
 FileAccess.open("res://artifacts/d04_commons_vertical_route_probe002.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"samples":samples,"bad_legs":bad,"legs":results}));quit()
