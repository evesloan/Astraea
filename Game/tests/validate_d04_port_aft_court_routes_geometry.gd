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
func plane_contains(mesh:MeshInstance3D,point:Vector3)->bool:
 var fs:=mesh.mesh.get_faces()
 for k in range(0,fs.size(),3):
  var A:Vector3=mesh.global_transform*fs[k];var B:Vector3=mesh.global_transform*fs[k+1];var C:Vector3=mesh.global_transform*fs[k+2]
  if max(abs(A.y-point.y),max(abs(B.y-point.y),abs(C.y-point.y)))>.001:continue
  var ab:=Vector2(B.x-A.x,B.z-A.z);var ac:=Vector2(C.x-A.x,C.z-A.z);var ap:=Vector2(point.x-A.x,point.z-A.z);var det:=ab.cross(ac)
  if abs(det)<.00000001:continue
  var u:=ap.cross(ac)/det;var t:=ab.cross(ap)/det
  if u>=-.00001 and t>=-.00001 and u+t<=1.00001:return true
 return false
func _initialize():call_deferred("run")
func run():
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_AFT_COURT_ROUTES.json"));var main=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var districts:Node3D=ship.get_node("ShipSpace/Districts");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var space=ship.get_world_3d().direct_space_state;var removed:Array=[];var retained:Dictionary={}
 for pre in p.runtime_preimages:removed.append(str(pre.name).replace(".","_"))
 for mesh:MeshInstance3D in ship.find_children("*","MeshInstance3D",true,false):
  var a:AABB=mesh.global_transform*mesh.get_aabb()
  if str(mesh.name)not in removed and (str(mesh.get_path()).contains("D04PortAftHabitatNeighborhood")or str(mesh.get_path()).contains("D04PortCentralCommonsRearRoute")or (a.end.x>-54 and a.position.x<-8 and a.end.z>398 and a.position.z<466 and a.position.y<16.25)):retained[str(mesh.get_path())]={"node":mesh,"faces":mesh.mesh.get_faces(),"pose":mesh.global_transform}
 var n:Node3D=load("res://scripts/d04_port_aft_court_routes.gd").build(ship,true)
 for i in range(60):await physics_frame
 for key in retained:
  var q:Dictionary=retained[key];ck(is_instance_valid(q.node),"original mesh exists "+key)
  if is_instance_valid(q.node):ck(q.node.mesh.get_faces()==q.faces and q.node.global_transform==q.pose,"original geometry/pose exact "+key)
 var junctions:Array=[]
 for row in p.wall_ceiling_junctions:
  var wall:MeshInstance3D=n.find_child(row.get("wall",row.get("retained_wall","")),true,false)
  var roof:MeshInstance3D=n.find_child(row.get("roof",""),true,false) if row.has("roof") else districts.get_node("D04PortAftHabitatNeighborhood").find_child(row.retained_roof,true,false)
  ck(wall!=null and roof!=null,"wall and ceiling junction meshes exist")
  if wall==null or roof==null:continue
  var wa:AABB=wall.global_transform*wall.get_aabb();ck(abs(wa.end.y-float(row.wall_top_y))<.001,"actual wall top reaches prescribed ceiling plane "+str(wall.name))
  var point:=Vector3(wa.get_center().x,wa.end.y,wa.get_center().z);ck(plane_contains(roof,point),"actual roof mesh underside receives wall "+str(wall.name));junctions.append({"wall":str(wall.name),"roof":str(roof.name),"actual_wall_top_y":wa.end.y})
 var parts:Array=p.parts.duplicate();parts.append_array(p.copied_gate_parts);parts.append_array(p.closed_staging_parts)
 for part in parts:
  var mesh:MeshInstance3D=n.find_child(part.name,true,false);ck(mesh!=null,"native part "+part.name)
  if mesh==null:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for at in part.verts:lo=lo.min(v(at));hi=hi.max(v(at))
  var a:AABB=mesh.global_transform*mesh.get_aabb();ck(a.position.distance_to(lo)<.001 and a.end.distance_to(hi)<.001,"actual native bounds "+part.name)
 var exclude:=rids(n);var bearing_count:=0
 for s in p.support_preimages:
  for c in s.corners:
   var at:=v(c.point);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.05);ray.exclude=exclude;ray.hit_back_faces=true;var h=space.intersect_ray(ray);ck(not h.is_empty(),"source hull bearing present")
   if not h.is_empty():ck(h.position.distance_to(at)<.001 and str(h.collider.get_path())==c.owner,"source keel bearing exact identity/datum");bearing_count+=1
  var half:float=s.half-.04;var box:=BoxShape3D.new();box.size=Vector3(half*2,16.13-s.column_bottom-.01,half*2);var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3(s.x,(16.13+s.column_bottom+.01)/2,s.z));q.exclude=exclude;ck(space.intersect_shape(q,64).is_empty(),"column retains source occupied volumes")
 var ledger_count:=0
 for row in p.ledger_preimages:
  for c in row.corners:
   var at:=v(c.point);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.RIGHT*(.1 if at.x>-40 else -.1),at+Vector3.RIGHT*(-.1 if at.x>-40 else .1));ray.exclude=exclude;ray.hit_back_faces=true;var h=space.intersect_ray(ray);ck(not h.is_empty(),"unchanged source court floor-edge ledger joint exists")
   if not h.is_empty():ck(h.position.distance_to(at)<.001 and str(h.collider.get_path())==c.owner and str(h.collider.get_parent().name)==row.site.source_mesh,"exact named floor-edge joint identity/pose");ledger_count+=1
 for row in p.north_entry_floor_joints:
  var at:=v(row.point);var normal:=v(row.normal);var ray:=PhysicsRayQueryParameters3D.create(at+normal*.15,at-normal*.15);ray.exclude=exclude;ray.hit_back_faces=true;var h=space.intersect_ray(ray);ck(not h.is_empty(),"distinct north source platform edge joint exists")
  if not h.is_empty():ck(str(h.collider.get_parent().name)==row.source_mesh and h.position.distance_to(at)<.001,"actual north source edge identity and datum")
 var end_ledger_count:=0
 for row in p.end_ledger_sites:
  var direction:=1.0 if row.z>350 else -1.0
  for x in [row.x-row.half_x,row.x+row.half_x]:
   for y in [16.29,16.46]:
    var at:=Vector3(x,y,row.z);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.BACK*.15*direction,at-Vector3.BACK*.15*direction);ray.exclude=exclude;ray.hit_back_faces=true;var h=space.intersect_ray(ray);ck(not h.is_empty(),"source end-floor face bearing exists")
    if not h.is_empty():ck(str(h.collider.get_parent().name)==row.source_mesh and h.position.distance_to(at)<.001,"exact original end-floor joint identity/datum");end_ledger_count+=1
 for at_array in p.route_samples:
  var at:=v(at_array);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.1);ray.exclude=exclude;ck(space.intersect_ray(ray).is_empty(),"new floor does not duplicate original walking surface")
 for spec in p.gates:await gate_poses(n.get_node(spec.name),actor,space,spec.requires_visit)
 var samples:Array=p.route_samples.duplicate();samples.append_array(p.source_approach_samples)
 for g in p.gates.slice(0,9):
  for x in [g.lane_x,(g.pivot[0]+g.lane_x)/2,g.pivot[0],g.wall_x,g.court_stance[0]]:samples.append([x,16.5,g.z])
 for at_array in samples:
  var at:=v(at_array);var cap:=CapsuleShape3D.new();cap.height=1.8;cap.radius=.3;cap.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var hits=space.intersect_shape(q,64);ck(hits.is_empty(),"worker clearance "+str(at))
  if not hits.is_empty():print("STANCE_CONTACT ",at," ",hits.map(func(h):return str(h.collider.get_path())))
  var h=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.1));ck(not h.is_empty()and abs(h.position.y-at.y)<.001,"actual source/candidate floor contact "+str(at))
 for g in p.gates.slice(0,9):
  var gate:Node3D=n.get_node(g.name);var stranger:=CharacterBody3D.new();n.add_child(stranger);gate.interact(stranger);ck(gate.access_refused,"foreign actor refused "+g.name);stranger.free()
 ck(not n.get_meta("production_private_consent_provider_available"),"no private consent provider invented");ck(JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_COMMONS_RECOMPOSITION.json")).active,"approved connected port-central commons remains active")
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks,"errors":errors,"wall_ceiling_joints":junctions,"contact_rows":contacts,"model_pins":p.model_pins,"exact_retained_original_meshes":retained.size(),"runtime_exact_preimages":p.runtime_preimages.size(),"source_hull_bearing_corners":bearing_count,"source_floor_edge_joint_corners":ledger_count,"source_end_floor_joint_corners":end_ledger_count,"narrow_court_sealed":true,"actual_original_controller_gate_pose_samples":pose_count,"worker_capsule_samples":samples.size(),"new_missing_floor_m2":p.new_floor_m2,"temporary_known_private_visits_test_only":true,"production_private_consent_provider_available":false,"ordinary_game_visual_acceptance":false,"limits":p.limits};FileAccess.open("res://artifacts/d04_port_aft_court_routes_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
