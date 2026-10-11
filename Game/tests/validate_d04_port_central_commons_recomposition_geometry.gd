extends SceneTree
var checks:=0
var errors:Array=[]
var pose_count:=0
var contacts:Array=[]
func ck(ok:bool,label:String):
 checks+=1
 if not ok:errors.append(label);print("FAIL ",label)
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func visit(gate:Node3D,actor:CharacterBody3D):
 var x:RefCounted=load("res://scripts/d04_court_service_visit.gd").new();x.actor=weakref(actor);x.request_id=&"geometry_explicit_temporary_known_visit";x.court_ids.assign([gate.persistent_id]);x.consent_known=true;x.consent_allowed=true;x.active=true;gate.visit=x
func checked_pose(gate:Node3D,space:PhysicsDirectSpaceState3D,frame:int,phase:String):
 pose_count+=1
 var members:Array=gate.fitting.members;var index:=0
 for contact:CollisionShape3D in gate.leaves[0].find_children("*","CollisionShape3D",true,false):
  var moving:String=str(members[index]);index+=1;var q:=PhysicsShapeQueryParameters3D.new();q.shape=contact.shape;q.transform=contact.global_transform;q.exclude=[gate.leaves[0].get_rid()];var hits=space.intersect_shape(q,64)
  ck(hits.size()<64,"unsaturated exact shape contact query "+str(gate.name))
  var points:PackedVector3Array=contact.shape.points;var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for point in points:lo=lo.min(contact.global_transform*point);hi=hi.max(contact.global_transform*point)
  for hit in hits:
   var fixed:Node=hit.collider.get_parent();var row={"gate":str(gate.name),"phase":phase,"frame":frame,"moving":moving,"moving_lo":[lo.x,lo.y,lo.z],"moving_hi":[hi.x,hi.y,hi.z],"fixed":str(fixed.name),"classification":"UNEXPLAINED_CONTACT"};var accepted:=false
   if fixed is MeshInstance3D:
    var a:AABB=fixed.global_transform*fixed.get_aabb();row.fixed_lo=[a.position.x,a.position.y,a.position.z];row.fixed_hi=[a.end.x,a.end.y,a.end.z];var overlap:Vector3=hi.min(a.end)-lo.max(a.position);row.aabb_overlap=[overlap.x,overlap.y,overlap.z]
    # Only named source bearing/frame contacts qualify. No world/control exemption.
    var own_jamb:bool=moving.ends_with("D04PC_CourtSouth_Leaf")and str(fixed.name)in gate.fitting.control_members and str(fixed.name).ends_with("D04PC_CourtSouth_Jamb_1")
    var hinge_bearing:=false
    var surface_bound:float=2.0*contact.shape.margin+0.0001220703125
    if own_jamb and min(overlap.x,min(overlap.y,overlap.z))<=surface_bound:accepted=true;row.classification="SOURCE_FRAME_SURFACE_CONTACT_WITHIN_MARGIN_AND_FLOAT32_BOUND";row.surface_bound_m=surface_bound
    if hinge_bearing:accepted=true;row.classification="RETAINED_SOURCE_HINGE_BEARING_ON_OWN_FIXED_JAMB"
   contacts.append(row);ck(accepted,"actual moving fitting contact classified "+str(gate.name)+" "+moving+" "+str(fixed.name)+" "+phase+" frame="+str(frame))
   if not accepted:print("CONTACT ",JSON.stringify(row))
func gate_poses(gate:Node3D,actor:CharacterBody3D,space:PhysicsDirectSpaceState3D,private_gate:bool):
 ck(gate.open_fraction==0 and not gate.desired_open,"initial fitting closed "+str(gate.name))
 if private_gate:
  gate.interact(actor);ck(gate.access_refused and not gate.desired_open,"unknown private visit refused "+str(gate.name));visit(gate,actor)
 for phase in ["open","close"]:
  gate.interact(actor)
  for i in range(100):
   await physics_frame
   if i%5==0:checked_pose(gate,space,i,phase)
  ck(gate.open_fraction==(1.0 if phase=="open"else 0.0),"original controller endpoint "+phase+" "+str(gate.name))
 # Open for the source floor and worker stance samples.
 gate.interact(actor)
 for i in range(100):await physics_frame
func rids(n:Node)->Array[RID]:
 var out:Array[RID]=[]
 if n is CollisionObject3D:out.append(n.get_rid())
 for c in n.get_children():out.append_array(rids(c))
 return out
func _initialize():call_deferred("run")
func run():
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_COMMONS_RECOMPOSITION.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var districts:Node3D=ship.get_node("ShipSpace/Districts");var space:=ship.get_world_3d().direct_space_state;var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var retained:Dictionary={};var excluded:Array=[]
 for pre in p.runtime_preimages:excluded.append(districts.get_node(pre.source_root).find_child(pre.name,true,false))
 for mesh:MeshInstance3D in districts.find_children("*","MeshInstance3D",true,false):
  if not mesh in excluded:retained[str(mesh.get_path())]={"node":mesh,"faces":mesh.mesh.get_faces(),"pose":mesh.global_transform}
 var n:Node3D=load("res://scripts/d04_port_central_commons_recomposition.gd").build(ship,true)
 for i in range(60):await physics_frame
 for key in retained:
  var q:Dictionary=retained[key];ck(is_instance_valid(q.node),"retained mesh exists "+key)
  if is_instance_valid(q.node):ck(q.node.mesh.get_faces()==q.faces and q.node.global_transform==q.pose,"retained geometry/pose exact "+key)
 var parts:Array=p.parts.duplicate();parts.append_array(p.copied_gate_parts)
 for part in parts:
  var mesh:MeshInstance3D=n.find_child(str(part.name).replace(".","_"),true,false);ck(mesh!=null,"native part "+part.name)
  if mesh==null:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for at in part.verts:lo=lo.min(v(at));hi=hi.max(v(at))
  var a:AABB=mesh.global_transform*mesh.get_aabb();ck(a.position.distance_to(lo)<.001 and a.end.distance_to(hi)<.001,"actual native bounds "+part.name)
 for row in p.moves:
  if row.name in p.front_clip_boxes:continue
  var pre:Dictionary=p.runtime_preimages.filter(func(q):return q.name==row.name)[0];var mesh:MeshInstance3D=n.find_child(row.name,true,false);ck(mesh!=null,"rigid native successor "+row.name)
  if mesh==null:continue
  var a:AABB=mesh.global_transform*mesh.get_aabb();ck(a.position.distance_to(v(pre.bounds[0])+v(row.delta))<.002 and a.end.distance_to(v(pre.bounds[1])+v(row.delta))<.002,"translated source bounds "+row.name)
 # Geometric bearings on source floor edges; no new lower-programme columns.
 var ex:=rids(n);var joints:Array=[]
 for x in [-96.0]:
  for z in [-.95,.95]:
   for y in [16.29,16.46]:
    var at:=Vector3(x,y,z);var ray:=PhysicsRayQueryParameters3D.create(at-Vector3.RIGHT*.1,at+Vector3.RIGHT*.1);ray.exclude=ex;ray.hit_back_faces=true;var h=space.intersect_ray(ray);ck(not h.is_empty(),"source bridge floor-edge joint exists")
    if not h.is_empty():joints.append({"point":[h.position.x,h.position.y,h.position.z],"owner":str(h.collider.get_path())});ck(abs(h.position.x-x)<.001 and str(h.collider.get_parent().name)in["PCW_PerimeterFloor","PCC_CommonsFloor"],"bridge joint exact floor identity")
 for x in [-102.0,-100.0,-98.0]:
  var at:=Vector3(x,16.5,0);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.1);ray.exclude=ex;ck(space.intersect_ray(ray).is_empty(),"bridge floor missing-only")
 for g in p.gates:await gate_poses(n.get_node(g.name),actor,space,false)
 var samples:Array=p.route_samples.duplicate();samples.append_array(p.guest_route_points)
 for at_array in samples:
  var at:=v(at_array);var cap:=CapsuleShape3D.new();cap.height=1.8;cap.radius=.3;cap.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var hits=space.intersect_shape(q,64);ck(hits.is_empty(),"worker/guest clearance "+str(at))
  if not hits.is_empty():print("STANCE_CONTACT ",at," ",hits.map(func(h):return str(h.collider.get_path())))
  var h=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.1));ck(not h.is_empty()and abs(h.position.y-at.y)<.001,"actual retained/new floor "+str(at))
 for g in p.gates:
  var gate:Node3D=n.get_node(g.name);var stranger:=CharacterBody3D.new();n.add_child(stranger);gate.interact(stranger);ck(gate.access_refused,"foreign actor denied staff route "+g.name);stranger.free()
 for root_name in ["D04PortCentralCourtWorkLinks","D04PortCentralWestStaffCircuit","D04StarboardForwardWorkBranches","D04StarboardForwardRemainingCourts"]:
  var owner:Node3D=districts.get_node(root_name)
  for gate:Node in owner.get_children():
   if "fitting"in gate and gate.fitting.requires_visit:ck(gate.visit==null and not gate.desired_open and gate.open_fraction==0,"prior private gate remains defaultclosed/no provider "+str(gate.name))
 for pair in [[[-88,17.5,3],[-88,17.5,2]], [[-85.5,17.5,1.5],[-87,17.5,1.5]], [[-91.5,17.5,-8.2],[-94,17.5,-8.2]], [[-88,17.5,-10],[-88,17.5,-8]], [[-86.115,17.5,-7],[-87,17.5,-7]]]:
  var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(v(pair[0]),v(pair[1])));ck(not hit.is_empty()and (str(hit.collider.get_parent().name).begins_with("PCR_")or str(hit.collider.get_parent().name)=="PCC_ServiceWest"),"physical guest/staff separation boundary")
 var h:Node3D=districts.get_node(p.source_co_root);ck(h.get_meta("preserved_home_allocations")==20 and h.get_meta("preserved_reserved_rests")==25,"original homes/rests preserved")
 ck(FileAccess.get_sha256("res://data/whole_ship_layout.json")==p.protected_programme_layout_sha256,"protected allocations unchanged")
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks,"errors":errors,"contact_rows":contacts,"model_pins":p.model_pins,"exact_retained_original_meshes":retained.size(),"runtime_exact_preimages":p.runtime_preimages.size(),"source_floor_edge_joints":joints,"actual_original_controller_gate_pose_samples":pose_count,"worker_and_guest_capsule_samples":samples.size(),"new_missing_floor_m2":p.new_floor_m2,"production_private_consent_provider_available":false,"ordinary_game_visual_acceptance":false,"limits":p.limits};FileAccess.open("res://artifacts/d04_port_central_commons_recomposition_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
